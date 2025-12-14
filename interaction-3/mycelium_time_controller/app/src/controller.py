from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.button import Button
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    mycelium_counter = 0

    def setup(self):
        self.button = Button(GPIO.GPIO32, onPress=self.increment_mycelium)

    def increment_mycelium(self):
        self.mycelium_counter += 1
        WebsocketInterface().send_value("mycelium_led_strip", self.mycelium_counter % 2 == 0, "bool", "ESP32-030002")

    def update(self):
        pass

    def on_frame_received(self, frame: Frame):
        pass
