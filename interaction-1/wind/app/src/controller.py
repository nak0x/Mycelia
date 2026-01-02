from framework.controller import Controller
from framework.components.relay import Relay
from framework.utils.gpio import GPIO

class WindController(Controller):
    
    def __init__(self):
        super().__init__()
        Relay(GPIO.GPIO14, "01-wind-toggle")
