from machine import Pin, ADC
from framework.app import App
from framework.utils.frames.frame import Frame
from framework.utils.ws.interface import WebsocketInterface

class LedResistor:

    def __init__(self, pin, threshold, target):
        self.adc = Pin(pin, Pin.OUT, Pin.PULL_DOWN)
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.target = target
        self.threshold = threshold
        App().update.append(self.update)

    def update(self):
        value = self.adc.read()
        if App().config.debug:
            print(f"LIGHT: {value}")
        WebsocketInterface().send_value(self.slug, value, "int", self.target)