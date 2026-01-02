from framework.app import App
from machine import Pin, ADC
import time

class Microphone:

    def __init__(self, blow_callback, pin=32, threshold=25, hold_ms=20, cooldown_ms=30, limit=15, debug=False):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)      # ~0..3.3V (ESP32 classic)
        self.adc.width(ADC.WIDTH_12BIT)    # 0..4095

        # Filters
        self.baseline = self.adc.read()
        self.alpha_base = 0.01   # baseline tracking speed (slow)
        self.env = 0.0
        self.alpha_env = 0.2     # envelope smoothing (faster)
        # Detection tuning
        self.threshold = threshold       # envelope threshold (start here, calibrate)
        self.hold_ms = hold_ms       # must stay above threshold this long
        self.cooldown_ms = cooldown_ms   # debounce / avoid retrigger spam
        self.above_since = None
        self.cooldown_until = 0
        self.blow_limit=limit
        self.blow_conter = 0
        self.blow_callback = blow_callback

        App().update.append(self.update)

    def update(self):
        x = self.adc.read()

        # Update baseline (slow drift compensation)
        baseline = (1 - self.alpha_base) * self.baseline + self.alpha_base * x

        # Envelope
        amp = abs(x - baseline)
        env = (1 - self.alpha_env) * self.env + self.alpha_env * amp

        t = time.ticks_ms()

        if App().config.debug:
            print(f"Microphone value: {int(env)}")

        if time.ticks_diff(t, self.cooldown_until) < 0:
            return

        if env > self.threshold:
            if self.above_since is None:
                self.above_since = t
            elif time.ticks_diff(t, self.above_since) >= self.hold_ms:
                self.blow_conter += 1
                if self.blow_conter >= self.blow_limit:
                    print("BLOW detected", "env=", int(env))
                    self.blow_callback()
                self.cooldown_until = time.ticks_add(t, self.cooldown_ms)
                self.above_since = None
        else:
            self.above_since = None

    def now_ms(self):
        return 
