import random
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasureReward, TreasurePlay, Level, display


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
        return (action, state[1], state[2]+1)

    def mob_next_state(self, state, action):
        if state[0] == state[1]:
            return (state[0], action, state[2]+self.puzzle.get_mobs_info()[0]['cost'])
        else:
            return (state[0], action, state[2])

    def max_function(self, state, depth):
        # YOUR CODE HERE

    def min_function(self, state, depth):
        # YOUR CODE HERE

    def step(self, puzzle: Treasure):
        if not self.stepped:
            self.stepped = True
            self.puzzle = puzzle
        state = (puzzle.player, puzzle.get_mobs_info()[0]['location'], 0)
        return self.max_function(state, 1)[1]


treasureUI.LEVEL = 3
for i in range(0, 10):
    Treasure(seed=i).start(MinMaxAgent())
