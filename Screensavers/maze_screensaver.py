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
import bitmaptools

import adafruit_imageload

SCREENWIDTH=320
SCREENHEIGHT=240

BOTTOM = 0x01
RIGHT = 0x02

# palette colors
BLACK = 0
GRAY = 1
WHITE = 2
RED = 3

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
    def cell_join(self, cell1, cell2):

        val = mazepath[cell2];
        # set mazepath value
        for incr in range(self.sizex*self.sizey - 1, -1, -1):
            if self.mazepath[incr] == val:
                self.mazepath[incr] = self.mazepath[cell1]
        # set graphics
        if cell1 + 1 == cell2: # open right wall
            self.maze[cell1] = self.maze[cell1]&~RIGHT
        else: # open bottom wall
            self.maze[cell1] = self.maze[cell1]&~BOTTOM

    """
    connect() attempts to connect two squares together, returning
    FALSE if the attempt failed
    """
    def connect(self, cell):
        cellcheck = [2]

        # check if cell is a border, if so, return false
        if (cell < self.sizex) or (cell%self.sizex == 0): # top or left line
            return False
        # determine order of cell attempts
        cellcheck[0]=random.randomint(2);
        cellcheck[1]=(cellcheck[0]+1)%2;
        # check cells to see if can be connected
        for incr in range(2):
            if (self.getX(cell,self.sizex) == (self.sizex-1)) and (cellcheck[incr]==0):
                continue # do not attempt to open right edge of maze
            if (self.getY(cell,self.sizex) == (self.sizey-1)) and (cellcheck[incr]==1):
                continue # do not attempt to open bottom edge of maze
            if self.mazepath[cell] != self.mazepath[cell+1+cellcheck[incr]]:
                self.cell_join(cell,cell+1+cellcheck[incr]*(self.sizex-1))
                return True

        return False

    """
       generate() is the function that generates a random maze.  It calls connect()
       (which, in turn, calls cell_join()) to generate the maze.
    """
    def generate(self):

        while True:
            complete=True
            # pick a random cell
            cell = self.sizex + random.randint(self.sizex*(self.sizey-1))
            # find the next cell that can be connected
            for incr in range(self.sizex * self.sizey):

                checkcell=(incr+cell)%(self.sizex*self.sizey)
                if (checkcell < sizex) or ((checkcell%sizex)==0):
                    continue
                if self.connect(checkcell):
                    complete = False
                    break
            if complete == True:
                break
        # break walls for start and end of maze, near center
        cell = self.sizex/4 + random.randint(self.sizex/2)
        self.maze[cell] = self.maze[cell]&~BOTTOM
        cell = self.sizex/4 + random.randint(self.sizex/2) + self.sizex*(self.sizey-1)
        self.maze[cell] = self.maze[cell]&~BOTTOM

class MazeScreenSaver(Group):
    display_size = (SCREENWIDTH, SCREENHEIGHT)
    last_move_time = 0
    move_cooldown = 0.05  # seconds
    counter = 0
    lwidth = 3
    cellsize = 10

    def __init__(self):
        print("__init__")
        super().__init__()
        self.init_graphics()
        self.maze = maze()

    def init_graphics(self):
        print("init_graphics()")
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

    def reset():
        print("reset()")

    def tick(self):
        now = time.monotonic()
        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            if self.counter%20 == 0:
                print("tick")
            self.counter += 1

            return True

        return False


    """
    display_maze() prints the maze on the graphics device
    """
    def display_maze(self,maze):
        xcenter = 0 - maze.cellsize//2
        ycenter = 0 - maze.cellsize//2
        print(f"maze centering adjustment: {xcenter}, {ycenter}")
        self.bg_bmp.fill(WHITE)
        
        // draw horizontal lines
        for incry in range(maze.sizey):
            xstart = -1
            xend = -1
            for incrx in range(maze.sizex):
                if maze[incry*sizex+incrx]&BOTTOM != 0 and xstart == -1:
                    xstart = incrx
                elif maze[incry*sizex+incrx]&BOTTOM == 0 and xtart != -1:
                    xend = incrx
                    bitmaptools.fill_region(self.bg_bmp,xcenter + xstart*self.cellsize,ycenter + (incry+1)*self.cellsize,(xend - xstart)*self.cellsize+self.lwidth,self.lwidth,BLACK)
                    xstart = -1
                    xend = -1
            if xstart != -1:
              # finish line
              xend = sizex
              bitmaptools.fill_region(self.bg_bmp,xcenter + xstart*self.cellsize,ycenter + (incry+1)*self.cellsize,(xend - xstart)*self.cellsize+self.lwidth,self.lwidth,BLACK)
              xstart = -1
              xend = -1
        
        # draw vertical lines

        for incrx in range(maze.sizex):
            ystart = -1
            yend = -1
            for(int incry = 0; incry < sizey; incry++)
            for incry in range(maze.sizey):
                if maze[incry*sizex+incrx]&RIGHT !- 0 and incry > 0 and ystart == -1:
                    ystart = incry
                elif maze[incry*sizex+incrx]&RIGHT == 0 and incry > 0 and ystart != -1:
                    yend = incry
                    bitmaptools.fill_region(self.bg_bmp, xcenter + (incrx+1)*self.cellsize,ycenter + ystart*self.cellsize,self.lwidth,(yend - ystart)*self.cellsize+self.lwidth,BLACK);
                    ystart = -1
                    yend = -1
            
            if ystart != -1:
                # finish line
                yend = sizey
                bitmaptools.fill_region(self.bg_bmp, xcenter + (incrx+1)*self.cellsize,ycenter + ystart*self.cellsize,lwidth,(yend - ystart)*self.cellsize+self.lwidth,BLACK);

