# The Fruit Jam Screensaver Bundle

This repository is a collection of screensavers created for the Adafruit [Fruit Jam OS](https://learn.adafruit.com/fruit-jam-os), an operating system running on the Fruit Jam by [Adafruit](https://adafruit.com). It is a credit-card-sized, RP2350-powered mini computer designed for retro emulation and other fun projects.

This bundle contains 4 screensavers:

* Weather Clock - A display containing the current date, time, temperature and weather icon
* 15 Puzzle - Images are displayed as sliding tiles in a 4x4 grid
* Maze - A screensaver that creates random mazes and then solves them.
* Star Field - a screen of moving stars reminiscent of a famous 1960s SciFi TV show.

The weather clock displays a simple view of the current weather and time. The background display also indicates whether it is currently daytime or nighttime (determined by sunrise and sunset times). In addition to the wifi settings, the location and timezone are configured in the settings.toml file. If not set, the weather and time for New York City are displayed. From the weather_clock_screensaver.py file, copy the LATITUDE, LONGITUDE, TMZ and METRIC lines to the settings.toml file on the CircuitPython drive and modify them for your location. Note: Latitude and longitude values can be defined either by direction (N,S,E,W) or by signed number. The screensaver requires signed numbers. So, for latitudes with an "S" and/or longitudes with "W", use a minus sign with the value.Set METRIC to 1 for displaying metric values (Celcius temperatures) or set to 0 for non-metric values (Fahrenheit temperatures).

For the 15 puzzle, a different image is chosen each time the screensaver is activated, then converted into tiles and slid within a 4x4 grid like the classic toy. With the default settings, the tiles slide randomly for about 1 minute before resolving to the initial starting position, and then started again. Several images are included, but you can add your own to the ssbundle_assets/15puzzle folder, which should be 320 pixels width and 240 pixels height and 256 colors.

For the maze screensaver, 3 different size mazes are created, from easy to hard. You can change this behavior by modifying the **MAZE_PICK** line near the top of the file. You can change it to a specific size maze (0-2), random choice (**MAZE_RANDOM**),
or the default display of the maze sizes in order (**MAZE_SEQUENCE**). The harder the maze, the longer it takes to generate the maze and solve it, so you will see a blank screen at the start when the first maze is being created.

For the star field screensaver, you can specify whether are not to show the star streaks by modifying the **STREAK** line near the top of the file to "True" or "False". You can also modify the number of stars to display with the **STARCOUNT** line, 
however, the more stars you have the slower the performance will be.

## Installation

It is always best to install the latest version of [CircuitPython](https://CircuitPython.org). You will first need to install the [Fruit Jam OS](https://learn.adafruit.com/fruit-jam-os) for the Adafruit Fruit Jam. This will also include the libraries needed by the Screensaver Bundle, so no additional libraries are needed.

Copy the screensaver files in this folder to the "/apps/screensavers" folder on the Fruit Jam. Run the Screensaver app on the Fruit Jam OS to choose one of the screensavers. 
Refer to the Fruit Jam OS learn guide for how to configure the screensaver manually.

## Related Links

- [Adafruit Fruit Jam Learn Guide](https://learn.adafruit.com/adafruit-fruit-jam) - The credit card sized microcomputer used to run these screensavers
- [Fruit Jam OS Learn Guide](https://learn.adafruit.com/fruit-jam-os) - Required for running the Screensaver Bundle
- [ePaper Maze Maker Learn Guide](https://learn.adafruit.com/epaper-maze-maker) - A maze making program written by the same author written for Arduino in C++ using an ePaper display

---
These screen savers were written by Dan Cogliano. You will find more information about Dan and his projects at [DanTheGeek.com](https://DanTheGeek.com).
Other Fruit Jam apps written by Dan include the [CPZ Machine](https://danthegeek.com/cpz-machine/), a Zork/Z Machine port to the Fruit Jam, and the retro-styled [Moon Miner](https://danthegeek.com/moon-miner/) arcade game.

