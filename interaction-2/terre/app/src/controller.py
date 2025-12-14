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

        self.ws = WebsocketInterface()

        print("Controller initialisé - Bouton prêt sur GPIO 5")

    def update(self):
        # Debug : afficher l'état du pin toutes les secondes environ
        # (Le framework appelle update() en boucle)
        pass

    def shutdown(self):
        print("Controller arrêté")

    def on_button_press(self):
        print(">> Bouton PRESSÉ - Envoi de la commande ON au serveur")

        # Envoyer un message au serveur pour allumer les LEDs
        self.ws.send_value(
            slug="led",
            value=True,
            type="boolean",
            receiver_id="ESP32-FF7700"
        )

    def on_button_release(self):
        print(">> Bouton RELÂCHÉ - Envoi de la commande OFF au serveur")

        # Envoyer un message au serveur pour éteindre les LEDs
        self.ws.send_value(
            slug="led",
            value=False,
            type="boolean",
            receiver_id="ESP32-FF7700"
        )

    def on_frame_received(self, frame: Frame):
        pass
