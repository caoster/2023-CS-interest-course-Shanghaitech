import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasurePlay, Level, display


class DFSAgent(PlayerAgent):
    def __init__(self):
        self.path = []

    def step(self, puzzle: Treasure):
        if len(self.path) == 0:
            visited = []
            stack = []
            current = puzzle.entrance
            init = puzzle.surrounding(current)
            for i in init:
                visited.append(i)
                if init[i] != PixelType.WALL:
                    stack.append((i, [current, i]))

            while len(stack) != 0:
                head = stack.pop()
                res = puzzle.surrounding(head[0])
                for i in res:
                    if i not in visited and res[i] != PixelType.WALL:
                        if i == puzzle.exit:
                            self.path = (head[1] + [i])[1:]
                            return self.path.pop(0)
                        visited.append(i)
                        stack.append((i, head[1] + [i]))
        else:
            return self.path.pop(0)


class UCSAgent(PlayerAgent):
    def __init__(self):
        self.path = None

    def ucs(self, puzzle: Treasure):
        g = {puzzle.entrance: 0}
        previous = {}
        to_explore = [puzzle.entrance]
        while len(to_explore) > 0:
            u = min(to_explore, key=lambda u: g[u])
            to_explore.remove(u)
            if u == puzzle.exit:
                self.path = [u]
                while u != puzzle.entrance:
                    u = previous[u]
                    self.path.append(u)
            for v, type_v in puzzle.surrounding(u).items():
                if type_v == PixelType.WALL:
                    continue
                new_cost_v = g[u] + 1 + sum(mob['cost'] for mob in puzzle.get_mobs_info() if mob['location'] == v)
                if v not in g:  # 这是第一条到v的路径
                    g[v] = new_cost_v
                    previous[v] = u
                    to_explore.append(v)
                elif g[v] > new_cost_v:  # 这不是第一条到v的路径，但是比之前的更短
                    g[v] = new_cost_v
                    previous[v] = u

    def step(self, puzzle: Treasure):
        if self.path is None:
            self.ucs(puzzle)
        return self.path.pop()


treasureUI.WAIT = True
for i in range(5):
    treasure = Treasure(seed=i)
    agent = UCSAgent()
    treasure.start(agent)
#
# display()
# for i in range(1, 5):
#     Treasure(seed=i).start(DFSAgent())
# treasureUI.display()
# Treasure(seed=99).start(DFSAgent())
# treasureUI.display()
# treasureUI.clear()
# Treasure(seed=979).start(DFSAgent())
# treasureUI.display()
#
# treasureUI.LEVEL = Level((0, 0), (17, 8), [300], [100, 100, 100])
# TreasurePlay()
