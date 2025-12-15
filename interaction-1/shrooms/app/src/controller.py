from framework.controller import Controller
from framework.utils.frames.frame import Frame

from .shrooms.shrooms_controller import ShroomsController

class ExampleController(Controller):
    def __init__(self):
        super().__init__()
        self.shrooms = ShroomsController()
