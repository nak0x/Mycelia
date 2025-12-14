from framework.controller import Controller
from framework.utils.frames.frame import Frame
# from framework.components.button import Button  # PULL_DOWN (bouton vers 3.3V)
from src.button_pullup import ButtonPullUp as Button  # PULL_UP (bouton vers GND)
from framework.utils.ws.interface import WebsocketInterface

class ExampleController(Controller):

    def setup(self):
        print("=== SETUP DEBUT ===")

        # Configuration du bouton sur le pin 5
        self.button = Button(
            pin=5,
            onPress=self.on_button_press,
            onRelease=self.on_button_release
        )

        # Référence au WebSocket pour envoyer des messages
        self.ws = WebsocketInterface()

        print("Controller initialisé - Bouton prêt sur GPIO 5")
        print("Callbacks configurés - Test en appuyant sur le bouton...")
        print("=== SETUP FIN ===")

    def update(self):
        # Debug : afficher l'état du pin toutes les secondes environ
        # (Le framework appelle update() en boucle)
        pass

    def shutdown(self):
        print("Controller arrêté")

    def on_button_press(self):
        """Appelé quand le bouton est pressé"""
        print(">> Bouton PRESSÉ - Envoi de la commande ON au serveur")

        # Envoyer un message au serveur pour allumer les LEDs
        self.ws.send_value(
            slug="led",
            value=True,
            type="boolean",
            receiver_id="ESP32-FF7700"  # ID de l'ESP32 qui contrôle les LEDs
        )

    def on_button_release(self):
        """Appelé quand le bouton est relâché"""
        print(">> Bouton RELÂCHÉ - Envoi de la commande OFF au serveur")

        # Envoyer un message au serveur pour éteindre les LEDs
        self.ws.send_value(
            slug="led",
            value=False,
            type="boolean",
            receiver_id="ESP32-FF7700"  # ID de l'ESP32 qui contrôle les LEDs
        )

    def on_frame_received(self, frame: Frame):
        """Appelé quand une frame est reçue du serveur"""
        pass
