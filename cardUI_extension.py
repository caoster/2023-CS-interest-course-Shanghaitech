import time

from cardUI import _DISP, display, _linspace, _get_card_image_path
from copy import deepcopy


def cardUI_help():
    pass


def _upd_card(self: _DISP, cards):
    if self.on_board is not None:
        for i in self.on_board:
            self.canvas.delete(f"card_{i[0]}_{i[1]}")
    for i in cards:
        self.canvas.delete(f"card_{i[0]}_{i[1]}")
    pos = _linspace(300, 500, len(cards))
    for idx, card in enumerate(cards):
        self.canvas.create_image(pos[idx], 160,
                                 image=self.textures[_get_card_image_path(card)],
                                 tags=f"card_{card[0]}_{card[1]}",
                                 anchor="nw")


def _game_logic(self: _DISP):
    if self.gameInit is False:
        self.player1, self.player2 = self.new_card_func()
        self.player1.sort()
        self.player2.sort()

        pos = _linspace(120, 700, len(self.player1))
        for idx, card in enumerate(self.player1):
            self.canvas.create_image(pos[idx], 310,
                                     image=self.textures[_get_card_image_path(card)],
                                     tags=f"card_{card[0]}_{card[1]}",
                                     anchor="nw")
        _linspace(120, 300, len(self.player2))
        for idx, card in enumerate(self.player2):
            self.canvas.create_image(pos[idx], 30,
                                     image=self.textures[_get_card_image_path(card)],
                                     tags=f"card_{card[0]}_{card[1]}",
                                     anchor="nw")
        self.gameInit = True
        self.on_board = None
    else:
        # Take a step
        if self.p1_turn == 1:
            take = self.player_1_agent(deepcopy(self.player1), deepcopy(self.player2), deepcopy(self.on_board))
        else:
            take = self.player_2_agent(deepcopy(self.player2), deepcopy(self.player1), deepcopy(self.on_board))

        if take is None:
            self.on_board = None
        else:
            if self.on_board is None or first_is_larger(take, self.on_board):
                if self.p1_turn:
                    for i in take:
                        if i not in self.player1:
                            print(f"{i}不在你的手牌中")
                            exit(1)
                        self.player1.remove(i)
                        _upd_card(self, take)
                else:
                    for i in take:
                        if i not in self.player2:
                            print(f"{i}不在你的手牌中")
                            exit(1)
                        self.player2.remove(i)
                        _upd_card(self, take)

                self.on_board = take
            else:
                print(f"你出的牌{take}小于场上的{self.on_board}")
                exit(1)
        self.p1_turn = not self.p1_turn

        if len(self.player2) == 0:
            print("对方获胜!")
            self.gameInit = False
            self.root.update()
            time.sleep(1)
            input("按回车进入下一局")
        elif len(self.player1) == 0:
            print("我方获胜!")
            self.gameInit = False
            self.root.update()
            time.sleep(1)
            input("按回车进入下一局")

    self.root.after(100, _game_logic, display)


def _game(self: _DISP, new_card, your, opponent=None):
    self.started = True
    self.gameInit = False
    self.p1_turn = True

    if opponent is None:
        opponent = your

    self.new_card_func = new_card
    self.player_1_agent = your
    self.player_2_agent = opponent

    self.canvas.delete("card_1", "card_2", "card_3", "card_4", "misc")

    self.canvas.create_text(100, 40, text="对方", fill="White",
                            font='Helvetica 24 bold', tags="card", anchor="ne")
    self.canvas.create_rectangle((120, 20), (780, 150), outline="White")

    self.canvas.create_text(100, 380, text="手牌", fill="White",
                            font='Helvetica 24 bold', tags="card", anchor="ne")
    self.canvas.create_rectangle((120, 300), (780, 430), outline="White")

    self.root.after(0, _game_logic, display)
    self.root.mainloop()


def first_is_larger(card1, card2):
    if type(card1) != list or type(card2) != list \
            or type(card1[0]) != list or type(card2[0]) != list:
        print("参与比较的应当是带花色的牌组")
        return
    card1.sort()
    card2.sort()
    if len(card1) != len(card2):
        print("张数不同，无法比较！")
        return
    cat = sorted(card1 + card2)
    for i in range(0, len(cat) - 1):
        if cat[i] == cat[i + 1]:
            print("手牌中不可能有重复的牌")
            return
    pts1 = [i[0] for i in card1]
    pts2 = [i[0] for i in card2]
    if len(pts1) == 1:
        # 单牌
        return pts1 > pts2
    if 3 <= len(pts1) == len(set(pts1)):
        # 顺子
        for i in range(len(pts1) - 1):
            if pts1[i] != pts1[i] - 1:
                print("无效的牌型：必须是对子或顺子")
        for i in range(len(pts2) - 1):
            if pts2[i] != pts2[i] - 1:
                print("牌型必须是对子或顺子，对子和顺子无法比较")
        return pts1[0] > pts2[0]
    elif len(set(pts1)) == 1:
        return pts1[0] > pts2[0]
    else:
        print("无效的牌型：必须是对子或顺子")


def game(new_card, your, opponent=None):
    return _game(display, new_card, your, opponent)
