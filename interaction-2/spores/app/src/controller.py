from framework.controller import Controller
from framework.components.relay import Relay
from framework.app import App

class FanController(Controller):

    def __init__(self):
        super().__init__()
        pin_power = App().config.pins["fan_power"]

        self.fan = Relay(
            pin_power,
            "02-fan-toggle"
        )
        self.fan.open()
