from framework.app import App
from framework.utils.wifi import WifiManager
from framework.utils.integrity import run_integrity_checks
from framework.utils.ws.interface import WebsocketInterface
from src.controller import FanController

# Check that the esp32 don't have any problems
run_integrity_checks()

# Instantiate the app
app = App()

wifi_manager = WifiManager()
wifi_manager.config(ssid=app.config.wifi.SSID, password=app.config.wifi.password)

ws_client = WebsocketInterface()

controller = FanController()

# Run the app
# Note that anything below this line won't be executed
app.run()