from framework.app import App
from machine import Pin
from framework.utils.frames.frame import Frame

class Relay:
    is_open = False

    def __init__(self, pin, action = None, on_payload_received = None):
        self.pin = Pin(pin, Pin.OUT)
        self.action = action
        self.on_payload_received_callback = on_payload_received
        App().on_frame_received.append(self.on_frame_received)

    def open(self):
        self.pin.value(0)
        self.is_open = True

    def close(self):
        self.pin.value(1)
        self.is_open = False

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def on_frame_received(self, frame: Frame):
        print(f"Relay : {frame} \n action: {self.action}")
        if self.action != frame.action:
            return

        if self.on_payload_received_callback is not None:
            self.on_payload_received_callback(self, frame.value)
        elif isinstance(frame.value, bool):
            self.close() if frame.value else self.open()
