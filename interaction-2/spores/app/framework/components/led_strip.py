from framework.app import App
from machine import Pin
from neopixel import NeoPixel
from framework.utils.frames.frame import Frame

class LedStrip:
    def __init__(self, pin, pixel_num, slug=None, default_color=(255, 255, 255), on_payload_received=None):
        self.np = NeoPixel(Pin(pin), pixel_num)
        self.slug = slug
        self.default_color = default_color
        self.on_payload_received_callback = on_payload_received

        self.pixels = [(0, 0, 0)] * pixel_num
        self.display()

        App().on_frame_received.append(self.on_frame_received)

    def display(self):
        for i, c in enumerate(self.pixels):
            self.np[i] = c
        self.np.write()

    def fill(self, color):
        for i in range(len(self.pixels)):
            self.pixels[i] = color

    def clear(self):
        self.fill((0, 0, 0))

    def on(self, color=None):
        self.fill(color or self.default_color)
        self.display()

    def off(self):
        self.clear()
        self.display()

    def set_pixel(self, i, color=None, show=False):
        if 0 <= i < len(self.pixels):
            self.pixels[i] = color or self.default_color
            if show:
                self.display()

    def _last_index_of_color(self, color):
        for i in range(len(self.pixels) - 1, -1, -1):
            if self.pixels[i] == color:
                return i
        return None
    
    def next_pixel(self, color=None, show=False):
        c = color or self.default_color
        last = self._last_index_of_color(c)

        i = 0 if last is None else min(last + 1, len(self.pixels) - 1)
        self.pixels[i] = c

        if show:
            self.display()
        return i

    def previous_pixel(self, color=None, show=False):
        c = color or self.default_color
        last = self._last_index_of_color(c)

        i = (len(self.pixels) - 1) if last is None else max(last - 1, 0)
        self.pixels[i] = c

        if show:
            self.display()
        return i

    def on_frame_received(self, frame: Frame):
        if self.slug is None:
            return

        for payload in frame.payload:
            if payload.slug == self.slug:
                if self.on_payload_received_callback is not None:
                    self.on_payload_received_callback(self, payload)
                elif payload.datatype == "bool":
                    self.on() if payload.value else self.off()