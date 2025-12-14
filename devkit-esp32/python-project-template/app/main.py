from src.app import App
from src.utils.wifi import WifiManager
from src.utils.integrity import run_integrity_checks
from src.utils.ws.interface import WebsocketInterface
from src.utils.gpio import GPIO
from src.components.button import Button
from src.components.led_strip import LedStrip

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

led_strip = LedStrip(
    pin=GPIO.GPIO25,
    pixel_num=10
)

# Run the app
# Note that anything below this line won't be executed
app.run()