import time

from mazeUI import _maze, Maze, _PixelType


def strategy(maze: Maze):
    x, y = maze.size
    print(x, y)
    for i in range(x):
        for j in range(y):
            print(maze.explore(i, j))
            time.sleep(0.1)
    print("Finish")


def dfs(maze: Maze):
    visited = []
    stack = []
    init = maze.explore(0, 0)
    for i in init:
        visited.append(i)
        if init[i] != _PixelType.WALL:
            stack.append((i, [(0, 0), i]))

    while len(stack) != 0:
        head = stack.pop()
        res = maze.explore(head[0][0], head[0][1])
        time.sleep(0.1)
        for i in res:
            if i not in visited and res[i] != _PixelType.WALL:
                if res[i] == _PixelType.EXIT:
                    return head[1] + [i]
                visited.append(i)
                stack.append((i, head[1] + [i]))
        print(head)


def bfs(maze: Maze):
    visited = []
    queue = []
    init = maze.explore(0, 0)
    for i in init:
        visited.append(i)
        if init[i] != _PixelType.WALL:
            queue.append((i, [(0, 0), i]))

    while len(queue) != 0:
        head = queue.pop(0)
        res = maze.explore(head[0][0], head[0][1])
        time.sleep(0.1)
        for i in res:
            if i not in visited and res[i] != _PixelType.WALL:
                if res[i] == _PixelType.EXIT:
                    return head[1] + [i]
                visited.append(i)
                queue.append((i, head[1] + [i]))
        print(head)


# _maze.start(strategy)
# _maze.start(dfs)
_maze.start(bfs)
