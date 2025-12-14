from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.led_strip import LedStrip
from framework.utils.gpio import GPIO

class MainController(Controller):

    def setup(self):
        self.led_strip = LedStrip(GPIO.GPIO27, 108, "mycelium_led_strip")

    def update(self):
        pass

    def on_frame_received(self, frame: Frame):
        pass
