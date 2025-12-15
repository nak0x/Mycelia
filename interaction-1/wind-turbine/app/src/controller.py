from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.utils.gpio import GPIO
from framework.components.button import Button
from framework.utils.ws.interface import WebsocketInterface

class WindTurbineController(Controller):
    
    def __init__(self):
        super().__init__()
        Button(GPIO.GPIO4, self.wind_turbine_activated)
    
    def wind_turbine_activated(self):
        WebsocketInterface().send_value("wind-turbine", True, "string", "SERVER-FFFFFF")