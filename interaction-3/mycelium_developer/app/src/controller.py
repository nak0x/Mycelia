from framework.controller import Controller
from framework.components.led import Led
from framework.utils.gpio import GPIO
from framework.utils.frames.frame import Payload
from framework.utils.timer import Timer
from framework.utils.ws.interface import WebsocketInterface

class MainController(Controller):
    started = True

    def setup(self):
        self.led = Led(GPIO.GPIO27, 'mycelium_led', on_payload_received=self.on_led_payload_received)

        # Paramètres
        self.experiment_duration_ms = 10000
        self.max_silence_ms = 5000
        self.led_auto_off_ms = 2000

        # Timers
        self.experiment_timer = Timer(self.experiment_duration_ms, self.end_experiment)
        self.watchdog_timer   = Timer(self.max_silence_ms, self.stop_experiment_due_to_silence)
        self.led_off_timer    = Timer(self.led_auto_off_ms, self.light_off_led)

    def start_experiment(self):
        print("Start experiment")
        self.started = True
        self.experiment_timer.start()
        self.watchdog_timer.start()

    def on_led_payload_received(self, led: Led, payload: Payload):
        print("New input")
        if not self.started:
            self.start_experiment()


        # 1) On a reçu un signal -> on reset le watchdog (preuve de vie)
        self.watchdog_timer.restart()

        # 2) On allume la LED et on planifie son extinction automatique
        self.led.on()
        self.led_off_timer.restart()

    def light_off_led(self):
        print("Led off")
        self.led.off()

    def stop_experiment_due_to_silence(self):
        # Appelé quand on n'a pas reçu de payload assez souvent
        print("Stop: silence (watchdog timeout)")
        self.stop_all()
        self.started = False

    def end_experiment(self):
        print("End: experiment duration reached")
        self.stop_all()
        self.started = False
        WebsocketInterface().send_value("nutrient_animated", True, "bool", "ESP32-030201")

    def stop_all(self):
        print("Stop all")
        # Stoppe proprement tous les timers et remet l'état souhaité
        self.experiment_timer.quit()
        self.watchdog_timer.quit()
        self.led_off_timer.quit()
        self.led.off()