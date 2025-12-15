from framework.controller import Controller
from framework.components.button import Button
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    def setup(self):
        Button(GPIO.GPIO32, onPress=self.increment_mycelium)

    def increment_mycelium(self):
        WebsocketInterface().send_value("mycelium_led", True, "bool", "ESP32-030102")
