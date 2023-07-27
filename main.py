from enum import Enum


class _PixelType(Enum):
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
                elif hardcoded_maze[i][j] == 3:
                    self._maze[i][j].pixel_type = _PixelType.EXIT

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
