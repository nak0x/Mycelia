from framework.controller import Controller
from framework.components.relay import Relay


class RainController(Controller):
    
    def __init__(self):
        super().__init__()
        relay = Relay(27, "01-rain-toggle")
        relay.close()

