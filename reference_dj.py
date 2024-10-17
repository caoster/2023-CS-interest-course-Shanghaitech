import random
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasureReward, TreasurePlay, Level, display


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
        MAX_DEPTH = 5

        def evaluate_score(player, mob):
            def distance(place1, place2):
                return abs(place1[0] - place2[0]) + abs(place1[1] - place2[1])

            mob_distance = distance(player, mob["location"])
            exit_distance = distance(player, puzzle.exit)
            return mob_distance * 2 - exit_distance  # 对比一下有没有2倍的情况

        def extra_cost(player, mob):
            if player == mob["location"]:
                return mob["cost"]
            else:
                return 0

        def valid_next_move(location):
            moves = puzzle.surrounding(location)
            valid_moves = []
            for move in moves:
                if moves[move] == PixelType.ROAD:
                    valid_moves.append(move)
            return valid_moves

        def max_function(player, mob, depth):
            # 0. If the game can finish
            if puzzle.exit in puzzle.surrounding(player):
                return puzzle.exit, 0
            elif depth >= MAX_DEPTH:
                return player, evaluate_score(player, mob)

            # 1. Find all possible moves
            moves = valid_next_move(player)

            # 2. Iterate all possible moves
            best_move = None
            best_score = -999999999
            for move in moves:
                # 3. Move player to new place and evaluate
                _, score = min_function(move, mob, depth + 1)
                score -= puzzle.cost + extra_cost(move, mob)
                if score > best_score:
                    best_score = score
                    best_move = move

            # 4. Return the best move
            return best_move, best_score

        def min_function(player, mob, depth):
            # 1. Find all possible mob moves
            all_moves = [mob["location"]] + valid_next_move(mob["location"])

            # 2. Iterate all possible moves
            worst_move = None
            worst_score = 999999999

            for move in all_moves:
                new_mob = mob.copy()
                new_mob["location"] = move
                # 3. Record the evaluation of new mob locations
                _, score = max_function(player, new_mob, depth + 1)
                if score < worst_score:
                    worst_score = score
                    worst_move = move

            # 4. Return the worst move
            return worst_move, worst_score

        assert len(puzzle.get_mobs_info()) == 1
        return max_function(puzzle.player, puzzle.get_mobs_info()[0], 0)[0]

class MinMaxAgent(PlayerAgent):

    def __init__(self):
        self.stepped = False
        self.puzzle: Treasure = None
        self.depth_limit = 5

    def payoff(self, state):
        return -state[2]

    def h(self, state):

        def distance(u, v):
            return abs(u[0] - v[0]) + abs(u[1] - v[1])

        mob_distance = distance(state[0], state[1])
        exit_distance = distance(state[0], self.puzzle.exit)
        return -state[2] + 2 * mob_distance - exit_distance

    def player_actions_from(self, state):
        if state[0] == self.puzzle.exit:
            return []
        else:
            list_action = []
            for v, type_v in self.puzzle.surrounding(state[0]).items():
                if type_v != PixelType.WALL:
                    list_action.append(v)
            return list_action

    def mob_actions_from(self, state):
        list_action = [state[1]]
        for v, type_v in self.puzzle.surrounding(state[1]).items():
            if type_v != PixelType.WALL:
                list_action.append(v)
        return list_action

    def player_next_state(self, state, action):
        return (action, state[1], state[2]+1)

    def mob_next_state(self, state, action):
        if state[0] == state[1]:
            return (state[0], action, state[2]+self.puzzle.get_mobs_info()[0]['cost'])
        else:
            return (state[0], action, state[2])

    def max_function(self, state, depth):
        list_action = self.player_actions_from(state)
        if list_action == []:
            return self.payoff(state), None
        elif depth == self.depth_limit:
            return self.h(state), None
        else:
            max_payoff, max_action = None, None
            for action in list_action:
                next_payoff = self.min_function(self.player_next_state(state, action), depth+1)[0]
                if max_payoff == None or max_payoff < next_payoff:
                    max_payoff, max_action = next_payoff, action
            return max_payoff, max_action

    def min_function(self, state, depth):
        list_action = self.mob_actions_from(state)
        if list_action == []:
            return self.payoff(state), None
        elif depth == self.depth_limit:
            return self.h(state), None
        else:
            min_payoff, min_action = None, None
            for action in list_action:
                next_payoff = self.max_function(self.mob_next_state(state, action), depth+1)[0]
                if min_payoff == None or min_payoff > next_payoff:
                    min_payoff, min_action = next_payoff, action
            return min_payoff, min_action

    def step(self, puzzle: Treasure):
        if not self.stepped:
            self.stepped = True
            self.puzzle = puzzle
        state = (puzzle.player, puzzle.get_mobs_info()[0]['location'], 0)
        return self.max_function(state, 1)[1]

class ExpDijkstraAgent(PlayerAgent):

    def __init__(self):
        self.stepped = False

    def init(self, puzzle: Treasure):
        assert len(puzzle.get_mobs_info()) == 1
        self.mob_cost = puzzle.get_mobs_info()[0]['cost']
        self.possible_mob_location = []
        for x in range(puzzle.size[0]):
            for y in range(puzzle.size[1]):
                if puzzle.map[x][y] == PixelType.ROAD or puzzle.map[x][y] == PixelType.EXIT:
                    self.possible_mob_location.append((x, y))

    def Dijkstra(self, puzzle: Treasure):
        g = {puzzle.player: 0}
        previous = {}
        to_explore = [puzzle.player]
        while len(to_explore) > 0:
            u = min(to_explore, key=lambda u: g[u])
            to_explore.remove(u)
            if u == puzzle.exit:
                path = [u]
                while u != puzzle.player:
                    u = previous[u]
                    path.append(u)
                return path[::-1]
            for v, type_v in puzzle.surrounding(u).items():
                if type_v == PixelType.WALL:
                    continue
                new_cost_v = g[u] + 1
                if v in self.possible_mob_location:
                    new_cost_v += self.mob_cost / len(self.possible_mob_location)
                if v not in g:  # 这是第一条到v的路径
                    g[v] = new_cost_v
                    previous[v] = u
                    to_explore.append(v)
                elif g[v] > new_cost_v:  # 这不是第一条到v的路径，但是比之前的更短
                    g[v] = new_cost_v
                    previous[v] = u

    def update_possible_mob_location(self, player_loc, mob_rad):
        old_possible = self.possible_mob_location
        self.possible_mob_location = []
        for mob_loc in old_possible:  # 枚举怪可能的位置
            if player_loc == mob_loc:
                possible = (mob_rad == 1.0)
            elif abs(player_loc[0] - mob_loc[0]) <= 1 and abs(player_loc[1] - mob_loc[1]) <= 1:
                possible = (mob_rad == 0.5)
            else:
                possible = (mob_rad == 0.0)
            if possible:  # 如果不可能，则移除该位置
                self.possible_mob_location.append(mob_loc)

    def step(self, puzzle: Treasure):
        if not self.stepped:
            self.stepped = True
            self.init(puzzle)
        self.update_possible_mob_location(puzzle.player, puzzle.get_mobs_info()[0]['radiation'])
        path = self.Dijkstra(puzzle)  # 从puzzle.player位置开始Dijkstra
        return path[1]  # 返回最短路的下一个位置


class QLearningAgent(PlayerAgent):

    def __init__(self):
        self.stepped = False
        self.alpha = None
        self.gamma = None

    def init(self, puzzle: Treasure):
        assert len(puzzle.get_mobs_info()) == 1
        self.Q = {}
        road = []
        for x in range(puzzle.size[0]):
            for y in range(puzzle.size[1]):
                if puzzle.map[x][y] != PixelType.WALL:
                    road.append((x, y))
        for player_loc in road:
            for mob_loc in road:
                state = (player_loc, mob_loc)
                self.Q[state] = {}
                for action, type_action in puzzle.surrounding(player_loc).items():
                    if type_action != PixelType.WALL:
                        self.Q[state][action] = 0.0

    def step(self, puzzle: Treasure):
        if not self.stepped:
            self.stepped = True
            self.init(puzzle)
        mob = puzzle.get_mobs_info()[0]
        state = (puzzle.player, mob['location'])
        Qmax_state = max(self.Q[state].values())
        action_choices = []
        for action in self.Q[state].keys():
            if self.Q[state][action] == Qmax_state:
                action_choices.append(action)
        return random.choice(action_choices)

    def reward(self, state, action, state_new, value):
        sample = value + self.gamma * max(self.Q[state_new].values())
        self.Q[state][action] += self.alpha * (sample - self.Q[state][action])

    def train(self, n):
        treasureUI.DISP = False
        treasureUI.WAIT = False
        treasureUI.AUTO_CLOSE = True
        self.alpha = 0.5
        self.gamma = 0.9
        for i in range(n):
            treasure = TreasureReward(seed=random.randint(0, 999999))
            treasure.start(self)

    def test(self, n):
        treasureUI.DISP = True
        treasureUI.WAIT = True
        treasureUI.AUTO_CLOSE = False
        self.alpha = 0.0
        self.gamma = 0.0
        for i in range(n):
            treasure = TreasureReward(seed=random.randint(0, 999999))
            treasure.start(self)


# treasureUI.LEVEL = 3
# agent = QLearningAgent()
# agent.train(1000)
# agent.test(10)

# treasureUI.DISP = True
# treasureUI.WAIT = True
# treasureUI.AUTO_CLOSE = True
treasureUI.LEVEL = 3
for i in range(0, 10):
    Treasure(seed=i).start(MinMaxAgent())
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
