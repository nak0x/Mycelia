from framework.components.button import Button

class Shroom:
    lighten = False
    def __init__(self, name, pin):
        self.button = Button(pin, onPress=self.on_light_detected)
        self.name = name

    def on_light_detected(self):
        if self.lighten:
            return
        self.lighten = True
        print(f"{self.name}: Lighten")