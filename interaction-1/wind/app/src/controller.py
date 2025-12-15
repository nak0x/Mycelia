from framework.controller import Controller
from framework.components.engine import Engine
from framework.utils.gpio import GPIO

class WindController(Controller):
    
    def __init__(self):
        super().__init__()
        Engine(GPIO.GPIO12, "fan")
