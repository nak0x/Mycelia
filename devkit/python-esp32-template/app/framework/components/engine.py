from machine import Pin
from framework.app import App
from framework.utils.frames.frame import Frame

class Engine:
    is_on = False

    def __init__(self, pin, action = None, on_payload_received = None):
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.action = action
        self.on_payload_received_callback = on_payload_received
        App().on_frame_received.append(self.on_frame_received)

    def on(self):
        self.pin.on()
        self.is_on = True

    def off(self):
        self.pin.off()
        self.is_on = False

    def on_frame_received(self, frame: Frame):
        if frame.action != self.action:
            return

        if self.on_payload_received_callback is not None:
            self.on_payload_received_callback(self, frame.value)
        elif isinstance(frame.value, bool):
            self.on() if frame.value else self.off()
        
