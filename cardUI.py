import math
import random
from tkinter import Frame, Canvas, Tk
from PIL import ImageTk, Image
from copy import deepcopy

_COLOR = {0: "club", 1: "diamond", 2: "heart", 3: "spade"}
_CARD_PATH = "imgs/"
# Random number that stands for empty
_EMPTY_CARD = random.randint(0x3b0a73, 0x649168c2a) + 0x6abc5826


def _linspace(a, b, n):
    if n == 1:
        return [(a + b) / 2]
    return [(float(b) - a) / (n - 1) * i + a for i in range(n)]


class _Texture:
    def __init__(self):
        self._textures = {str(_EMPTY_CARD): ImageTk.PhotoImage(
            Image.open(f"{_CARD_PATH}empty.png").resize((80, 115)))
        }
        for i in range(4):
            for j in range(2, 15):
                self._textures[f"{_CARD_PATH}{_COLOR[i]}_{j}.png"] = ImageTk.PhotoImage(
                    Image.open(f"{_CARD_PATH}{_COLOR[i]}_{j}.png").resize((80, 115)))

    def __getitem__(self, item):
        return self._textures[item]


def _get_card_image_path(card_name: list[int] | int) -> str | None:
    if card_name == _EMPTY_CARD:
        return str(_EMPTY_CARD)
    if type(card_name) == int:
        if card_name > 14 or card_name < 2:
            print("卡牌必须是[2, 14]中的整数")
            return None
        return f"{_CARD_PATH}heart_{card_name}.png"
    else:  # type(card_name) == list[int]
        if len(card_name) != 2 or type(card_name[0]) != int or type(card_name[1]) != int:
            print(f"{card_name} 无法表示有效的卡牌")
            return None
        if card_name[0] > 14 or card_name[0] < 2:
            print("卡牌必须是[2, 14]中的整数")
            return None
        if card_name[1] not in _COLOR:
            print("花色必须是[0, 3]中的整数")
            return None
        return f"{_CARD_PATH}{_COLOR[card_name[1]]}_{card_name[0]}.png"


class _DISP:
    def __init__(self):
        print("v<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("v  Welcome to Python class!  ^")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>^")
        self.root = Tk(className="Cards")
        self.root.resizable(False, False)
        # self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.frame = Frame(self.root)
        self.frame.pack()
        self.root.geometry("800x450")

        self.canvas = Canvas(self.frame, bg="black", width=800, height=450)

        self.background = ImageTk.PhotoImage(Image.open(f"{_CARD_PATH}background.jpg"))
        self.check = ImageTk.PhotoImage(Image.open(f"{_CARD_PATH}check.png").resize((70, 70)))
        self.cross = ImageTk.PhotoImage(Image.open(f"{_CARD_PATH}cross.png").resize((70, 70)))
        self.canvas.create_image(800 / 2, 450 / 2, image=self.background, tags="bg")
        self.canvas.pack()
        self.textures = _Texture()

        self.new_card_func = None
        self.sort_card_func = None
        self.search_card_func = None
        self.current_cards = []
        self.target_card = None

        self.started = False

        self.gameInit = None
        self.p1_turn = None
        self.player_1_agent = None
        self.player_2_agent = None

        self.canvas.create_rectangle((50, 20), (400, 215), outline="White", tags="misc")
        self.canvas.create_rectangle((400, 20), (750, 215), outline="White", tags="misc")
        self.canvas.create_rectangle((50, 215), (400, 420), outline="White", tags="misc")
        self.canvas.create_rectangle((400, 215), (750, 420), outline="White", tags="misc")
        self.root.update()

    def __del__(self):
        if not self.started:
            input("Press enter to exit.")

    def _get_best_size(self, num: int):
        if self.started:
            return num, 1
        else:
            return 13, max(math.ceil(num / 13), 3)

    def _get_seg_loc(self, loc: int):
        x = y = 0
        if self.started:
            if loc == 1:
                return 100, 525, 80, 80
            elif loc == 2:
                return 675, 720, 80, 80
            elif loc == 3:
                return 100, 525, 290, 290
        else:
            if loc == 2 or loc == 4:
                x = 375
            if loc == 3 or loc == 4:
                y = 200
            return 100 + x, 320 + x, 30 + y, 100 + y

    def _draw(self, loc: int, args_list: list[int] | list[list[int]]):
        if loc < 1 or loc > 4:
            print("展示的位置必须为[1, 4]中的整数")
            return None
        self.canvas.delete(f"card_{loc}")
        start_x, end_x, start_y, end_y = self._get_seg_loc(loc)
        x, y = self._get_best_size(len(args_list))
        offset_x = _linspace(start_x, end_x, x)
        offset_y = _linspace(start_y, end_y, y)
        all_index = tuple((x, y) for y in offset_y for x in offset_x)
        for idx, arg in enumerate(args_list):
            if _get_card_image_path(arg) is not None:
                self.canvas.create_image(all_index[idx][0], all_index[idx][1],
                                         image=self.textures[_get_card_image_path(arg)],
                                         tags=f"card_{loc}",
                                         anchor="n")
            else:
                return
        self.root.update()
        return

    def __call__(self, *args, **kwargs):
        if len(args) != 2:
            print("display() 应当接受两个参数，第一个为展示的位置，第二个为要展示的列表")
            return
        if type(args[0]) != int:
            print("display() 第一个参数为展示的位置，类型应当为<int>")
            return
        if type(args[1]) != list:
            print("display() 第二个参数为展示的列表，类型应当为<list>")
            return
        self._draw(args[0], args[1])

    def _new_cards(self):
        self.current_cards = self.new_card_func()
        self(1, self.current_cards)

    def _sort_cards(self):
        if len(self.current_cards) == 0:
            print("目前没有需要排序的牌")
            return None
        if self.sort_card_func is None:
            print("没有实现排序功能")
            return None
        self.current_cards = self.sort_card_func(self.current_cards)
        self(1, self.current_cards)

    def _search_cards(self):
        if len(self.current_cards) == 0:
            print("目前没有需要搜索的牌")
            return None
        if self.search_card_func is None:
            print("没有实现查找功能")
            return None
        if self.target_card is None:
            self.target_card = [list(t) for t in zip([random.randint(1, 14)] * 2, random.sample(range(4), k=2))]
            print(f"随机选择查找: {self.target_card}")
            self(2, self.target_card)
        results = self.search_card_func(self.current_cards, self.target_card)
        disp_cards = []
        for result in results:
            disp_cards += result
            disp_cards += [_EMPTY_CARD] * 2
        if len(disp_cards) > 11:
            disp_cards.pop()
            disp_cards.pop()
        while len(disp_cards) < 10:
            disp_cards.append(_EMPTY_CARD)
        self(3, disp_cards)

    def _canvas_on_click(self, event):
        if 650 < event.x < 750:
            if 270 < event.y < 300:
                self._new_cards()
            elif 310 < event.y < 340:
                self._sort_cards()
            elif 350 < event.y < 380:
                self._search_cards()

    def start(self, new_card, sort_card=None, search_card=None, target_card=None):
        self.started = True
        self.target_card = target_card

        self.new_card_func = new_card
        self.sort_card_func = sort_card
        self.search_card_func = search_card

        self.canvas.delete("card_1", "card_2", "card_3", "card_4", "misc")
        if self.target_card is not None:
            self(2, self.target_card)
        self.canvas.create_text(300, 20, text="发牌 / 排序", fill="White",
                                font='Helvetica 24 bold', tags="card", anchor="n")
        self.canvas.create_rectangle((30, 50), (600, 225), outline="White")
        self.canvas.create_text(700, 20, text="目标", fill="White",
                                font='Helvetica 24 bold', tags="card", anchor="n")
        self.canvas.create_rectangle((625, 50), (775, 225), outline="White")
        self.canvas.create_text(300, 230, text="搜索", fill="White",
                                font='Helvetica 24 bold', tags="card", anchor="n")
        self.canvas.create_rectangle((30, 260), (600, 435), outline="White")

        self.canvas.create_rectangle((650, 270), (750, 300), fill="#907050", outline="")
        self.canvas.create_text(700, 285, text="发牌", fill="White",
                                font='Helvetica 22', tags="card")
        self.canvas.create_rectangle((650, 310), (750, 340), fill="#907050", outline="")
        self.canvas.create_text(700, 325, text="排序", fill="White",
                                font='Helvetica 22', tags="card")
        self.canvas.create_rectangle((650, 350), (750, 380), fill="#907050", outline="")
        self.canvas.create_text(700, 365, text="搜索", fill="White",
                                font='Helvetica 22', tags="card")
        self.canvas.bind("<Button-1>", self._canvas_on_click)
        self.root.mainloop()

    def _upd_card(self, cards):
        if self.on_board is not None:
            for i in self.on_board:
                self.canvas.delete(f"card_{i[0]}_{i[1]}")
        if cards is None:
            return
        for i in cards:
            self.canvas.delete(f"card_{i[0]}_{i[1]}")
        pos = _linspace(300, 500, len(cards))
        for idx, card in enumerate(cards):
            self.canvas.create_image(pos[idx], 160,
                                     image=self.textures[_get_card_image_path(card)],
                                     tags=f"card_{card[0]}_{card[1]}",
                                     anchor="nw")

    def _game_logic(self):
        if self.gameInit is False:
            self.player1, self.player2 = self.new_card_func()
            self.player1.sort()
            self.player2.sort()

            for i in range(2, 15):
                for j in range(0, 4):
                    self.canvas.delete(f"card_{i}_{j}")

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
                self._upd_card(None)
                self.on_board = None
            else:
                if self.on_board is None or _first_is_larger(take, self.on_board):
                    if self.p1_turn:
                        for i in take:
                            if i not in self.player1:
                                print(f"{i}不在你的手牌中")
                                exit(1)
                            self.player1.remove(i)
                        self._upd_card(take)
                    else:
                        for i in take:
                            if i not in self.player2:
                                print(f"{i}不在你的手牌中")
                                exit(1)
                            self.player2.remove(i)
                        self._upd_card(take)

                    self.on_board = take
                else:
                    print(f"你出的牌{take}小于场上的{self.on_board}")
                    exit(1)
            self.p1_turn = not self.p1_turn

            if len(self.player2) == 0:
                print("对方获胜!")
                self.gameInit = False
                print("即将开始下一局")
                self.root.after(1000, self._game_logic)
                return
            elif len(self.player1) == 0:
                print("我方获胜!")
                self.gameInit = False
                print("即将开始下一局")
                self.root.after(1000, self._game_logic)
                return

        self.root.after(100, self._game_logic)

    def game(self, new_card, your, opponent=None):
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

        self.root.after(0, self._game_logic)
        self.root.mainloop()


def _first_is_larger(card1, card2):
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


display = _DISP()


def start(new_card, your, opponent=None):
    return display.start(new_card, your, opponent)


def game(new_card, your, opponent=None):
    return display.game(new_card, your, opponent)
