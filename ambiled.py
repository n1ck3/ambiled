#!/usr/bin/env python3

__author__ = "Niclas Helbro <niclas.helbro@gmail.com>"
__version__ = "AmbiLED 0.1"

import sys
import shutil
import os
import argparse
import time
import logging
import pyscreenshot as ImageGrab

V_LEDS = 46
H_LEDS = 76

LOGFORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(
    format=LOGFORMAT,
    datefmt='%m-%d %H:%M'
)
logger = logging.getLogger(__name__)


class AmbiLED():
    """
    * Get the current screen
    * Figure out which RGB color each LED should have
    * Send the LED color arryas to the LED stript.
    """
    def __init__(self, fps, loglevel):
        """
        Setup some constants.

        Arguments:
        fps = Specifies how many times per second the LEDs should update
        loglevel = Specify what loglevel should be used when running ambiled
        """
        self.run_interval = float(1000/fps)  # milliseconds
        self.loglevel = loglevel

    def get_colors_from_screen(self):
        """
        * Reset the leds color arrays
        * Grab the screen
        * Resize the image to the resolution of the LEDs available (See note)
        * figure out which LED should have which RGB color and update self.leds

        Note:
        Picking a pixel as a representation of which RGB color each LED
        should have is naïve and will not render a true result. To get the
        desired color for each LED, we will have to interpolate a bunch of
        pixels' colors. The idea behind rezising the image is that instead of
        calculating zones for each LED and interpolating these zones to get
        the RGB color that each LED should have, we resize the screen image
        to have as many pixels vertically and horizontally as we know we have
        LEDs and allow PIL to do the interpolation only once. Each pixel of
        the resized image will be an interpolated color that will result in
        each LED getting the right RGB color.
        """
        self.leds = {side: [] for side in ["top", "right", "bottom", "left"]}
        screen_path = os.path.join("tmp", "screens", "%s.jpg" % time.clock())
        screen = ImageGrab.grab()
        screen = screen.resize((H_LEDS, V_LEDS))
        if self.loglevel == "debug":
            screen.save(screen_path.replace(".jpg", "-resize.jpg"))

        screen = screen.load()
        for side in self.leds.keys():
            x_pos = y_pos = 0
            limit = H_LEDS if side in ["top", "bottom"] else V_LEDS
            while x_pos < limit and y_pos < limit:
                self.leds[side].append(screen[x_pos, y_pos])
                if side in ["top", "bottom"]:
                    x_pos += 1
                else:
                    y_pos += 1

    def run(self):
        """
        This will be the main loop of the program. When this method is called,
        it will keep running until KeyboardInterrupt (ctrl-c) or SystemExit
        is raised.
        """
        try:
            while True:
                start_time = time.clock() * 1000  # milliseconds
                self.get_colors_from_screen()
                end_time = time.clock() * 1000  # milliseconds
                run_time = (end_time-start_time)  # milliseconds
                logger.info("Ran in: %1.1f ms" % run_time)
                if run_time < self.run_interval:
                    logger.info("Next run in: %1.1f ms" % (
                        self.run_interval-run_time),
                    )
                    time.sleep((self.run_interval-run_time)/1000)
        except KeyboardInterrupt:
            logger.critical("Caught ctrl-c. Exiting.")
            sys.exit(1)
        except SystemExit:
            raise


def __main__():
    """
    """
    loglevels = ["critical", "error", "warning", "info", "debug"]

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--loglevel",
        help="Set loglevel",
        default="info",
        choices=loglevels
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

    # Set loglevel
    if args.loglevel in loglevels:
        logger.setLevel(getattr(logging, args.loglevel.upper()))

    # Do some cleaning up before running AmbiLED
    tmp_screens = os.path.join("tmp", "screens")
    shutil.rmtree("tmp", ignore_errors=True)
    if args.loglevel == "debug":
        # Create the tmp direcotry and the tmp/screens directory
        os.makedirs(tmp_screens)

        # Setup another loghandler and write the log to tmp/ambiled.log
        handler = logging.FileHandler(os.path.join("tmp/ambiled.log"))
        formatter = logging.Formatter(LOGFORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Instantiate and run AmbiLED
    ambiled = AmbiLED(fps=args.fps, loglevel=args.loglevel)
    ambiled.run()

if __name__ == __main__():
    __main__()
