from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.engine import Engine
from framework.utils.timer import Timer

class MainController(Controller):
    animation_duration = 1000   # ms
    
    def setup(self):
        self.engine = Engine(GPIO.GPIO27)
        self.animation_timer = Timer(self.animation_duration, self.stop_animation)

    def start_animation(self):
        self.engine.on()
        self.animation_timer.start()

    def stop_animation(self):
        self.engine.off()

    def on_frame_received(self, frame):
        if frame.action == "3-engine-on":
            self.engine.on()
        elif frame.action == "3-engine-off":
            self.engine.off()
        elif frame.action == "3-start-animation":
            self.start_animation()
