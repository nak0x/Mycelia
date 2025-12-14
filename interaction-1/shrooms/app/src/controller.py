from framework.app import App
from framework.components.button import Button
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface

class Controller:

    def __init__(self):
        button = Button(
            pin=GPIO.GPIO32,
            onPress=self.send_btn_pressed,
            onRelease=self.send_btn_released
        )

    def send_btn_pressed(self):
        WebsocketInterface().send_value("btn_pressed", True, "bool", "IPHONE-FFEEFF")

    def send_btn_released(self):
        WebsocketInterface().send_value("btn_released", False, "bool", App().config.device_id)
