import random

from cardUI import display, test
import time

suits = ["club", "diamond", "heart", "spade"]
points = list(range(1, 14))


# time.sleep(2)
# for i in range(0, 65):
#     display([f"{random.choice(suits)}-{random.choice(points)}" for _ in range(i)])
#     time.sleep(0.15)
# time.sleep(50)
def func(para: list):
    # para[1], para[0] = para[0], para[2]
    # return para
    return sorted(para, key=lambda x: int(x))


time.sleep(5)
test("1-1", func)
time.sleep(10)
