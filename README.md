# Aeroplane Chess (飞行棋) - Python Pygame Implementation

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

这是一个基于 Python 和 Pygame 开发的经典飞行棋游戏。支持人机对战，具备完整的游戏规则（起飞、跳跃、空投、击退等）以及智能 AI 决策系统。

## ✨ 项目亮点
- **核心逻辑完备**：严格遵循传统飞行棋规则，包括掷 6 起飞、同色跳跃、快捷航道、终点精确走位。
- **启发式 AI**：内置贪婪策略 AI，能够根据棋局动态做出决策（优先起飞、优先击退对手、进度最优）。
- **平滑渲染**：使用高阶坐标映射技术实现平滑的格点定位，并加入高亮脉冲、UI 实时反馈等视觉效果。
- **跨平台兼容**：自动识别 Windows/Linux 系统中文字体，解决经典 Pygame 中文乱码问题。

## 🎮 游戏画面
*(建议此处上传一张游戏截图 `screenshot.png`)*

## 🛠️ 技术实现
- **坐标系统**：采用线性索引与像素坐标映射，通过 `densify_path` 算法预处理复杂的主轨道和终点跑道。
- **状态机管理**：通过 `wait_roll -> rolling -> choose -> animating` 状态切换，确保游戏逻辑严密。
- **UI 交互**：基于像素级碰撞检测实现棋子选择，左侧为动态博弈区，右侧为实时状态面板。

## 🚀 快速开始
1. 确保安装了 Python 3.x
2. 安装依赖：
   ```bash
   pip install pygame


   运行游戏：
Bash
python dice_game.py
🤖 AI 决策逻辑
AI 决策基于以下权重：

起飞优先级 (Highest)：只要能起飞，绝不闲置。
攻击优先级：如果移动后能将对手送回基地，优先执行。
进度优先级：选择最接近终点的飞机以最大化行军效率。
📜 许可
本项目采用 MIT License 开源。

Text
---
### 第二部分：CSDN 博文 (详细、教学向、互动性强)
**标题建议：** 
*   【Python项目】从零开始：用 Pygame 打造一款带智能 AI 的飞行棋游戏（附源码）
*   经典重温：基于 Python 状态机逻辑的智能飞行棋实现
*   如何用 500 行 Python 代码写出带 AI 决策的飞行棋？
**正文大纲：**
#### 1. 引言
小时候在纸上玩的飞行棋，能不能用 Python 还原？不仅要还原，还要给它加上“大脑”。今天分享一个基于 Pygame 开发的飞行棋项目，涵盖了坐标映射、状态机控制和启发式 AI 策略。
#### 2. 核心功能展示
*   **支持 4 人对战**：默认玩家为绿方，其余三方为智能 AI。
*   **完整规则实现**：掷 6 连续投掷、同色格子跳跃、加油站飞跃、踩踏送回基地。
*   **动态面板**：右侧实时更新各玩家状态（基地中、飞行中、已到达数）。
#### 3. 技术难点解析
*   **坐标系统的“升维”处理**
    飞行棋的棋盘不是规则的正方形，有拐角、有斜线。我设计了一个 `AXIS_MAP` 坐标映射表，配合 `densify_closed_path` 函数，将原本杂乱的网格坐标转化为一维的 `progress` 进度值，大大简化了碰撞和移动判断。
    
*   **AI 决策大脑**
    为了不让 AI 显得太“笨”，我实现了一个简单的启发式评估算法：
    ```python
    def ai_choose(self, movable):
        # 1. 优先起飞
        # 2. 优先击退对手 (模拟移动后的坐标碰撞)
        # 3. 优先移动进度最前的飞机
跨平台字体解决方案 Pygame 初学者经常遇到中文乱码。代码中通过扫描系统路径（Windows 的 msyh.ttc 或 Linux 的 NotoSans），自动匹配可用的中文字体。
4. 代码实现要点
(此处可以插入 1-2 段关键代码，比如执行移动逻辑 execute_move 或 绘图主循环)

5. 如何运行
只需安装 pygame 库，直接运行 dice_game.py 即可。
