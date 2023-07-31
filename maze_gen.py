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

    # def _wall_to_grid(self, num):
    #     size_x, size_y = self._size
    #     center = num * 2
    #     x = center // (2 * size_y - 1)
    #     y = center % (2 * size_y - 1)
    #
    #     result = []
    #     if x % 2 == 0:  # Horizontal
    #         if y - 1 >= 0:
    #             result.append((x, y - 1))
    #         result.append((x, y))
    #         if y + 1 < size_y:
    #             result.append((x, y + 1))
    #     else:  # Vertical
    #         if x - 1 >= 0:
    #             result.append((x - 1, y))
    #         result.append((x, y))
    #         if x + 1 < size_x:
    #             result.append((x + 1, y))
    #     return result
    def _wall_to_grid(self, num):
        size_x, size_y = self._size
        cell1, cell2 = self._barrier_to_block(num)
        cell1 -= 1
        cell2 -= 1
        cell1_x = cell1 // size_x
        cell1_y = cell1 % size_x
        cell2_x = cell2 // size_x
        cell2_y = cell2 % size_x
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
        # random_wall = self._unchecked_walls.pop()
        block1, block2 = self._barrier_to_block(random_wall)
        root_1, root_2 = self._get_root(block1), self._get_root(block2)
        if root_1 != root_2:
            self._root[root_2 - 1] = root_1
            print(f"remove {random_wall}")
        else:
            self._walls_kept.append(random_wall)

    def run(self):
        temp_state = random.getstate()
        random.setstate(self._random_state)

        self._init_var()
        for i in range(1, 23):
            print(i, self._barrier_to_block(i))
        while len(self._unchecked_walls) != 0:
            self._step()

        self._random_state = random.getstate()
        random.setstate(temp_state)

        # self._walls_kept = [3, 4, 5, 6, 15, 16, 18]
        # self._walls_kept = [6]
        result = []
        for i in range(self._size[0] - 1):
            for j in range(self._size[1] - 1):
                result.append((2 * i + 1, 2 * j + 1))
        # result.remove((0, 0))
        # result.remove((2 * (self._size[0] - 1), 2 * (self._size[1] - 1)))
        return [self._wall_to_grid(i) for i in self._walls_kept] + result


m = _MazeGenerator((25, 15))
# m = _MazeGenerator((5, 3))
print(m.run())
print(m._walls_kept)
pass
