import random
import time

from cardUI import display, start
from cardUI_extension import game, cardUI_help

NUM_CARDS = 20


def new_card():
    all_cards = [[card // 4 + 2, card % 4] for card in random.sample(range(52), NUM_CARDS * 2)]
    return [all_cards[:NUM_CARDS], all_cards[NUM_CARDS:]]


def agent(my_card, opponent, on_board):
    pass


game(new_card, None, None)
time.sleep(10)
