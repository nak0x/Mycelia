from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.button import Button
from framework.utils.ws.interface import WebsocketInterface

class ExampleController(Controller):

    def setup(self):
        self.button = Button(
            pin=5,
            onPress=self.on_button_press,
            onRelease=self.on_button_release
        )

        self.button2 = Button(
            pin=18,
            onPress=self.on_button2_press,
            onRelease=self.on_button2_release
        )

        self.ws = WebsocketInterface()

        self.terre_status = False
        self.sphero_status = False
        self.last_checksum = None

        print("Controller initialisé - Boutons prêts sur GPIO 5 et 18")

    def update(self):
        current_checksum = (self.terre_status, self.sphero_status)

        # N'envoyer que si l'état a changé
        if current_checksum != self.last_checksum:
            led_value = self.terre_status and self.sphero_status

            self.ws.send_value(
                slug="led",
                value=led_value,
                type="boolean",
                receiver_id="ESP32-FF7700"
            )

            self.last_checksum = current_checksum
            print(f">> État changé - LED: {led_value} (terre: {self.terre_status}, sphero: {self.sphero_status})")

    def shutdown(self):
        print("Controller arrêté")

    def on_button_press(self):
        print(">> Bouton 1 PRESSÉ")
        self.terre_status = True

    def on_button_release(self):
        print(">> Bouton 1 RELÂCHÉ")
        self.terre_status = False

    def on_button2_press(self):
        print(">> Bouton 2 PRESSÉ")
        self.sphero_status = True

    def on_button2_release(self):
        print(">> Bouton 2 RELÂCHÉ")
        self.sphero_status = False

    def on_frame_received(self, frame: Frame):
        pass
