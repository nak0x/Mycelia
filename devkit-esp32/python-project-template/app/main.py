from src.app import App
from src.utils.wifi import WifiManager
from src.utils.integrity import run_integrity_checks
from src.utils.ws.interface import WebsocketInterface
from src.components.button import Button
from src.utils.gpio import GPIO

# Check that the esp32 don't have any problems
run_integrity_checks()

# Instantiate the app
app = App()

wifi_manager = WifiManager()
wifi_manager.config(ssid=app.config.wifi.SSID, password=app.config.wifi.password)

ws_client = WebsocketInterface()

button = Button(
    pin=GPIO.GPIO32,
    onPress=lambda: print("Button pressed"),
    onRelease=lambda: print("Button released")
)

# Run the app
# Note that anything below this line won't be executed
app.run()