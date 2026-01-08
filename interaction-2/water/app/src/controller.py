from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.relay import Relay

class WaterController(Controller):
    
    def setup(self):
        self.relay = Relay(27, "02-balance-toggle")

