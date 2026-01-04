from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.relay import Relay

class MainController(Controller):

    def setup(self):
        self.relay = Relay(GPIO.GPIO27)
