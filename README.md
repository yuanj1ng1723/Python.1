# Python.1
Python实现简易飞行棋游戏
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
