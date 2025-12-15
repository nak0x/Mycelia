import time
from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.led_strip import LedStrip
from src.nurtient_flow import NutrientFlow

class MainController(Controller):
    animated = False
    def setup(self):
        self.led_strip = LedStrip(GPIO.GPIO27, 100, "nutrient_led_strip")
        self.pixels = self.led_strip.pixels

        # Paramètres réglables
        self.flow = NutrientFlow(
            num_pixels=len(self.pixels),
            color=(0, 255, 0),
            wave_len=20,   # longueur d’un “paquet”
            gap_len=15,   # leds éteintes entre deux paquets
            speed=100.0,   # leds/seconde
            fade=True
        )

        # (optionnel) limiter la fréquence d'affichage pour économiser CPU
        self._frame_ms = 20  # 50 FPS max
        self._t_last_frame = time.ticks_ms()

    def update(self):
        if self.animated:
            self.handle_animation()

    def handle_animation(self):
        # (optionnel) throttle
        now = time.ticks_ms()
        if time.ticks_diff(now, self._t_last_frame) < self._frame_ms:
            return
        self._t_last_frame = now

        # 1) Met à jour le buffer
        self.pixels = self.flow.step(self.pixels)

        # 2) Push sur les neopixels
        for i, c in enumerate(self.pixels):
            self.led_strip.np[i] = c
        self.led_strip.display()

    def on_frame_received(self, frame):
        for payload in frame.payload:
            if payload.slug == "animated" and payload.datatype == "bool":
                self.animated = payload.value
