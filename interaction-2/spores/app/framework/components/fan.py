from machine import Pin, PWM
from framework.app import App
from framework.utils.frames.frame import Frame

class Fan:
    is_on = False

    def __init__(self, pin, slug=None, default_speed=100, on_payload_received=None):
        self.pin_num = pin  # On sauvegarde le numéro du pin pour pouvoir recréer le PWM plus tard
        self.slug = slug
        self.on_payload_received_callback = on_payload_received
        self.default_speed = default_speed
        
        # Le PWM sera initialisé par _set_pwm appelé dans off() ou on()
        self.pwm = None 
        
        # On force l'extinction propre au démarrage
        self.off()
        
        App().on_frame_received.append(self.on_frame_received)

    def _init_pwm(self):
        """(Re)crée l'objet PWM si nécessaire"""
        if self.pwm is None:
            self.pwm = PWM(Pin(self.pin_num), freq=25000)

    def _set_pwm(self, percent):
        # 1. On s'assure que le PWM est actif
        self._init_pwm()

        # 2. On applique la vitesse
        safe_percent = max(0, min(100, int(percent)))
        duty = int((safe_percent / 100) * 65535)
        self.pwm.duty_u16(duty)

    def off(self):
        """Désactive le PWM et force le Pin à 0V (GND)"""
        if self.pwm is not None:
            # Sécurité : on met le duty à 0 avant de couper
            self.pwm.duty_u16(0)
            # On détruit l'objet PWM pour libérer le Pin
            self.pwm.deinit()
            self.pwm = None

        # Hack : On reconfigure le Pin en simple sortie digitale à 0 (GND)
        # Cela supprime tout signal résiduel que le ventilo pourrait interpréter
        p = Pin(self.pin_num, Pin.OUT)
        p.value(0)
        
        self.is_on = False

    def on(self):
        self._set_pwm(self.default_speed)
        self.is_on = True

    def on_frame_received(self, frame: Frame):
        if self.slug is None:
            return

        for payload in frame.payload:
            if payload.slug == self.slug:
                if self.on_payload_received_callback is not None:
                    self.on_payload_received_callback(self, payload)

                else:
                    val = payload.value
                    
                    if str(val).upper() == "ON" or val is True:
                        self.on()
                    elif str(val).upper() == "OFF" or val is False:
                        self.off()