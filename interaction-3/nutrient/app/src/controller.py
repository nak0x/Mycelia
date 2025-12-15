from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.led_strip import LedStrip
from framework.utils.timer import Timer
from src.nurtient_flow import NutrientFlow
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    animation_duration = 5000  # ms

    def setup(self):
        self.led_strip = LedStrip(GPIO.GPIO27, 100, "nutrient_led_strip")
        self.pixels = self.led_strip.pixels

        self.flow = NutrientFlow(
            num_pixels=len(self.pixels),
            color=(0, 255, 0),
            wave_len=20,
            gap_len=15,
            speed=100.0,
            fade=True
        )

        self.animated = False

        # Timer qui stoppera l'animation après animation_duration
        self.animation_timer = Timer(self.animation_duration, self.stop_animation)

    def update(self):
        if self.animated:
            self.handle_animation()

    def handle_animation(self):
        self.flow.step(self.pixels)
        self.led_strip.display()

    def start_animation(self):
        self.animated = True
        self.animation_timer.restart()

    def stop_animation(self):
        self.animated = False
        # optionnel: clear strip à la fin
        for i in range(len(self.pixels)):
            self.pixels[i] = (0, 0, 0)
        self.led_strip.display()
        WebsocketInterface().send_value("shroom_growing", True, "bool", "ESP32-030301")

    def on_frame_received(self, frame):
        for payload in frame.payload:
            if payload.slug == "nutrient_animated" and payload.datatype == "bool":
                if payload.value:
                    self.start_animation()
                else:
                    self.stop_animation()