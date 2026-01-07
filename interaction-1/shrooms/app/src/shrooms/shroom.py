from framework.components.light_resistor import LightResistor
import time

class Shroom:
    def __init__(self, name, pin, threshold_drop=700, delta_ms=350, cooldown_ms=1000, buf_size=32):
        self.button = LightResistor(pin, callback=self.handle_light_level, name="[%d] %s" % (pin, name))
        self.name = name

        self.threshold_drop = int(threshold_drop)   # required drop amount
        self.delta_ms = int(delta_ms)               # time window in ms
        self.cooldown_ms = int(cooldown_ms)
        self.lighten = False

        # ring buffer: times + levels
        self._ts = [0] * buf_size
        self._lv = [0] * buf_size
        self._n = 0            # number of valid samples (<= buf_size)
        self._head = 0         # next write index

        self._last_trigger = time.ticks_ms()

    def handle_light_level(self, level):
        # print(f"{self.name}: {level}")
        now = time.ticks_ms()
        level = int(level)

        # cooldown
        if time.ticks_diff(now, self._last_trigger) < self.cooldown_ms:
            # still store samples or not? typically no, keeps logic clean
            return

        # push into ring buffer
        self._ts[self._head] = now
        self._lv[self._head] = level
        self._head = (self._head + 1) % len(self._ts)
        if self._n < len(self._ts):
            self._n += 1

        if self._n < 2:
            return

        # Find the maximum level within the last delta_ms window.
        # We walk backwards from newest sample until we exit the window or exhaust samples.
        max_lv = level
        i = (self._head - 1) % len(self._ts)  # newest index
        checked = 0

        while checked < self._n:
            t = self._ts[i]
            lv = self._lv[i]

            if time.ticks_diff(now, t) > self.delta_ms:
                break

            if lv > max_lv:
                max_lv = lv

            i = (i - 1) % len(self._ts)
            checked += 1

        drop = max_lv - level
        if drop >= self.threshold_drop:
            self._last_trigger = now
            self.on_light_detected()

            # reset buffer to avoid retriggering on the same falling edge
            self._n = 0
            self._head = 0

    def on_light_detected(self):
        if self.lighten:
            return
        self.lighten = True
        print("%s: Lighten" % self.name)
