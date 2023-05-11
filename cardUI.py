import math
import time
from tkinter import Frame, Canvas, Tk
from PIL import ImageTk, Image

_questions = {
    "1-1": {
        "name": "Sort-naive",
        "testcases": [
            {
                "case": ["1", "7", "13", "2", "4"],
                "answer": ["1", "2", "4", "7", "13"]
            },
            {
                "case": ["8", "1", "2", "7", "4", "10", "7", "3", "2", "4"],
                "answer": ["1", "2", "2", "3", "4", "4", "7", "7", "8", "10"]
            },
            {
                "case": ["1", "2", "1", "1", "1", "1", "1", "1", "1", "1"],
                "answer": ["1", "1", "1", "1", "1", "1", "1", "1", "1", "2"]
            }
        ]
    },
}


def _linspace(a, b, n):
    if n == 1:
        return [(a + b) / 2]
    return [(float(b) - a) / (n - 1) * i + a for i in range(n)]


class _Texture:
    def __init__(self):
        self._textures = {}
        for i in ["club", "diamond", "heart"]:
            for j in range(1, 14):
                self._textures[f"imgs/{i}_{str(j)}.png"] = ImageTk.PhotoImage(
                    Image.open(f"imgs/{i}_{str(j)}.png").resize((80, 115)))

    def __getitem__(self, item):
        if item not in self._textures:
            return self._textures["imgs/heart_1.png"]
        return self._textures[item]


def _get_card_image_path(card_name: str):
    if type(card_name) != str:
        print(f"{card_name} is a {type(card_name)} instead of str!")
        return None
    try:
        name = card_name.split("-")
        if len(name) == 1:
            name = int(name[0])
            if name < 1 or name > 13:
                print(f"value {name} exceeds limit.")
                return None
            return f"imgs/heart_{name}.png"
        elif len(name) == 2:
            if name[0] not in ["club", "diamond", "heart", "spade"]:
                print(f"Card must be one of \"club\", \"diamond\", \"heart\", \"spade\", {name[0]} is not one of them.")
                return None
            elif int(name[1]) < 1 or int(name[1]) > 13:
                print(f"value {name} exceeds limit.")
                return None
            else:
                return f"imgs/{name[0]}_{name[1]}.png"
        else:
            print(f"Wrong card format: {card_name}")
            return None
    except ValueError as e:
        print(e)
        return None


def _get_best_size(num: int):
    return 8, max(math.ceil(num / 8), 3)


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

        self.background = ImageTk.PhotoImage(Image.open("imgs/background.jpg"))
        self.check = ImageTk.PhotoImage(Image.open("imgs/check.png").resize((70, 70)))
        self.cross = ImageTk.PhotoImage(Image.open("imgs/cross.png").resize((70, 70)))
        self.canvas.create_image(800 / 2, 450 / 2, image=self.background, tags="bg")
        self.canvas.pack()
        self.textures = _Texture()

        self.root.update()

    def _draw(self, args_list):
        self.canvas.delete("card")
        x, y = _get_best_size(len(args_list))
        offset_x = _linspace(100, 700, x)
        offset_y = _linspace(50, 280, y)
        all_index = tuple((x, y) for y in offset_y for x in offset_x)
        for idx, arg in enumerate(args_list):
            if _get_card_image_path(arg) is not None:
                self.canvas.create_image(all_index[idx][0], all_index[idx][1],
                                         image=self.textures[_get_card_image_path(arg)],
                                         tags="card",
                                         anchor="n")
            else:
                return
        self.root.update()
        return

    def __call__(self, *args, **kwargs):
        args_list = []
        for i in args:
            if type(i) == list or type(i) == tuple:
                args_list += list(i)
            else:
                args_list.append(i)
        self._draw(args_list)

    def _disp_test(self, name, case, answer, submit, correct: bool):
        self.canvas.delete("card")
        self.canvas.create_text(400, 15, text=name, fill="White",
                                font='Helvetica 30 bold', tags="card", anchor="n")
        self.canvas.create_text(150, 100, text="Input", fill="White", font='Helvetica 22 bold', tags="card", anchor="e")
        self.canvas.create_text(150, 250, text="Your answer", fill="White",
                                font='Helvetica 22 bold', tags="card", anchor="e")
        self.canvas.create_text(150, 350, text="Solution", fill="White",
                                font='Helvetica 22 bold', tags="card", anchor="e")
        for i, j in [(case, 75), (submit, 200), (answer, 275)]:
            offset_x = _linspace(200, 700, len(i))
            for idx, val in enumerate(i):
                if _get_card_image_path(val) is not None:
                    self.canvas.create_image(offset_x[idx], j,
                                             image=self.textures[_get_card_image_path(val)],
                                             tags="card",
                                             anchor="n")
                else:
                    return
        if correct:
            self.canvas.create_image(800, 450,
                                     image=self.check, tags="card", anchor="se")
        else:
            self.canvas.create_image(800, 450,
                                     image=self.cross, tags="card", anchor="se")
        self.root.update()

    def test(self, question: str, submit):
        if question not in _questions:
            print(f"{question} is not a valid question")
            return None
        question = _questions[question]
        name = question["name"]
        testcases = question["testcases"]
        for testcase in testcases:
            case = testcase["case"]
            answer = testcase["answer"]
            student_out = submit(case)
            correct = answer == student_out
            self._disp_test(name, case, answer, student_out, correct)
            if correct:
                time.sleep(1)
            else:
                print("Incorrect!")
                break


display = _DISP()
test = display.test

# Hi students!
# Thank you for participation if you are reading this.
# Python is a great language and a lot more than what you have learned here.
# The tkinter code here is inappropriate for real engineering.
# The reason why I write them in this way lies:
#       In short, running `mainloop()' in a thread rather than main thread would throw an exception (expected behaviour)
#       While running `mainloop()' in another process causes other trouble on an M-chip mac.
# This bug should have been resolved by the time you start using tkinter.
# Good luck!
