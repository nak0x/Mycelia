from framework.app import App
from dht import DHT11, DHT22
from machine import Pin

class DHTSensor:
    temperature = None
    humidity = None

    def __init__(self, pin, onChange=None, onTemperatureChange=None, onHumidityChange=None):
        self.onChange = onChange
        self.onTemperatureChange = onTemperatureChange
        self.onHumidityChange = onHumidityChange

        self.d = DHT11(Pin(pin))

        App().update.append(self.update)

    def update(self):
        try:
            self.d.measure()
            t = self.d.temperature()
            h = self.d.humidity()
            print(f"Temperature: {t}°C, Humidity: {h}%")
        except Exception as e:
            print(f"An error occured while updating DHT sensor: {e}")
            return

        temp_changed = (t != self.temperature)
        hum_changed = (h != self.humidity)

        self.temperature = t
        self.humidity = h

        if temp_changed and self.onTemperatureChange:
            self.onTemperatureChange(t)

        if hum_changed and self.onHumidityChange:
            self.onHumidityChange(h)

        if (temp_changed or hum_changed) and self.onChange:
            self.onChange(t, h)