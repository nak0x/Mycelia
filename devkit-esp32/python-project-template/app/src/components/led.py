from src.app import App
from machine import Pin

class Led:
    is_on = False

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)

    def on(self):
        self.pin.on()
        self.is_on = True

    def off(self):
        self.pin.off()
        self.is_on = False
