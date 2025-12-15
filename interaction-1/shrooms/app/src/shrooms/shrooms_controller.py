from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface
from src.shrooms.shroom import Shroom



class ShroomsController(Controller):
    shrooms = []
    forest_lighten = False

    def __init__(self):
        super().__init__()
        self.shrooms.append(Shroom("SH_1", GPIO.GPIO4))
        self.shrooms.append(Shroom("SH_2", GPIO.GPIO5))
        self.shrooms.append(Shroom("SH_3", GPIO.GPIO19))

    def update(self):
        if self.is_shrooms_lighten() and not self.forest_lighten:
            self.forest_lighten = True
            print("Shroom forest lighten !")
            WebsocketInterface().send_value("shroom_forest", self.forest_lighten, "bool", "SERVER-0E990F")

    def is_shrooms_lighten(self):
        checksum = True
        for shroom in self.shrooms:
            checksum = checksum and shroom.lighten
        return checksum