"""
Maze Screensaver
Dan Cogliano, https://DanTheGeek.com
"""

import os
import random
import time
import math
import random

from displayio import Group, OnDiskBitmap, TileGrid, Bitmap, Palette

import adafruit_imageload

SCREENWIDTH=320
SCREENHEIGHT=240
class star:
    width = SCREENWIDTH
    height = SCREENHEIGHT
    counter = 0

    def __init__(self, bmp):
        self.bmp = bmp
        self.reset()

    def reset(self):

class StarFieldScreenSaver(Group):

    display_size = (SCREENWIDTH, SCREENHEIGHT)
    last_move_time = 0
    move_cooldown = 0.05  # seconds
    colors = [0x000000, 0x111111, 0x222222, 0x333333, 0x444444, 0x555555, 0x666666, 0x777777,
        0x888888, 0x999999, 0xaaaaaa, 0xbbbbbb, 0xcccccc, 0xdddddd, 0xeeeeee, 0xffffff]


    def __init__(self):
        super().__init__()
        self.init_graphics()

    def init_graphics(self):
        self.bmp = bg_bmp = Bitmap(self.display_size[0], self.display_size[1], 4)
        bg_palette = Palette(4)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x888888
        bg_palette[2] = 0xffffff
        bg_palette[3] = 0xff0000

        bg_tg = TileGrid(bitmap=bg_bmp, pixel_shader=bg_palette)
        bg_bmp.fill(0)
        bg_group = Group(scale=1)
        bg_group.append(bg_tg)
        self.append(bg_group)

    def tick(self):

        now = time.monotonic()
        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            #print("tick")
            return True

        return False
