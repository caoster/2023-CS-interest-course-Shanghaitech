# MazeUI 使用指南

## 依赖/环境检测

本系统没有任何第三方库依赖。

验证该系统是否正常工作，可以将`mazeUI.py`与新建的`main.py`放于同一路径下:

```python
import mazeUI
from mazeUI import Maze, PixelType, display_result, MazePlay

MazePlay()
```

此时应当出现窗口，可以通过W/A/S/D作为方向键。

## 接口调用规则

`mazeUI`提供了`Maze`, `PixelType`, `MazePlay`三个类。
一个函数`display_result`, 以及`WAIT`, `MASK`, `PERF`三项设置。

### `PixelType`

定义如下：

```python
class PixelType(Enum):
    UNKNOWN = -2  # 不需要
    EXPLORED = -1  # 不需要
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3
    PATH = 4  # 不需要
```

在Python中，有一种用法叫列举类型(enum)，由于课程没有涉及，这里直接展示其用法。

在该项目中，你可能会使用到的值有：

```python
PixelType.EMPTY
PixelType.WALL
PixelType.START
PixelType.EXIT
```

其对应的含义是：

- `EMPTY`表示给定坐标点的迷宫为一片空地。
- `WALL`表示给定坐标点的迷宫为墙体。
- `START`表示该位置为起始点（本项目中默认为左上角）。
- `EXIT`表示该位置为迷宫出口（本项目中默认为右下角）。

这个类在使用时应该主要用于确认迷宫中的某个点是否为墙壁/出口：

```python
from mazeUI import PixelType

pixel = PixelType.EMPTY  # 迷宫中获取的一个点

if pixel == PixelType.EXIT:
    pass  # 如果是迷宫出口
elif pixel == PixelType.EMPTY:
    pass  # 如果是空地
elif pixel == PixelType.START:
    pass  # 如果是迷宫入口
elif pixel == PixelType.WALL:
    pass  # 如果是墙壁
else:
    assert False, "在正常程序中不可能是其他情况"
```

### `Maze`

该类提供了一个构造函数: `Maze(seed: int = 1234, size: tuple[int, int] = (49, 29))`

- seed 的作用是"种子"，类似于`random.seed()`的功能。使用相同的该参数可以确保每次生成相同的迷宫。注意如果不传入该参数，种子将保持默认值(1234)。
- size 参数可以限制地图的大小。其大小应当处于`(7, 5)`到`(49, 29)`之间。

为了开始一局游戏，你需要提供一个函数代表你的"策略"。

该函数应当接受一个迷宫对象`Maze`作为参数，通过调用`Maze.explore`逐步对迷宫进行探索，最终找到终点。

使用`Maze.start`开始游戏。

示例：

```python
import mazeUI
from mazeUI import Maze, PixelType, display_result, MazePlay


def strategy(maze: Maze):
    x, y = maze.size
    for i in range(x):
        for j in range(y):
            print(maze.explore(i, j))


maze = Maze(seed=7890, size=(31, 7))
maze.start(strategy)
```

这份示例代码在语法上是正确的，但不能实现相关功能，因为我们需要针对迷宫的地形选择需要探索的点，而不是简单的遍历一遍所有的点。

### 详解`Maze.explore`

正如上文所述，`explore`函数接受两个参数，即一个点在迷宫中的坐标(左上角为(0, 0))。

`Maze.explore()`会返回一个字典，其中的key为坐标，value为该点的信息。

例如，在游戏开始我们可以选择`maze.explore(0, 0)`，这将告诉我们迷宫入口附近的情况。

他的返回值表明了该点上下左右的情况。

例如在上述例子中，返回值可能是`{(0, 1): PixelType.EMPTY, (1, 0): PixelType.WALL}`。

这代表通过探索(0, 0)，我们得知了迷宫的(0, 1)为空地，(1, 0)为墙壁。而该点的上/左两个方向已经超出了迷宫范围，自然是不包含在返回值里。

### 我的策略函数应该什么时候返回，返回什么？

当你的策略找到了并探索了终点，就可以返回了。

如果你的策略记录了路径，可以返回路径评测正确性。
返回格式应当是`List[tuple[int, int]]`：

```python
[(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)]  # 表示了一条从(0, 0)到(2, 2)的路径。
```

注意，如果违背以下任何一条，该路径都将被视为无效！

- 路径中的第一项应当为迷宫入口
- 路径中的最后一项应当为迷宫出口
- 路径中的每个点必须在迷宫范围内的空地上
- 路径中的点必须与下一个点相邻

在策略函数返回后，迷宫的一局数据会被自动记录，包括调用`explore`的次数，返回路径的长度。

如果你的策略没有记录路径，直接写`return None`即可。

### `MazePlay`

该类提供一个构造函数: `MazePlay(seed: int = 1234, size: tuple[int, int] = (49, 29))`

一旦MazePlay的实例创造完成，立即启动一个迷宫窗口。使用W/A/S/D控制人物（蓝色小方块）在迷宫中移动。

该类没有评测作用，仅用于帮助学生熟悉迷宫规则。

### `display_result()`

```python
import mazeUI
from mazeUI import Maze, PixelType, display_result, MazePlay


def strategy(maze: Maze):
    pass

for i in range(5):
    maze = Maze(seed=i, size=(31, 7))
    maze.start(strategy)

display_result()
```

运行完成后会打印如下的数据统计：

```text
----------------------------------------------------------
| Seed:               0 | Explore:    94 | Length:    59 |
| Seed:               1 | Explore:    72 | Length:    51 |
| Seed:               2 | Explore:    90 | Length:    47 |
| Seed:               3 | Explore:    86 | Length:    47 |
| Seed:               4 | Explore:   116 | Length:    51 |
|-----------------------|----------------|---------------|
| Seed:             Sum | Explore:  91.6 | Length:  51.0 |
----------------------------------------------------------
```

统计数据显示，在运行了五个种子的地图(0, 1, 2, 3, 4)后，平均每个迷宫探索91.6次，寻找的路径平均长度为51.0


## 设置

该部分提供的功能有利于学生进行调试或展示：

### `WAIT`

该变量默认为`True`，当设置为`True`时，在每一次`Maze.explore()`时会停顿0.05秒，有利于学生观察算法的进行。

如果被设置为`False`，系统会取消上述延迟，一般可以用于快速评测算法寻找优秀路径的能力。

### `MASK`

该变量默认为`False`，学生一直可以观察完整的迷宫。

如果被设置为`True`，迷宫中未探索的位置一直呈现灰色，隐藏视野。只有当周围(上下左右)有位置被探索过以后才会展示。

注意该设置项仅影响展示，对算法本身的逻辑没有任何影响。

### `PERF`

该变量默认为`False`。

如果被设置为`True`，程序将以最快的方式运行，不会显示任何迷宫窗口。


### 如何调整设置
```python
import mazeUI

mazeUI.WAIT = False
mazeUI.MASK = True
mazeUI.PERF = True
```
