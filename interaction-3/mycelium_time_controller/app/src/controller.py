from framework.controller import Controller
from framework.components.encoder import Encoder
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    def setup(self):
        Encoder(pinA=GPIO.GPIO25, pinB=GPIO.GPIO26, onCw=self.increment_mycelium)

    def increment_mycelium(self):
        print("> grow mycelium")
        WebsocketInterface().send_value("03-grow-mycelium", None)
