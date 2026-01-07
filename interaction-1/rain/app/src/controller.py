from framework.controller import Controller
from framework.components.dht_sensor import DHTSensor
from framework.utils.gpio import GPIO


class RainController(Controller):
    
    def __init__(self):
        super().__init__()
        relay = DHTSensor(GPIO.GPIO14, onHumidityChange=self.handle_humidity)

    def handle_humidity(self, humidity):
        print(humidity)
        

