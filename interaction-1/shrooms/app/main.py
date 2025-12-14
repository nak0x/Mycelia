from framework.app import App
from framework.utils.wifi import WifiManager
from framework.utils.integrity import run_integrity_checks
from framework.utils.ws.interface import WebsocketInterface
from framework.utils.gpio import GPIO
from framework.components.button import Button
from framework.components.led_strip import LedStrip

from src.controller import Controller

# Check that the esp32 don't have any problems
run_integrity_checks()

# Instantiate the app
app = App()

wifi_manager = WifiManager()
wifi_manager.config(ssid=app.config.wifi.SSID, password=app.config.wifi.password)

ws_client = WebsocketInterface()

controller = Controller()

# Run the app
# Note that anything below this line won't be executed
app.run()