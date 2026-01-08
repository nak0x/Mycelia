from framework.controller import Controller
from framework.components.dht_sensor import DHTSensor
from framework.utils.gpio import GPIO
from framework.utils.timer import Timer
from framework.utils.ws.interface import WebsocketInterface


class RainController(Controller):

    HUMIDITY_DELTA_THRESHOLD = 10

    baseline_humidity = 0
    current_humidity = None

    is_raining = False

    def setup(self):
        self.humidity_sensor = DHTSensor(GPIO.GPIO14, onHumidityChange=self.on_humidity_changed)
        self.baseline_update_timer = Timer(1000, self.update_humidity_baseline)
        self.rain_reset_timer = Timer(2000, self.reset_rain_state)

    def on_humidity_changed(self, humidity):
        is_first_measure = self.current_humidity is None
        self.current_humidity = humidity

        if is_first_measure:
            self.baseline_update_timer.start()
            self.update_humidity_baseline()

        if (
            self.current_humidity is not None
            and not self.is_raining
            and self.current_humidity > self.baseline_humidity + self.HUMIDITY_DELTA_THRESHOLD
        ):
            print("It's raining!")
            WebsocketInterface().send_value("01-rain-toggle", True)
            self.is_raining = True
            self.rain_reset_timer.start()

    def update_humidity_baseline(self):
        if self.current_humidity is None:
            return

        self.baseline_humidity = self.current_humidity
        self.baseline_update_timer.restart()
        print(f"New baseline humidity: {self.baseline_humidity}")

    def reset_rain_state(self):
        print("Resetting rain state")
        self.is_raining = False