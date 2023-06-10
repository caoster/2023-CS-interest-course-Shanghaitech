import random
import time

from cardUI import display, start, game

NUM_CARDS = 20


def new_card():
    all_cards = [[card // 4 + 2, card % 4] for card in random.sample(range(52), NUM_CARDS * 2)]
    return [all_cards[:NUM_CARDS], all_cards[NUM_CARDS:]]


def agent(my_card, opponent, on_board):
    my_card.sort()
    my_card_dict = {}
    for i in my_card:
        if i[0] not in my_card_dict:
            my_card_dict[i[0]] = [i]
        else:
            my_card_dict[i[0]].append(i)

    if on_board is None:
        for i in range(2, 15):
            if i in my_card_dict:
                return my_card_dict[i]
    on_board.sort()
    on_board = [tuple(i) for i in on_board]

    if len(on_board) == 1:
        for i in my_card:
            if i[0] > on_board[0][0]:
                return [i]
        return None
    elif len(set([i[0] for i in on_board])) == 1:
        # 对子
        len_of_board = len(on_board)
        for i in range(on_board[0][0] + 1, 15):
            if i in my_card_dict and len(my_card_dict[i]) >= len_of_board:
                return my_card_dict[i][:len_of_board]
        return None
    else:
        # 顺子
        start = on_board[0][0]
        len_of_board = len(on_board)
        for i in range(start, 15):
            found = True
            for j in range(len_of_board):
                if i + j not in my_card_dict:
                    found = False
                    break
            if found:
                return [my_card_dict[i][0] for i in range(start, start + len_of_board)]


game(new_card, agent, None)
