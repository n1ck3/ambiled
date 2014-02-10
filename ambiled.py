import pyscreenshot as ImageGrab
import time

TOP = [
    "t0", "t1", "t2", "t3", "t4", "t5",
    "t6", "t7", "t8", "t9", "t10", "t11",
]
RIGHT = [
    "r0", "r1", "r2", "r3", "r4", "r5",
    "r6", "r7", "r8"
]
BOTTOM = [
    "b0", "b1", "b2", "b3", "b4", "b5",
    "b6", "b7", "b8", "b9", "b10", "b11",
]
LEFT = [
    "l0", "l1", "l2", "l3", "l4", "l5",
    "l6", "l7", "l8"
]

TICK = 200/1000  # Milliseconds


class AmbiLed():
    """
    The base class which does the cool stuff.
    """
    def __init__(self):
        """
        This method makes sure we save some constants, like the screen width
        and height.
        """
        self.width, self.height = self.get_current_screen().size
        self.sides = {
            "TOP": {
                "length": self.width,
                "num_leds": len(TOP),
                "step_x": int(self.width / len(TOP)),
                "step_y": 0,
                "leds": [[key, None] for key in TOP]
            },
            "RIGHT": {
                "length": self.height,
                "num_leds": len(RIGHT),
                "step_x": 0,
                "step_y": int(self.height / len(RIGHT)),
                "leds": [[key, None] for key in RIGHT]
            },
            "BOTTOM": {
                "length": self.width,
                "num_leds": len(BOTTOM),
                "step_x": int(self.width / len(BOTTOM)),
                "step_y": 0,
                "leds": [[key, None] for key in BOTTOM]
            },
            "LEFT": {
                "length": self.height,
                "num_leds": len(LEFT),
                "step_x": 0,
                "step_y": int(self.height / len(LEFT)),
                "leds": [[key, None] for key in LEFT]
            }
        }
        self.get_colors_for_leds()

    def get_current_screen(self):
        return ImageGrab.grab()

    def get_colors_for_leds(self):
        screen = self.get_current_screen().load()
        for name, side in self.sides.items():
            x_pos = y_pos = 0
            idx = 0
            while idx < side["num_leds"]:
                led, color = side["leds"][idx]
                self.sides[name]["leds"][idx][1] = screen[x_pos, y_pos]
                x_pos += side["step_x"]
                y_pos += side["step_y"]
                idx += 1

    def print_colors_for_leds(self):
        print(self.sides)


def __main__():
    ambiled = AmbiLed()
    try:
        idx = 0
        while True:
            start = time.clock()
            ambiled.get_colors_for_leds()
            ambiled.print_colors_for_leds()
            idx += 1

            print("Run: %s took %1.3f seconds" % (idx, (time.clock()-start)))
            print()

            time.sleep(TICK)
    except (KeyboardInterrupt, SystemExit):
        raise

if __name__ == __main__():
    __main__()
