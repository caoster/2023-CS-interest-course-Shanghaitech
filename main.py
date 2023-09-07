import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasurePlay, Level, display


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


treasureUI.WAIT = False
for i in range(5):
    treasure = Treasure(seed=i)
    agent = DFSAgent()
    treasure.start(agent)

display()
# for i in range(1, 5):
#     Treasure(seed=i).start(DFSAgent())
# treasureUI.display()
# Treasure(seed=99).start(DFSAgent())
# treasureUI.display()
# treasureUI.clear()
# Treasure(seed=979).start(DFSAgent())
# treasureUI.display()
#
# treasureUI.LEVEL = Level((0, 0), (17, 8), [], [100, 100, 100])
# TreasurePlay()
