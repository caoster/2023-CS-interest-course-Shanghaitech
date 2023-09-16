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


class MiniMaxAgent(PlayerAgent):
    def step(self, puzzle: Treasure):
        def extra_cost(player, mobs):
            total_cost = 0
            for mob in mobs:
                if player == mob["location"]:
                    total_cost += mob["cost"]
            return total_cost

        def valid_next_move(location):
            moves = puzzle.surrounding(location)
            valid_moves = []
            for move in moves:
                if moves[move] == PixelType.ROAD:
                    valid_moves.append(move)
            return valid_moves

        def max_function(player, mobs):
            # 0. If the game can finish
            if puzzle.exit in puzzle.surrounding(player):
                return puzzle.exit, 0

            # 1. Find all possible moves
            moves = valid_next_move(player)

            # 2. Iterate all possible moves
            scores = {}
            for move in moves:
                # 3. Move player to new place and evaluate
                _, score = min_function(move, mobs)
                scores[move] = score - puzzle.cost - extra_cost(move, mobs)

            # 4. Return the best move
            next_best_move = max(scores, key=scores.get)
            return next_best_move, scores[next_best_move]

        def min_function(player, mobs):
            # 1. Find all combination of new locations
            all_combinations = []
            for mob in mobs:
                all_combinations.append(valid_next_move(mob["location"]) + [mob["location"]])

            scores = {}
            # 2. Try every single combination
            from itertools import product
            for combine in product(*all_combinations):
                new_mobs = mobs.copy()
                for i in range(len(new_mobs)):
                    new_mobs[i]["location"] = combine[i]
                # 3. Record the evaluation of new mob locations
                _, score = max_function(player, new_mobs)
                scores[new_mobs] = score

            # 4. Return the worst move
            next_worst_move = min(scores, key=scores.get)
            return next_worst_move, scores[next_worst_move]

        return max_function(puzzle.player, puzzle.get_mobs_info())[0]


treasureUI.WAIT = True
treasure = Treasure()
agent = MiniMaxAgent()
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
