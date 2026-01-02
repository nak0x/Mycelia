import time
import gc
from .client import connect as ws_connect
from framework.app import App
from framework.utils.frames.frame_parser import FrameParser
from framework.utils.frames.frame import Frame, Metadata
from framework.utils.abstract_singleton import SingletonBase

class WebsocketInterface(SingletonBase):
    CONNECTED = False
    CLOSED = False
    RECONNECT = False

    ws = None

    def __init__(self):
        App().setup.append(self.connect)
        App().update.append(self.update)
        self.RECONNECT = App().config.websocket.reconnect

    def connect(self):
        print("Websocket connecting ...")
        try:
            self.ws = ws_connect(App().config.websocket.server)
        except Exception as e:
            print(f"An error occured while connecting websocket: {e}")
            return
        self.CONNECTED = True
        print("Websocket connected")

    def send_value(self, action: str, value: any):
        frame = Frame(
            metadata={
                "senderId": App().config.device_id,
                "timestamp": int(time.time()),
            },
            action=action,
            value=value,
        )
        self.send_frame(frame)

    def send_frame(self, frame):
        self.ws.send(frame.to_json())

    def update(self):
        """
        Non-blocking ws loop.
            - Send a heartbeat message
            - Check for incoming messages (recv is now non-blocking)
            - Print a message when server gets disconnected
        """
        # The self.ws only exist when we establish connection. Otherwise it's None
        if self.ws:
            self.CONNECTED = self.ws.check_connection()
        if self.CLOSED:
            return
        if self.CONNECTED:
            try:
                # Check for incoming messages (non-blocking)
                data = self.ws.recv()
                if data:  # Only process if data is available
                    print(f"Recv: {data} from {self.ws.get_remote_address()}")
                    frame = FrameParser(data).parse()
                    print(f"Recv: {frame.action} from {frame.metadata.sender_id}")
                    App().broadcast_frame(frame)
            except Exception as e:
                print(f"An error occured while updating websocket: {e}")
                if self.CONNECTED:
                    print("Websocket server disconnected.")
                self.close(not self.RECONNECT)
        elif self.RECONNECT:
            self.connect()

    async def aupdate(self):
        """
        Async update method using arecv().
        Use this with uasyncio for fully asynchronous websocket handling.
        
        Example:
            import uasyncio as asyncio
            ws_interface = WebsocketInterface()
            asyncio.create_task(ws_interface.aupdate())
        """
        if self.CLOSED:
            return
        if self.CONNECTED:
            try:
                data = await self.ws.arecv()
                if data:  # Only process if data is available
                    frame = FrameParser(data).parse()
                    print(f"Recv: {frame.action} from {frame.metadata.sender_id}")
                    App().broadcast_frame(frame)
            except Exception as e:
                print(f"An error occured while updating websocket: {e}")
                if self.CONNECTED:
                    print("Websocket server disconnected.")
                self.close(not self.RECONNECT)
        elif self.RECONNECT:
            self.connect()

    def close(self, shutdown=True):
        self.CONNECTED = False
        self.CLOSED = shutdown
        try:
            self.ws.close()
        except Exception as e:
            print(f"An error occured when closing websocket: {e}")
            del self.ws
            gc.collect()
            pass
