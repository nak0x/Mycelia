from machine import Pin, PWM
from framework.app import App
from framework.utils.frames.frame import Frame

class Fan:
    is_on = False

    def __init__(self, pin_pwm, pin_power, slug=None, default_speed=100, on_payload_received=None, active_low=True):
        """
        pin_pwm: Pin du fil BLEU (Vitesse)
        pin_power: Pin du Relais (IN1)
        active_low: True si le relais s'active avec 0
        """
        self.pin_num_pwm = pin_pwm
        
        # Configuration du Relais
        self.power_pin = Pin(pin_power, Pin.OUT)
        self.active_low = active_low
        
        self.slug = slug
        self.default_speed = default_speed
        self.on_payload_received_callback = on_payload_received
        
        # Initialisation PWM
        self._init_pwm()
        
        # Démarrage éteint
        self.off()
        
        App().on_frame_received.append(self.on_frame_received)

    def _init_pwm(self):
        if not hasattr(self, 'pwm') or self.pwm is None:
            self.pwm = PWM(Pin(self.pin_num_pwm), freq=25000)

    def _set_speed(self, percent):
        self._init_pwm()
        safe_percent = max(0, min(100, int(percent)))
        duty = int((safe_percent / 100) * 65535)
        self.pwm.duty_u16(duty)

    def _set_power_pin(self, state_on):
        """Gère la logique Active Low / High"""
        if state_on:
            # Si on veut allumer : 0 si active_low, sinon 1
            self.power_pin.value(0 if self.active_low else 1)
        else:
            # Si on veut éteindre : 1 si active_low, sinon 0
            self.power_pin.value(1 if self.active_low else 0)

    def on(self):
        self._set_power_pin(True)
        self._set_speed(self.default_speed)
        self.is_on = True

    def off(self):
        if self.pwm:
            self.pwm.duty_u16(0)
        
        self._set_power_pin(False)
        self.is_on = False

    def on_frame_received(self, frame: Frame):
        if self.slug is None:
            return

        for payload in frame.payload:
            if payload.slug == self.slug:
                if self.on_payload_received_callback:
                    self.on_payload_received_callback(self, payload)
                else:
                    val = payload.value
                    if str(val).upper() == "ON" or val is True:
                        self.on()
                    elif str(val).upper() == "OFF" or val is False:
                        self.off()
