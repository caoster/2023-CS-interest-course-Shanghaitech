import mazeUI
from mazeUI import Maze, PixelType, display_result, MazePlay


def strategy(maze: Maze):
    x, y = maze.size
    print(x, y)
    for i in range(x):
        for j in range(y):
            print(maze.explore(i, j))
    print("Finish")


def dfs(maze: Maze):
    visited = []
    stack = []
    init = maze.explore(0, 0)
    for i in init:
        visited.append(i)
        if init[i] != PixelType.WALL:
            stack.append((i, [(0, 0), i]))

    while len(stack) != 0:
        head = stack.pop()
        res = maze.explore(head[0][0], head[0][1])
        for i in res:
            if i not in visited and res[i] != PixelType.WALL:
                if res[i] == PixelType.EXIT:
                    return head[1] + [i]
                visited.append(i)
                stack.append((i, head[1] + [i]))


def bfs(maze: Maze):
    visited = []
    queue = []
    init = maze.explore(0, 0)
    for i in init:
        visited.append(i)
        if init[i] != PixelType.WALL:
            queue.append((i, [(0, 0), i]))

    while len(queue) != 0:
        head = queue.pop(0)
        res = maze.explore(head[0][0], head[0][1])
        for i in res:
            if i not in visited and res[i] != PixelType.WALL:
                if res[i] == PixelType.EXIT:
                    return head[1] + [i]
                visited.append(i)
                queue.append((i, head[1] + [i]))


mazeUI.WAIT = False
mazeUI.MASK = True
for i in range(5):
    maze = Maze(seed=i, size=(31, 7))
    maze.start(dfs)
    # maze.start(bfs)

display_result()

MazePlay()
