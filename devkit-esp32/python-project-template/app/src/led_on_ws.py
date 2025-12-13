from src.app import App

class WSLed:
    def __init__(self):
        App().on_frame_received.append(self.handle_frame)

    def handle_frame(self, frame):
        if frame.payload[0].slug == "led":
            App().config.pins["led"].value(1 if frame.payload[0].value else 0)