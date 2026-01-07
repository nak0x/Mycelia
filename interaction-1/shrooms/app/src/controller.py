from framework.controller import Controller

from .shrooms.shrooms_controller import ShroomsController

class MainController(Controller):
    def __init__(self):
        super().__init__()
        self.shrooms = ShroomsController(leds_pin=27, leds=136, shrooms=20, shroom_len=3, gap=7, color=(229, 141,18), aux_leds_pin=26,aux_leds=250)
