from framework.app import App
from machine import Pin

class ButtonPullUp:
    """
    Bouton avec PULL_UP (pour branchement à GND)

    Avec PULL_UP:
    - État normal (non pressé) : pin.value() == 1
    - État pressé (connecté à GND) : pin.value() == 0
    """
    pressed = False

    def __init__(self, pin, onPress=None, onRelease=None):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)  # PULL_UP au lieu de PULL_DOWN
        self.onPress = onPress
        self.onRelease = onRelease
        App().update.append(self.update)

        print(f"Bouton PULL_UP initialisé sur pin {pin}")
        print(f"État initial du pin: {self.pin.value()}")

    def update(self):
        # Avec PULL_UP : 0 = pressé, 1 = relâché
        if self.pin.value() == 0:  # Inversé par rapport à PULL_DOWN
            if not self.pressed:
                self.pressed = True
                print(f"[DEBUG] Pin détecté à 0 - PRESSÉ")
                if self.onPress is not None:
                    self.onPress()
        else:
            if self.pressed:
                self.pressed = False
                print(f"[DEBUG] Pin détecté à 1 - RELÂCHÉ")
                if self.onRelease is not None:
                    self.onRelease()
