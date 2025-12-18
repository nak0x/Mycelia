from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.fan import Fan
from framework.app import App

class FanController(Controller):

    def setup(self):
        app = App()

        pin_fan = app.config.pins["fan"]

        self.fan = Fan(
            pin=pin_fan,
            slug="fan",  # Adapté au serveur WebSocket
            default_speed=100,
        )

        print("Controller initialisé - Fans prêt")

    def update(self):
        pass

    def shutdown(self):
        # Éteindre les Fans proprement
        if hasattr(self, 'fan'):
            self.fan.off()
        print("Controller arrêté - Fans éteints")

    def on_frame_received(self, frame):
        pass
