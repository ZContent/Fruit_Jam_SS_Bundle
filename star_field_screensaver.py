"""
Starfield Screensaver for the Adafruit Fruit Jam
and Fruit Jam OS
Dan Cogliano, https://DanTheGeek.com
"""

import os
import random
import time
import math
import random

from displayio import Group, OnDiskBitmap, TileGrid, Bitmap, Palette
import bitmaptools

import adafruit_imageload

STARCOUNT = 100
# set True to show star streaks
STREAK = True

SCREENWIDTH=320
SCREENHEIGHT=240

class star:
    width = SCREENWIDTH
    height = SCREENHEIGHT
    x = width/2
    y = height/2
    px = x
    py = y
    velocity = 2
    acceleration = .1
    acceleration = .05
    accellist = [.02,.02,.05,.05,.05,.05,.05,.05,.1,.15]
    angle = 30
    color = 0
    counter = 0

    def __init__(self, bmp):
        self.bmp = bmp
        self.reset()

    def reset(self):
        self.x = self.px = 0
        self.y = self.py = 0
        self.angle = random.randint(0,359)
        self.velocity = random.uniform(0,1.0)
        self.xvelocity = self.velocity * math.sin(math.radians(self.angle))
        self.yvelocity = self.velocity * math.cos(math.radians(self.angle))
        self.maxcolor = random.randint(10,15)
        self.acceleration = self.accellist[random.randint(0,len(self.accellist)-1)]
        self.color = 0
        #print(f"angle:{self.angle}, velocity:{self.xvelocity},{self.yvelocity}")

    def move(self):
        if self.px < self.width/2 and self.py < self.height/2:
            if STREAK:
                # erase streak line
                bitmaptools.draw_line(self.bmp,
                    int(self.width//2+self.px),int(self.height//2+self.py),
                    int(self.width//2+self.x),int(self.height//2+self.y),0)
            else:
                self.bmp[int(self.width//2 + self.x), int(self.height//2 + self.y)] = 0
            self.px = self.x
            self.py = self.y
            self.x += self.xvelocity + (self.acceleration*(abs(self.x)))*math.sin(math.radians(self.angle))
            self.y += self.yvelocity + (self.acceleration*(abs(self.y)))*math.cos(math.radians(self.angle))
            if abs(self.px) < self.width/2 and abs(self.py) < self.height/2:
                if STREAK:
                # draw streak line
                    bitmaptools.draw_line(self.bmp,
                    int(self.width//2+self.px),int(self.height//2+self.py),
                    int(self.width//2+self.x),int(self.height//2+self.y),self.color)
                else:
                    self.bmp[int(self.width//2 + self.x), int(self.height//2 + self.y)] = self.color
                self.color = min(self.maxcolor,int((self.x*self.x + self.y*self.y) /(self.height/2*self.height/2)*self.maxcolor))
                self.counter += 1

            else:
                self.reset()



class StarFieldScreenSaver(Group):

    display_size = (SCREENWIDTH, SCREENHEIGHT)
    last_move_time = 0
    move_cooldown = 0.01  # seconds

    def __init__(self):
        super().__init__()
        self.stars = []
        self.init_graphics()

    def init_graphics(self):
        self.bmp = bg_bmp = Bitmap(self.display_size[0], self.display_size[1], 16)
        for i in range(STARCOUNT):
            test_object = star(bg_bmp)
            self.stars.append(test_object)
        bg_palette = Palette(16)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x111111
        bg_palette[2] = 0x222222
        bg_palette[3] = 0x333333
        bg_palette[4] = 0x444444
        bg_palette[5] = 0x888888
        bg_palette[6] = 0x999999
        bg_palette[7] = 0x999999
        bg_palette[8] = 0xaaaaaa
        bg_palette[9] = 0xaaaaaa
        bg_palette[10] = 0xbbbbbb
        bg_palette[11] = 0xbbbbbb
        bg_palette[12] = 0xcccccc
        bg_palette[13] = 0xdddddd
        bg_palette[14] = 0xeeeeee
        bg_palette[15] = 0xffffff

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
            for i in range(STARCOUNT):
                self.stars[i].move()
            #self.stars.move()
            #self.stars[0].move()
            return True

        return False
