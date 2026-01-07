from framework.controller import Controller
from framework.utils.gpio import GPIO
from framework.utils.ws.interface import WebsocketInterface
from src.shrooms.shroom import Shroom
from framework.components.led_strip import LedStrip
from framework.app import App


class ShroomsController(Controller):
    shrooms = []
    forest_lighten = False

    def __init__(
        self,
        leds_pin,
        leds=136,
        shrooms=8,
        shroom_len=3,
        gap=10,
        color=(255, 255, 0),
        aux_leds_pin=None,
        aux_leds=300,
    ):
        super().__init__()
        self.shrooms.append(Shroom("SH_1", GPIO.GPIO34, 100, 350, 500))
        self.shrooms.append(Shroom("SH_2", GPIO.GPIO36, 100, 350, 500))
        # self.shrooms.append(Shroom("SH_3", GPIO.GPIO39))

        # Main strip (existing)
        self.leds_main = LedStrip(leds_pin, leds, default_color=color)
        self.leds_main_count = leds

        # Aux strip (new, len 300 by default)
        self.leds_aux = None
        self.leds_aux_count = int(aux_leds)
        if aux_leds_pin is not None:
            self.leds_aux = LedStrip(aux_leds_pin, self.leds_aux_count, default_color=color)

        self.shrooms_count = shrooms
        self.shroom_len = shroom_len
        self.gap = gap
        self.color = color

        App().setup.append(self.setup)

    def _layout_shrooms_on_strip(self, strip: LedStrip, strip_len: int, shrooms_count:int):
        # Enforce minimums
        shroom_len = max(3, int(self.shroom_len))
        min_gap = max(0, int(self.gap))  # interpret self.gap as MINIMUM internal gap
        shrooms = max(0, int(shrooms_count))

        if shrooms == 0:
            return

        # Minimum required length: shrooms blocks + minimum internal gaps
        required_min = shrooms * shroom_len + (shrooms - 1) * min_gap
        if required_min > strip_len:
            print(
                f"Cannot fit on strip: leds={strip_len}, shrooms={shrooms}, shroom_len={shroom_len}, min_gap={min_gap} "
                f"(required_min={required_min} > leds={strip_len})"
            )
            return

        leftover = strip_len - required_min

        # We have (shrooms + 1) gaps: left end, (shrooms-1) internal, right end
        gaps_count = shrooms + 1
        extra_each = leftover // gaps_count
        remainder = leftover % gaps_count

        # Base gaps: ends start at 0, internal start at min_gap
        gaps = [0] + [min_gap] * (shrooms - 1) + [0]

        # Evenly spread extra across all gaps
        gaps = [g + extra_each for g in gaps]

        # Put remainder preferentially on the ends to make them longer (then inward)
        order = [0, len(gaps) - 1] + list(range(1, len(gaps) - 1))
        for k in range(remainder):
            gaps[order[k]] += 1

        # Paint shrooms using computed gaps
        idx = gaps[0]  # left end gap
        for s in range(shrooms):
            start = idx
            end = idx + shroom_len  # exclusive

            for j in range(start, end):
                strip.set_pixel(j, self.color, False)

            idx = end
            if s < shrooms - 1:
                idx += gaps[s + 1]  # internal gap after this shroom

    def setup(self):
        # Apply layout to main strip
        self._layout_shrooms_on_strip(self.leds_main, self.leds_main_count, 10)

        # Apply layout to aux strip (if configured)
        if self.leds_aux is not None:
            self._layout_shrooms_on_strip(self.leds_aux, self.leds_aux_count, 20)

    def update(self):
        if self.is_shrooms_lighten() and not self.forest_lighten:
            # Display both strips
            self.leds_main.display()
            if self.leds_aux is not None:
                self.leds_aux.display()

            self.forest_lighten = True
            print("Shroom forest lighten !")
            WebsocketInterface().send_value("01-shroom-forest-lighten", self.forest_lighten)

    def is_shrooms_lighten(self):
        checksum = True
        for shroom in self.shrooms:
            checksum = checksum and shroom.lighten
        return checksum
