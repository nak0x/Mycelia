from framework.controller import Controller
from framework.components.relay import Relay
from framework.app import App
from framework.utils.timer import Timer

class FanController(Controller):

    def __init__(self):
        super().__init__()
        pin_power = App().config.pins["fan_power"]

        self.timer = Timer(15000, self.turn_off_fan)

        # Relay initialized with action=None so it ignores frames by default
        self.fan = Relay(
            pin_power,
            action=None, 
            on_payload_received=self.on_fan_command
        )
        self.fan.open()

        # Register manual dispatcher
        App().on_frame_received.append(self.dispatch_frame)

    def dispatch_frame(self, frame):
        if frame.action == "02-fan-toggle":
            self.on_fan_command(self.fan, frame.value)
        elif frame.action == "01-interaction-done":
            self.on_fan_command(self.fan, True)

    def on_fan_command(self, relay: Relay, value):
        if value:
            print("Fan ON (Timer started)")
            relay.close()
            self.timer.restart()
        else:
            print("Fan OFF (Timer stopped)")
            relay.open()
            self.timer.stop()

    def turn_off_fan(self):
        print("Fan Timer Limit Reached -> OFF")
        self.fan.open()
