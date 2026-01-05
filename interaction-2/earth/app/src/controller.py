from framework.controller import Controller
from framework.utils.frames.frame import Frame
from framework.components.button import Button
from framework.utils.ws.interface import WebsocketInterface

class EarthController(Controller):

    def setup(self):
        print("Début de l'initialisation...")

        self.button = Button(
            pin=5,
            onPress=self.on_button_press,
            onRelease=self.on_button_release
        )

        self.balance_status = False
        self.last_status = None

        print("Controller initialisé - Bouton balance prêt sur GPIO 5")
        print("Attendez un appui sur le bouton...")

    def update(self):
        # N'envoyer que si l'état a changé
        if self.balance_status != self.last_status:
            WebsocketInterface().send_value(
                action="02-balance-toggle",
                value=self.balance_status,
            )

            self.last_status = self.balance_status
            print(f">> État changé - BALANCE: {self.balance_status}")

    def shutdown(self):
        print("Controller arrêté")

    def on_button_press(self):
        print(">> Bouton BALANCE PRESSÉ")
        self.balance_status = True

    def on_button_release(self):
        print(">> Bouton BALANCE RELÂCHÉ")
        self.balance_status = False

    def on_frame_received(self, frame: Frame):
        pass
