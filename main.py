import random
import time

from cardUI import display, start


def new_card():
    return [[random.randint(2, 14), random.randint(0, 3)] for _ in range(30)]


def sort_all(cards: list):
    return sorted(cards, key=lambda x: x[0] * 4 + x[1])


def search_all(cards: list, target_card: list):
    cards = sort_all(cards)
    result = []
    i = 0
    while i < len(cards) - 1:
        if cards[i] == target_card[0] and cards[i + 1] == target_card[1]:
            result.append([cards[i], cards[i + 1]])
            i += 1
        i += 1
    return result


time.sleep(2)
for i in range(1, 5):
    a = []
    for j in range(52):
        a.append([random.randint(2, 14), random.randint(0, 3)])
        display(i, a)
time.sleep(1)

start(new_card, sort_all, search_all, [[3, 1], [3, 2]])
