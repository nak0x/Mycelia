from machine import Pin
from framework.app import App
from framework.utils.frames.frame import Frame

class Engine:
    is_on = False

    def __init__(self, pin, slug = None):
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.slug = slug
        App().on_frame_received.append(self.on_frame_received)

    def on(self):
        self.pin.on()
        self.is_on = True

    def off(self):
        self.pin.off()
        self.is_on = False

    def on_frame_received(self, frame: Frame):
        if self.slug is None:
            return
        
        for payload in frame.payload:
            if payload.slug == self.slug and payload.datatype == "bool":
                self.on() if payload.value else self.off()