from src.app import App
from machine import Pin
from neopixel import NeoPixel
from src.utils.frames.frame import Frame

class LedStrip:

    def __init__(self, pin, pixel_num, slug = None):
        self.np = NeoPixel(Pin(pin), pixel_num)
        self.slug = slug
        App().on_frame_received.append(self.on_frame_received)

    def on(self, color = (255, 255, 255)):
        for i in range(len(self.np)):
            self.np[i] = color
        self.np.write()

    def off(self):
        for i in range(len(self.np)):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def on_frame_received(self, frame: Frame):
        if self.slug is None:
            return
        
        for payload in frame.payload:
            if payload.slug == self.slug and payload.datatype == "bool":
                self.on() if payload.value else self.off()
