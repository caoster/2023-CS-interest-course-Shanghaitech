import random
import ast
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasureReward


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


treasureUI.LEVEL = 3
agent = QLearningAgent()
# agent.load_file('Q.txt')  # 可以从文件里读取之前训练好的Q值表，如果不读取就是从0开始
agent.train(1000)  # 训练多少局游戏
agent.save_file('Q.txt')  # 可以向文件输出现在Q值表，以便之后继续训练
agent.test(10)  # 测试多少局游戏，展示游戏界面
agent.test_stat(10)  # 测试多少局游戏，不展示游戏界面，但统计Cost的平均值
