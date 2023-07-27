from enum import Enum


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


class _Maze:
    def __init__(self):
        self._size = (10, 8)
        self._maze = [[_Pixel(i, j, _PixelType.EMPTY) for j in range(self._size[0])] for i in range(self._size[1])]
        self._mask = [[False for _ in range(self._size[0])] for _ in range(self._size[1])]
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
        for i in range(self._size[1]):
            for j in range(self._size[0]):
                if hardcoded_maze[i][j] == 1:
                    self._maze[i][j].pixel_type = _PixelType.WALL
                elif hardcoded_maze[i][j] == 2:
                    self._maze[i][j].pixel_type = _PixelType.START
                    self._start = (i, j)
                elif hardcoded_maze[i][j] == 3:
                    self._maze[i][j].pixel_type = _PixelType.EXIT
                    self._exit = (i, j)

    def explore(self, x: int, y: int):
        if self._mask[x][y]:
            print(f"Warning: 你多次访问了({x}, {y})！")
        self._mask[x][y] = True
        result = {"up": _PixelType.BOUNDARY, "down": _PixelType.BOUNDARY, "left": _PixelType.BOUNDARY, "right": _PixelType.BOUNDARY}
        if x > 0:
            result["up"] = self._maze[x - 1][y]
        if x < self._size[0] - 1:
            result["down"] = self._maze[x + 1][y]
        if y > 0:
            result["left"] = self._maze[x][y - 1]
        if y < self._size[1] - 1:
            result["right"] = self._maze[x][y + 1]
        return result

    def solve(self, path: [tuple[int, int]]):
        if path is None:
            return False  # TODO: No solution?
        if path[0] != self._start or path[-1] != self._exit:
            return False
        for idx in range(len(path)):
            a = path[idx]
            b = path[idx + 1]
            if not (0 <= a[0] < self._size[0] and 0 <= a[1] < self._size[1] and 0 <= b[0] < self._size[0] and 0 <= b[1] < self._size[1]):
                return False
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
                return False
        return True

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


a = _Maze()
print(a)
