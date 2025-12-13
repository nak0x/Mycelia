import gc
from .client import connect as ws_connect
from src.app import App
from src.utils.frames.frame_parser import FrameParser

class WebsocketInterface():
    CONNECTED = False
    CLOSED = False
    RECONNECT = False

    ws = None

    def __init__(self):
        App().update.append(self.update)
        App().setup.append(self.connect)
        self.RECONNECT = App().config.ws_reconnect

    def connect(self):
        print("Websocket connecting ...")
        try:
            self.ws = ws_connect(App().config.ws_server)
        except Exception as e:
            print(f"An error occured while connecting websocket: {e}")
            return
        self.CONNECTED = True
        print("Websocket connected")

    def update(self):
        """
        Non-blocking ws loop.
            - Send a heartbeat message
            - Check for incoming messages (recv is now non-blocking)
        """
        if self.CLOSED:
            return
        if self.CONNECTED:
            try:
                # Check for incoming messages (non-blocking)
                data = self.ws.recv()
                if data:  # Only process if data is available
                    frame = FrameParser(data).parse()
                    print(f"Recv: {frame.metadata.message_id} from {frame.metadata.sender_id}")
                    App().send_frame(frame)
            except Exception as e:
                print(f"An error occured while updating websocket: {e}")
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
                    print(f"Recv: {frame.metadata.message_id} from {frame.metadata.sender_id}")
                    App().send_frame(frame)
            except Exception as e:
                print(f"An error occured while updating websocket: {e}")
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
