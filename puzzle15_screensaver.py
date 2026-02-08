"""
15 Puzzle Screensaver for the Adafruit Fruit Jam
and Fruit Jam OSDan Cogliano, https://DanTheGeek.com
"""

#import supervisor
from adafruit_fruitjam.peripherals import request_display_config, get_display_config
import adafruit_imageload

import board
import displayio
import os
import random
import time
import math
import random

SCREENWIDTH = 320
SCREENHEIGHT = 240
SCREENDEPTH = 8

from displayio import Group, OnDiskBitmap, TileGrid, Bitmap, Palette
import bitmaptools

class Puzzle15():
    def getX(self,num):
        return num%4

    def getY(self,num):
        return num//4

    def toNum(self,x,y):
        return y*4+x

    def __init__(self):
        self.grid = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,-1]
        self.pos = len(self.grid)-1
        self.lastmove = 0 # 1: horizontal, 1: vertical

    def print_puzzle(self):
        for i in range(16):
            if i%4 == 0:
                print()
            print(f"{self.grid[i]:02d} ",end="")
        print()
    # num: puzzle position (0-15)
    # num has a tile
    def move(self,num):
        print("before:")
        self.print_puzzle()
        num = num%16
        x = self.getX(num)
        y = self.getY(num)
        # can this piece move?
        if self.pos != num:
            #horizontal check
            hcheck = [
                self.toNum(0,y),
                self.toNum(1,y),
                self.toNum(2,y),
                self.toNum(3,y)
            ]
            #vertical check
            vcheck = [
                self.toNum(x,0),
                self.toNum(x,1),
                self.toNum(x,2),
                self.toNum(x,3)
            ]
            print(f"num: {num}, blank square at {self.pos}")
            print(f"hcheck: {hcheck}, vcheck: {vcheck}")
            if self.grid[num] in hcheck:
                index = hcheck.index(num)
                print(f"h index: {index}")
                last = self.grid[hcheck[0]]
                self.grid[hcheck[0]] = -1
                for i in range(index+1,4):
                    tmp = self.grid[hcheck[i]]
                    self.grid[hcheck[i]] = last
                    last = tmp
            elif self.grid[num] in vcheck:
                index = vcheck.index(num)
                print(f"v index: {index}")

                last = self.grid[vcheck[0]]
                self.grid[vcheck[0]] = -1
                for i in range(index+1,4):
                    tmp = self.grid[vcheck[i]]
                    self.grid[vcheck[i]] = last
                    last = tmp

        print("after:")
        self.print_puzzle()

    def random_move(self):
        x = self.getX(self.lastmove)
        y = self.getY(self.lastmove)
        check = []
        move = -1
        if lastmove == 1: #last vertical, now horizontal
            check = [
                self.toNum(0,y),
                self.toNum(1,y),
                self.toNum(2,y),
                self.toNum(3,y)
            ]
        else: #last horizontal, now vertical
            check = [
                self.toNum(x,0),
                self.toNum(x,1),
                self.toNum(x,2),
                self.toNum(x,3)
            ]
        while True:
            move = random.randint(0,3)
            if move != self.pos:
                break
        lastmove = (lastmove+1)%2
        # move affected squares (future)

class Puzzle15ScreenSaver(Group):

    #display_size = get_display_config()
    #screenwidth = display_size[0]
    #screenheight = display_size[1]
    #screendepth = display_size[2]
    display_size = [SCREENWIDTH,SCREENHEIGHT]
    screenwidth = SCREENWIDTH
    screenheight = SCREENHEIGHT

    tile_width = screenwidth//4
    tile_height = screenheight//4
    #display_size = (screenwidth, screenheight)
    tiles = []
    last_move_time = 0
    move_cooldown = 5  # seconds
    pos = 0
    move = 0
    moves = [12,0,3,15]

    def __init__(self):
        super().__init__()
        self.init_graphics()
        self.puzzle = Puzzle15()
        #self.get_screensnapshot()
        self.load_image()

    def init_graphics(self):
        print("debug init_graphics")
        self.bmp = Bitmap(self.screenwidth, self.screenheight, SCREENDEPTH)
        bg_palette = Palette(2)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x004400
        bg_tg = TileGrid(bitmap=self.bmp, pixel_shader=bg_palette)
        self.bmp.fill(1)
        bg_group = Group(scale=1)
        print(bg_group)
        bg_group.append(bg_tg)
        self.append(bg_group)
        print(f"display size: {self.display_size}")
        print("debug end init_graphics")

    def load_image(self):
        #"""
        bitmap, bpal = adafruit_imageload.load(
            "/apps/Screensavers/adafruit-logo.bmp",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
            )
        #"""
        self.group = Group(scale=1)
        for i in range(16):
            self.tiles.append(TileGrid(bitmap,pixel_shader=bpal,width=1,height=1,
                tile_width=self.tile_width,tile_height=self.tile_height))

            self.group.append(self.tiles[-1])
        self.append(self.group)

    def tick(self):
        #print("debug tick")
        now = time.monotonic()
        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            print("tick")
            for i in range(16):
                self.group[i].x = (self.screenwidth//4)*(i%4)
                self.group[i].y = (self.screenheight//4)*(i//4)
                print(f"tile coords: ({i}){self.group[i].x},{self.group[i].y}: {self.puzzle.grid[i]}")
                if self.puzzle.grid[i] != -1:
                    self.tiles[i][0] = self.puzzle.grid[i]
                    self.group[i].hidden = False
                else:
                    self.tiles[i][0] == None
                    self.group[i].hidden = True
            self.puzzle.move(self.moves[self.move%len(self.moves)])
            self.move+=1
            return True

        return False
