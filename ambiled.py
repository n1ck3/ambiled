import time
import pyscreenshot as ImageGrab
from PIL import Image, ImageFilter

LEDS = {
    "TOP": [
        "t0", "t1", "t2", "t3", "t4", "t5",
        "t6", "t7", "t8", "t9", "t10", "t11",
    ],
    "RIGHT": [
        "r0", "r1", "r2", "r3", "r4", "r5",
        "r6", "r7", "r8"
    ],
    "BOTTOM": [
        "b0", "b1", "b2", "b3", "b4", "b5",
        "b6", "b7", "b8", "b9", "b10", "b11",
    ],
    "LEFT": [
        "l0", "l1", "l2", "l3", "l4", "l5",
        "l6", "l7", "l8"
    ]
}

TICK = 500/1000  # Milliseconds


class AmbiLed():
    """
    The base class which does the cool stuff.
    """
    def __init__(self):
        """
        This method makes sure we save some constants.
        """
        self.width = len(LEDS["TOP"])
        self.height = len(LEDS["RIGHT"])
        self.leds = {
            side: [[led, None] for led in LEDS[side]] for side in LEDS.keys()
        }

    def get_current_screen(self):
        return ImageGrab.grab()

    def get_colors_for_leds(self):
        screen = self.get_current_screen()
        screen = screen.resize((self.width, self.height), Image.NEAREST)
        screen = screen.filter(ImageFilter.BLUR)
        screen = screen.load()

        for side, leds in self.leds.items():
            x_pos = y_pos = idx = 0
            while idx < len(leds):
                self.leds[side][idx][1] = screen[x_pos, y_pos]
                if side in ["TOP", "BOTTOM"]:
                    x_pos += 1
                else:
                    y_pos += 1
                idx += 1

    def run(self):
        try:
            idx = 0
            while True:
                idx += 1
                start = time.clock()
                self.get_colors_for_leds()
                print(self.leds)
                print("#%s took %1.3f seconds\n" % (idx, (time.clock()-start)))
                time.sleep(TICK)
        except (KeyboardInterrupt, SystemExit):
            raise


def __main__():
    ambiled = AmbiLed()
    ambiled.run()

if __name__ == __main__():
    __main__()
