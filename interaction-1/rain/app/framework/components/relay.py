from framework.app import App
from machine import Pin
from framework.utils.frames.frame import Frame

class Relay:
    is_open = False

    def __init__(self, pin, slug = None, on_payload_received = None):
        self.pin = Pin(pin, Pin.OUT)
        self.slug = slug
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
        if self.slug is None:
            return
        
        for payload in frame.payload:
            if payload.slug == self.slug:
                if self.on_payload_received_callback is not None:
                    self.on_payload_received_callback(self, payload)
                elif payload.datatype == "bool":
                    self.open() if payload.value else self.close()

    