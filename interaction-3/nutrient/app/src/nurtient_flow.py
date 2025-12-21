import time

class NutrientFlow:
    """
    Animation: des 'paquets' (vagues) se déplacent sur le strip.
    - wave_len : longueur (nb leds allumées) d'un paquet
    - gap_len  : nb leds éteintes entre 2 paquets
    - speed    : leds par seconde (float possible)
    - fade     : True -> bord adouci (petit dégradé)
    - reverse  : True -> flux inversé (droite->gauche au lieu de gauche->droite)
    """
    def __init__(self, num_pixels, color=(0, 255, 0), wave_len=6, gap_len=10, speed=20.0, fade=True, reverse=False):
        # ✅ Bon choix: c'est une propriété du flow (direction), donc dans le constructeur
        self.n = num_pixels
        self.color = color
        self.wave_len = max(1, int(wave_len))
        self.gap_len = max(0, int(gap_len))
        self.speed = float(speed)
        self.fade = bool(fade)
        self.reverse = bool(reverse)

        self.period = self.wave_len + self.gap_len  # longueur d’un motif complet
        self.pos = 0.0
        self._last = time.ticks_ms()

    def set_speed(self, speed):
        self.speed = float(speed)

    def set_reverse(self, reverse=True):
        self.reverse = bool(reverse)

    def toggle_reverse(self):
        self.reverse = not self.reverse

    def set_pattern(self, wave_len=None, gap_len=None):
        if wave_len is not None:
            self.wave_len = max(1, int(wave_len))
        if gap_len is not None:
            self.gap_len = max(0, int(gap_len))
        self.period = self.wave_len + self.gap_len

    def _scale(self, c, k):
        # k: 0..1
        return (int(c[0]*k), int(c[1]*k), int(c[2]*k))

    def step(self, pixels):
        # delta time
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last) / 1000.0
        self._last = now

        # avance en "leds" (sens selon reverse)
        direction = -1.0 if self.reverse else 1.0
        self.pos = (self.pos + direction * self.speed * dt) % self.period

        # Nettoyage buffer
        for i in range(self.n):
            pixels[i] = (0, 0, 0)

        # Dessin des vagues (motif répété sur tout le strip)
        base = int(self.pos)  # décalage entier
        for start in range(-self.period, self.n + self.period, self.period):
            head = start + base

            # wave_len leds allumées à partir de head
            for j in range(self.wave_len):
                idx = head + j
                if 0 <= idx < self.n:
                    if self.fade and self.wave_len >= 3:
                        # bords adoucis: 20% -> 100% -> 20%
                        if j == 0 or j == self.wave_len - 1:
                            k = 0.2
                        elif j == 1 or j == self.wave_len - 2:
                            k = 0.6
                        else:
                            k = 1.0
                        pixels[idx] = self._scale(self.color, k)
                    else:
                        pixels[idx] = self.color

        return pixels