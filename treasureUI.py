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


class _Mob:
    def __init__(self, location, cost):
        self.location = location
        self.cost = cost

    def step(self, puzzle):
        raise NotImplementedError


class _IdleMob(_Mob):
    def step(self, puzzle):
        return self.location


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
        self.exit = (17, 8)
        self.mobs = [
            _IdleMob((4, 6), 100),
            _IdleMob((7, 0), 150)
        ]
        self.player = self.entrance
        self._score = 1000

        self._disp: _DISP = _DISP(self)
        self._init_disp()

        self._update_player()
        self._update_mobs()

    def _init_disp(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self._disp.update(i, j, self.map[i][j])

        x, y = self.exit
        self._disp.update(x, y, PixelType.EXIT)

    def _update_player(self):
        self._disp.update_player(*self.player)

    def _update_mobs(self):
        self._disp.update_mobs(self.mobs)

    def start(self, agent: PlayerAgent):
        if not isinstance(agent, PlayerAgent):
            return  # TODO: Error msg

        def logic_mainloop():
            while True:
                move = agent.step(self)
                if self._is_invalid_move(move):
                    return  # TODO: Error msg

                delta = self._evaluate_score(move)
                self.player = move
                self._update_player()

                if delta == "Victory":
                    return  # TODO: win
                else:
                    self._score += delta

                self._perform_mobs_move()

                self._score += self._evaluate_mobs_score()
                self._disp.update_score(self._score)

                if self._score < 0:
                    return  # TODO: lose
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
        if abs(x - self.player[0]) + abs(y - self.player[1]) > 1:
            return True

        return False

    def _evaluate_score(self, to):
        x, y = to
        if to == self.exit:
            return "Victory"
        if self.map[x][y] == PixelType.ROAD:
            return -1

    def _perform_mobs_move(self):
        for mob in self.mobs:
            move = mob.step(self)
            mob.location = move
        self._update_mobs()

    def _evaluate_mobs_score(self):
        delta = 0
        for mob in self.mobs:
            if mob.location == self.player:
                delta -= mob.cost
        return delta

    def explore(self, x: int, y: int):
        result = {}
        if x > 0:
            result[(x - 1, y)] = self.map[x - 1][y]
        if x < self.size[0] - 1:
            result[(x + 1, y)] = self.map[x + 1][y]
        if y > 0:
            result[(x, y - 1)] = self.map[x][y - 1]
        if y < self.size[1] - 1:
            result[(x, y + 1)] = self.map[x][y + 1]
        return result


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

        self.score_notice = self.canvas.create_text(850, 10, text="分数", fill="gray85",
                                                    font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        self.score = self.canvas.create_text(850, 40, text=1000, fill="gray85",
                                             font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)

        self.treasure = treasure

        self.player = None
        self.mobs = []

    @staticmethod
    def _get_position(x, y, small=False, medium=False):
        large = 40
        offset = 20
        small_delta = 10
        medium_delta = 5
        if small:
            return x * large + offset + small_delta, y * large + offset + small_delta, \
                   x * large + offset + large - small_delta, y * large + offset + large - small_delta
        elif medium:
            return x * large + offset + medium_delta, y * large + offset + medium_delta, \
                   x * large + offset + large - medium_delta, y * large + offset + large - medium_delta
        else:
            return x * large + offset, y * large + offset, x * large + offset + large, y * large + offset + large

    def start(self):
        self.root.mainloop()

    def update(self, x: int, y: int, scheme: PixelType):
        if scheme == PixelType.ROAD:
            self.canvas.itemconfigure(self.cells[x][y], fill="gray85")
        elif scheme == PixelType.WALL:
            self.canvas.itemconfigure(self.cells[x][y], fill="gray15")
        elif scheme == PixelType.START:
            self.canvas.itemconfigure(self.cells[x][y], fill="red")
        elif scheme == PixelType.EXIT:
            self.canvas.itemconfigure(self.cells[x][y], fill="gold")
        elif scheme == PixelType.MOB:
            self.canvas.itemconfigure(self.cells[x][y], fill="green")

    def update_score(self, score: int):
        self.canvas.itemconfigure(self.score, text=score)

    def update_player(self, x, y):
        self.canvas.delete(self.player)
        x_start, y_start, x_end, y_end = self._get_position(x, y, medium=True)
        self.player = self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="blue")

    def update_mobs(self, mobs):
        for mob in self.mobs:
            self.canvas.delete(mob)

        self.mobs.clear()
        for mob in mobs:
            x, y = mob.location
            x_start, y_start, x_end, y_end = self._get_position(x, y, small=True)
            self.mobs.append(self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="red"))


class DFSAgent(PlayerAgent):
    def __init__(self):
        self.path = []

    def step(self, puzzle):
        if len(self.path) == 0:
            visited = []
            stack = []
            current = puzzle.player
            init = puzzle.explore(*current)
            for i in init:
                visited.append(i)
                if init[i] != PixelType.WALL:
                    stack.append((i, [current, i]))

            while len(stack) != 0:
                head = stack.pop()
                res = puzzle.explore(*head[0])
                for i in res:
                    if i not in visited and res[i] != PixelType.WALL:
                        if i == puzzle.exit:
                            self.path = (head[1] + [i])[1:]
                            return self.path.pop(0)
                        visited.append(i)
                        stack.append((i, head[1] + [i]))
        else:
            return self.path.pop(0)


Treasure().start(DFSAgent())
