import json
from machine import Pin
from framework.utils.gpio import GPIO
from framework.utils.json.validator import JsonValidator
from framework.utils.json.template import TemplateBuilder

class Config:
    pins = {}
    _data = {}
    def __init__(self):
        self.load_from_file("config.json")
        self.setup_pins()

    def setup_pins(self):
        self.pins["builtin-led"] = Pin(GPIO.LED, Pin.OUT, Pin.PULL_DOWN)
        self.pins["led"] = Pin(GPIO.GPIO4, Pin.OUT, Pin.PULL_DOWN)

    def load_from_file(self, filepath):
        print("Trying to load config ...")
        with open(filepath, "r") as f:
            data = f.read()
            self.validate(data)
        self.load_config(json.loads(data))
        del data

    def validate(self, raw_data: str):
        template_builder = TemplateBuilder()
        template = template_builder.build_from_file("config_template", "templates/config.template.json")
        validator = JsonValidator(template)
        errors = validator.validate(raw_data)
        if len(errors) > 0:
            raise ValueError(f"Cannot validate config: {errors}")

    def load_config(self, data):
        self._data["device_id"] = data["device_id"]
        self._data["debug"] = data["debug"]
        self._data["slowed"] = data["slowed"]
        self._data["wifi"] = WifiConfig(data["wifi"]["SSID"], data["wifi"]["password"], data["wifi"]["timeout"])
        self._data["websocket"] = WebsocketConfig(data["websocket"]["server"], data["websocket"]["reconnect"])
        
        # Debug: Print all config data
        print("=== Config Data (Debug) ===")
        for key in self._data:
            value = self._data[key]
            if isinstance(value, (WifiConfig, WebsocketConfig)):
                # Print object attributes
                print(f"  {key}:")
                if isinstance(value, WifiConfig):
                    print(f"    SSID: {value.SSID}")
                    print(f"    password: {'*' * len(value.password)}")  # Hide password
                    print(f"    timeout: {value.timeout}")
                elif isinstance(value, WebsocketConfig):
                    print(f"    server: {value.server}")
                    print(f"    reconnect: {value.reconnect}")
            else:
                print(f"  {key}: {value}")
        print("===========================")

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


class WifiConfig:
    SSID = ""
    password = ""
    timeout = 3000

    def __init__(self, ssid, password, timeout):
        self.SSID = ssid
        self.password = password
        self.timeout = timeout

class WebsocketConfig:
    server = ""
    reconnect = True

    def __init__(self, server, reconnect):
        self.server = server
        self.reconnect = reconnect