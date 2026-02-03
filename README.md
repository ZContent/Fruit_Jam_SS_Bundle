# The Fruit Jam Screensaver Bundle

This repository is a collection of screensavers for the Adafruit [Fruit Jam OS](https://learn.adafruit.com/fruit-jam-os), an operating system running on the Fruit Jam by [Adafruit](https://adafruit.com). It is a credit-card-sized, RP2350-powered mini computer designed for retro emulation and other fun projects.
This bundle currently contains 2 screensavers. Visit us again to see if we have added more!

The screensavers included in this bundle are:
* Maze - A screensaver that creates random mazes and then solves them.
* Star Field - a screen of moving stars reminiscent of a famous 1960s SciFi TV show.

For the maze screensaver, 3 different size mazes are created, from easy to hard. You can change this behavior by modifying the **MAZE_PICK** line near the top of the file. You can change it to a specific size maze (0-2), random choice (**MAZE_RANDOM**),
or the default display of the maze sizes in order (**MAZE_SEQUENCE**). The harder the maze, the longer it takes to generate the maze and solve it, so you will see a blank screen at the start when the first maze is being created.

For the star field screensaver, you can specify whether are not to show the star streaks by modifying the **STREAK** line near the top of the file to "True" or "False". You can also modify the number of stars to display with the **STARCOUNT** line, 
however, the more stars you have the slower the performance will be.

These screen savers were written by Dan Cogliano. You will find more information about Dan and his projects at [DanTheGeek.com](https://DanTheGeek.com). 
