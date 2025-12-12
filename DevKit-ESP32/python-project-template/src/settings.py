from machine import Pin
from src.utils.gpio import GPIO

class Config:
    def __init__(self):
        self._data = {
            "pins": {},
            "SSID": "Livebox-8810_EXT",
            "PASSWORD": "ZiwfswvFwWTsqsV7q5",
        }
        self.setup_pins()

    # Dict-style access: cfg["SSID"]
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    # Attribute-style access: cfg.SSID
    def __getattr__(self, name):
        # Only called if normal attribute lookup fails
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        # Keep internal attributes normal; redirect others to the dict
        if name == "_data" or name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def setup_pins(self):
        pins = self._data["pins"]
        pins["led"] = Pin(GPIO.LED, Pin.OUT, Pin.PULL_UP)
        pins["button"] = Pin(GPIO.GPIO4, Pin.IN, Pin.PULL_DOWN)