"""
Maze Screensaver for the Adafruit Fruit Jam
and Fruit Jam OS
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

BOTTOM = 0x01
RIGHT = 0x02

class maze:
    width = SCREENWIDTH
    height = SCREENHEIGHT
    counter = 0
    maze = []
    mazepath = []

    def __init__(self, bmp):
        self.bmp = bmp
        self.reset()

    def reset(self,cs,lw):
        self.cellsize = cs
        self.lwidth = lw
        self.sizex = self.width // self.cellsize
        self.sizey = self.height // cellsize
        for i in range(self.sizex * self.sizey):
            if i == 0:
                item = 0
            elif i < self.sizex:
                item = BOTTOM
            elif i % self.sizex == 0:
            	item = RIGHT
            else:
            	item = BOTTOM | RIGHT
            maze.append(item)
            mazepath.append(i)

    def getX(item,width):
        return item % width

    def getY(item,width):
        return item // width

    """
    cell_join() joins two cells together, effectively breaking down a wall within
    the maze.
    """
    def cell_join(int cell1, int cell2):
  
        val = mazepath[cell2];
        # set mazepath value
        for incr = range(self.sizex*self.sizey - 1, -1, -1):
            if mazepath[incr] == val:
            mazepath[incr] = mazepath[cell1]
        # set graphics
        if cell1 + 1 == cell2: # open right wall
            maze[cell1] = maze[cell1]&~RIGHT
        else: # open bottom wall
            maze[cell1] = maze[cell1]&~BOTTOM

    """
    connect() attempts to connect two squares together, returning
    FALSE if the attempt failed
    """
    def connect(int cell):
        cellcheck = [2]
        int incr;
        int cellcheck[2]; /* adjacent cell attempts */
        # check if cell is a border, if so, return false 
        if((cell < self.sizex) or ((cell%self.sizex == 0)): /* top or left line */
            return False
        # determine order of cell attempts
        cellcheck[0]=random.randomint(2);
        cellcheck[1]=(cellcheck[0]+1)%2;
        /* check cells to see if can be connected */
        for incr in range(2):
            if self.getX(cell,self.sizex)==(self.sizex-1))&&(cellcheck[incr]==0)):
                continue # do not attempt to open right edge of maze
            if((self.getY(cell,self.sizex)==(self.sizey-1))&&(cellcheck[incr]==1)):
                continue; # do not attempt to open bottom edge of maze
            if(*(mazepath+cell)!=*(mazepath+cell+1+cellcheck[incr]*(self.sizex-1)))
            if mazepath[cell] != mazepath[cell+1+cellcheck[incr]]
            {
                cell_join(cell,cell+1+cellcheck[incr]*(self.sizex-1))
                return True
            }
    return False

class MazeScreenSaver(Group):

    display_size = (SCREENWIDTH, SCREENHEIGHT)
    last_move_time = 0
    move_cooldown = 0.05  # seconds


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
