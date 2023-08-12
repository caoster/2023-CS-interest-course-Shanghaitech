import random
import threading
import time
import tkinter
from typing import Optional
from enum import Enum
from tkinter import Tk, Canvas

WAIT = True
MASK = False


def _optional_sleep():
    if WAIT:
        time.sleep(0.05)


class _Record:
    stats = []

    def __init__(self, seed, explore, length, record: bool = True):
        self.seed = seed
        self.explore = explore
        self.length = length
        if record:
            _Record.stats.append(self)

    def __str__(self):
        return f"| Seed: {self.seed:>15} | Explore: {self.explore:>5} | Length: {self.length:>5} |"

    def __repr__(self):
        return f"| Seed: {self.seed:>15} | Explore: {self.explore:>5} | Length: {self.length:>5} |"

    def __add__(self, other):
        return _Record("", self.explore + other.explore, self.length + other.length, False)

    def __truediv__(self, other):
        return _Record("Sum", round(self.explore / other, 1), round(self.length / other, 1), False)


def display_result():
    print("----------------------------------------------------------")
    for _stat in _Record.stats:
        print(_stat)
    print("|-----------------------|----------------|---------------|")
    print(sum(_Record.stats, _Record("", 0, 0, False)) / len(_Record.stats))
    print("----------------------------------------------------------")


class _MazeGenerator:
    def __init__(self, size: tuple[int, int], seed: int):
        self._size = size
        self._init_var()
        self.seed = seed
        temp_state = random.getstate()
        random.seed(seed)
        self._random_state = random.getstate()
        random.setstate(temp_state)

    def _init_var(self):
        self._root = [i + 1 for i in range(self._size[1] * self._size[0])]
        self._unchecked_walls = [i + 1 for i in range(self._size[1] * (self._size[0] * 2 - 1) - self._size[0])]
        self._walls_kept = []

    def _barrier_to_block(self, num):
        size = self._size[0]
        a = num // (2 * size - 1)
        b = num % (2 * size - 1)
        if b == 0:
            return size * a + b, size * (a + 1) + b
        elif b < size:
            return size * a + b, size * a + b + 1
        else:
            return size * (a - 1) + b + 1, size * a + b + 1

    def _wall_to_grid(self, num):
        size_x, size_y = self._size
        cell1, cell2 = self._barrier_to_block(num)
        cell1 -= 1
        cell2 -= 1
        cell1_x = cell1 // size_x
        cell1_y = cell1 % size_x
        cell2_x = cell2 // size_x
        # cell2_y = cell2 % size_x
        if cell1_x == cell2_x:
            return 2 * cell1_y + 1, 2 * cell1_x
        else:
            return 2 * cell1_y, 2 * cell1_x + 1

    def _get_root(self, num):
        if self._root[num - 1] == num:
            return num
        else:
            return self._get_root(self._root[num - 1])

    def _step(self):
        random_wall = self._unchecked_walls.pop(random.randrange(len(self._unchecked_walls)))
        block1, block2 = self._barrier_to_block(random_wall)
        root_1, root_2 = self._get_root(block1), self._get_root(block2)
        if root_1 != root_2:
            self._root[root_2 - 1] = root_1
        else:
            self._walls_kept.append(random_wall)

    def run(self):
        temp_state = random.getstate()
        random.setstate(self._random_state)

        self._init_var()
        while len(self._unchecked_walls) != 0:
            self._step()

        for i in range(len(self._walls_kept) // 50):
            self._walls_kept.pop(random.randrange(len(self._walls_kept)))

        self._random_state = random.getstate()
        random.setstate(temp_state)

        return [self._wall_to_grid(i) for i in self._walls_kept] + \
            [(2 * i + 1, 2 * j + 1) for i in range(self._size[0] - 1) for j in range(self._size[1] - 1)]


class PixelType(Enum):
    UNKNOWN = -2
    EXPLORED = -1
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3
    PATH = 4

    def is_start_exit(self):
        return self == PixelType.START or self == PixelType.EXIT


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
    def __init__(self, seed: int = 1234, size: tuple[int, int] = (49, 29)):
        self._steps = 0
        self._path_len = 0
        if size[0] < 7 or size[1] < 5:
            print(f"Size should be at least 7x5!")
            exit(1)
        elif size[0] > 49 or size[1] > 29:
            print(f"Size should be at most 49x29!")
            exit(1)
        self._size = size
        self._generator = _MazeGenerator(((self._size[0] + 1) // 2, (self._size[1] + 1) // 2), seed)
        self._maze = [[_Pixel(i, j, PixelType.EMPTY) for j in range(self._size[1])] for i in range(self._size[0])]
        self._mask = [[False for _ in range(self._size[1])] for _ in range(self._size[0])]
        self._explored = [[False for _ in range(self._size[1])] for _ in range(self._size[0])]
        self._start = (-1, -1)
        self._exit = (-1, -1)
        wall_list = self._generator.run()
        maze = [[0 for _ in range(self._size[1])] for _ in range(self._size[0])]
        maze[0][0] = 2
        maze[-1][-1] = 3
        for i in wall_list:
            maze[i[0]][i[1]] = 1
        for i in range(self._size[0]):
            for j in range(self._size[1]):
                if maze[i][j] == 1:
                    self._maze[i][j].pixel_type = PixelType.WALL
                elif maze[i][j] == 2:
                    self._maze[i][j].pixel_type = PixelType.START
                    self._start = (i, j)
                    self._mask[i][j] = True
                    self._explored[i][j] = True
                elif maze[i][j] == 3:
                    self._maze[i][j].pixel_type = PixelType.EXIT
                    self._exit = (i, j)
                    self._mask[i][j] = True
                    self._explored[i][j] = True

        self._disp: _DISP = _DISP(self)
        self._init_disp()

    def start(self, strategy: callable):
        def run_function():
            result = strategy(self)
            if self._submit(result):
                _Record(self._generator.seed, self._steps, self._path_len)
            else:
                print(f"Wrong Answer! Seed: {self._generator.seed}")
                assert False

        timer = threading.Timer(interval=1, function=run_function)
        timer.start()
        self._disp.start()

    def explore(self, x: int, y: int):
        _optional_sleep()
        assert self._mask[x][y], "你只能探索可见区域"
        assert self._maze[x][y] != PixelType.WALL, "你不能走到墙上"
        self._steps += 1
        self._explored[x][y] = True
        if not self._maze[x][y].pixel_type.is_start_exit():
            self._disp.update(x, y, PixelType.EXPLORED)
        else:
            pass
        self._disp.update_score(self._steps)
        result = {}
        if x > 0:
            result[(x - 1, y)] = self._maze[x - 1][y].pixel_type
            self._mask[x - 1][y] = True
            if (not self._explored[x - 1][y]) or self._maze[x - 1][y].pixel_type.is_start_exit():
                self._disp.update(x - 1, y, self._maze[x - 1][y].pixel_type)
            else:
                self._disp.update(x - 1, y, PixelType.EXPLORED)
        if x < self._size[0] - 1:
            result[(x + 1, y)] = self._maze[x + 1][y].pixel_type
            self._mask[x + 1][y] = True
            if (not self._explored[x + 1][y]) or self._maze[x + 1][y].pixel_type.is_start_exit():
                self._disp.update(x + 1, y, self._maze[x + 1][y].pixel_type)
            else:
                self._disp.update(x + 1, y, PixelType.EXPLORED)
        if y > 0:
            result[(x, y - 1)] = self._maze[x][y - 1].pixel_type
            self._mask[x][y - 1] = True
            self._disp.update(x, y - 1, self._maze[x][y - 1].pixel_type)
            if (not self._explored[x][y - 1]) or self._maze[x][y - 1].pixel_type.is_start_exit():
                self._disp.update(x, y - 1, self._maze[x][y - 1].pixel_type)
            else:
                self._disp.update(x, y - 1, PixelType.EXPLORED)
        if y < self._size[1] - 1:
            result[(x, y + 1)] = self._maze[x][y + 1].pixel_type
            self._mask[x][y + 1] = True
            self._disp.update(x, y + 1, self._maze[x][y + 1].pixel_type)
            if (not self._explored[x][y + 1]) or self._maze[x][y + 1].pixel_type.is_start_exit():
                self._disp.update(x, y + 1, self._maze[x][y + 1].pixel_type)
            else:
                self._disp.update(x, y + 1, PixelType.EXPLORED)
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
                if not MASK or self._mask[i][j]:
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
        self.root = Tk(className="Maze")
        self.root.resizable(False, False)
        # self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.geometry("850x450")
        self.maze_canvas = Canvas(self.root, width=850, height=450, background="#000")
        self.maze_canvas.pack()
        self.maze_canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.cells = []
        for x in range(49):
            self.cells.append([])
            for y in range(29):
                x_start, y_start, x_end, y_end = self._get_position(x, y)
                rect = self.maze_canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="gray55")
                self.cells[-1].append(rect)

        self.score_notice = self.maze_canvas.create_text(850, 10, text="探索步数", fill="gray85",
                                                         font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        self.score = self.maze_canvas.create_text(850, 40, text=0, fill="gray85",
                                                  font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)

        self.length_notice = self.maze_canvas.create_text(850, 80, text="路径长度", fill="green",
                                                          font=('Helvetica', '15', 'bold'),
                                                          anchor=tkinter.NE, tags="length")
        self.length = self.maze_canvas.create_text(850, 110, text=0, fill="green",
                                                   font=('Helvetica', '21', 'bold'),
                                                   anchor=tkinter.NE, tags="length")
        self.maze: Optional[Maze, MazePlay] = maze

        # Display person in `MazePlay` mode
        self.person = None

    @staticmethod
    def _get_position(x, y, small=False):
        side = 15
        offset = 7
        smaller = 4
        if small:
            return x * side + offset + smaller, y * side + offset + smaller, \
                   x * side + offset + side - smaller, y * side + offset + side - smaller
        else:
            return x * side + offset, y * side + offset, x * side + offset + side, y * side + offset + side

    def start(self):
        self.root.mainloop()

    def update(self, x: int, y: int, scheme: PixelType):
        if scheme == PixelType.UNKNOWN:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray55")
        elif scheme == PixelType.EXPLORED:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="pink")
        elif scheme == PixelType.EMPTY:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray85")
        elif scheme == PixelType.WALL:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gray15")
        elif scheme == PixelType.START:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="gold")
        elif scheme == PixelType.EXIT:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="red")
        elif scheme == PixelType.PATH:
            self.maze_canvas.itemconfigure(self.cells[x][y], fill="green")

    def update_score(self, score: int):
        self.maze_canvas.itemconfigure(self.score, text=score)

    def update_length(self, length: int):
        self.maze_canvas.itemconfigure(self.length, text=length)

    def update_person(self, x, y):
        x_start, y_start, x_end, y_end = self._get_position(x, y, True)
        self.maze_canvas.coords(self.person, x_start, y_start, x_end, y_end)

    def bind_wasd(self):
        self.maze_canvas.itemconfigure(self.score_notice, text="行走步数")
        self.maze_canvas.itemconfigure(self.length_notice, text="探索次数")
        x_start, y_start, x_end, y_end = self._get_position(0, 0, True)
        self.person = self.maze_canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="blue")
        self.root.bind("<w>", self.maze.w)
        self.root.bind("<a>", self.maze.a)
        self.root.bind("<s>", self.maze.s)
        self.root.bind("<d>", self.maze.d)
        self.root.bind("<Control-h>", self.maze.display_all)


class MazePlay(Maze):
    def __init__(self, seed: int = 1234, size: tuple[int, int] = (49, 29)):
        super().__init__(seed, size)
        global WAIT
        self.prev_wait = WAIT
        WAIT = False
        self.person_pos = [0, 0]
        self.explore(0, 0)
        self._disp.bind_wasd()
        self._disp.start()
        WAIT = self.prev_wait

    def _possible_position(self, x, y):
        if not (0 <= x < self._size[0] and 0 <= y < self._size[1]):
            return False
        if self._maze[x][y].pixel_type != PixelType.EMPTY \
                and self._maze[x][y].pixel_type != PixelType.EXIT \
                and self._maze[x][y].pixel_type != PixelType.START \
                and self._maze[x][y].pixel_type != PixelType.EXPLORED:
            return False
        return True

    def update_explores(self):
        self._disp.update_length(sum([sum(i) for i in self._explored]))

    def a(self, *_):
        if self._possible_position(self.person_pos[0] - 1, self.person_pos[1]):
            self.person_pos[0] -= 1
            self.explore(self.person_pos[0], self.person_pos[1])
            self._disp.update_person(self.person_pos[0], self.person_pos[1])
            self.update_explores()

    def d(self, *_):
        if self._possible_position(self.person_pos[0] + 1, self.person_pos[1]):
            self.person_pos[0] += 1
            self.explore(self.person_pos[0], self.person_pos[1])
            self._disp.update_person(self.person_pos[0], self.person_pos[1])
            self.update_explores()

    def s(self, *_):
        if self._possible_position(self.person_pos[0], self.person_pos[1] + 1):
            self.person_pos[1] += 1
            self.explore(self.person_pos[0], self.person_pos[1])
            self._disp.update_person(self.person_pos[0], self.person_pos[1])
            self.update_explores()

    def w(self, *_):
        if self._possible_position(self.person_pos[0], self.person_pos[1] - 1):
            self.person_pos[1] -= 1
            self.explore(self.person_pos[0], self.person_pos[1])
            self._disp.update_person(self.person_pos[0], self.person_pos[1])
            self.update_explores()

    def display_all(self, *_):
        for x in range(self._size[0]):
            for y in range(self._size[1]):
                self._mask[x][y] = True
                if not self._explored[x][y]:
                    self._disp.update(x, y, self._maze[x][y].pixel_type)


print("v<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
print("v  Welcome to Python class!  ^")
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>^")
