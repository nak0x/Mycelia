from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.relay import Relay
from framework.utils.timer import Timer

class MainController(Controller):
    animation_duration = 1000   # ms
    
    def setup(self):
        self.relay = Relay(GPIO.GPIO27)
        self.animation_timer = Timer(self.animation_duration, self.stop_animation)

    def start_animation(self):
        self.relay.open()
        self.animation_timer.start()

    def stop_animation(self):
        self.relay.close()

    def on_frame_received(self, frame):
        if frame.action == "03-grow-shroom":
            self.start_animation()
