from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.engine import Engine
from framework.utils.gpio import GPIO
from framework.app import App


class RainController(Controller):
    
    def __init__(self):
        super().__init__()
        self.engine = Engine(GPIO.GPIO4, "rain-toggle")