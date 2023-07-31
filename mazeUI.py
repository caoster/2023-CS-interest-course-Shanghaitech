import threading
import time
import tkinter
from enum import Enum
from tkinter import Tk, Canvas

WAIT = True


def _optional_sleep():
    if WAIT:
        time.sleep(0.1)


class PixelType(Enum):
    UNKNOWN = -2
    BOUNDARY = -1
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3
    PATH = 4


class _Pixel:
    def __init__(self, x: int, y: int, pixel_type: PixelType):
        self._location = (x, y)
        self._pixel_type: PixelType = pixel_type

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
        self._path_len = 0
        self._size = (49, 29)
        self._maze = [[_Pixel(i, j, PixelType.EMPTY) for j in range(self._size[1])] for i in range(self._size[0])]
        self._mask = [[False for _ in range(self._size[1])] for _ in range(self._size[0])]
        self._start = (-1, -1)
        self._exit = (-1, -1)
        m = [(23, 12), (39, 6), (9, 18), (14, 3), (37, 4), (37, 24), (10, 19), (32, 23), (4, 9), (33, 26), (9, 24), (19, 24), (38, 11), (38, 9), (3, 8), (6, 3), (21, 26), (38, 21), (17, 18), (4, 21), (36, 9), (28, 27), (46, 19), (40, 27), (14, 23), (8, 15), (6, 15), (44, 25), (9, 26), (15, 22), (7, 16), (42, 25), (12, 21), (42, 1), (16, 19), (13, 18), (25, 6), (19, 18), (30, 7), (30, 3), (29, 0), (46, 9), (43, 8), (40, 25), (35, 6), (24, 23), (11, 6), (7, 12), (9, 22), (45, 16), (31, 28), (16, 17), (34, 13), (26, 19), (12, 17), (45, 10), (36, 13), (47, 14), (45, 28), (39, 12), (16, 27), (29, 10), (5, 18), (22, 27), (0, 9), (1, 16), (46, 17), (30, 13), (25, 8), (34, 23), (7, 0), (26, 21), (13, 12), (3, 10), (1, 14), (35, 8), (43, 18), (3, 22), (35, 28), (11, 26), (5, 24), (40, 19), (16, 5), (48, 21), (37, 6), (28, 5), (27, 26), (26, 27), (8, 7), (11, 28), (38, 1), (10, 9), (35, 10), (38, 27), (42, 7), (23, 20), (39, 14), (9, 10), (28, 11), (38, 15), (6, 25), (4, 5), (42, 13), (3, 20), (7, 20), (28, 13), (41, 8), (43, 12), (30, 15), (10, 3), (29, 16), (26, 25), (48, 13), (48, 1), (42, 5), (8, 5), (22, 19), (17, 10), (41, 4), (44, 11), (48, 7), (8, 23), (13, 6), (46, 7), (33, 0), (33, 4), (39, 22), (35, 20), (18, 3), (10, 1), (30, 1), (5, 28), (46, 23), (29, 8), (12, 15), (16, 11), (11, 12), (33, 10), (30, 21), (3, 16), (0, 21), (40, 5), (44, 13), (31, 14), (13, 0), (23, 10), (45, 22), (2, 23), (15, 10), (18, 27), (9, 12), (48, 23), (21, 8), (6, 7), (17, 24), (28, 17), (21, 24), (20, 17), (35, 16), (42, 19), (18, 13), (24, 21), (13, 10), (30, 17), (15, 16), (1, 10), (39, 24), (39, 20), (27, 12), (22, 9), (42, 11), (3, 6), (7, 6), (38, 17), (5, 6), (2, 1), (26, 9), (39, 26), (4, 25), (13, 16), (32, 25), (28, 7), (34, 19), (31, 20), (39, 0), (35, 18), (43, 2), (37, 2), (22, 3), (34, 11), (27, 18), (15, 24), (31, 18), (12, 11), (14, 15), (10, 27), (27, 16), (30, 27), (34, 27), (20, 23), (0, 3), (18, 15), (45, 0), (36, 27), (32, 7), (41, 6), (47, 6), (47, 20), (40, 23), (15, 4), (9, 14), (34, 3), (12, 27), (16, 7), (7, 2), (3, 14), (26, 15), (3, 24), (19, 8), (24, 17), (48, 3), (12, 7), (48, 27), (33, 24), (47, 12), (19, 28), (18, 23), (25, 14), (20, 7), (14, 9), (25, 4), (16, 1), (24, 27), (41, 14), (23, 6), (22, 15), (14, 7), (2, 27), (28, 1), (8, 9), (27, 4), (43, 22), (27, 20), (19, 10), (23, 4), (24, 15), (10, 7), (21, 6), (17, 22), (20, 21), (29, 4), (1, 8), (7, 14), (35, 26), (6, 17), (1, 0), (29, 22), (23, 16), (22, 7), (31, 10), (48, 25), (21, 0), (23, 0), (34, 17), (40, 21), (15, 12), (19, 0), (34, 21), (11, 22), (23, 26), (1, 22), (0, 17), (25, 12), (32, 19), (33, 16), (27, 22), (16, 15), (16, 23), (36, 19), (39, 16), (33, 12), (19, 6), (6, 13), (11, 18), (25, 0), (4, 1), (26, 7), (28, 25), (18, 19), (24, 3), (13, 14), (12, 23), (32, 5), (20, 13), (43, 16), (39, 4), (36, 1), (0, 19), (4, 17), (1, 4), (30, 19), (18, 5), (45, 6), (33, 2), (21, 20), (43, 24), (46, 3), (13, 24), (1, 26), (31, 4), (7, 28), (40, 1), (40, 13), (18, 11), (14, 1), (17, 4), (43, 10), (2, 25), (9, 0), (47, 16), (12, 3), (26, 23), (32, 9), (37, 26), (21, 12), (23, 2), (3, 4), (42, 17), (42, 27), (35, 4), (8, 19), (10, 11), (5, 10), (15, 8), (19, 12), (46, 11), (1, 1), (1, 3), (1, 5), (1, 7), (1, 9), (1, 11), (1, 13), (1, 15), (1, 17), (1, 19), (1, 21), (1, 23), (1, 25), (1, 27), (3, 1), (3, 3), (3, 5), (3, 7), (3, 9), (3, 11), (3, 13), (3, 15), (3, 17), (3, 19), (3, 21), (3, 23), (3, 25), (3, 27), (5, 1), (5, 3), (5, 5), (5, 7), (5, 9), (5, 11), (5, 13), (5, 15), (5, 17), (5, 19), (5, 21), (5, 23), (5, 25), (5, 27), (7, 1), (7, 3), (7, 5), (7, 7), (7, 9), (7, 11), (7, 13), (7, 15), (7, 17), (7, 19), (7, 21), (7, 23), (7, 25), (7, 27), (9, 1), (9, 3), (9, 5), (9, 7), (9, 9), (9, 11), (9, 13), (9, 15), (9, 17), (9, 19), (9, 21), (9, 23), (9, 25), (9, 27), (11, 1), (11, 3), (11, 5), (11, 7), (11, 9), (11, 11), (11, 13), (11, 15), (11, 17), (11, 19), (11, 21), (11, 23), (11, 25), (11, 27), (13, 1), (13, 3), (13, 5), (13, 7), (13, 9), (13, 11), (13, 13), (13, 15), (13, 17), (13, 19), (13, 21), (13, 23), (13, 25), (13, 27), (15, 1), (15, 3), (15, 5), (15, 7), (15, 9), (15, 11), (15, 13), (15, 15), (15, 17), (15, 19), (15, 21), (15, 23), (15, 25), (15, 27), (17, 1), (17, 3), (17, 5), (17, 7), (17, 9), (17, 11), (17, 13), (17, 15), (17, 17), (17, 19), (17, 21), (17, 23), (17, 25), (17, 27), (19, 1), (19, 3), (19, 5), (19, 7), (19, 9), (19, 11), (19, 13), (19, 15), (19, 17), (19, 19), (19, 21), (19, 23), (19, 25), (19, 27), (21, 1), (21, 3), (21, 5), (21, 7), (21, 9), (21, 11), (21, 13), (21, 15), (21, 17), (21, 19), (21, 21), (21, 23), (21, 25), (21, 27), (23, 1), (23, 3), (23, 5), (23, 7), (23, 9), (23, 11), (23, 13), (23, 15), (23, 17), (23, 19), (23, 21), (23, 23), (23, 25), (23, 27), (25, 1), (25, 3), (25, 5), (25, 7), (25, 9), (25, 11), (25, 13), (25, 15), (25, 17), (25, 19), (25, 21), (25, 23), (25, 25), (25, 27), (27, 1), (27, 3), (27, 5), (27, 7), (27, 9), (27, 11), (27, 13), (27, 15), (27, 17), (27, 19), (27, 21), (27, 23), (27, 25), (27, 27), (29, 1), (29, 3), (29, 5), (29, 7), (29, 9), (29, 11), (29, 13), (29, 15), (29, 17), (29, 19), (29, 21), (29, 23), (29, 25), (29, 27), (31, 1), (31, 3), (31, 5), (31, 7), (31, 9), (31, 11), (31, 13), (31, 15), (31, 17), (31, 19), (31, 21), (31, 23), (31, 25), (31, 27), (33, 1), (33, 3), (33, 5), (33, 7), (33, 9), (33, 11), (33, 13), (33, 15), (33, 17), (33, 19), (33, 21), (33, 23), (33, 25), (33, 27), (35, 1), (35, 3), (35, 5), (35, 7), (35, 9), (35, 11), (35, 13), (35, 15), (35, 17), (35, 19), (35, 21), (35, 23), (35, 25), (35, 27), (37, 1), (37, 3), (37, 5), (37, 7), (37, 9), (37, 11), (37, 13), (37, 15), (37, 17), (37, 19), (37, 21), (37, 23), (37, 25), (37, 27), (39, 1), (39, 3), (39, 5), (39, 7), (39, 9), (39, 11), (39, 13), (39, 15), (39, 17), (39, 19), (39, 21), (39, 23), (39, 25), (39, 27), (41, 1), (41, 3), (41, 5), (41, 7), (41, 9), (41, 11), (41, 13), (41, 15), (41, 17), (41, 19), (41, 21), (41, 23), (41, 25), (41, 27), (43, 1), (43, 3), (43, 5), (43, 7), (43, 9), (43, 11), (43, 13), (43, 15), (43, 17), (43, 19), (43, 21), (43, 23), (43, 25), (43, 27), (45, 1), (45, 3), (45, 5), (45, 7), (45, 9), (45, 11), (45, 13), (45, 15), (45, 17), (45, 19), (45, 21), (45, 23), (45, 25), (45, 27), (47, 1), (47, 3), (47, 5), (47, 7), (47, 9), (47, 11), (47, 13), (47, 15), (47, 17), (47, 19), (47, 21), (47, 23), (47, 25), (47, 27)]

        hardcoded_maze = [[0 for _ in range(self._size[1])] for _ in range(self._size[0])]
        hardcoded_maze[0][0] = 2
        hardcoded_maze[-1][-1] = 3
        for i in m:
            hardcoded_maze[i[0]][i[1]] = 1
        for i in range(self._size[0]):
            for j in range(self._size[1]):
                if hardcoded_maze[i][j] == 1:
                    self._maze[i][j].pixel_type = PixelType.WALL
                elif hardcoded_maze[i][j] == 2:
                    self._maze[i][j].pixel_type = PixelType.START
                    self._start = (i, j)
                    self._mask[i][j] = True
                elif hardcoded_maze[i][j] == 3:
                    self._maze[i][j].pixel_type = PixelType.EXIT
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
        _optional_sleep()
        assert self._mask[x][y], "你只能探索可见区域"
        self._steps += 1
        self._disp.update_score(self._steps)
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
            if not ((self._maze[a[0]][a[1]].pixel_type == PixelType.START) or
                    (self._maze[a[0]][a[1]].pixel_type == PixelType.EMPTY and
                     self._maze[b[0]][b[1]].pixel_type == PixelType.EMPTY) or
                    (self._maze[b[0]][b[1]].pixel_type == PixelType.EXIT)):
                return False  # Empty space

            if self._maze[a[0]][a[1]].pixel_type == PixelType.EMPTY:
                self._path_len += 1
                self._disp.update(a[0], a[1], PixelType.PATH)
                self._disp.update_length(self._path_len)
                _optional_sleep()
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
                if j.pixel_type == PixelType.EMPTY:
                    display += " "
                elif j.pixel_type == PixelType.WALL:
                    display += "X"
                elif j.pixel_type == PixelType.START:
                    display += "S"
                elif j.pixel_type == PixelType.EXIT:
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
        self.root.geometry("850x450")
        self.maze_canvas = Canvas(self.root, width=850, height=450, background="#000")
        self.maze_canvas.pack()
        self.maze_canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.cells = []
        side = 15
        offset = 7
        for ix in range(49):
            self.cells.append([])
            for iy in range(29):
                x, y = ix * side + offset, iy * side + offset
                rect = self.maze_canvas.create_rectangle(x, y, x + side,
                                                         y + side, fill="gray55")
                self.cells[-1].append(rect)

        self.score_notice = self.maze_canvas.create_text(850, 10, text="探索步数", fill="gray85",
                                                         font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        self.score = self.maze_canvas.create_text(850, 40, text=0, fill="gray85",
                                                  font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)

        self.length_notice = self.maze_canvas.create_text(850, 80, text="路径长度", fill="green",
                                                          font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        self.length = self.maze_canvas.create_text(850, 110, text=0, fill="green",
                                                   font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)
        self.maze: Maze = maze

    def start(self):
        self.root.mainloop()

    def update(self, x: int, y: int, scheme: PixelType):
        if scheme == PixelType.UNKNOWN:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray55")
        elif scheme == PixelType.BOUNDARY:
            raise
        elif scheme == PixelType.EMPTY:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray85")
        elif scheme == PixelType.WALL:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray15")
        elif scheme == PixelType.START:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gold")
        elif scheme == PixelType.EXIT:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="coral")
        elif scheme == PixelType.PATH:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="green")

    def update_score(self, score: int):
        self.maze_canvas.itemconfigure(self.score, text=score)

    def update_length(self, length: int):
        self.maze_canvas.itemconfigure(self.length, text=length)


_maze = Maze()
