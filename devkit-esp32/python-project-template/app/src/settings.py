from machine import Pin
import json
from src.utils.gpio import GPIO

class Config:
    pins = {}
    def __init__(self):
        self._data = self.load_from_file("config.json")
        self.setup_pins()

    def setup_pins(self):
        self.pins["led"] = Pin(GPIO.LED, Pin.OUT, Pin.PULL_UP)
        self.pins["button"] = Pin(GPIO.GPIO4, Pin.IN, Pin.PULL_DOWN)

    def load_from_file(self, filepath):
        print("Trying to load config ...")
        f = open(filepath)
        raw_data = f.read()
        # Keep file the least amount of time im memory
        f.close()
        config = json.loads(raw_data)
        # Dont keep raw_data in memory
        del raw_data
        # TODO: Add a config parser
        return config


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
