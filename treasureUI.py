import random
import time
from enum import Enum
import tkinter
from tkinter import Tk, Canvas
from typing import Optional

WAIT = True
DISP = True
AUTO_CLOSE = False
LEVEL = 1

__VERSION__ = "0.0.1"


def clear():
    _Record.stats.clear()


def display():
    print("-----------------------------------------")
    for _stat in _Record.stats:
        print(_stat)
    print("|-----------------------|---------------|")
    print(sum(_Record.stats, _Record("", 0, False)) / len(_Record.stats))
    print("-----------------------------------------")


def _optional_sleep():
    if WAIT and DISP:
        time.sleep(0.1)


class PixelType(Enum):
    ROAD = 0
    WALL = 1
    EXIT = 2
    START = 3


class Level:
    def __init__(self, entrance, goal, idle, smart, visible=True):
        self.entrance = entrance
        self.goal = goal
        self.idle = idle
        self.smart = smart
        self.visible = visible


_in_class_levels = {
    1: Level((0, 0), (17, 8), [100, 150], [], True),
    2: Level((0, 0), (17, 8), [100, 150], [], False),
    3: Level((0, 0), (17, 8), [], [100], True),
}

_game_map = [
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
_game_map = list(map(list, zip(*_game_map)))
_game_map = [[PixelType(j) for j in i] for i in _game_map]


class PlayerAgent:
    def step(self, puzzle):
        raise NotImplementedError
    
    def reward(self, state, action, state_new, value):
        raise NotImplementedError


class _Record:
    stats = []

    def __init__(self, seed, cost, record: bool = True):
        self.seed = seed
        self.cost = cost
        if record:
            _Record.stats.append(self)

    def __str__(self):
        return f"| Seed: {self.seed:>15} | Cost: {self.cost:>7} |"

    def __repr__(self):
        return f"| Seed: {self.seed:>15} | Cost: {self.cost:>7} |"

    def __add__(self, other):
        return _Record("", self.cost + other.cost, False)

    def __truediv__(self, other):
        return _Record("Sum", round(self.cost / other, 1), False)


class _Mob:
    def __init__(self, location, cost):
        self.location = location
        self.cost = cost

    def step(self, puzzle):
        raise NotImplementedError


class _IdleMob(_Mob):
    def step(self, puzzle):
        return self.location


class _BFSMob(_Mob):
    def step(self, puzzle):
        visited = []
        queue = []
        current = self.location
        if current == puzzle.player:
            return current
        init = puzzle.surrounding(current)
        init_list = list(init)
        random.shuffle(init_list)
        for i in init_list:
            if i == puzzle.player:
                return i
            visited.append(i)
            if init[i] != PixelType.WALL:
                queue.append((i, [current, i]))

        while len(queue) != 0:
            head = queue.pop(0)
            res = puzzle.surrounding(head[0])
            for i in res:
                if i not in visited and res[i] != PixelType.WALL:
                    if i == puzzle.player:
                        return (head[1] + [i])[1]
                    visited.append(i)
                    queue.append((i, head[1] + [i]))


class Treasure:
    def __init__(self, seed=1234):
        self._map = _game_map
        self.size = len(self.map), len(self.map[0])
        if type(LEVEL) == Level:
            self.level = LEVEL
        else:
            self.level = _in_class_levels[LEVEL]

        self.seed = seed
        self._entrance = self.level.entrance
        self._exit = self.level.goal
        self.mobs = self._generate_mobs()
        self._player = self.entrance
        self._total_cost = 0
        self._step_cost = 1

        self._disp: _DISP = _DISP(self)
        self._init_disp()

        self._update_player()
        self._update_mobs()

    @property
    def cost(self):
        return self._step_cost

    @property
    def player(self):
        return self._player

    @property
    def entrance(self):
        return self._entrance

    @property
    def exit(self):
        return self._exit

    @property
    def map(self):
        return self._map

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

    def get_mobs_info(self):
        if self.level.visible:
            return [{"location": mob.location, "cost": mob.cost} for mob in self.mobs]
        else:
            result = []
            for mob in self.mobs:
                if self.player == mob.location:
                    result.append({"radiation": 1.0, "cost": mob.cost})
                elif (abs(self.player[0] - mob.location[0]) <= 1 and
                      abs(self.player[1] - mob.location[1]) <= 1):
                    result.append({"radiation": 0.5, "cost": mob.cost})
                else:
                    result.append({"radiation": 0.0, "cost": mob.cost})
            return result

    def _process_move(self, move):
        if self._is_invalid_move(move):
            return True

        delta = self._evaluate_cost(move)
        self._player = move
        self._update_player()

        if delta == "Victory":
            print(f"You win with cost {self._total_cost}")
            return True
        else:
            self._total_cost += delta

        self._perform_mobs_move()

        self._total_cost += self._evaluate_mobs_cost()
        self._disp.update_cost(self._total_cost)

        return False

    def start(self, agent: PlayerAgent):
        if not isinstance(agent, PlayerAgent):
            print("Invalid agent")
            return

        _interval_ = 1 if DISP else 0

        def logic_mainloop():
            _optional_sleep()
            move = agent.step(self)
            if self._process_move(move):
                if AUTO_CLOSE:
                    self._disp.root.destroy()
            else:
                self._disp.root.after(_interval_, logic_mainloop)

        self._disp.root.after(0, logic_mainloop)
        self._disp.start()
        _Record(self.seed, self._total_cost)

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

    def _evaluate_cost(self, to):
        x, y = to
        if to == self.exit:
            return "Victory"
        if self.map[x][y] == PixelType.ROAD:
            return self._step_cost

    def _perform_mobs_move(self):
        for mob in self.mobs:
            move = mob.step(self)
            mob.location = move
        self._update_mobs()

    def _evaluate_mobs_cost(self):
        delta = 0
        for mob in self.mobs:
            if mob.location == self.player:
                delta += mob.cost
        return delta

    def _generate_mobs(self):
        state = random.getstate()
        random.seed(self.seed)

        available_list = []
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == PixelType.ROAD:
                    available_list.append((i, j))
        available_list.remove(self.entrance)

        # random choose total from available_list
        locations = random.sample(available_list, len(self.level.idle + self.level.smart))

        random.setstate(state)
        return ([_IdleMob(loc, cost) for loc, cost in zip(locations[:len(self.level.idle)], self.level.idle)]
                + [_BFSMob(loc, cost) for loc, cost in zip(locations[len(self.level.idle):], self.level.smart)])

    def surrounding(self, u: [int, int]):
        x, y = u
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

        self.cost_notice = self.canvas.create_text(850, 10, text="探索成本", fill="gray85",
                                                   font=('Helvetica', '15', 'bold'), anchor=tkinter.NE)
        self.cost = self.canvas.create_text(850, 40, text=0, fill="gray85",
                                            font=('Helvetica', '21', 'bold'), anchor=tkinter.NE)

        self.treasure: Optional[Treasure, TreasurePlay] = treasure

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
        elif scheme == PixelType.EXIT:
            self.canvas.itemconfigure(self.cells[x][y], fill="gold")

    def update_cost(self, cost: int):
        self.canvas.itemconfigure(self.cost, text=cost)

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

    def bind_wasd(self):
        self.root.bind("<w>", self.treasure.w)
        self.root.bind("<W>", self.treasure.w)
        self.root.bind("<a>", self.treasure.a)
        self.root.bind("<A>", self.treasure.a)
        self.root.bind("<s>", self.treasure.s)
        self.root.bind("<S>", self.treasure.s)
        self.root.bind("<d>", self.treasure.d)
        self.root.bind("<D>", self.treasure.d)

class TreasureReward(Treasure):

    def __init__(self, seed: int = 1234):
        super().__init__(seed)
        self.total_step = 0

    def start(self, agent: PlayerAgent):
        if not isinstance(agent, PlayerAgent):
            print("Invalid agent")
            return

        _interval_ = 1 if DISP else 0

        def logic_mainloop():
            _optional_sleep()
            self.total_step += 1
            state = (self.player, self.get_mobs_info()[0]['location'])
            move = agent.step(self)
            last_total_cost = self._total_cost
            reach_exit = self._process_move(move)
            state_new = (self.player, self.get_mobs_info()[0]['location'])
            if reach_exit:  # success, reward 100
                agent.reward(state, move, state_new, last_total_cost - self._total_cost+ 100)
                if AUTO_CLOSE:
                    self._disp.root.destroy()
            elif self.total_step >= 100:  # total step too large
                print('Too many steps! Game over.')
                agent.reward(state, move, state_new, last_total_cost - self._total_cost)
                if AUTO_CLOSE:
                    self._disp.root.destroy()
            else:
                agent.reward(state, move, state_new, last_total_cost - self._total_cost)
                self._disp.root.after(_interval_, logic_mainloop)

        self._disp.root.after(0, logic_mainloop)
        self._disp.start()
        _Record(self.seed, self._total_cost)


class TreasurePlay(Treasure):
    def __init__(self, seed: int = 1234):
        global DISP
        assert DISP, "Cannot play in training mode"

        super().__init__(seed)
        self._player = list(self._player)

        global WAIT
        self.prev_wait = WAIT
        WAIT = False
        self.surrounding(self._entrance)
        self._disp.bind_wasd()
        self._disp.start()
        WAIT = self.prev_wait

    def _possible_position(self, x, y):
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
            return False
        if (self._map[x][y] != PixelType.ROAD
                and self._map[x][y] != PixelType.START):
            return False
        return True

    def a(self, *_):
        move = self.player[0] - 1, self.player[1]
        self._process_move(move)

    def d(self, *_):
        move = self.player[0] + 1, self.player[1]
        self._process_move(move)

    def s(self, *_):
        move = self.player[0], self.player[1] + 1
        self._process_move(move)

    def w(self, *_):
        move = self.player[0], self.player[1] - 1
        self._process_move(move)


print("v<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
print("v  Welcome to Python class!  ^")
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>^")
