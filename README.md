ambiled
=======

Ambiled is a python app that is allows WS2811 and WS2812 RGB LED strips mounted at the back of a TV create ambient light matching what is currently on the the TV. See screenshot.

![Ambilight](http://upload.wikimedia.org/wikipedia/commons/3/39/Ambilight-2.jpg "Ambilight")

# What do you need?

1. A computer outputting its graphics to a TV
1. Python 3
1. WS2811 and WS2812 RGB LED Strips (with appropriate power supply)
1. A microcontroller that can drive the LED strips

# How does it work:

1. Take a screenshot of what is currently on the screen.
1. Rezise the screenshot to the `x` by `y` pixels where `x` is the amount of LEDs in the top and bottom LED strips and `y` is the number of LEDs on the left and right LED strips.
1. Create arrays of RGB colors for all the LEDs in the 4 strips.
1. Update the LEDs in the strips via a microcrontroller which has the ability to control WS2811 and WS2812 LED strips. 
