import network
from src.app import App

class WifiManager:
    _config = {}

    def __init__(self):
        # Append WifiManager setup to app hooks
        App().setup.append(self.setup)

    def config(self, ssid: str, password: str):
        self._config = {
            "ssid": ssid,
            "password": password
        }

    def setup(self):
        print(f"{__name__} : WifiManager setup")

        if self._config == {}:
            raise ValueError("WifiManager cannot have an empty config.")

        print(f"Configuring wifi interface on SSID {self._config['ssid']} ... ")
        self.connect()

    def connect(self):
        wlan = network.WLAN()
        wlan.active(True)
        if not wlan.isconnected():
            print('Connecting to network...')
            wlan.connect(self._config["ssid"], self._config["password"])
            while not wlan.isconnected():
                App().idle()
        print('Network config:', wlan.ipconfig('addr4'))
