"""
15 Puzzle Screensaver for the Adafruit Fruit Jam
and Fruit Jam OSDan Cogliano, https://DanTheGeek.com
"""

from adafruit_fruitjam.peripherals import request_display_config, get_display_config
import adafruit_imageload

import board
import displayio
import os
import random
import time
import math
import random
import gc

SCREENWIDTH = 320
SCREENHEIGHT = 240
SCREENDEPTH = 8

#animation speed (slow to fast)
#1,2,4,5,10,20
ASPEED = 5

#start pause in ticks
STARTPAUSE=20

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
        print(f"move({num})")
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
            if self.pos in hcheck:
                index = hcheck.index(num)
                print(f"h index: {index}")
                if num < self.pos:
                    # slide left to right
                    last = self.grid[hcheck[index]]
                    self.grid[hcheck[index]] = -1
                    for i in range(index+1,4):
                        tmp = self.grid[hcheck[i]]
                        self.grid[hcheck[i]] = last
                        last = tmp
                    self.pos = num
                else:
                    # slide right to left
                    last = self.grid[hcheck[index]]
                    self.grid[hcheck[index]] = -1
                    for i in range(index-1,self.getX(self.pos)-1,-1):
                        print(f"i:{i}")
                        tmp = self.grid[hcheck[i]]
                        self.grid[hcheck[i]] = last
                        last = tmp
                    self.pos = num

            elif self.pos in vcheck:
                index = vcheck.index(num)
                print(f"v index: {index}")

                if num < self.pos:
                    #slide top to bottom
                    last = self.grid[vcheck[index]]
                    self.grid[vcheck[index]] = -1
                    for i in range(index+1,4):
                        tmp = self.grid[vcheck[i]]
                        self.grid[vcheck[i]] = last
                        last = tmp
                    self.pos = num
                else:
                    #slide bottom to top
                    last = self.grid[vcheck[index]]
                    self.grid[vcheck[index]] = -1
                    for i in range(index-1,self.getY(self.pos)-1,-1):
                        tmp = self.grid[vcheck[i]]
                        self.grid[vcheck[i]] = last
                        last = tmp
                    self.pos = num

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
    atiles = []
    last_move_time = 0
    move_cooldown = .05  # seconds
    pos = 0
    move = 0
    #moves = [12,0,3,15]
    #moves = [13,5,7,15]
    moves = [13,5,7,15, 12,0,3,15]
    group = []
    agroup = []
    animate_frame = 0
    animating = False
    startcount = 0

    def __init__(self):
        super().__init__()
        os.chdir("/".join(__file__.split("/")[:-1])+"/ssbundle_assets/15puzzle")
        self.init_graphics()
        self.puzzle = Puzzle15()
        #self.get_screensnapshot()
        self.load_image()

    def init_graphics(self):
        print("debug init_graphics")
        self.bmp = Bitmap(self.screenwidth, self.screenheight, SCREENDEPTH)
        bg_palette = Palette(2)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x666666
        bg_tg = TileGrid(bitmap=self.bmp, pixel_shader=bg_palette)
        self.bmp.fill(1)
        bg_group = Group(scale=1)
        print(bg_group)
        bg_group.append(bg_tg)
        self.append(bg_group)
        print(f"display size: {self.display_size}")
        print("debug end init_graphics")
        self.startcount = STARTPAUSE

    def load_image(self):
        #"""
        bitmap, bpal = adafruit_imageload.load(
            "blinka.bmp",
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
            )
        #"""
        self.group = Group(scale=1)
        self.agroup = Group(scale=1)
        # puzzle tiles here
        for i in range(16):
            self.tiles.append(TileGrid(bitmap,pixel_shader=bpal,width=1,height=1,
                tile_width=self.tile_width,tile_height=self.tile_height))
            self.group.append(self.tiles[-1])
        self.append(self.group)
        # animation tiles here
        for i in range(3):
            self.atiles.append(TileGrid(bitmap,pixel_shader=bpal,width=1,height=1,
                tile_width=self.tile_width,tile_height=self.tile_height))
            self.agroup.append(self.atiles[-1])
        self.append(self.agroup)

    def animate_move(self):
        #print(f"changed positions: {self.changed}")
        # calculate move distances
        #print(f"debug: oldpos {self.oldpos} to newpos {self.newpos}")

        xdelta = min(ASPEED,abs(self.xlen))
        ydelta = min(ASPEED,abs(self.ylen))
        if self.xlen < 0:
            xdelta = 0 - xdelta
        if self.ylen < 0:
            ydelta = 0 - ydelta
        #print(f"animate distances:({self.xlen},{self.ylen}), deltas:({xdelta},{ydelta})")
        # move now
        self.xmove += xdelta
        self.ymove += ydelta
        self.animate_frame +=1
        if abs(self.xmove) > abs(self.xlen) or abs(self.ymove) > abs(self.ylen):
            #print(f"debug move: x:{self.xmove}/{self.xlen}, y:{self.ymove}/{self.ylen}")
            self.animate_frame = 0
            print("animation complete")
            return False
        else:
            atilecount = max(abs(self.puzzle.getX(self.oldpos) - self.puzzle.getX(self.newpos)),
            abs(self.puzzle.getY(self.oldpos) - self.puzzle.getY(self.newpos)))

            for pos in range(atilecount):
                self.agroup[pos].x += xdelta
                self.agroup[pos].y += ydelta
                #print(f"debug move tile {pos} to ({self.agroup[pos].x},{self.agroup[pos].y})")

        return True

        # turn off animation tiles
        #for i in range(len(self.agroup)):
        #    self.agroup[i].hidden = True


    def update_puzzle(self):
        for i in range(16):
            self.group[i].x = (self.screenwidth//4)*(i%4)
            self.group[i].y = (self.screenheight//4)*(i//4)
            #print(f"tile coords: ({i}){self.group[i].x},{self.group[i].y}: {self.puzzle.grid[i]}")
            if self.puzzle.grid[i] != -1:
                self.tiles[i][0] = self.puzzle.grid[i]
                self.group[i].hidden = False
            else:
                self.tiles[i][0] == None
                self.group[i].hidden = True

    def tick(self):
        #print("debug tick")
        now = time.monotonic()
        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            print("***tick***")
            if self.startcount > 0:
                self.update_puzzle()
                self.startcount-= 1
                return True
            elif self.animating:
                self.animating = self.animate_move()
            else:
                self.update_puzzle()
                before = self.puzzle.grid[:]
                self.oldpos = self.puzzle.pos
                self.puzzle.move(self.moves[self.move%len(self.moves)])
                self.newpos = self.puzzle.pos
                after = self.puzzle.grid[:]
                #get ready for animation
                self.changed = []
                #find changed positions
                for i in range(16):
                    if before[i] != after[i]:
                        self.changed.append(i)
                # initial positions
                for i in range(len(self.agroup)):
                    self.agroup[i].hidden = True
                pos = 0
                for i in range(len(self.changed)):
                    if self.puzzle.grid[self.changed[i]] >= 0:

                        #self.atiles[pos][0] = self.tiles[changed[i]][0]
                        print(f"debug: set anim tile {pos} to {self.changed[i]}/{self.puzzle.grid[self.changed[i]]}")
                        self.atiles[pos][0] = self.puzzle.grid[self.changed[i]]
                        #self.agroup[pos] = self.group[changed[i]]
                        self.agroup[pos].x = self.group[self.changed[i]].x
                        self.agroup[pos].y = self.group[self.changed[i]].y
                        self.agroup[pos].hidden = False
                        print(f"agroup {pos} set to ({self.agroup[pos].x},{self.agroup[pos].y})")
                        pos+=1

                if self.oldpos > self.newpos:
                    self.xlen = self.group[self.changed[1]].x - self.group[self.changed[0]].x
                    self.ylen = self.group[self.changed[1]].y - self.group[self.changed[0]].y
                else:
                    self.xlen = self.group[self.changed[0]].x - self.group[self.changed[1]].x
                    self.ylen = self.group[self.changed[0]].y - self.group[self.changed[1]].y

                print(f"debug xlen:{self.xlen}, ylen:{self.ylen}")
                # ensure starting and ending blocks are hidden
                self.group[self.oldpos].hidden = True
                self.group[self.newpos].hidden = True

                # set starting pos
                for pos in range(len(self.changed)-1):
                    if self.xlen > 0:
                        self.agroup[pos].x -= self.tile_width
                    elif self.xlen < 0:
                        self.agroup[pos].x += self.tile_width
                    if self.ylen > 0:
                        self.agroup[pos].y -= self.tile_height
                    elif self.ylen < 0:
                        self.agroup[pos].y += self.tile_height
                self.xmove = 0
                self.ymove = 0
                self.animating = True
                #self.update_puzzle()
                self.move+=1
            return True
        return False
