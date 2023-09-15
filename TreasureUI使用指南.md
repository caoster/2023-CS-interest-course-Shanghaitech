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

`treasureUI`提供了`Treasure`, `TreasurePlay`, `PixelType`, `LEVEL`, `PlayerAgent`五个类。
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

本项目使用了列举类型(enum)表示地图中的位置种类。

其对应的含义是：

- `ROAD`表示给定坐标点的地图为一片空地。
- `WALL`表示给定坐标点的地图为墙体。
- `EXIT`表示该位置为地图出口。
- `START`表示该位置为起始点。

这个类在使用时应该主要用于确认地图中的某个点是否为墙壁/出口：

### `Treasure`

该类提供了一个构造函数: `Treasure(seed=1234)`

- seed 的作用是"种子"，类似于`random.seed()`的功能。使用相同的该参数可以确保每次生成的怪物位置相同。注意如果不传入该参数，种子将保持默认值(1234)。

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

### `Treasure`类的重要属性

- `Treasure.cost` 每在地图中走一步的成本，默认为1。
- `Treasure.player` 人物当前位置，为一个`tuple`，例如`(0, 0)`。
- `Treasure.entrance` 入口位置，为一个`tuple`，例如`(0, 0)`。
- `Treasure.exit` 出口位置，为一个`tuple`，例如`(17, 8)`。
- `Treasure.map` 地图，为一个二维数组，例如`[[PixelType.ROAD, PixelType.WALL], [PixelType.EXIT, PixelType.START]]`。

### 详解`Treasure.surrounding`

正如上文所述，`surrounding`函数接受一个`tuple`作为参数，即一个点在地图中的坐标(左上角为(0, 0))。

`Treasure.surrounding()`会返回一个字典，其中的key为坐标，value为该点的信息。

例如，在游戏开始我们可以选择`treasure.surrounding((0, 0))`，这将告诉我们地图入口附近的情况。

他的返回值表明了该点上下左右的情况。

例如在上述例子中，返回值可能是`{(0, 1): PixelType.ROAD, (1, 0): PixelType.WALL}`。

这代表通过探索(0, 0)，我们得知了地图的(0, 1)为空地，(1, 0)为墙壁。而该点的上/左两个方向已经超出了地图范围，自然是不包含在返回值里。

### 详解`Treasure.get_mobs_info`

在“正常情况”下，该函数返回一个列表，其中的元素为字典。字典中`key`为`location`和`cost`，分别代表怪物的位置以及成本。

当关卡的`visible`属性设为`False`时(详解见下方`LEVEL`解释)，该函数返回一个列表，其中的元素为字典。字典中`key`为`radiation`和`cost`，分别代表与怪物之间的距离以及成本。

- 当人物已经和怪物重合，`radiation`为1.0
- 当人物在怪物周围一圈范围内时，`radiation`为0.5
- 当人物在更远距离时，`radiation`为0.0

### `PlayerAgent`

这是一个基类(base class)，应当被继承，并且实现指定功能，类似于其他语言中的协议(protocol)：

```python
class PlayerAgent:
    def step(self, puzzle):
        raise NotImplementedError
```

学生实现功能时，应当继承此类，并且提供方法`step`。
该函数应当接收一个参数，运行时会被传入一个`Treasure`对象。

该函数在每次轮到人物移动时会被调用，应当返回一个坐标，代表下一步移动的位置。

示例：

```python
class RightAgent(PlayerAgent):
    def step(self, puzzle):
        position = puzzle.player  # 获取当前游戏中人物位置

        new_position = position[0] + 1, position[1]
        # 向右移动一个格子

        return new_position  # 返回新位置
```

### `TreasurePlay`

该类提供一个构造函数: `TreasurePlay(seed=1234)`

一旦TreasurePlay的实例创造完成，立即启动一个游戏窗口。使用W/A/S/D控制人物（蓝色小方块）在地图中移动。

该类仅用于帮助学生熟悉地图规则。

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

### `clear()`

```python
import treasureUI
from treasureUI import PlayerAgent, PixelType, Treasure, display, clear


class DFSAgent(PlayerAgent):
    def step(self, puzzle):
        pass


for i in range(5):
    treasure = Treasure(seed=i)
    agent = DFSAgent()
    treasure.start(agent)

display()
clear()

for i in range(100, 105):
    treasure = Treasure(seed=i)
    agent = DFSAgent()
    treasure.start(agent)

display()
```

运行后，系统清空所有历史记录，重新记录新的游戏信息。

## 设置

该部分提供的功能有利于学生进行调试或展示：

### `WAIT`

该变量默认为`True`，当设置为`True`时，在每一次移动时会停顿0.1秒，有利于学生观察算法的进行。

如果被设置为`False`，系统会取消上述延迟，一般可以用于评分。

### `LEVEL`

该变量默认为`1`，默认使用第一题信息。

按照课程背景，提供三个默认关卡：

```python
_in_class_levels = {
    1: Level((0, 0), (17, 8), [100, 150], [], True),
    2: Level((0, 0), (17, 8), [100, 150], [], False),
    3: Level((0, 0), (17, 8), [], [100], True),
}
```

只要将该变量设置为1，2，3中的一个，就可以使用教学需要的关卡。

若把该变量设置为`Level`类型，则会使用该变量携带的关卡信息。

构造一个新关卡如下：

```python
Level((0, 0), (17, 8), [100], [100, 200, 150], True)
```

在所有关卡中，移动一步的成本为1。
第一个参数代表游戏开始的位置。
第二个参数代表游戏出口。
第三个参数为列表，代表“原地不动”的怪物数量和经过他们的成本。
第四个参数为列表，代表“相对智能”的怪物数量和经过他们的成本。
第五个参数为布尔值，代表怪物对于**Agent**是否可见，即影响`get_mobs_info`的表现。

### 如何调整设置

```python
import treasureUI
from treasureUI import Level

treasureUI.WAIT = False
treasureUI.LEVEL = 3
treasureUI.LEVEL = Level((0, 0), (17, 8), [], [100, 100, 100])
```
