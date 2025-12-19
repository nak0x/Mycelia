from framework.app import App
from machine import Pin
import time

class Encoder:
    position = 0  # en crans

    _TRANS = (
        0,  -1,  +1,  0,
        +1,  0,   0, -1,
        -1,  0,   0, +1,
        0,  +1,  -1,  0
    )

    def __init__(self, pinA, pinB, onCw=None, onCcw=None, onChange=None,
                 pull=Pin.PULL_UP, steps_per_detent=4, min_us=150):

        # 🔁 inversion interne : on swap l’init
        self.pinA = Pin(pinB, Pin.IN, pull)  # <- était pinA
        self.pinB = Pin(pinA, Pin.IN, pull)  # <- était pinB

        self.onCw = onCw
        self.onCcw = onCcw
        self.onChange = onChange

        # 🔁 et donc la lecture suit naturellement ces pins swappées
        self._state = (self.pinA.value() << 1) | self.pinB.value()
        self._acc = 0
        self._steps = steps_per_detent

        self._min_us = int(min_us)
        self._last_us = time.ticks_us()

        self._pending = 0

        self.pinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._irq)
        self.pinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._irq)

        App().update.append(self.update)

    def _irq(self, _pin):
        now = time.ticks_us()
        if time.ticks_diff(now, self._last_us) < self._min_us:
            return
        self._last_us = now

        new_state = (self.pinA.value() << 1) | self.pinB.value()
        if new_state == self._state:
            return

        delta = self._TRANS[(self._state << 2) | new_state]
        self._state = new_state
        if delta == 0:
            return

        self._acc += delta

        if self._acc >= self._steps:
            self._acc = 0
            self._pending += 1
        elif self._acc <= -self._steps:
            self._acc = 0
            self._pending -= 1

    def update(self):
        if self._pending == 0:
            return

        step = self._pending
        self._pending = 0

        self.position += step

        if step > 0:
            if self.onCw:
                for _ in range(step):
                    self.onCw()
            if self.onChange:
                self.onChange(self.position, step)
        else:
            if self.onCcw:
                for _ in range(-step):
                    self.onCcw()
            if self.onChange:
                self.onChange(self.position, step)

    def reset(self, value=0):
        self.position = value
        self._acc = 0
        self._pending = 0