from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.fan import Fan
from framework.app import App

class FanController(Controller):

    def setup(self):
        app = App()

        pin_pwm = app.config.pins["fan_pwm"]
        pin_power = app.config.pins["fan_power"]

        self.fan = Fan(
            pin_pwm=pin_pwm,
            pin_power=pin_power,
            slug="fan",
            default_speed=100,
            active_low=False
        )

        print("Controller initialisé - Fans prêt")

    def update(self):
        pass

    def shutdown(self):
        # Éteindre les Fans
        if hasattr(self, 'fan'):
            self.fan.off()
        print("Controller arrêté - Fans éteints")

    def on_frame_received(self, frame):
        pass
