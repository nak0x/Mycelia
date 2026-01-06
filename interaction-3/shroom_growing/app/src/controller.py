from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.relay import Relay

class MainController(Controller):

    def setup(self):
        self.r1 = Relay(GPIO.GPIO27)
        self.r2 = Relay(GPIO.GPIO26)

    def on_frame_received(self, frame):
        if frame.action == "3-engine-cw":
            self.r1.open()
            self.r2.close()
        elif frame.action == "3-engine-ccw":
            self.r1.close()
            self.r2.open()
        elif frame.action == "3-engine-off":
            self.r1.close()
            self.r2.close()
        elif frame.action == "3-start-animation":
            pass
