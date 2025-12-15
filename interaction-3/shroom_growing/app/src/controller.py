from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.engine import Engine
from framework.utils.frames.frame import Payload
from framework.utils.timer import Timer

class MainController(Controller):

    def setup(self):
        self.engine = Engine(GPIO.GPIO27, "shroom_growing", on_payload_received=self.on_engine_payload_received)
        self.engine.off()

        self.engine_duration = 5000
        self.timer = Timer(self.engine_duration, self.engine.off)

    def on_engine_payload_received(self, engine: Engine, payload: Payload):
        if payload.datatype == "bool":
            if payload.value:
                engine.on()
                self.timer.restart()
            else:
                engine.off()
