from framework.controller import Controller
from framework.utils.frames.frame import Payload
from framework.components.led_strip import LedStrip
from framework.utils.gpio import GPIO

class MainController(Controller):

    def setup(self):
        self.led_strip = LedStrip(GPIO.GPIO27, 108, "mycelium_led_strip", on_frame_received=self.mycelium_led_strip_frame_received)

    def mycelium_led_strip_frame_received(self, led: LedStrip, payload: Payload):
        led.next_pixel((255, 0, 0), show=True)
