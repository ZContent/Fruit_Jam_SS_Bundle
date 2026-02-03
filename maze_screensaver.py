"""
Maze Screensaver for the Adafruit Fruit Jam
and Fruit Jam OS
Dan Cogliano, https://DanTheGeek.com
"""

import os
import sys
import random
import time
import math

from displayio import Group, OnDiskBitmap, TileGrid, Bitmap, Palette
import bitmaptools

import adafruit_imageload

MAZE_RANDOM = -1
MAZE_SEQUENCE = -2

"""
 Pick a maze from the list
 pick a # from maze_list, or
 MAZE_RANDOM for random pick,
 MAZE_SEQUENCE for sequencial pick
"""
MAZE_PICK = MAZE_SEQUENCE

# [columns,rows,wall width]
maze_list = [
    [22,17,4], # easy
    [32,24,3], # medium
    [45,34,2], # hard
]

SCREENWIDTH=320
SCREENHEIGHT=240

BOTTOM = 0x01
RIGHT = 0x02

# palette colors
BLACK = 0
GRAY = 1
WHITE = 2
RED = 3

class MazeMaker:
    width = SCREENWIDTH
    height = SCREENHEIGHT
    counter = 0
    startcell = -1
    endcell = -1
    maze = []
    mazepath = []
    mazesolution = []


    def __init__(self,columns,rows):
        #random.seed(42) # for debugging
        self.sizex = columns+1
        self.sizey = rows+1
        self.reset()

    def reset(self):
        self.mazepath.clear()
        self.maze.clear()
        self.mazesolution.clear()
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

    def getCell(self, x, y, width):
        return y*width + x

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
        self.reset()
        while not self.generate_tick(0.05):
            pass
        print("generate() done")

    def generate_tick(self,timer):
        #print("generate_tick()")
        start = time.monotonic()
        complete=True
        while (timer == 0) or (start + timer) > time.monotonic():
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
        if complete == True:
            # break walls for start and end of maze, near center
            # top to bottom
            #self.startcell = self.sizex//4 + random.randint(0,self.sizex//2)
            #self.maze[self.startcell] = self.maze[self.startcell]&~BOTTOM
            #self.endcell = self.sizex//4 + random.randint(0,self.sizex//2) + self.sizex*(self.sizey-1)
            #self.maze[self.endcell] = self.maze[self.endcell]&~BOTTOM
            #left to right
            self.startcell = (self.sizey//4 + random.randint(0,self.sizey//2))*self.sizex
            self.mazesolution.append([self.startcell,3])
            self.maze[self.startcell] = (self.maze[self.startcell])&~RIGHT
            self.startcell += 1
            print(f"**start cell: {self.startcell} {self.coord(self.startcell,self.sizex)}")
            self.mazesolution.append([self.startcell,0])
            self.endcell = (self.sizey//4 + random.randint(0,self.sizey//2))*self.sizex-1
            print(f"**end cell: {self.endcell} {self.coord(self.endcell,self.sizex)}")
            self.maze[self.endcell] = (self.maze[self.endcell])&~RIGHT
            return True
        return False

    def solve_tick(self):
        basecell = self.mazesolution[-1][0]
        basedir = self.mazesolution[-1][1]
        basecellx = self.getX(basecell,self.sizex)
        basecelly = self.getY(basecell,self.sizex)
        #print(f"checking cell {basecell} {self.coord(basecell,self.sizex)}")
        """
        directions:
        0: north
        1: west
        2: south
        3: east
        """
        for i in range(basedir,4):
            if i == 0: # north
                if basecelly > 0:
                    cell = self.getCell(basecellx, basecelly-1, self.sizex)
                    if cell != self.mazesolution[-2][0] and basecelly-1 != 0:
                        if (self.maze[cell] & BOTTOM) == 0:
                            #print(f"debug {i}: {cell} {basecell} {self.mazesolution[-1]}")
                            self.mazesolution[-1][1] = 0
                            self.mazesolution.append([cell,0])
                            return True
            if i == 1: # west
                if basecellx > 0:
                    cell = self.getCell(basecellx-1, basecelly, self.sizex)
                    if cell != self.mazesolution[-2][0] and basecellx-1 != 0:
                        if (self.maze[cell] & RIGHT) == 0:
                            #print(f"debug {i}: {cell} {basecell} {self.mazesolution[-1]}")
                            self.mazesolution[-1][1] = 1
                            self.mazesolution.append([cell,0])
                            return True
            if i == 2: # south
                if basecelly < (self.sizey - 1):
                    cell = self.getCell(basecellx, basecelly+1, self.sizex)
                    if cell != self.mazesolution[-2][0]:
                        if (self.maze[basecell] & BOTTOM) == 0:
                            #print(f"debug {i}: {cell} {basecell} {self.mazesolution[-1]}")
                            self.mazesolution[-1][1] = 2
                            self.mazesolution.append([cell,0])
                            return True
            if i == 3: # east
                if basecellx < (self.sizex - 1):
                    cell = self.getCell(basecellx+1, basecelly, self.sizex)
                    if cell != self.mazesolution[-2][0]:
                        if (self.maze[basecell] & RIGHT) == 0:
                            #print(f"debug {i}: {cell} {basecell} {self.mazesolution[-1]}")
                            self.mazesolution[-1][1] = 3
                            self.mazesolution.append([cell,0])
                            return True
        # if we got this far then we are at a dead end
        #print("debug: dead end found.")
        return False

    def solve(self):
        self.mazesolution.clear()
        self.mazesolution.append([self.startcell,3])
        self.mazesolution.append([self.startcell,3])
        count = 0
        while self.mazesolution[-1][0] != self.endcell:
            if self.solve_tick():
                #print(f"add element {self.mazesolution[-1]} (count:{len(self.mazesolution)})")
                pass
            else:
                element = self.mazesolution.pop()
                #print(f"popped element {element}  (count:{len(self.mazesolution)})")

            count += 1
            if count > 10000:
                print("maze solution out of range (bug?)")
                sys.exit(1)
        print("maze solved!!!")

class MazeScreenSaver(Group):
    display_size = (SCREENWIDTH, SCREENHEIGHT)
    last_move_time = 0
    move_cooldown = .01  # seconds
    counter = 0
    lwidth = 2
    solved = False
    generated = False
    #time_before_solve = 5
    #time_before_new_maze = 10
    time_before_solve = 1
    time_before_new_maze = 2
    solve_countdown = 0
    mode = 1

    def __init__(self):
        print("__init__")
        super().__init__()
        #self.maze = self.new_maze(-1)
        self.init_graphics()
        self.solved = False
        self.maze_item = -1

    def init_graphics(self):
        print("init_graphics()")
        self.bmp = Bitmap(self.display_size[0], self.display_size[1], 4)
        bg_palette = Palette(4)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0xaaaaaa
        bg_palette[2] = 0xffffff
        bg_palette[3] = 0xff0000

        bg_tg = TileGrid(bitmap=self.bmp, pixel_shader=bg_palette)
        self.bmp.fill(BLACK)
        bg_group = Group(scale=1)
        bg_group.append(bg_tg)
        self.append(bg_group)

    def new_maze(self,maze_pick):
        print(f"new_maze({maze_pick})")
        if maze_pick < len(maze_list):
            if maze_pick == MAZE_RANDOM:
                self.maze_item = random.randint(0,len(maze_list)-1)
                print(f"random maze pick is {self.maze_item}")
            elif maze_pick == MAZE_SEQUENCE:
                self.maze_item = (self.maze_item+1)%len(maze_list)
                print(f"random maze pick is {self.maze_item}")
            self.lwidth = maze_list[self.maze_item][2]
            self.cellsize = min(
                SCREENWIDTH//maze_list[self.maze_item][0],
                SCREENHEIGHT//maze_list[self.maze_item][1])
            return MazeMaker(
                maze_list[self.maze_item][0],
                maze_list[self.maze_item][1]
            )
        return None

    def tick(self):
        """
        modes:
        1: reset()
        2: generate()
        3: pause before solve
        4: solve
        5: pause after solve
        """
        screen_update = False
        now = time.monotonic()
        time.sleep(.001)
        if now - self.last_move_time > self.move_cooldown:
            self.last_move_time = now
            #print(".",end="")
            if self.mode == 1:
                self.maze = self.new_maze(MAZE_PICK)
                self.mode = 2
                print(f"tick mode:{self.mode}")
            if self.mode == 2:
                if self.maze.generate_tick(.05):
                    screen_update = True
                    self.draw_maze(self.maze)
                    self.solve_countdown = self.time_before_solve
                    self.mode = 3
                    print(f"tick mode:{self.mode}")
            if self.mode == 3:
                self.solve_countdown -= self.move_cooldown
                if self.solve_countdown <= 0:
                    self.maze.mazesolution.clear()
                    self.maze.mazesolution.append([self.maze.startcell,0])
                    self.maze.mazesolution.append([self.maze.startcell,0])
                    self.mode = 4
                    print(f"tick mode:{self.mode}")
            if self.mode == 4:
                screen_update = True
                #if(not self.solved):
                if len(self.maze.mazesolution) <= 2:
                    self.draw_box(self.maze.mazesolution[-1][0],RED)
                if self.maze.mazesolution[-1][0] != self.maze.endcell:
                    if self.maze.solve_tick():
                        #print(f"add element {self.maze.mazesolution[-1]} (count:{len(self.maze.mazesolution)})")
                        self.draw_box(self.maze.mazesolution[-1][0],RED)
                    else:
                        self.draw_box(self.maze.mazesolution[-1][0],GRAY)
                        element = self.maze.mazesolution.pop()
                        #print(f"count:{len(self.maze.mazesolution)}")
                        #if len(self.maze.mazesolution) < 2:
                        #    print(f"element: {element}")
                        #    while True:
                        #        pass
                        self.maze.mazesolution[-1][1] += 1
                        #print(f"popped element {element}  (count:{len(self.maze.mazesolution)})")
                else:
                    print("maze solved!!!")
                    self.solved = True
                    # clear mouse droppings
                    for cellx in range(1,self.maze.sizex):
                        for celly in range(1,self.maze.sizey):
                            cell = celly*self.maze.sizex + cellx
                            self.draw_box(cell,WHITE)
                    # draw solution lines
                    count = 0
                    lastcell = self.maze.mazesolution[1][0]

                    print(f"debug: start:{self.maze.startcell}")
                    x1 = self.maze.getX(self.maze.startcell,self.maze.sizex)*self.cellsize+self.xcenter
                    y1 = self.maze.getY(self.maze.startcell,self.maze.sizex)*self.cellsize+self.ycenter+(self.lwidth-self.lwidth//2)+1
                    x2 = x1 + self.cellsize-self.lwidth-1
                    y2 = y1 + self.cellsize-self.lwidth-2
                    print(f"debug start line at {lastcell} ({x1},{y1},{x2},{y2})")
                    bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,RED)

                    for cell in self.maze.mazesolution:
                        if count > 1:
                            x1 = self.maze.getX(lastcell,self.maze.sizex)*self.cellsize
                            y1 = self.maze.getY(lastcell,self.maze.sizex)*self.cellsize
                            x2 = self.maze.getX(cell[0],self.maze.sizex)*self.cellsize
                            y2 = self.maze.getY(cell[0],self.maze.sizex)*self.cellsize
                            #print(f"debug1 draw line from {lastcell} to {cell[0]} ({x1},{y1},{x2},{y2})")
                            # fix coordinate order for fill_region()
                            if x1 > x2:
                                t = x1
                                x1 = x2
                                x2 = t
                            if y1 > y2:
                                t = y1
                                y1 = y2
                                y2 = t

                            print(f"debug2 draw line from {lastcell} to {cell[0]} ({x1},{y1},{x2},{y2})")
                            bitmaptools.fill_region(self.bmp,
                                #x1+self.xcenter+(self.lwidth-self.lwidth//2)+0,
                                x1+self.xcenter+(self.lwidth//2) + 1,
                                #y1+self.ycenter+(self.lwidth-self.lwidth//2)+0,
                                y1+self.ycenter+(self.lwidth//2) + 1,
                                #min(self.maze.width-(self.lwidth-self.lwidth//2)-4,x2),
                                #min(self.maze.height-(self.lwidth-self.lwidth//2)-4,y2),
                                #x2-self.lwidth,
                                #y2-self.lwidth,
                                x2+self.xcenter+self.cellsize-(self.lwidth-self.lwidth//2)-1,
                                y2+self.ycenter+self.cellsize-(self.lwidth-self.lwidth//2)-1,
                                RED)
                        lastcell = cell[0]

                        count+=1
                    print(f"debug: end:{self.maze.endcell}")
                    #x1 = self.maze.getX(self.maze.endcell,self.maze.sizex)*self.cellsize+self.xcenter+1
                    #y1 = self.maze.getY(self.maze.endcell,self.maze.sizex)*self.cellsize+self.ycenter+1
                    #x2 = min(x2 + self.cellsize,SCREENWIDTH)
                    #y2 = y1 + self.cellsize-self.lwidth-2

                    x1 = self.maze.getX(self.maze.endcell,self.maze.sizex)*self.cellsize+self.xcenter+self.lwidth//2+1
                    y1 = self.maze.getY(self.maze.endcell,self.maze.sizex)*self.cellsize+self.ycenter+self.lwidth//2+1
                    x2 = x1+self.cellsize-self.lwidth
                    y2 = y1+self.cellsize-self.lwidth-2
                    print(f"debug end line at {self.maze.endcell} ({x1},{y1},{x2},{y2})")
                    bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,RED)

                    self.new_maze_countdown = self.time_before_new_maze
                    self.mode = 5
                    print(f"tick mode:{self.mode}")
            if self.mode == 5:
                self.new_maze_countdown -= self.move_cooldown
                if self.new_maze_countdown <= 0:
                    self.mode = 1
                    print(f"tick mode:{self.mode}")
        return screen_update

    def draw_box(self,cell,color):
        x = self.maze.getX(cell,self.maze.sizex)
        y = self.maze.getY(cell,self.maze.sizex)
        x1 = x*self.cellsize + self.xcenter + (self.lwidth//2) + 1
        x2 = x1+self.cellsize - self.lwidth-2
        y1 = y*self.cellsize + self.ycenter  + (self.lwidth//2) + 1
        y2 = y1+self.cellsize - self.lwidth-2
        #print(f"draw_box: cell {cell} ({x},{y}) to {x1},{y1}-{x2},{y2}")
        bitmaptools.fill_region(self.bmp,x1,y1,x2,y2,color)

    """
    draw_maze() prints the maze on the graphics device
    """
    def draw_maze(self,maze):
        self.xcenter = (SCREENWIDTH-self.cellsize*(self.maze.sizex-1))//2-self.cellsize
        self.ycenter = (SCREENHEIGHT-self.cellsize*(self.maze.sizey-1))//2-self.cellsize

        #self.xcenter = -self.cellsize
        #self.ycenter = -self.cellsize

        print(f"maze centering adjustment: {self.xcenter}, {self.ycenter}")
        self.bmp.fill(WHITE)
        # remove white border from maze
        #left edge
        bitmaptools.fill_region(self.bmp,0,0,
            (SCREENWIDTH-self.cellsize*(maze.sizex-1))//2,
            SCREENHEIGHT,BLACK)
        #right edge
        bitmaptools.fill_region(self.bmp,
            SCREENWIDTH-(SCREENWIDTH-self.cellsize*(maze.sizex-1))//2,
            0,
            SCREENWIDTH,SCREENHEIGHT,BLACK)
        #top edge
        bitmaptools.fill_region(self.bmp,0,0,
            SCREENWIDTH,(SCREENHEIGHT-self.cellsize*(maze.sizey-1))//2,
            BLACK)
        #bottom edge
        bitmaptools.fill_region(self.bmp,0,
            SCREENHEIGHT-(SCREENHEIGHT-self.cellsize*(maze.sizey-1))//2,
            SCREENWIDTH,SCREENHEIGHT,
            BLACK)

        # draw horizontal lines
        for incry in range(maze.sizey):
            xstart = -1
            xend = -1
            for incrx in range(maze.sizex):
                if maze.maze[incry*maze.sizex+incrx]&BOTTOM != 0 and xstart == -1:
                    xstart = incrx
                elif maze.maze[incry*maze.sizex+incrx]&BOTTOM == 0 and xstart != -1:
                    xend = incrx
                    x1 = self.xcenter + xstart*self.cellsize-(self.lwidth-self.lwidth//2)
                    y1 = self.ycenter + (incry+1)*self.cellsize-(self.lwidth-self.lwidth//2)
                    x2 = x1 + min(maze.sizex*self.cellsize,(xend - xstart)*self.cellsize+self.lwidth)
                    y2 = y1 + self.lwidth
                    #print(f"debug1 line: xstart:{xstart}, xend {xend} * {self.cellsize} / ({x1},{y1},{x2},{y2})")
                    bitmaptools.fill_region(self.bmp,max(0,x1),max(0,y1),min(SCREENWIDTH,x2),y2,BLACK)
                    xstart = -1
                    xend = -1
            if xstart != -1:
                # bottom horizontal line
                xend = (maze.sizex)
                x1 = max(0,self.xcenter + xstart*self.cellsize-self.lwidth//2)
                y1 = self.ycenter + (incry+1)*self.cellsize-(self.lwidth-self.lwidth//2)
                x2 = x1 + (xend - xstart)*self.cellsize+self.lwidth//2
                y2 = y1 + self.lwidth
                #print(f"debug2 line: xstart:{xstart}, xend {xend} * {self.cellsize} / ({x1},{y1},{x2},{y2})")
                bitmaptools.fill_region(self.bmp,x1,max(0,y1),min(SCREENWIDTH,x2),min(SCREENHEIGHT,y2),BLACK)
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
                    x1 = self.xcenter + (incrx+1)*self.cellsize-(self.lwidth-self.lwidth//2)
                    y1 = max(0,self.ycenter + ystart*self.cellsize-self.lwidth//2)
                    x2 = x1 + self.lwidth
                    y2 = y1 + (yend - ystart)*self.cellsize+self.lwidth//2
                    #print(f"debug3 line: ystart:{ystart}, yend {yend} * {self.cellsize} / ({x1},{y1},{x2},{y2})")
                    bitmaptools.fill_region(self.bmp,max(0,x1),y1,min(SCREENWIDTH,x2),y2,BLACK)
                    ystart = -1
                    yend = -1

            if ystart != -1:
                # bottom vertical lines
                yend = maze.sizey
                x1 = self.xcenter + (incrx+1)*self.cellsize-(self.lwidth-self.lwidth//2)
                y1 = max(0,self.ycenter + ystart*self.cellsize-self.lwidth//2)
                x2 = min(SCREENWIDTH,x1 + self.lwidth)
                y2 = y1 + max(0,(yend - ystart)*self.cellsize)
                #print(f"debug4 line: ystart:{ystart}, yend {yend} * {self.cellsize} / ({x1},{y1},{x2},{y2})")
                bitmaptools.fill_region(self.bmp,max(0,x1),y1,x2,y2,BLACK)
