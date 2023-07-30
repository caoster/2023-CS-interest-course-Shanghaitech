import random


class _MazeGenerator:
    def __init__(self, size: tuple[int, int], seed: int = 1234):
        self._size = size
        self._init_var()
        temp_state = random.getstate()
        random.seed(seed)
        self._random_state = random.getstate()
        random.setstate(temp_state)

    def _init_var(self):
        self._root = [i for i in range(self._size[1] * (self._size[0] * 2 - 1) - self._size[0])]
        self._unchecked_walls = self._root.copy()
        self._walls_kept = []

    def _barrier_to_block(self, num):
        size = self._size[0]
        a = num // (2 * size - 1)
        b = num % (2 * size - 1)
        if b < size:
            return size * a + b, size * a + b + 1
        else:
            return size * (a - 1) + b + 1, size * a + b + 1

    def _get_root(self, num):
        if self._root[num] == num:
            return num
        else:
            return self._get_root(self._root[num])

    def _step(self):
        random_wall = self._unchecked_walls.pop(random.randrange(len(self._unchecked_walls)))
        block1, block2 = self._barrier_to_block(random_wall)
        if self._get_root(block1) != self._get_root(block2):
            self._root[block2] = self._get_root(block1)
        else:
            self._walls_kept.append(random_wall)

    def run(self):
        temp_state = random.getstate()
        random.setstate(self._random_state)

        self._init_var()
        while len(self._unchecked_walls) != 0:
            self._step()
        # TODO: translate walls to grid

        self._random_state = random.getstate()
        random.setstate(temp_state)


m = _MazeGenerator((50, 30))
m.run()
pass
