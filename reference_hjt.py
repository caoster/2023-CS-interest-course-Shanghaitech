import random, ast
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasureReward, TreasurePlay, Level, display


class DijkstraAgent(PlayerAgent):
    def __init__(self):
        self.path = None

    def Dijkstra(self, puzzle: Treasure):
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
                new_cost_v = g[u] + 1 + sum(mob['cost']
                                            for mob in puzzle.get_mobs_info() if mob['location'] == v)
                if v not in g:  # 这是第一条到v的路径
                    g[v] = new_cost_v
                    previous[v] = u
                    to_explore.append(v)
                elif g[v] > new_cost_v:  # 这不是第一条到v的路径，但是比之前的更短
                    g[v] = new_cost_v
                    previous[v] = u

    def step(self, puzzle: Treasure):
        if self.path is None:
            self.Dijkstra(puzzle)
        return self.path.pop()


class ExpDijkstraAgent(PlayerAgent):

    def __init__(self):
        self.stepped = False

    def init(self, puzzle: Treasure):
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
                    new_cost_v += self.mob_cost / \
                        len(self.possible_mob_location)
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
        self.update_possible_mob_location(
            puzzle.player, puzzle.get_mobs_info()[0]['radiation'])
        path = self.Dijkstra(puzzle)  # 从puzzle.player位置开始Dijkstra
        return path[1]  # 返回最短路的下一个位置


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
        return -state[2] - self.puzzle.get_mobs_info()[0]['cost'] // (mob_distance + 1) - exit_distance

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
        
        if state[0] != state[1] and action == state[1]:
            return (action, state[1], state[2]+1+self.puzzle.get_mobs_info()[0]['cost'])
        else:
            return (action, state[1], state[2]+1)

    def mob_next_state(self, state, action):
        if state[0] != state[1] and state[0] == action:
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
                next_payoff = self.min_function(
                    self.player_next_state(state, action), depth+1)[0]
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
                next_payoff = self.max_function(
                    self.mob_next_state(state, action), depth+1)[0]
                if min_payoff == None or min_payoff > next_payoff:
                    min_payoff, min_action = next_payoff, action
            return min_payoff, min_action

    def step(self, puzzle: Treasure):
        if not self.stepped:
            self.stepped = True
            self.puzzle = puzzle
        state = (puzzle.player, puzzle.get_mobs_info()[0]['location'], 0)
        return self.max_function(state, 1)[1]


class QLearningAgent(PlayerAgent):

    def __init__(self):
        self.Q = None

    def init_Q(self, puzzle: Treasure):
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
        if self.Q is None:
            self.init_Q(puzzle)
        mob = puzzle.get_mobs_info()[0]
        state = (puzzle.player, mob['location'])
        return max(self.Q[state].keys(), key=lambda action: self.Q[state][action])

    def reward(self, state, action, state_new, value):
        self.Q[state][action] =\
            (1 - self.alpha) * self.Q[state][action] +\
            self.alpha * (value + self.gamma * max(self.Q[state_new].values()))

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

    def test_stat(self, n):
        treasureUI.DISP = False
        treasureUI.WAIT = False
        treasureUI.AUTO_CLOSE = True
        self.alpha = 0.0
        self.gamma = 0.0
        treasureUI.clear()
        for i in range(n):
            treasure = TreasureReward(seed=random.randint(0, 999999))
            treasure.start(self)
        treasureUI.display()

    def save_file(self, filename):
        with open(filename, "w") as fp:
            print(self.Q, file=fp)

    def load_file(self, filename):
        with open(filename, "r") as fp:
            data = fp.read()
        self.Q = ast.literal_eval(data)

################# Day1 below #################
# treasureUI.LEVEL = 1
# for i in range(0, 3):
#     Treasure(seed=i).start(DijkstraAgent())
################# Day1 above #################

################# Day2 below #################
# treasureUI.LEVEL = 2
# for i in range(0, 3):
#     Treasure(seed=i).start(ExpDijkstraAgent())
################# Day2 above #################

################# Day3 below #################
# treasureUI.LEVEL = 3
# treasureUI.DISP = True
# treasureUI.WAIT = True
# treasureUI.AUTO_CLOSE = True
# for i in range(0, 10):
#     Treasure(seed=i).start(MinMaxAgent())
################# Day3 above #################

################# Day4 below #################
treasureUI.LEVEL = 3
agent = QLearningAgent()
# agent.load_file('Q.txt')  # 可以从文件里读取之前训练好的Q值表，如果不读取就是从0开始
agent.train(1000)  # 训练多少局游戏
agent.save_file('Q.txt')  # 可以向文件输出现在Q值表，以便之后继续训练
agent.test(10)  # 测试多少局游戏，展示游戏界面
agent.test_stat(10)  # 测试多少局游戏，不展示游戏界面，但统计Cost的平均值
################# Day4 above #################