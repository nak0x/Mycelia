import gc
from lib.uwebsockets.client import connect as ws_connect
from src.app import App
from src.utils.frames.frame_parser import FrameParser

class WebsocketClient():
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
        Blocking ws loop !
            - Send a heartbeat message
            - Wait for a reply (recv blocks)
        """
        if self.CLOSED:
            return
        if self.CONNECTED:
            try:
                self.ws.send("up")
                FrameParser(self.ws.recv())
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
