from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.components.dht_sensor import DHTSensor

class MainController(Controller):
    
    def setup(self):
        DHTSensor(GPIO.GPIO27)