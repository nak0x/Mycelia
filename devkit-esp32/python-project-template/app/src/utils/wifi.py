import network
import time
from src.app import App

class WifiManager:
    _config = {}
    wlan = None

    def __init__(self):
        # Append WifiManager setup to app hooks
        app = App()
        app.setup.append(self._setup)
        app.update.append(self._update)
        # Free the instance space
        del app

    def config(self, ssid: str, password: str):
        self._config = {
            "ssid": ssid,
            "password": password
        }

    def _update(self):
        if not self.wlan.isconnected():
            App().config.pins["builtin-led"].off()
            print(f"Wifi connection lost. Trying to reconnect...")
            self._connect()


    def _setup(self):
        print(f"{__name__} : WifiManager setup")

        if self._config == {}:
            raise ValueError("WifiManager cannot have an empty config.")

        print(f"Configuring wifi interface on SSID {self._config['ssid']} ... ")
        self._connect()

    def _connect(self):
        App().config.pins["builtin-led"].off()
        self.wlan = network.WLAN()
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self._config["ssid"], self._config["password"])
            t0 = time.ticks_ms()
            while not self.wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), t0) > App().config.wifi.timeout:
                    raise RuntimeError("Timeout while connecting to network")
            self.wlan.connect(self._config["ssid"], self._config["password"])
            t0 = time.ticks_ms()
            while not self.wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), t0) > App().config.wifi["timeout"]:
                    raise RuntimeError("Timeout while connecting to network")
                App().idle()
        # Light the builtin led when wifi is connected
        App().config.pins["builtin-led"].on()
        print('Network config:', self.wlan.ipconfig('addr4'))
