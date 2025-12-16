"""
Websockets protocol
"""

import ure as re
import ustruct as struct
import urandom as random
import usocket as socket
import uselect
from ucollections import namedtuple
from framework.app import App

try:
    import uasyncio as asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    import uerrno as errno
except ImportError:
    import errno


# Opcodes
OP_CONT = const(0x0)
OP_TEXT = const(0x1)
OP_BYTES = const(0x2)
OP_CLOSE = const(0x8)
OP_PING = const(0x9)
OP_PONG = const(0xa)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)

URL_RE = re.compile(r'(wss|ws)://([A-Za-z0-9-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('protocol', 'hostname', 'port', 'path'))


class NoDataException(Exception):
    pass


class ConnectionClosed(Exception):
    pass


def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        protocol = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path = match.group(4)

        if protocol == 'wss':
            if port is None:
                port = 443
        elif protocol == 'ws':
            if port is None:
                port = 80
        else:
            raise ValueError('Scheme {} is invalid'.format(protocol))

        return URI(protocol, host, int(port), path)


class Websocket:
    """
    Basis of the Websocket protocol.

    This can probably be replaced with the C-based websocket module, but
    this one currently supports more options.
    """
    is_client = False

    def __init__(self, sock):
        self.sock = sock
        self.open = True

        # Set socket to non-blocking mode for async operations
        self.sock.setblocking(False)

        # Poll object used for readiness / error checks
        self.poll = uselect.poll()
        self.poll.register(self.sock, uselect.POLLIN)

        # RX buffer for non-blocking partial reads
        self._rx = bytearray()

        if App().config.websocket.debug:
            print("[ws] init: non-blocking socket, poll registered, rx buffer created")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def _has_data(self, timeout=0) -> bool:
        """
        Poll-only readiness check for THIS socket.

        - Returns True if readable (POLLIN).
        - Closes and returns False on ERR/HUP/NVAL.
        """
        POLLNVAL = getattr(uselect, "POLLNVAL", 0)
        fatal_mask = uselect.POLLERR | uselect.POLLHUP | POLLNVAL

        try:
            events = self.poll.poll(timeout)
        except Exception as e:
            if App().config.websocket.debug:
                print("[ws] _has_data: poll failed:", repr(e))
            self._close()
            return False

        if App().config.websocket.debug and events:
            print("[ws] _has_data: events:", events)

        for obj, flags in events:
            if obj is self.sock:
                if flags & fatal_mask:
                    if App().config.websocket.debug:
                        print("[ws] _has_data: fatal flags:", flags)
                    self._close()
                    return False
                ready = bool(flags & uselect.POLLIN)
                if App().config.websocket.debug:
                    print("[ws] _has_data: ready=", ready, "flags=", flags)
                return ready

        return False

    def check_connection(self) -> bool:
        """
        Connection health check compatible with a frame-based recv().

        - Uses poll(0) to detect ERR/HUP/NVAL.
        - If POLLIN is set, calls recv() once to process control frames (PING/CLOSE).
          This prevents servers from disconnecting due to unprocessed control frames.
        - Does NOT touch the raw socket outside the frame parser.
        """
        if not self.open:
            if App().config.websocket.debug:
                print("[ws] check_connection: not open")
            return False

        POLLNVAL = getattr(uselect, "POLLNVAL", 0)
        fatal_mask = uselect.POLLERR | uselect.POLLHUP | POLLNVAL

        try:
            events = self.poll.poll(0)
        except Exception as e:
            if App().config.websocket.debug:
                print("[ws] check_connection: poll failed:", repr(e))
            self._close()
            return False

        if not events:
            if App().config.websocket.debug:
                print("[ws] check_connection: no events -> ok")
            return True

        if App().config.websocket.debug:
            print("[ws] check_connection: events:", events)

        for obj, flags in events:
            if obj is not self.sock:
                continue

            if flags & fatal_mask:
                if App().config.websocket.debug:
                    print("[ws] check_connection: fatal flags:", flags)
                self._close()
                return False

            if flags & uselect.POLLIN:
                if App().config.websocket.debug:
                    print("[ws] check_connection: POLLIN -> calling recv() to process control frames")
                try:
                    _ = self.recv()
                except OSError as e:
                    if e.args and e.args[0] == errno.EAGAIN:
                        if App().config.websocket.debug:
                            print("[ws] check_connection: recv() EAGAIN -> ok")
                    else:
                        if App().config.websocket.debug:
                            print("[ws] check_connection: recv() socket error:", repr(e))
                        self._close()
                        return False
                except ConnectionClosed:
                    if App().config.websocket.debug:
                        print("[ws] check_connection: ConnectionClosed from recv()")
                    return False
                except Exception as e:
                    if App().config.websocket.debug:
                        print("[ws] check_connection: recv() failed:", repr(e))
                    self._close()
                    return False

        return True

    def _fill_rx(self) -> None:
        """
        Pull whatever is available from the non-blocking socket into self._rx.

        Raises:
          - NoDataException if nothing can be read right now (EAGAIN)
          - ConnectionClosed if peer closed (recv returned b"")
          - OSError for real socket errors
        """
        try:
            chunk = self.sock.recv(1024)
        except OSError as e:
            if e.args and e.args[0] == errno.EAGAIN:
                if App().config.websocket.debug:
                    print("[ws] _fill_rx: EAGAIN (no data right now)")
                raise NoDataException()
            if App().config.websocket.debug:
                print("[ws] _fill_rx: socket error:", repr(e))
            raise

        if chunk == b"":
            if App().config.websocket.debug:
                print("[ws] _fill_rx: recv returned b'' -> peer closed")
            raise ConnectionClosed()

        self._rx.extend(chunk)
        if App().config.websocket.debug:
            print("[ws] _fill_rx: read", len(chunk), "bytes; rx_len=", len(self._rx))

    def _read_exactly(self, n: int) -> bytes:
        """
        Return exactly n bytes from the buffered stream, or raise NoDataException
        if not enough bytes are currently available.
        """
        while len(self._rx) < n:
            self._fill_rx()

        out = bytes(self._rx[:n])
        self._rx[:] = self._rx[n:]

        if App().config.websocket.debug:
            print("[ws] _read_exactly:", n, "bytes; remaining rx_len=", len(self._rx))

        return out

    def read_frame(self, max_size=None):
        """
        Read a frame from the socket (non-blocking safe).

        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.

        Raises:
          - NoDataException if not enough bytes are available yet
          - ConnectionClosed if peer closed the TCP socket
          - ValueError on protocol errors
        """
        # Frame header (2 bytes)
        b1, b2 = struct.unpack("!BB", self._read_exactly(2))

        fin = bool(b1 & 0x80)
        opcode = b1 & 0x0F

        masked = bool(b2 & 0x80)
        length = (b2 & 0x7F)

        if App().config.websocket.debug:
            print("[ws] read_frame: fin=", fin, "opcode=", opcode, "masked=", masked, "len7=", length)

        if length == 126:
            (length,) = struct.unpack("!H", self._read_exactly(2))
            if App().config.websocket.debug:
                print("[ws] read_frame: extended len16=", length)
        elif length == 127:
            (length,) = struct.unpack("!Q", self._read_exactly(8))
            if App().config.websocket.debug:
                print("[ws] read_frame: extended len64=", length)

        if max_size is not None and length > max_size:
            if App().config.websocket.debug:
                print("[ws] read_frame: payload too big:", length, "max_size=", max_size, "-> closing")
            self.close(code=CLOSE_TOO_BIG)
            return True, OP_CLOSE, None

        mask_bits = b""
        if masked:
            mask_bits = self._read_exactly(4)
            if App().config.websocket.debug:
                print("[ws] read_frame: mask_bits read")

        payload = self._read_exactly(length) if length else b""
        if App().config.websocket.debug:
            print("[ws] read_frame: payload_len=", len(payload))

        if masked:
            payload = bytes(b ^ mask_bits[i & 3] for i, b in enumerate(payload))

        return fin, opcode, payload

    def write_frame(self, opcode, data=b''):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        if App().config.websocket.debug:
            print("[ws] write_frame: opcode=", opcode, "len=", length, "mask=", mask)

        # Frame header
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        byte2 = 0x80 if mask else 0

        if length < 126:
            byte2 |= length
            self.sock.write(struct.pack('!BB', byte1, byte2))
        elif length < (1 << 16):
            byte2 |= 126
            self.sock.write(struct.pack('!BBH', byte1, byte2, length))
        elif length < (1 << 64):
            byte2 |= 127
            self.sock.write(struct.pack('!BBQ', byte1, byte2, length))
        else:
            raise ValueError()

        if mask:
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self.sock.write(mask_bits)
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        self.sock.write(data)

    def recv(self):
        """
        Receive data from the websocket (non-blocking).

        Returns:
          - '' if no data is available
          - str for text frames
          - bytes for binary frames
          - None on CLOSE (after replying with CLOSE and closing internally)
        """
        assert self.open

        if not self._has_data(0):
            if App().config.websocket.debug:
                print("[ws] recv: no data")
            return ''

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                if App().config.websocket.debug:
                    print("[ws] recv: partial frame / no data yet")
                return ''
            except ConnectionClosed:
                if App().config.websocket.debug:
                    print("[ws] recv: underlying TCP closed")
                self._close()
                raise
            except ValueError as e:
                if App().config.websocket.debug:
                    print("[ws] recv: protocol error:", repr(e))
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                if App().config.websocket.debug:
                    print("[ws] recv: TEXT frame")
                return data.decode('utf-8')

            elif opcode == OP_BYTES:
                if App().config.websocket.debug:
                    print("[ws] recv: BYTES frame")
                return data

            elif opcode == OP_CLOSE:
                if App().config.websocket.debug:
                    print("[ws] recv: CLOSE frame received")

                close_code = CLOSE_OK
                if data and len(data) >= 2:
                    close_code = struct.unpack('!H', data[:2])[0]

                if App().config.websocket.debug:
                    print("[ws] recv: close_code=", close_code)

                # Reply with CLOSE (RFC 6455)
                try:
                    payload = data[:2] if data and len(data) >= 2 else struct.pack('!H', CLOSE_OK)
                    self.write_frame(OP_CLOSE, payload)
                except Exception as e:
                    if App().config.websocket.debug:
                        print("[ws] recv: failed to send CLOSE reply:", repr(e))

                self._close()
                return None

            elif opcode == OP_PONG:
                if App().config.websocket.debug:
                    print("[ws] recv: PONG frame (ignored)")
                continue

            elif opcode == OP_PING:
                if App().config.websocket.debug:
                    print("[ws] recv: PING frame -> sending PONG")
                self.write_frame(OP_PONG, data)
                continue

            elif opcode == OP_CONT:
                raise NotImplementedError(opcode)

            else:
                raise ValueError(opcode)

    async def arecv(self):
        """
        Asynchronously receive data from the websocket.
        """
        if not ASYNC_AVAILABLE:
            raise RuntimeError("uasyncio is not available. Install uasyncio for async support.")

        assert self.open

        while self.open:
            while not self._has_data(0):
                await asyncio.sleep_ms(10)

            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                await asyncio.sleep_ms(10)
                continue
            except ConnectionClosed:
                self._close()
                raise
            except ValueError as e:
                if App().config.websocket.debug:
                    print("[ws] arecv: protocol error:", repr(e))
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                if App().config.websocket.debug:
                    print("[ws] arecv: CLOSE received")
                try:
                    payload = data[:2] if data and len(data) >= 2 else struct.pack('!H', CLOSE_OK)
                    self.write_frame(OP_CLOSE, payload)
                except Exception as e:
                    if App().config.websocket.debug:
                        print("[ws] arecv: failed to send CLOSE reply:", repr(e))
                self._close()
                return None
            elif opcode == OP_PONG:
                continue
            elif opcode == OP_PING:
                self.write_frame(OP_PONG, data)
                continue
            elif opcode == OP_CONT:
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)

    def send(self, buf):
        """Send data to the websocket."""
        assert self.open

        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        if App().config.websocket.debug:
            print("[ws] send: opcode=", opcode, "len=", len(buf))

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=''):
        """Close the websocket."""
        if not self.open:
            if App().config.websocket.debug:
                print("[ws] close: code=", code, "reason=", reason)
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')

        try:
            self.write_frame(OP_CLOSE, buf)
        except Exception as e:
            if App().config.websocket.debug:
                print("[ws] close: failed to send CLOSE:", repr(e))

        self._close()

    def _close(self):
        if App().config.websocket.debug:
            print("[ws] _close: Connection closed")

        self.open = False

        try:
            self.poll.unregister(self.sock)
        except Exception as e:
            if App().config.websocket.debug:
                print("[ws] _close: cannot unregister:", repr(e))

        try:
            self.sock.close()
        except Exception as e:
            if App().config.websocket.debug:
                print("[ws] _close: sock.close failed:", repr(e))
