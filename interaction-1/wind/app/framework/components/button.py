from framework.app import App
from machine import Pin

class Button:
    pressed = False

    def __init__(self, pin, onPress = None, onRelease = None):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.onPress = onPress
        self.onRelease = onRelease
        App().update.append(self.update)

    def update(self):
        if self.pin.value() == 1:
            if not self.pressed:
                self.pressed = True
                if self.onPress is not None:
                    self.onPress()
        else:
            if self.pressed:
                self.pressed = False
                if self.onRelease is not None:
                    self.onRelease()
