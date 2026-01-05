from framework.controller import Controller
from framework.components.relay import Relay
from framework.app import App
from framework.utils.timer import Timer

class FanController(Controller):

    def __init__(self):
        super().__init__()
        pin_power = App().config.pins["fan_power"]

        self.timer = Timer(5000, self.turn_off_fan)

        self.fan = Relay(
            pin_power,
            "02-fan-toggle",
            on_payload_received=self.on_fan_command
        )
        self.fan.open()

    def on_fan_command(self, relay: Relay, value):
        # Value is expected to be a bool (True = ON) based on Relay logic
        if value:
            print("Fan ON (Timer started)")
            relay.close() # Active low typically? Wait, Relay.py says close() -> pin(1). Let's assume close() is ON state requested.
            self.timer.restart()
        else:
            print("Fan OFF (Timer stopped)")
            relay.open()
            self.timer.stop()

    def turn_off_fan(self):
        print("Fan Timer Limit Reached -> OFF")
        self.fan.open()
