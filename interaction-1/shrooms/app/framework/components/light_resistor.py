from machine import Pin, ADC
from framework.app import App
from framework.utils.frames.frame import Frame
from framework.utils.ws.interface import WebsocketInterface

class LightResistor:

    def __init__(self, pin, callback=None, name="Light resistor"):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.callback = callback
        self.name = name
        App().update.append(self.update)

    def update(self):
        value = self.adc.read()
        if self.callback is not None:
            self.callback(value)
