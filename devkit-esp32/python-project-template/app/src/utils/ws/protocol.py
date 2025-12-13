"""
Websockets protocol
"""

import ure as re
import ustruct as struct
import urandom as random
import usocket as socket
import uselect
from ucollections import namedtuple

try:
    import uasyncio as asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


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
        self.poll = uselect.poll()
        self.poll.register(self.sock, uselect.POLLIN)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def _has_data(self, timeout=0):
        """
        Check if socket has data available using poll.
        Returns True if data is available, False otherwise.
        """
        events = self.poll.poll(timeout)
        return len(events) > 0 and events[0][1] & uselect.POLLIN

    def read_frame(self, max_size=None):
        """
        Read a frame from the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """

        # Frame header
        two_bytes = self.sock.read(2)

        if not two_bytes or len(two_bytes) < 2:
            raise NoDataException

        byte1, byte2 = struct.unpack('!BB', two_bytes)

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0f

        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7f

        if length == 126:  # Magic number, length header is 2 bytes
            length_bytes = self.sock.read(2)
            if not length_bytes or len(length_bytes) < 2:
                raise NoDataException
            length, = struct.unpack('!H', length_bytes)
        elif length == 127:  # Magic number, length header is 8 bytes
            length_bytes = self.sock.read(8)
            if not length_bytes or len(length_bytes) < 8:
                raise NoDataException
            length, = struct.unpack('!Q', length_bytes)

        if mask:  # Mask is 4 bytes
            mask_bits = self.sock.read(4)
            if not mask_bits or len(mask_bits) < 4:
                raise NoDataException

        try:
            data = self.sock.read(length)
            if not data or len(data) < length:
                raise NoDataException
        except MemoryError:
            # We can't receive this many bytes, close the socket
            print("Frame of length %s too big. Closing", length)
            self.close(code=CLOSE_TOO_BIG)
            return True, OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b''):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self.sock.write(struct.pack('!BB', byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self.sock.write(struct.pack('!BBH', byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self.sock.write(struct.pack('!BBQ', byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self.sock.write(mask_bits)

            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        self.sock.write(data)

    def recv(self):
        """
        Receive data from the websocket (non-blocking).

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        
        Returns empty string if no data is available (non-blocking).
        """
        assert self.open

        # Check if data is available before attempting to read
        if not self._has_data(0):
            return ''

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                return ''
            except ValueError:
                print("Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                self._close()
                return
            elif opcode == OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            elif opcode == OP_PING:
                # We need to send a pong frame
                self.write_frame(OP_PONG, data)
                # And then wait to receive
                continue
            elif opcode == OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)

    async def arecv(self):
        """
        Asynchronously receive data from the websocket.
        
        This method yields control when no data is available, making it
        suitable for use with uasyncio.
        
        Usage:
            data = await ws.arecv()
        """
        if not ASYNC_AVAILABLE:
            raise RuntimeError("uasyncio is not available. Install uasyncio for async support.")
        
        assert self.open

        while self.open:
            # Wait for data to be available (yields control to event loop)
            while not self._has_data(0):
                await asyncio.sleep_ms(10)  # Yield control and wait a bit
            
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                # No data available, yield and try again
                await asyncio.sleep_ms(10)
                continue
            except ValueError:
                print("Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                self._close()
                return None
            elif opcode == OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            elif opcode == OP_PING:
                # We need to send a pong frame
                self.write_frame(OP_PONG, data)
                # And then wait to receive
                continue
            elif opcode == OP_CONT:
                # This is a continuation of a previous frame
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

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=''):
        """Close the websocket."""
        if not self.open:
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')

        self.write_frame(OP_CLOSE, buf)
        self._close()

    def _close(self):
        if __debug__: print("Connection closed")
        self.open = False
        try:
            self.poll.unregister(self.sock)
        except:
            pass
        self.sock.close()
