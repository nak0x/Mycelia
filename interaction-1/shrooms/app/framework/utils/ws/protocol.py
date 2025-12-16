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

# Opcode names for logging
OPCODE_NAMES = {
    OP_CONT: "CONT",
    OP_TEXT: "TEXT",
    OP_BYTES: "BYTES",
    OP_CLOSE: "CLOSE",
    OP_PING: "PING",
    OP_PONG: "PONG",
}

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
        print(opcode)
        print(fin)

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
            print(data)
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
        opcode_name = OPCODE_NAMES.get(opcode, f"UNKNOWN(0x{opcode:x})")
        
        # Log outgoing frame
        if opcode == OP_PING or opcode == OP_PONG:
            print(f"[WS OUT] {opcode_name} (len={length})")
        elif opcode == OP_CLOSE:
            print(f"[WS OUT] {opcode_name} (len={length})")
        elif opcode == OP_TEXT:
            try:
                text_preview = data.decode('utf-8')[:50] if data else ""
                print(f"[WS OUT] {opcode_name} (len={length}): {text_preview}")
            except:
                print(f"[WS OUT] {opcode_name} (len={length})")
        else:
            print(f"[WS OUT] {opcode_name} (len={length})")

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
       
        # Flush socket to ensure data is sent immediately, especially critical for PONG responses
        # In MicroPython, socket writes may be buffered
        try:
            self.sock.flush()
        except AttributeError:
            # Some MicroPython implementations don't have flush(), that's okay
            pass

    def recv(self):
        """
        Receive data from the websocket (non-blocking).

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        
        Returns empty string if no data is available (non-blocking).
        This method processes ALL available frames including PING/PONG to
        maintain keepalive, even when no data frames are present.
        """
        assert self.open

        # Track if we've processed any frames to avoid infinite loops
        frames_processed = 0
        max_frames_per_call = 100  # Prevent infinite loops
        
        # Process all available frames in one call
        # This ensures PING frames are always processed even if no data frames are available
        while self.open and frames_processed < max_frames_per_call:
            # Check if data is available before attempting to read
            has_data = self._has_data(0)
            if not has_data:
                # No data available
                # If we haven't processed any frames, return immediately
                if frames_processed == 0:
                    return ''
                # If we've processed some frames (like PING), we're done processing this batch
                break

            try:
                fin, opcode, data = self.read_frame()
                frames_processed += 1
                opcode_name = OPCODE_NAMES.get(opcode, f"UNKNOWN(0x{opcode:x})")
                print(opcode_name, opcode)
                
                # Log incoming frame
                if opcode == OP_PING:
                    print(f"[WS IN]  {opcode_name} (len={len(data)}) - RESPONDING WITH PONG")
                elif opcode == OP_PONG:
                    print(f"[WS IN]  {opcode_name} (len={len(data)})")
                elif opcode == OP_CLOSE:
                    print(f"[WS IN]  {opcode_name} (len={len(data)})")
                elif opcode == OP_TEXT:
                    try:
                        text_preview = data.decode('utf-8')[:50] if data else ""
                        print(f"[WS IN]  {opcode_name} (len={len(data)}): {text_preview}")
                    except:
                        print(f"[WS IN]  {opcode_name} (len={len(data)})")
                else:
                    print(f"[WS IN]  {opcode_name} (len={len(data)})")
                    
            except NoDataException:
                # No more data available in this batch
                break
            except ValueError:
                print("[WS ERROR] Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                # Return data frame immediately
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                # Return data frame immediately
                return data
            elif opcode == OP_CLOSE:
                # Extract close code from received frame (first 2 bytes if present)
                close_code = CLOSE_OK
                if data and len(data) >= 2:
                    close_code = struct.unpack('!H', data[:2])[0]
                # Send close frame back to server (RFC 6455 requires this)
                try:
                    self.write_frame(OP_CLOSE, data[:2] if data and len(data) >= 2 else struct.pack('!H', CLOSE_OK))
                except:
                    pass  # Socket might already be closed
                self._close()
                return
            elif opcode == OP_PONG:
                # Ignore this frame, keep processing remaining frames
                continue
            elif opcode == OP_PING:
                # CRITICAL: Send PONG immediately to keep connection alive
                # This must be done even if no data frames are available
                print(f"[WS] Processing PING, sending PONG response...")
                try:
                    self.write_frame(OP_PONG, data)
                    print(f"[WS] PONG sent successfully")
                except Exception as e:
                    print(f"[WS ERROR] Failed to send PONG: {e}")
                    self._close()
                    raise ConnectionClosed()
                # Continue processing any remaining frames
                continue
            elif opcode == OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)
        
        # Return empty string if no data frame was received
        # Note: Control frames (PING/PONG) have been processed above
        return ''

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
                # Extract close code from received frame (first 2 bytes if present)
                close_code = CLOSE_OK
                if data and len(data) >= 2:
                    close_code = struct.unpack('!H', data[:2])[0]
                # Send close frame back to server (RFC 6455 requires this)
                try:
                    self.write_frame(OP_CLOSE, data[:2] if data and len(data) >= 2 else struct.pack('!H', CLOSE_OK))
                except:
                    pass  # Socket might already be closed
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

        # Log is handled in write_frame, but add context here
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
