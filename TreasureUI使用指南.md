# TreasureUI 使用指南

## 依赖/环境检测

本系统没有任何第三方库依赖。

验证该系统是否正常工作，可以将`treasureUI.py`与新建的`main.py`放于同一路径下:

```python
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, TreasurePlay, Level

treasureUI.LEVEL = Level((0, 0), (17, 8), [], [100, 100, 100])
TreasurePlay()
```

此时应当出现窗口，可以通过W/A/S/D作为方向键。

## 接口调用规则

`treasureUI`提供了`Treasure`, `TreasurePlay`, `PixelType`, `LEVEL`, `PlayerAgent`三个类。
两个函数`clear`, `display`, 以及`WAIT`, `LEVEL`两项设置。

### `PixelType`

定义如下：

```python
class PixelType(Enum):
    ROAD = 0
    WALL = 1
    EXIT = 2
    START = 3
```

本项目使用了列举类型(enum)表示迷宫中的位置种类。

其对应的含义是：

- `ROAD`表示给定坐标点的迷宫为一片空地。
- `WALL`表示给定坐标点的迷宫为墙体。
- `EXIT`表示该位置为迷宫出口。
- `START`表示该位置为起始点。

这个类在使用时应该主要用于确认迷宫中的某个点是否为墙壁/出口：

### `Treasure`

该类提供了一个构造函数: `Treasure(seed=1234)`

- seed 的作用是"种子"，类似于`random.seed()`的功能。使用相同的该参数可以确保每次生成相同的地图。注意如果不传入该参数，种子将保持默认值(1234)。

使用`Treasure.start`开始游戏。

示例：

```python
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure


class DFSAgent(PlayerAgent):
    def step(self, puzzle):
        pass


for i in range(5):
    treasure = Treasure(seed=i)
    agent = DFSAgent()
    treasure.start(agent)
```

### 详解`Treasure.explore`

正如上文所述，`explore`函数接受两个参数，即一个点在迷宫中的坐标(左上角为(0, 0))。

`Treasure.explore()`会返回一个字典，其中的key为坐标，value为该点的信息。

例如，在游戏开始我们可以选择`treasure.explore(0, 0)`，这将告诉我们迷宫入口附近的情况。

他的返回值表明了该点上下左右的情况。

例如在上述例子中，返回值可能是`{(0, 1): PixelType.ROAD, (1, 0): PixelType.WALL}`。

这代表通过探索(0, 0)，我们得知了迷宫的(0, 1)为空地，(1, 0)为墙壁。而该点的上/左两个方向已经超出了迷宫范围，自然是不包含在返回值里。

### 详解`Treasure.get_mobs_info`

TODO

### `TreasurePlay`

该类提供一个构造函数: `TreasurePlay(seed=1234)`

一旦TreasurePlay的实例创造完成，立即启动一个游戏窗口。使用W/A/S/D控制人物（蓝色小方块）在迷宫中移动。

该类没有评测作用，仅用于帮助学生熟悉迷宫规则。

`clear`, `display`

### `display()`

```python
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, display


class DFSAgent(PlayerAgent):
    def step(self, puzzle):
        pass


for i in range(5):
    treasure = Treasure(seed=i)
    agent = DFSAgent()
    treasure.start(agent)

display()
```

运行完成后会打印如下的数据统计：

```text
-----------------------------------------
| Seed:               0 | Cost:     194 |
| Seed:               1 | Cost:     294 |
| Seed:               2 | Cost:     144 |
| Seed:               3 | Cost:     194 |
| Seed:               4 | Cost:      44 |
|-----------------------|---------------|
| Seed:             Sum | Cost:   174.0 |
-----------------------------------------
```

统计数据显示，在运行了五个种子的地图(0, 1, 2, 3, 4)后，平均成本为174.0

## 设置

该部分提供的功能有利于学生进行调试或展示：

### `WAIT`

该变量默认为`True`，当设置为`True`时，在每一次移动时会停顿0.1秒，有利于学生观察算法的进行。

如果被设置为`False`，系统会取消上述延迟，一般可以用于评分。

### `LEVEL`

该变量默认为`1`，默认使用第一题信息。

TODO

### 如何调整设置

```python
import treasureUI
from treasureUI import Level

treasureUI.WAIT = False
treasureUI.LEVEL = 3
treasureUI.LEVEL = Level((0, 0), (17, 8), [], [100, 100, 100])
```
