#!/usr/bin/env python3

__author__ = "Niclas Helbro <niclas.helbro@gmail.com>"
__version__ = "AmbiLED 0.1"

import sys
import os
import serial
import glob
import shutil
import argparse
import time
import logging
import pyscreenshot as ImageGrab
from PIL import Image

V_LEDS = 46
H_LEDS = 76

LOGFORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(
    format=LOGFORMAT,
    datefmt='%m-%d %H:%M'
)
logger = logging.getLogger(__name__)


class NoSerialDeviceFound(Exception):
    def __init__(self, *args):
        logger.critical("No serial device found. Exiting...")
        sys.exit(1)


class FakeSerialDevice():
    def _save_led_strip(self, string):
        """
        Save an image of the LED strip for acceptance testing.

        Takes string of HEX (usually sent to LED strip) and saves an image of
        the colors of the LED strip.
        """
        rgb_list = self._hex_string_to_rgb_list(string)
        rgb_list.reverse()
        led_strip = Image.new("RGB", (len(rgb_list), 1))
        led_strip.putdata(rgb_list)
        led_strip.save(os.path.join("tmp", "leds.jpg"))

    def _hex_string_to_rgb_list(self, string):
        """
        Make an RGB list from a string of HEX colors
        """
        n = 6
        hex_list = [string[i:i+n] for i in range(0, len(string), n)][:-1]
        rgb_list = [(
            int(hex_color[2:4], 16),  # R
            int(hex_color[0:2], 16),  # G
            int(hex_color[4:5], 16)  # B
        ) for hex_color in hex_list]
        return rgb_list

    def write(self, string):
        logger.info("Writing to fake serial device: %s" % string)
        self._save_led_strip(string)


class AmbiLED():
    """
    * Get the current screen
    * Figure out which HEX RGB color each LED should have
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

        serial_devs = glob.glob('/dev/tty.usbmodem*')
        serial_dev = None if len(serial_devs) == 0 else serial_devs[0]

        # Build a dict of all the coordinates we want to sample later on.
        self.led_positions = {
            "left": [(0, y) for y in range(0, V_LEDS)],
            "top": [(x, V_LEDS-1) for x in range(0, H_LEDS)],
            "right": [(H_LEDS-1, y) for y in range(V_LEDS-1, -1, -1)],
            "bottom": [(x, 0) for x in range(H_LEDS-1, -1, -1)]
        }

        if not serial_dev:
            if loglevel == "debug":
                logger.warning("No serial device found. Using fake.")
                self.serial_dev = FakeSerialDevice()
            else:
                raise NoSerialDeviceFound()
        else:
            lpspeed = 115200
            self.serial_dev = serial.Serial(serial_dev, lpspeed, timeout=0)

    def _rgb_list_to_hex_string(self, rgb_list):
        """
        Takes a list of RGB values and returns a string of HRX GRB values
        """
        hex_list = ["%02x%02x%02x" % (x[1], x[0], x[2]) for x in rgb_list]
        return "%s\n" % "".join(hex_list)

    def get_colors_from_screen(self):
        """
        * Reset the leds color arrays
        * Grab the screen
        * Resize the image to the resolution of the LEDs available (See note)
        * figure out which LED should have which HEX GRB color and update
          self.leds

        Note:
        Picking a pixel as a representation of which HEX RGB color each LED
        should have is naïve and will not render a true result. To get the
        desired color for each LED, we will have to interpolate a bunch of
        pixels' colors. The idea behind rezising the image is that instead of
        calculating zones for each LED and interpolating these zones to get
        the HEX RGB color that each LED should have, we resize the screen image
        to have as many pixels vertically and horizontally as we know we have
        LEDs and allow PIL to do the interpolation only once. Each pixel of
        the resized image will be an interpolated color that will result in
        each LED getting the right HEX RGB color.
        """
        self.leds = {side: [] for side in ["top", "right", "bottom", "left"]}
        screen = ImageGrab.grab()
        screen = screen.resize((H_LEDS, V_LEDS))
        if self.loglevel == "debug":
            screen.save(os.path.join("tmp", "screen.jpg"))

        for side in self.leds.keys():
            for coordinate in self.led_positions[side]:
                rgb = screen.getpixel(coordinate)
                self.leds[side].append(rgb)
            self.leds[side].reverse()

    def update_led_strips(self):
        """
        Sends the color arrays to the LED strips.

        Assumes that the strips start at X=0, Y=0 (viewed from the front of
        TV), and runs clockwise (also viewed from the front of the TV).
        """
        # TODO: Understand this.
        # ordered_leds = \
        #     self.leds["left"] + \
        #     self.leds["top"] +  \
        #     self.leds["right"] + \
        #     self.leds["bottom"]

        ordered_leds = \
            self.leds["left"] + \
            self.leds["bottom"] +  \
            self.leds["right"] + \
            self.leds["top"]

        # LED strips wants the colors on the wrong order, the first color goes
        # to the LED at the end.
        ordered_leds.reverse()

        hex_string = self._rgb_list_to_hex_string(ordered_leds)
        self.serial_dev.write(hex_string)

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
                self.update_led_strips()

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
    shutil.rmtree("tmp", ignore_errors=True)
    if args.loglevel == "debug":
        # Create the tmp directory
        os.makedirs("tmp")

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
