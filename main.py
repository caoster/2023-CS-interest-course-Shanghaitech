import random
import time

from cardUI import display, start
from cardUI_extension import game, cardUI_help, first_is_larger

NUM_CARDS = 20


def new_card():
    all_cards = [[card // 4 + 2, card % 4] for card in random.sample(range(52), NUM_CARDS * 2)]
    return [all_cards[:NUM_CARDS], all_cards[NUM_CARDS:]]


def agent(my_card, opponent, on_board):
    if on_board is None:
        return [my_card[0]]
    my_card.sort()
    if len(on_board) == 1:
        for i in my_card:
            if i[0] > on_board[0][0]:
                return [i]
        return None


game(new_card, agent, None)
time.sleep(10)
