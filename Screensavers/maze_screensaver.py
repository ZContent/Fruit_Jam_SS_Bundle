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
    startcell = -1
    endcell = -1
    maze = []
    mazepath = []
    mazesolution = []

    def __init__(self):
        self.reset(10,3)

    def reset(self,cs,lw):
        self.cellsize = cs
        self.lwidth = lw
        self.sizex = self.width // self.cellsize
        self.sizey = self.height // self.cellsize
        for i in range(self.sizex * self.sizey):
            if i == 0:
                item = 0
            elif i < self.sizex:
                item = BOTTOM
            elif i % self.sizex == 0:
            	item = RIGHT
            else:
            	item = BOTTOM | RIGHT
            self.maze.append(item)
            self.mazepath.append(i)

    def getX(self,item,width):
        return item % width

    def getY(self,item,width):
        return item // width

    def coord(self,item,width):
        return f"[{self.getX(item,width)},{self.getY(item,width)}]"

    """
    cell_join() joins two cells together, effectively breaking down a wall within
    the maze.
    """
    def cell_join(self, cell1, cell2):
        #print(f"cell_join {cell1},{cell2} of {len(self.mazepath)}")
        if cell2 < self.sizex*self.sizey:
            val = self.mazepath[cell2]
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
        #print(f"connect({cell})")
        cellcheck = [0,0]

        # check if cell is a border, if so, return false
        if (cell < self.sizex) or (cell%self.sizex == 0): # top or left line
            return False
        # determine order of cell attempts
        cellcheck[0]=random.randint(0,1)
        cellcheck[1]=(cellcheck[0]+1)%2
        # check cells to see if can be connected
        for incr in range(2):
            if (self.getX(cell,self.sizex) == (self.sizex-1)) and (cellcheck[incr]==0):
                continue # do not attempt to open right edge of maze
            if (self.getY(cell,self.sizex) == (self.sizey-1)) and (cellcheck[incr]==1):
                continue # do not attempt to open bottom edge of maze
            # print(cell,cellcheck[incr],self.sizex,cell+1+cellcheck[incr]*(self.sizex-1))
            if self.mazepath[cell] != self.mazepath[cell+1+cellcheck[incr]*(self.sizex-1)]:
                self.cell_join(cell,cell+1+cellcheck[incr]*(self.sizex-1))
                return True

        return False

    """
       generate() is the function that generates a random maze.  It calls connect()
       (which, in turn, calls cell_join()) to generate the maze.
    """
    def generate(self):
        print("generate()")
        while True:
            complete=True
            # pick a random cell
            cell = self.sizex + random.randint(0,self.sizex*(self.sizey-1))
            # find the next cell that can be connected
            for incr in range(self.sizex * self.sizey):

                #checkcell=(incr+cell)%(self.sizex*(self.sizey-1))
                checkcell=(incr+cell)%(self.sizex*(self.sizey))
                if (checkcell < self.sizex) or ((checkcell%self.sizex)==0):
                    continue
                if self.connect(checkcell):
                    complete = False
                    break
            if complete == True:
                break
        # break walls for start and end of maze, near center
        # top to bottom
        #self.startcell = self.sizex//4 + random.randint(0,self.sizex//2)
        #self.maze[self.startcell] = self.maze[self.startcell]&~BOTTOM
        #self.endcell = self.sizex//4 + random.randint(0,self.sizex//2) + self.sizex*(self.sizey-1)
        #self.maze[self.endcell] = self.maze[self.endcell]&~BOTTOM
        #left to right
        self.startcell = (self.sizey//4 + random.randint(0,self.sizey//2))*self.sizex
        print(f"start cell: {self.startcell}")
        self.maze[self.startcell] = (self.maze[self.startcell])&~RIGHT
        self.endcell = (self.sizey//4 + random.randint(0,self.sizey//2))*(self.sizex)-1
        print(f"end cell: {self.endcell}")
        self.maze[self.endcell] = (self.maze[self.endcell])&~RIGHT

    """
    solve_r() - recursive solve routine, called by solve()
    """
    def solve_r(self, finish, pos, prevpos, dir):
        print(f"solve_r({finish},{pos},{prevpos},{dir})")
        if pos == prevpos:
            print("same square, backing up")
            solutioncount -= 1
            # same square, need to back up from here
            print("return False")
            return False
        self.mazesolution.append(pos)
        if pos == finish:
            print(f"Solved in {len(self.mazesolution)} moves")
            return True
        """
        directions:
        0: north
        1: west
        2: south
        3: east
        """
        posy = self.getY(pos, self.sizex);
        posx = self.getX(pos, self.sizex);
        print(f"trying square {self.coord(pos, self.sizex)} at direction {dir}")

        if dir == 0: # north
          newx = posx
          newy = posy - 1
          newpos = newy * self.sizex + newx;
          if (self.maze[newpos] & BOTTOM) == 0:
            return self.solve_r(finish, newpos, pos, 3)
        elif dir == 1: # west
          newx = posx - 1
          newy = posy
          newpos = newy * self.sizex + newx
          if (self.maze[newpos] & RIGHT) == 0:
            return self.solve_r(finish, newpos, pos, 0)
        elif dir == 2: # south
          newx = posx
          newy = posy + 1
          newpos = newy * self.sizex + newx
          if (self.maze[pos] & BOTTOM) == 0:
            return self.solve_r(finish, newpos, pos, 1)
        elif dir == 3: # east
          newx = posx + 1
          newy = posy
          newpos = newy * self.sizex + newx
          if (self.maze[pos] & RIGHT) == 0:
            return self.solve_r(finish, newpos, pos, 2)
        dir = (dir + 1) % 4
        print(f"next direction: {dir}")
        #solutioncount--;
        return self.solve_r(finish, pos, prevpos, dir)

    """
    solve() - solve the maze
    """
    def solve(self):
        start = 0
        finish = 0

        for i in range(self.sizex):
            if self.maze[i] & BOTTOM == 0:
              start = i + self.sizex #start at row below
              break

        for i in range((self.sizey-1)*self.sizex + 1,self.sizex*self.sizey):
            if (self.maze[i] & BOTTOM) == 0:
                finish = i
                break
        solutioncount = 0
        print(f"maze start: {self.coord(start, self.sizex)}, finish: {self.coord(finish, self.sizex)}")

        self.mazesolution.append(start)
        self.solve_r(finish, start, start - self.sizex, 1)

        # remove dead end moves
        """
        solutionpos = 0
        while True:
            while(solutionpos < solutioncount)
            {
            //Serial.println("solution pos: " + String(solutionpos) + COORD(mazesolution[solutionpos], sizex)
            //  + ", solution count: " + String(solutioncount));
            for(int i = solutioncount - 1; i > solutionpos; i--)
            {
              if(mazesolution[solutionpos] == mazesolution[i])
              {
                // remove dead end paths
                //Serial.println("removing " + String(i - solutionpos) + " duplicate path items");
                for(int j = 0; j < (solutioncount - solutionpos); j++)
                {
                  mazesolution[solutionpos + j] = mazesolution[i + j];
                }
                solutioncount -= i - solutionpos;
              }
            }
            solutionpos++;
        Serial.println("Solution reduced to " + String(solutioncount) + " moves");
        """

        # print out solution
        print("Solution in {len(self.mazesolution)} moves")
        for i in range(len(self.mazesolution)):
            print(f"{i}: {self.coord(self.mazesolution[i], self.sizex)}")

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
        self.maze = maze()
        self.init_graphics()

    def init_graphics(self):
        print("init_graphics()")
        self.bmp = bg_bmp = Bitmap(self.display_size[0], self.display_size[1], 4)
        bg_palette = Palette(4)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x888888
        bg_palette[2] = 0xffffff
        bg_palette[3] = 0xff0000

        bg_tg = TileGrid(bitmap=bg_bmp, pixel_shader=bg_palette)
        bg_bmp.fill(WHITE)
        bg_group = Group(scale=1)
        bg_group.append(bg_tg)
        self.append(bg_group)
        self.maze.generate()
        self.display_maze(self.maze)
        #self.maze.solve()

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
        self.bmp.fill(WHITE)

        # draw horizontal lines
        for incry in range(maze.sizey):
            xstart = -1
            xend = -1
            for incrx in range(maze.sizex):
                if maze.maze[incry*maze.sizex+incrx]&BOTTOM != 0 and xstart == -1:
                    xstart = incrx
                elif maze.maze[incry*maze.sizex+incrx]&BOTTOM == 0 and xstart != -1:
                    xend = incrx
                    x1 = xcenter + xstart*self.cellsize
                    y1 = ycenter + (incry+1)*self.cellsize
                    x2 = x1 + (xend - xstart)*self.cellsize+self.lwidth
                    y2 = y1 + self.lwidth
                    bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,BLACK)
                    xstart = -1
                    xend = -1
            if xstart != -1:
              # finish line
              xend = maze.sizex
              x1 = xcenter + xstart*self.cellsize
              y1 = ycenter + (incry+1)*self.cellsize
              x2 = x1 + (xend - xstart)*self.cellsize+self.lwidth
              y2 = y1 + self.lwidth
              bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,BLACK)
              xstart = -1
              xend = -1

        # draw vertical lines

        for incrx in range(maze.sizex):
            ystart = -1
            yend = -1
            for incry in range(maze.sizey):
                if maze.maze[incry*maze.sizex+incrx]&RIGHT != 0 and incry > 0 and ystart == -1:
                    ystart = incry
                elif maze.maze[incry*maze.sizex+incrx]&RIGHT == 0 and incry > 0 and ystart != -1:
                    yend = incry
                    x1 = xcenter + (incrx+1)*self.cellsize
                    y1 = ycenter + ystart*self.cellsize
                    x2 = x1 + self.lwidth
                    y2 = y1 + (yend - ystart)*self.cellsize+self.lwidth
                    bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,BLACK)
                    ystart = -1
                    yend = -1

            if ystart != -1:
                # finish line
                yend = maze.sizey
                x1 = xcenter + (incrx+1)*self.cellsize
                y1 = ycenter + ystart*self.cellsize
                x2 = x1 + self.lwidth
                y2 = y1 + (yend - ystart)*self.cellsize+self.lwidth
                bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,BLACK)
