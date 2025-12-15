from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.led_strip import LedStrip

class ExampleController(Controller):

    def setup(self):
        # Configuration du bandeau LED (100 LEDs sur le pin 4)
        self.led_strip = LedStrip(
            pin=4,
            pixel_num=100,
            slug="led",  # Adapté au serveur WebSocket
            default_color=(0, 200, 200),
            on_frame_received=self.handle_led_command
        )

        print("Controller initialisé - Bandeau LED prêt (100 LEDs)")

    def update(self):
        pass

    def shutdown(self):
        # Éteindre les LEDs proprement
        if hasattr(self, 'led_strip'):
            self.led_strip.off()
        print("Controller arrêté - LEDs éteintes")

    def on_frame_received(self, frame: Frame):
        pass

    def handle_led_command(self, led_strip, payload):
        value = payload.value

        if value is True or value == True:
            print(">> ACTION: Allumage des LEDs")
            led_strip.on()
        elif value is False or value == False:
            print(">> ACTION: Extinction des LEDs")
            led_strip.off()
        else:
            print(f">> Commande LED inconnue: {value}")
