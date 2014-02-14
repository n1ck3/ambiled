#!/usr/bin/env python3

__author__ = "Niclas Helbro <niclas.helbro@gmail.com>"
__version__ = "AmbiLED 0.1"

import argparse
import time
import logging
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

LOGLEVELS = ["critical", "error", "warning", "info", "debug"]
logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M'
)
logger = logging.getLogger("ambiled")


class AmbiLED():
    """
    Get the current screen and figure out which RGB color
    each LED should have.
    """
    def __init__(self, fps):
        """
        Setup some constant variables as well as self.leds which holds all
        four LED strips' color information at any given time.

        Arguments:
        fps = Specifies how many times per second the LEDs should update
        """
        self.tick = float(1000/fps)  # milliseconds
        self.width = len(LEDS["TOP"])
        self.height = len(LEDS["RIGHT"])
        self.leds = {
            side: [[led, None] for led in LEDS[side]] for side in LEDS.keys()
        }

    def get_colors_from_screen(self):
        """
        Grab the screen, resize the image to the resolution of the LEDs
        available (See note), figure out which led should have which RGB
        color and update self.leds.

        Note: Picking a pixel as a representation of which RGB color each LED
        should have is naïve and will not render a true result. To get the
        desired color for each LED, we will have to interpolate a bunch of
        pixels' colors. The idea behind rezising the image is that instead of
        calculating zones for each LED and interpolating these zones to get
        the RGB color that each LED should have, we resize the screen image
        to have as many pixels vertically and horizontally as we know we have
        LEDs and allow PIL to do the interpolation only once. Each pixel of the
        resized image will be an interpolated color that will result in each
        LED getting the right RGB color.
        """
        screen = ImageGrab.grab()
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
        """
        This will be the main loop of the program. When this method is called,
        it will keep running until KeyboardInterrupt (ctrl-c) or SystemExit
        is raised.
        """
        try:
            idx = 0
            while True:
                idx += 1
                start_time = time.clock() * 1000  # milliseconds
                self.get_colors_from_screen()
                logger.debug("leds: %s" % self.leds)
                end_time = time.clock() * 1000  # milliseconds
                run_time = (end_time-start_time)  # milliseconds
                logger.info("Run #%s:%1.3f ms" % (idx, run_time))
                if run_time < self.tick:
                    logger.info("Sleep: %1.3f ms" % (self.tick-run_time))
                    time.sleep((self.tick-run_time)/1000)
        except (KeyboardInterrupt, SystemExit):
            raise


def __main__():
    """
    Parse arguments, set the loglevel, instantiate and run AmbiLED.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--loglevel",
        help="Set loglevel",
        default="info",
        choices=LOGLEVELS
    )
    parser.add_argument(
        "-n",
        "--fps",
        help="Set fps",
        type=int,
        default=24,
        choices=range(1, 31)
    )
    args = parser.parse_args()

    if args.loglevel in LOGLEVELS:
        logger.setLevel(getattr(logging, args.loglevel.upper()))

    # Ok, so instantiate the ambiled class and tell it to run!
    ambiled = AmbiLED(fps=args.fps)
    ambiled.run()

if __name__ == __main__():
    __main__()
