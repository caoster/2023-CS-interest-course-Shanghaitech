import threading
import time
from enum import Enum
import tkinter
from tkinter import Tk, Canvas

WAIT = True


def _optional_sleep():
    if WAIT:
        time.sleep(0.05)


class PlayerAgent:
    def step(self, puzzle):
        raise NotImplementedError


class PixelType(Enum):
    ROAD = 0
    WALL = 1
    EXIT = 2
    START = 3
    MOB = 4


class Treasure:
    def __init__(self):
        self.map = [
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
        ]
        # Transpose!
        self.map = list(map(list, zip(*self.map)))
        self.map = [[PixelType(j) for j in i] for i in self.map]
        self.size = len(self.map), len(self.map[0])
        self.entrance = (0, 0)
        self.exit = (18, 9)
        self.mobs = [{"location": (5, 0), "cost": 100}, {"location": (7, 0), "cost": 150}]
        self.player = self.entrance

        self._disp: _DISP = _DISP(self)
        self._init_disp()

        self.update_player()
        self.update_mobs()

    def _init_disp(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self._disp.update(i, j, self.map[i][j])

    def update_player(self):
        self._disp.update_player(*self.player)

    def update_mobs(self):
        self._disp.update_mobs(self.mobs)

    def start(self, agent: PlayerAgent):
        if not isinstance(agent, PlayerAgent):
            return  # TODO: Error msg

        def logic_mainloop():
            while True:
                move = agent.step(self)
                if self._is_invalid_move(move):
                    return  # TODO: Error msg

                self.player = move
                self.update_player()

                _optional_sleep()

        timer = threading.Timer(interval=1, function=logic_mainloop)
        timer.start()
        self._disp.start()

    def _is_invalid_move(self, to):
        x, y = to
        # Index out of range
        if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
            return True
        # Onto walls
        if self.map[x][y] == PixelType.WALL:
            return True
        # Not relative
        if abs(x - self.player[0]) + abs(y - self.player[1]) != 1:
            return True

        return False


class _DISP:
    def __init__(self, treasure: Treasure):
        self.root = Tk(className="Treasure")
        self.root.resizable(False, False)
        # self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.geometry("850x400")
        self.canvas = Canvas(self.root, width=850, height=400, background="#000")
        self.canvas.pack()
        self.canvas.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.cells = []
        for x in range(18):
            self.cells.append([])
            for y in range(9):
                x_start, y_start, x_end, y_end = self._get_position(x, y)
                rect = self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="gray55")
                self.cells[-1].append(rect)

        # self.score_notice = self.canvas.create_text(850, 10, text="探索步数", fill="gray85",
        #                                             font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        # self.score = self.canvas.create_text(850, 40, text=0, fill="gray85",
        #                                      font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)
        #
        # self.length_notice = self.canvas.create_text(850, 80, text="路径长度", fill="green",
        #                                              font=('Helvetica', '15', 'bold'),
        #                                              anchor=tkinter.NE, tags="length")
        # self.length = self.canvas.create_text(850, 110, text=0, fill="green",
        #                                       font=('Helvetica', '21', 'bold'),
        #                                       anchor=tkinter.NE, tags="length")
        self.treasure = treasure

        self.player = None
        self.mobs = []

    @staticmethod
    def _get_position(x, y, small=False):
        side = 40
        offset = 20
        smaller = 8
        if small:
            return x * side + offset + smaller, y * side + offset + smaller, \
                   x * side + offset + side - smaller, y * side + offset + side - smaller
        else:
            return x * side + offset, y * side + offset, x * side + offset + side, y * side + offset + side

    def start(self):
        self.root.mainloop()

    def update(self, x: int, y: int, scheme: PixelType):
        if scheme == PixelType.ROAD:
            self.canvas.itemconfigure(self.cells[x][y], fill="gray85")
        elif scheme == PixelType.WALL:
            self.canvas.itemconfigure(self.cells[x][y], fill="gray15")
        elif scheme == PixelType.START:
            self.canvas.itemconfigure(self.cells[x][y], fill="gold")
        elif scheme == PixelType.EXIT:
            self.canvas.itemconfigure(self.cells[x][y], fill="red")
        elif scheme == PixelType.MOB:
            self.canvas.itemconfigure(self.cells[x][y], fill="green")

    # def update_score(self, score: int):
    #     self.canvas.itemconfigure(self.score, text=score)
    #
    # def update_length(self, length: int):
    #     self.canvas.itemconfigure(self.length, text=length)

    def update_player(self, x, y):
        self.canvas.delete(self.player)
        x_start, y_start, x_end, y_end = self._get_position(x, y, True)
        self.player = self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="blue")

    def update_mobs(self, mobs):
        for mob in self.mobs:
            self.canvas.delete(mob)

        self.mobs.clear()
        for mob in mobs:
            x, y = mob["location"]
            x_start, y_start, x_end, y_end = self._get_position(x, y, True)
            self.mobs.append(self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="red"))


class TestAgent(PlayerAgent):
    def step(self, puzzle):
        if puzzle.player != puzzle.entrance:
            return puzzle.entrance
        else:
            return 0, 1


Treasure().start(TestAgent())
