from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.led_strip import LedStrip
from framework.utils.timer import Timer
from src.nurtient_flow import NutrientFlow
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    animation_duration = 5000  # ms

    def setup(self):
        self.led_strip = LedStrip(GPIO.GPIO27, 200)
        self.pixels = self.led_strip.pixels
        
        self.reverse_led_strip = LedStrip(GPIO.GPIO26, 100)
        self.reverse_pixels = self.reverse_led_strip.pixels

        self.flow = NutrientFlow(
            num_pixels=len(self.pixels),
            color=(0, 255, 0),
            wave_len=20,
            gap_len=15,
            speed=50.0,
            fade=True
        )

        self.reverse_flow = NutrientFlow(
            num_pixels=len(self.reverse_pixels),
            color=(0, 0, 255),
            wave_len=20,
            gap_len=15,
            speed=50.0,
            fade=True,
            reverse=True
        )

        self.animated = True

        # Timer qui stoppera l'animation après animation_duration
        self.animation_timer = Timer(self.animation_duration, self.stop_animation)

    def update(self):
        if self.animated:
            self.handle_animation()

    def handle_animation(self):
        self.flow.step(self.pixels)
        self.reverse_flow.step(self.reverse_pixels)

        self.led_strip.display()
        self.reverse_led_strip.display()

    def start_animation(self):
        self.animated = True
        self.animation_timer.restart()

    def stop_animation(self):
        self.animated = False

        # Clear les leds
        self.led_strip.clear()
        self.reverse_led_strip.clear()

        WebsocketInterface().send_value("shroom_growing", True)

    def on_frame_received(self, frame):
        if frame.action == "nutrient_animated":
            if frame.value:
                self.start_animation()
            else:
                self.stop_animation()
