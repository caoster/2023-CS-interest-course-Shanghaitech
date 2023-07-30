import threading
import tkinter
from enum import Enum
from tkinter import Tk, Canvas


class _PixelType(Enum):
    UNKNOWN = -2
    BOUNDARY = -1
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3


class _Pixel:
    def __init__(self, x: int, y: int, pixel_type: _PixelType):
        self._location = (x, y)
        self._pixel_type: _PixelType = pixel_type

    @property
    def location(self):
        return self._location

    @property
    def pixel_type(self):
        return self._pixel_type

    @pixel_type.setter
    def pixel_type(self, value):
        self._pixel_type = value

    def __repr__(self):
        return f"({self._pixel_type.name}, {self._location[0]}, {self._location[1]})"


class Maze:
    def __init__(self):
        self._steps = 0
        self._size = (8, 10)
        self._maze = [[_Pixel(i, j, _PixelType.EMPTY) for j in range(self._size[1])] for i in range(self._size[0])]
        self._mask = [[False for _ in range(self._size[1])] for _ in range(self._size[0])]
        self._start = (-1, -1)
        self._exit = (-1, -1)
        # TODO: remove this
        hardcoded_maze = [
            [2, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 3]
        ]
        for i in range(self._size[0]):
            for j in range(self._size[1]):
                if hardcoded_maze[i][j] == 1:
                    self._maze[i][j].pixel_type = _PixelType.WALL
                elif hardcoded_maze[i][j] == 2:
                    self._maze[i][j].pixel_type = _PixelType.START
                    self._start = (i, j)
                    self._mask[i][j] = True
                elif hardcoded_maze[i][j] == 3:
                    self._maze[i][j].pixel_type = _PixelType.EXIT
                    self._exit = (i, j)
                    self._mask[i][j] = True

        self._disp: _DISP = _DISP(self)
        self._init_disp()

    def start(self, strategy: callable):
        def run_function():
            result = strategy(self)
            print(self._submit(result))

        timer = threading.Timer(interval=1, function=run_function)
        timer.start()
        self._disp.start()

    def explore(self, x: int, y: int):
        assert self._mask[x][y], "你只能探索可见区域"
        self._steps += 1
        result = {}
        if x > 0:
            result[(x - 1, y)] = self._maze[x - 1][y].pixel_type
            self._mask[x - 1][y] = True
            self._disp.update(x - 1, y, self._maze[x - 1][y].pixel_type)
        if x < self._size[0] - 1:
            result[(x + 1, y)] = self._maze[x + 1][y].pixel_type
            self._mask[x + 1][y] = True
            self._disp.update(x + 1, y, self._maze[x + 1][y].pixel_type)
        if y > 0:
            result[(x, y - 1)] = self._maze[x][y - 1].pixel_type
            self._mask[x][y - 1] = True
            self._disp.update(x, y - 1, self._maze[x][y - 1].pixel_type)
        if y < self._size[1] - 1:
            result[(x, y + 1)] = self._maze[x][y + 1].pixel_type
            self._mask[x][y + 1] = True
            self._disp.update(x, y + 1, self._maze[x][y + 1].pixel_type)
        return result

    def _submit(self, path: [tuple[int, int]]):
        if path[0] != self._start or path[-1] != self._exit:
            return False
        for idx in range(len(path) - 1):
            a = path[idx]
            b = path[idx + 1]
            if not (self._mask[a[0]][a[1]] and self._mask[b[0]][b[1]]):
                return False  # Explore before commit
            if not (0 <= a[0] < self._size[0] and 0 <= a[1] < self._size[1] and
                    0 <= b[0] < self._size[0] and 0 <= b[1] < self._size[1]):
                return False  # Check in-range
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
                return False  # Check connectivity
            if not ((self._maze[a[0]][a[1]].pixel_type == _PixelType.START) or
                    (self._maze[a[0]][a[1]].pixel_type == _PixelType.EMPTY and
                     self._maze[b[0]][b[1]].pixel_type == _PixelType.EMPTY) or
                    (self._maze[b[0]][b[1]].pixel_type == _PixelType.EXIT)):
                return False  # Empty space
        return True

    def _init_disp(self):
        for i in range(self._size[0]):
            for j in range(self._size[1]):
                if self._mask[i][j]:
                    self._disp.update(i, j, self._maze[i][j].pixel_type)

    def __str__(self):
        display = ""
        for i in self._maze:
            display += "|"
            for j in i:
                if j.pixel_type == _PixelType.EMPTY:
                    display += " "
                elif j.pixel_type == _PixelType.WALL:
                    display += "X"
                elif j.pixel_type == _PixelType.START:
                    display += "S"
                elif j.pixel_type == _PixelType.EXIT:
                    display += "E"
                else:
                    raise
            display += "|\n"
        return display

    @property
    def size(self):
        return self._size


class _DISP:
    def __init__(self, maze: Maze):
        print("v<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("v  Welcome to Python class!  ^")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>^")
        self.root = Tk(className="Maze")
        self.root.resizable(False, False)
        # self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.geometry("800x450")
        self.maze_canvas = Canvas(self.root, width=800, height=450, background="#000")
        self.maze_canvas.pack()
        self.maze_canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.cells = []
        side = 15
        for ix in range(50):
            self.cells.append([])
            for iy in range(30):
                x, y = ix * side, iy * side
                rect = self.maze_canvas.create_rectangle(x, y, x + side,
                                                         y + side, fill="gray55")
                self.cells[-1].append(rect)

        self.maze: Maze = maze

    def start(self):
        self.root.mainloop()

    def update(self, x: int, y: int, scheme: _PixelType):
        if scheme == _PixelType.UNKNOWN:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray55")
        elif scheme == _PixelType.BOUNDARY:
            raise
        elif scheme == _PixelType.EMPTY:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray85")
        elif scheme == _PixelType.WALL:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray15")
        elif scheme == _PixelType.START:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gold")
        elif scheme == _PixelType.EXIT:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="coral")


_maze = Maze()
