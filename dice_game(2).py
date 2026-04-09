#!/usr/bin/env python3
"""飞行棋 (Aeroplane Chess) - Pygame 图形化实现"""

import pygame
import random
import sys
import os
import math

pygame.init()

# ── 常量 ──
CELL = 40
GRID = 19
BOARD_PX = CELL * GRID  # 760
PANEL_W = 260
WIN_W = BOARD_PX + PANEL_W
WIN_H = BOARD_PX
FPS = 30

DICE_SIZE = 68
PLANE_RADIUS = 16
STACK_OFFSET = 14
CLICK_RADIUS = 24
ARROW_SIZE = 8
AXIS_MAP = [0, 1, 2, 3, 4, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18]

# ── 颜色 ──
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (250, 245, 230)
GRAY = (190, 190, 190)
DARK_GRAY = (100, 100, 100)
PANEL_BG = (245, 245, 245)

PALETTE = {
    'green':  {'main': (76, 175, 80),   'dark': (56, 142, 60),  'bg': (200, 232, 201), 'light': (165, 214, 167)},
    'red':    {'main': (244, 67, 54),    'dark': (211, 47, 47),  'bg': (255, 205, 210), 'light': (239, 154, 154)},
    'blue':   {'main': (33, 150, 243),   'dark': (25, 118, 210), 'bg': (187, 222, 251), 'light': (144, 202, 249)},
    'yellow': {'main': (255, 193, 7),    'dark': (255, 160, 0),  'bg': (255, 249, 196), 'light': (255, 236, 179)},
}

PLAYER_ORDER = ['green', 'red', 'blue', 'yellow']
PLAYER_NAMES = {'green': '绿方', 'red': '红方', 'blue': '蓝方', 'yellow': '黄方'}

# ── 主跑道原始 52 格 (col, row) ──
RAW_MAIN_TRACK = [
    (0,6),(1,6),(2,6),(3,6),(4,6),(5,6),           # 0‑5   左臂上行→
    (6,5),(6,4),(6,3),(6,2),(6,1),(6,0),            # 6‑11  上臂左列↑
    (7,0),                                           # 12    上臂顶中
    (8,0),(8,1),(8,2),(8,3),(8,4),(8,5),            # 13‑18 上臂右列↓
    (9,6),(10,6),(11,6),(12,6),(13,6),(14,6),       # 19‑24 右臂上行→
    (14,7),                                          # 25    右臂右中
    (14,8),(13,8),(12,8),(11,8),(10,8),(9,8),       # 26‑31 右臂下行←
    (8,9),(8,10),(8,11),(8,12),(8,13),(8,14),       # 32‑37 下臂右列↓
    (7,14),                                          # 38    下臂底中
    (6,14),(6,13),(6,12),(6,11),(6,10),(6,9),       # 39‑44 下臂左列↑
    (5,8),(4,8),(3,8),(2,8),(1,8),(0,8),            # 45‑50 左臂下行←
    (0,7),                                           # 51    左臂左中
]

# ── 玩家原始配置 ──
RAW_CFG = {
    'green': {
        'start': 0, 'home_entry': 51,
        'home_stretch': [(1,7),(2,7),(3,7),(4,7),(5,7),(6,7)],
        'base_slots': [(1.5,1.5),(3.5,1.5),(1.5,3.5),(3.5,3.5)],
        'colored_cells': [0, 4, 8, 12],
    },
    'red': {
        'start': 13, 'home_entry': 12,
        'home_stretch': [(7,1),(7,2),(7,3),(7,4),(7,5),(7,6)],
        'base_slots': [(10.5,1.5),(12.5,1.5),(10.5,3.5),(12.5,3.5)],
        'colored_cells': [13, 17, 21, 25],
    },
    'blue': {
        'start': 26, 'home_entry': 25,
        'home_stretch': [(13,7),(12,7),(11,7),(10,7),(9,7),(8,7)],
        'base_slots': [(10.5,10.5),(12.5,10.5),(10.5,12.5),(12.5,12.5)],
        'colored_cells': [26, 30, 34, 38],
    },
    'yellow': {
        'start': 39, 'home_entry': 38,
        'home_stretch': [(7,13),(7,12),(7,11),(7,10),(7,9),(7,8)],
        'base_slots': [(1.5,10.5),(3.5,10.5),(1.5,12.5),(3.5,12.5)],
        'colored_cells': [39, 43, 47, 51],
    },
}

def expand_coord(value):
    if isinstance(value, int):
        return AXIS_MAP[value]

    left = math.floor(value)
    right = math.ceil(value)
    if left == right:
        return float(AXIS_MAP[left])

    ratio = value - left
    return AXIS_MAP[left] + (AXIS_MAP[right] - AXIS_MAP[left]) * ratio


def densify_closed_path(points):
    dense = []
    index_map = {}
    count = len(points)

    for i in range(count):
        sx, sy = points[i]
        ex, ey = points[(i + 1) % count]
        index_map[i] = len(dense)
        dense.append((sx, sy))

        dx = 0 if ex == sx else (1 if ex > sx else -1)
        dy = 0 if ey == sy else (1 if ey > sy else -1)
        x, y = sx, sy
        while (x + dx, y + dy) != (ex, ey):
            x += dx
            y += dy
            dense.append((x, y))

    return dense, index_map


def densify_open_path(points):
    dense = [points[0]]
    for i in range(len(points) - 1):
        sx, sy = points[i]
        ex, ey = points[i + 1]
        dx = 0 if ex == sx else (1 if ex > sx else -1)
        dy = 0 if ey == sy else (1 if ey > sy else -1)
        x, y = sx, sy

        while (x, y) != (ex, ey):
            x += dx
            y += dy
            dense.append((x, y))

    return dense


EXPANDED_MAIN_TRACK = [(expand_coord(col), expand_coord(row)) for col, row in RAW_MAIN_TRACK]
MAIN_TRACK, TRACK_INDEX_MAP = densify_closed_path(EXPANDED_MAIN_TRACK)
TRACK_LEN = len(MAIN_TRACK)

NUM_ORIGINAL = len(RAW_MAIN_TRACK)  # 52

CFG = {}
for color, cfg in RAW_CFG.items():
    dense_home_stretch = densify_open_path(
        [(expand_coord(col), expand_coord(row)) for col, row in cfg['home_stretch']]
    )
    orig_home_coords = [(expand_coord(col), expand_coord(row)) for col, row in cfg['home_stretch']]
    CFG[color] = {
        **cfg,
        'start': cfg['start'],                    # 原始索引 (0-51)
        'home_entry': cfg['home_entry'],           # 原始索引 (0-51)
        'home_stretch': dense_home_stretch,        # 密集坐标, 用于棋盘绘制
        'home_stretch_orig': orig_home_coords,     # 原始坐标, 用于棋子定位
        'base_slots': [(expand_coord(col), expand_coord(row)) for col, row in cfg['base_slots']],
        'colored_cells': cfg['colored_cells'],     # 原始索引
    }

ORIG_HOME_LEN = len(next(iter(RAW_CFG.values()))['home_stretch'])  # 6
FINISH_PROGRESS = NUM_ORIGINAL + ORIG_HOME_LEN

# ── 每个阵营从基地到起点的入口跑道 (19-grid 坐标) ──
ENTRY_PATHS = {
    'green':  [(2, 6), (1, 6)],     # → 起点 (0, 7)
    'red':    [(12, 2), (12, 1)],   # → 起点 (11, 0)
    'blue':   [(16, 12), (17, 12)], # → 起点 (18, 11)
    'yellow': [(6, 16), (6, 17)],   # → 起点 (7, 18)
}

# 每个阵营起点在主跑道上的坐标
START_CELLS = {}
for c in PLAYER_ORDER:
    si = TRACK_INDEX_MAP[CFG[c]['start']]
    START_CELLS[c] = MAIN_TRACK[si]

# 所有格子的颜色映射
CELL_COLOR_MAP = {}
for c in PLAYER_ORDER:
    for idx in CFG[c]['colored_cells']:
        CELL_COLOR_MAP[TRACK_INDEX_MAP[idx]] = c
    for pos in CFG[c]['home_stretch']:
        CELL_COLOR_MAP[pos] = c

# 52个原始格子在密集跑道中的索引集合
ORIGINAL_DENSE_INDICES = set(TRACK_INDEX_MAP[i] for i in range(NUM_ORIGINAL))

# ── 字体 ──
# 输入: size 像素高度。输出: pygame.font.Font，须覆盖中文；避免 SysFont：pygame 2.6 + Win 注册表偶发 int 路径会崩。
def load_font(size):
    windir = os.environ.get('WINDIR') or os.environ.get('SystemRoot') or r'C:\Windows'
    font_dir = os.path.join(windir, 'Fonts')
    paths = [
        # Windows 常见中文字体
        os.path.join(font_dir, 'msyh.ttc'),
        os.path.join(font_dir, 'msyhbd.ttc'),
        os.path.join(font_dir, 'simhei.ttf'),
        os.path.join(font_dir, 'simsun.ttc'),
        os.path.join(font_dir, 'simsunb.ttf'),
        os.path.join(font_dir, 'msyhl.ttc'),
        os.path.join(font_dir, 'Deng.ttf'),
        os.path.join(font_dir, 'Dengb.ttf'),
        # macOS
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
        # Linux
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
    ]
    for p in paths:
        if os.path.isfile(p):
            try:
                return pygame.font.Font(p, size)
            except (OSError, pygame.error):
                continue
    # 不再调用 SysFont：部分环境下 initsysfonts_win32 会 TypeError
    return pygame.font.Font(None, size)

FONT_SM = load_font(18)
FONT_MD = load_font(26)
FONT_LG = load_font(34)
FONT_XL = load_font(46)


# ── 工具函数 ──
def grid_to_px(col, row):
    return (int(col * CELL + CELL // 2), int(row * CELL + CELL // 2))

def px_to_grid(x, y):
    return (x / CELL, y / CELL)

def dist_sq(p1, p2):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2


# ── 飞机类 ──
class Plane:
    def __init__(self, color, idx):
        self.color = color
        self.idx = idx
        self.state = 'base'     # base / track / home / finished
        self.progress = 0       # 0..TRACK_LEN-1=主跑道, TRACK_LEN..FINISH_PROGRESS-1=终点跑道

    def track_index(self):
        """当前在主跑道上的绝对位置(密集索引，用于渲染和碰撞检测)"""
        if self.state == 'track':
            orig_idx = (CFG[self.color]['start'] + self.progress) % NUM_ORIGINAL
            return TRACK_INDEX_MAP[orig_idx]
        return None

    def get_pixel_pos(self):
        """返回像素坐标 (x, y)"""
        cfg = CFG[self.color]
        if self.state == 'base':
            col, row = cfg['base_slots'][self.idx]
            return grid_to_px(col, row)
        elif self.state == 'track':
            ti = self.track_index()
            col, row = MAIN_TRACK[ti]
            return grid_to_px(col, row)
        elif self.state == 'home':
            hi = self.progress - NUM_ORIGINAL
            col, row = cfg['home_stretch_orig'][hi]
            return grid_to_px(col, row)
        else:  # finished
            return grid_to_px(expand_coord(7), expand_coord(7))

    def can_move(self, dice):
        if self.state == 'base':
            return dice == 6
        elif self.state == 'track':
            return self.progress + dice <= FINISH_PROGRESS
        elif self.state == 'home':
            return self.progress + dice <= FINISH_PROGRESS
        return False


# ── 游戏主类 ──
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption('飞行棋')
        self.clock = pygame.time.Clock()

        # 飞机: 每色4架
        self.planes = {}
        for c in PLAYER_ORDER:
            self.planes[c] = [Plane(c, i) for i in range(4)]

        self.current = 0            # 当前玩家索引
        self.dice = 0               # 当前骰子值
        self.state = 'wait_roll'    # wait_roll / rolling / choose / animating / game_over
        self.roll_timer = 0
        self.roll_anim_val = 1
        self.movable = []           # 可移动的飞机列表
        self.winner = None
        self.message = '点击骰子投掷'
        self.human_player = 'green'
        self.ai_delay = 0
        self.extra_turn = False     # 掷到6额外一次

        # 骰子区域 (中心)
        self.dice_rect = pygame.Rect(
            BOARD_PX // 2 - DICE_SIZE // 2,
            BOARD_PX // 2 - DICE_SIZE // 2,
            DICE_SIZE,
            DICE_SIZE,
        )

    @property
    def cur_color(self):
        return PLAYER_ORDER[self.current]

    def is_human_turn(self):
        return self.cur_color == self.human_player

    # ── 骰子 ──
    def roll_dice(self):
        self.dice = random.randint(1, 6)
        self.state = 'rolling'
        self.roll_timer = 28  # 帧数 (约1秒动画)

    def draw_dice_face(self, surface, cx, cy, size, val, color=BLACK):
        """在指定位置画骰子面"""
        r = size // 2
        rect = pygame.Rect(cx - r, cy - r, size, size)
        pygame.draw.rect(surface, WHITE, rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, rect, 2, border_radius=8)

        dot_r = max(3, size // 10)
        off = size // 4
        positions = {
            1: [(0,0)],
            2: [(-off,-off),(off,off)],
            3: [(-off,-off),(0,0),(off,off)],
            4: [(-off,-off),(off,-off),(-off,off),(off,off)],
            5: [(-off,-off),(off,-off),(0,0),(-off,off),(off,off)],
            6: [(-off,-off),(off,-off),(-off,0),(off,0),(-off,off),(off,off)],
        }
        for dx, dy in positions.get(val, []):
            pygame.draw.circle(surface, color, (cx+dx, cy+dy), dot_r)

    # ── 绘制棋盘 ──
    def draw_board(self):
        self.screen.fill(CREAM)

        # 四个基地
        bases = [
            ('green',  0, 0),
            ('red',    13, 0),
            ('blue',   13, 13),
            ('yellow', 0, 13),
        ]
        for color, gc, gr in bases:
            x, y = gc * CELL, gr * CELL
            w = 6 * CELL
            pal = PALETTE[color]
            # 外框
            pygame.draw.rect(self.screen, pal['main'], (x, y, w, w))
            # 内部白色区域
            margin = CELL * 0.8
            inner = pygame.Rect(x + margin, y + margin, w - 2*margin, w - 2*margin)
            pygame.draw.rect(self.screen, WHITE, inner, border_radius=12)
            # 基地标签 "ready"
            txt = FONT_SM.render('ready', True, pal['dark'])
            if gr == 0:
                self.screen.blit(txt, (x + w//2 - txt.get_width()//2, y + w - 22))
            else:
                self.screen.blit(txt, (x + w//2 - txt.get_width()//2, y + 6))

        # 十字臂背景
        arm_color = (240, 235, 225)
        # 上臂
        pygame.draw.rect(self.screen, arm_color, (7*CELL, 0, 5*CELL, 7*CELL))
        # 下臂
        pygame.draw.rect(self.screen, arm_color, (7*CELL, 13*CELL, 5*CELL, 6*CELL))
        # 左臂
        pygame.draw.rect(self.screen, arm_color, (0, 7*CELL, 7*CELL, 5*CELL))
        # 右臂
        pygame.draw.rect(self.screen, arm_color, (13*CELL, 7*CELL, 6*CELL, 5*CELL))
        # 中心
        pygame.draw.rect(self.screen, arm_color, (7*CELL, 7*CELL, 5*CELL, 5*CELL))

        # 入口跑道 (基地到起点的连接路)
        for color in PLAYER_ORDER:
            pal = PALETTE[color]
            entry = ENTRY_PATHS[color]
            start_col, start_row = START_CELLS[color]
            start_px = grid_to_px(start_col, start_row)

            # 画入口跑道格子
            all_pts = entry + [(start_col, start_row)]
            for ec, er in entry:
                px, py = grid_to_px(ec, er)
                pygame.draw.circle(self.screen, pal['light'], (px, py), CELL // 2 - 3)
                pygame.draw.circle(self.screen, pal['dark'], (px, py), CELL // 2 - 3, 2)

            # 画连接线
            for idx in range(len(all_pts) - 1):
                p1 = grid_to_px(*all_pts[idx])
                p2 = grid_to_px(*all_pts[idx + 1])
                pygame.draw.line(self.screen, pal['main'], p1, p2, 3)

        # 主跑道路径线 (连接所有密集格子, 显示行走路径)
        for i in range(len(MAIN_TRACK)):
            c1, r1 = MAIN_TRACK[i]
            c2, r2 = MAIN_TRACK[(i + 1) % len(MAIN_TRACK)]
            p1 = grid_to_px(c1, r1)
            p2 = grid_to_px(c2, r2)
            pygame.draw.line(self.screen, GRAY, p1, p2, 2)

        # 主跑道格子 (只画52个原始格子)
        for i, (c, r) in enumerate(MAIN_TRACK):
            if i not in ORIGINAL_DENSE_INDICES:
                continue
            px, py = grid_to_px(c, r)
            if i in CELL_COLOR_MAP:
                cc = PALETTE[CELL_COLOR_MAP[i]]['main']
                pygame.draw.circle(self.screen, cc, (px, py), CELL//2 - 3)
                pygame.draw.circle(self.screen, PALETTE[CELL_COLOR_MAP[i]]['dark'], (px, py), CELL//2 - 3, 2)
            else:
                pygame.draw.circle(self.screen, WHITE, (px, py), CELL//2 - 3)
                pygame.draw.circle(self.screen, GRAY, (px, py), CELL//2 - 3, 2)

        # 起点标记 "起"
        for color in PLAYER_ORDER:
            pal = PALETTE[color]
            sc, sr = START_CELLS[color]
            spx, spy = grid_to_px(sc, sr)
            txt = FONT_SM.render('起', True, WHITE)
            self.screen.blit(txt, (spx - txt.get_width() // 2, spy - txt.get_height() // 2))

        # 终点跑道
        for color in PLAYER_ORDER:
            pal = PALETTE[color]
            for pos in CFG[color]['home_stretch']:
                px, py = grid_to_px(*pos)
                pygame.draw.circle(self.screen, pal['light'], (px, py), CELL//2 - 3)
                pygame.draw.circle(self.screen, pal['dark'], (px, py), CELL//2 - 3, 2)
                # 箭头指示
                self._draw_arrow(px, py, color)

        # 中心终点区域
        cx, cy = grid_to_px(expand_coord(7), expand_coord(7))
        # 画四色三角形拼成的终点
        size = CELL * 1.2
        for i, color in enumerate(PLAYER_ORDER):
            angle = i * 90
            pts = self._rotated_triangle(cx, cy, size, angle)
            pygame.draw.polygon(self.screen, PALETTE[color]['main'], pts)
            pygame.draw.polygon(self.screen, PALETTE[color]['dark'], pts, 2)

        # 骰子
        dcx, dcy = self.dice_rect.center
        if self.state == 'rolling':
            self.draw_dice_face(self.screen, dcx, dcy, DICE_SIZE, self.roll_anim_val)
        elif self.dice > 0:
            self.draw_dice_face(self.screen, dcx, dcy, DICE_SIZE, self.dice)
        else:
            self.draw_dice_face(self.screen, dcx, dcy, DICE_SIZE, 1, GRAY)

        # 骰子提示文字
        if self.state == 'wait_roll':
            txt = FONT_SM.render('请投骰', True, (220, 50, 50))
            self.screen.blit(txt, (dcx - txt.get_width()//2, dcy - (DICE_SIZE // 2 + 20)))

    def _draw_arrow(self, px, py, color):
        """在终点跑道格子上画小三角箭头"""
        cfg = CFG[color]
        hs = cfg['home_stretch']
        if len(hs) < 2:
            return
        # 箭头方向: 指向终点
        dx = hs[-1][0] - hs[0][0]
        dy = hs[-1][1] - hs[0][1]
        length = max(abs(dx), abs(dy))
        if length == 0:
            return
        dx, dy = dx / length, dy / length
        sz = ARROW_SIZE
        tip = (int(px + dx * sz), int(py + dy * sz))
        left = (int(px - dx * sz - dy * sz * 0.6), int(py - dy * sz + dx * sz * 0.6))
        right = (int(px - dx * sz + dy * sz * 0.6), int(py - dy * sz - dx * sz * 0.6))
        pygame.draw.polygon(self.screen, PALETTE[color]['dark'], [tip, left, right])

    def _rotated_triangle(self, cx, cy, size, angle_deg):
        rad = math.radians(angle_deg)
        pts = []
        pts.append((cx, cy))  # center point
        for a in [rad - math.radians(45), rad + math.radians(45)]:
            pts.append((cx + math.cos(a) * size, cy + math.sin(a) * size))
        return pts

    # ── 绘制飞机 ──
    def draw_planes(self):
        # 收集同位置的飞机用于偏移
        pos_map = {}
        all_planes = []
        for c in PLAYER_ORDER:
            for p in self.planes[c]:
                px, py = p.get_pixel_pos()
                key = (px, py)
                if key not in pos_map:
                    pos_map[key] = []
                pos_map[key].append(p)
                all_planes.append(p)

        for key, group in pos_map.items():
            bx, by = key
            offsets = self._get_offsets(len(group))
            for i, plane in enumerate(group):
                ox, oy = offsets[i]
                x, y = bx + ox, by + oy
                self._draw_single_plane(x, y, plane)

    def _get_offsets(self, n):
        if n == 1:
            return [(0, 0)]
        elif n == 2:
            return [(-STACK_OFFSET, 0), (STACK_OFFSET, 0)]
        elif n == 3:
            return [(-STACK_OFFSET, -5), (STACK_OFFSET, -5), (0, STACK_OFFSET)]
        else:
            return [
                (-STACK_OFFSET, -STACK_OFFSET),
                (STACK_OFFSET, -STACK_OFFSET),
                (-STACK_OFFSET, STACK_OFFSET),
                (STACK_OFFSET, STACK_OFFSET),
            ]

    def _draw_single_plane(self, x, y, plane):
        pal = PALETTE[plane.color]
        r = PLANE_RADIUS
        highlight = plane in self.movable and self.state == 'choose'

        # 高亮脉冲效果
        if highlight:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.5 + 0.5
            glow_r = int(r + 4 + pulse * 4)
            glow_color = (*pal['main'][:3],)
            pygame.draw.circle(self.screen, (255, 255, 200), (x, y), glow_r)
            pygame.draw.circle(self.screen, glow_color, (x, y), glow_r, 3)

        # 主体
        pygame.draw.circle(self.screen, pal['main'], (x, y), r)
        pygame.draw.circle(self.screen, pal['dark'], (x, y), r, 2)

        # 飞机图标 (简化为白色 ✈ 形状)
        # 机身
        pygame.draw.line(self.screen, WHITE, (x, y - 9), (x, y + 9), 3)
        # 主翼
        pygame.draw.line(self.screen, WHITE, (x - 8, y), (x + 8, y), 3)
        # 尾翼
        pygame.draw.line(self.screen, WHITE, (x - 5, y + 7), (x + 5, y + 7), 2)

    # ── 信息面板 ──
    def draw_panel(self):
        px = BOARD_PX
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, PANEL_W, WIN_H))
        pygame.draw.line(self.screen, GRAY, (px, 0), (px, WIN_H), 2)

        y = 20
        title = FONT_LG.render('飞行棋', True, BLACK)
        self.screen.blit(title, (px + PANEL_W//2 - title.get_width()//2, y))
        y += 50

        # 当前玩家
        cur = self.cur_color
        pal = PALETTE[cur]
        name = PLAYER_NAMES[cur]
        label = FONT_MD.render(f'当前: {name}', True, pal['dark'])
        self.screen.blit(label, (px + 15, y))
        y += 35

        # 骰子值
        if self.dice > 0:
            dtxt = FONT_MD.render(f'骰子: {self.dice}', True, BLACK)
            self.screen.blit(dtxt, (px + 15, y))
        y += 35

        # 消息
        msg = FONT_SM.render(self.message, True, DARK_GRAY)
        self.screen.blit(msg, (px + 15, y))
        y += 40

        # 各玩家状态
        pygame.draw.line(self.screen, GRAY, (px + 10, y), (px + PANEL_W - 10, y))
        y += 10
        for c in PLAYER_ORDER:
            pal = PALETTE[c]
            finished = sum(1 for p in self.planes[c] if p.state == 'finished')
            on_track = sum(1 for p in self.planes[c] if p.state in ('track', 'home'))
            in_base = sum(1 for p in self.planes[c] if p.state == 'base')
            # 颜色标记
            pygame.draw.circle(self.screen, pal['main'], (px + 25, y + 12), 8)
            txt = FONT_SM.render(f'{PLAYER_NAMES[c]}  基地:{in_base}  飞行:{on_track}  到达:{finished}', True, BLACK)
            self.screen.blit(txt, (px + 40, y + 3))
            if c == self.cur_color:
                pygame.draw.rect(self.screen, pal['main'], (px + 5, y, 3, 24))
            y += 30

        # 规则提示
        y += 20
        pygame.draw.line(self.screen, GRAY, (px + 10, y), (px + PANEL_W - 10, y))
        y += 10
        rules = [
            '※ 规则提示:',
            '1. 点击骰子投掷',
            '2. 掷6起飞/额外一次',
            '3. 四架到终点获胜',
            '4. 落在同色格跳4格',
            '5. 踩到对手送回基地',
            '',
            f'你是: {PLAYER_NAMES[self.human_player]}',
        ]
        for line in rules:
            txt = FONT_SM.render(line, True, DARK_GRAY)
            self.screen.blit(txt, (px + 15, y))
            y += 22

        # 胜利信息
        if self.winner:
            y = WIN_H - 60
            wtxt = FONT_LG.render(f'{PLAYER_NAMES[self.winner]} 获胜!', True, PALETTE[self.winner]['dark'])
            self.screen.blit(wtxt, (px + PANEL_W//2 - wtxt.get_width()//2, y))

    # ── 游戏逻辑 ──
    def get_movable(self, color, dice):
        result = []
        for p in self.planes[color]:
            if p.can_move(dice):
                result.append(p)
        return result

    def execute_move(self, plane, dice):
        """执行飞机移动, 处理特殊规则"""
        cfg = CFG[plane.color]

        if plane.state == 'base':
            # 起飞到起点
            plane.state = 'track'
            plane.progress = 0
            self.message = f'{PLAYER_NAMES[plane.color]} 起飞!'
        elif plane.state in ('track', 'home'):
            plane.progress += dice
            if plane.progress >= FINISH_PROGRESS:
                plane.state = 'finished'
                plane.progress = FINISH_PROGRESS
                self.message = f'{PLAYER_NAMES[plane.color]} 一架到达终点!'
            elif plane.progress >= NUM_ORIGINAL:
                plane.state = 'home'
                self.message = f'{PLAYER_NAMES[plane.color]} 进入终点跑道'
            else:
                plane.state = 'track'
                # 当前原始索引
                orig_idx = (cfg['start'] + plane.progress) % NUM_ORIGINAL
                # 同色跳跃
                if orig_idx in cfg['colored_cells']:
                    idx_in_list = cfg['colored_cells'].index(orig_idx)
                    if idx_in_list < len(cfg['colored_cells']) - 1:
                        next_ci = cfg['colored_cells'][idx_in_list + 1]
                        jump_steps = (next_ci - orig_idx) % NUM_ORIGINAL
                        plane.progress += jump_steps
                        self.message = f'{PLAYER_NAMES[plane.color]} 同色跳跃!'
                        if plane.progress >= NUM_ORIGINAL:
                            if plane.progress >= FINISH_PROGRESS:
                                plane.state = 'finished'
                                plane.progress = FINISH_PROGRESS
                            else:
                                plane.state = 'home'

        # 碰撞检测: 送回对手基地
        if plane.state == 'track':
            ti = plane.track_index()
            for other_color in PLAYER_ORDER:
                if other_color == plane.color:
                    continue
                for op in self.planes[other_color]:
                    if op.state == 'track' and op.track_index() == ti:
                        op.state = 'base'
                        op.progress = 0
                        self.message = f'{PLAYER_NAMES[plane.color]} 击退了 {PLAYER_NAMES[other_color]}!'

    def check_winner(self):
        for c in PLAYER_ORDER:
            if all(p.state == 'finished' for p in self.planes[c]):
                return c
        return None

    def next_turn(self):
        if self.extra_turn:
            self.extra_turn = False
            self.state = 'wait_roll'
            self.message = f'{PLAYER_NAMES[self.cur_color]} 再投一次!'
        else:
            self.current = (self.current + 1) % 4
            self.state = 'wait_roll'
            self.message = f'{PLAYER_NAMES[self.cur_color]} 的回合'
        self.dice = 0
        self.movable = []

    def ai_choose(self, movable):
        """AI 选择策略"""
        # 优先起飞
        for p in movable:
            if p.state == 'base':
                return p
        # 优先能击退对手的
        for p in movable:
            if p.state == 'track':
                # 模拟移动看看能不能踩人
                new_prog = p.progress + self.dice
                if new_prog < NUM_ORIGINAL:
                    new_orig = (CFG[p.color]['start'] + new_prog) % NUM_ORIGINAL
                    new_ti = TRACK_INDEX_MAP[new_orig]
                    for oc in PLAYER_ORDER:
                        if oc == p.color:
                            continue
                        for op in self.planes[oc]:
                            if op.state == 'track' and op.track_index() == new_ti:
                                return p
        # 优先最接近终点的
        best = max(movable, key=lambda p: p.progress)
        return best

    # ── 事件处理 ──
    def handle_click(self, pos):
        mx, my = pos
        if mx >= BOARD_PX:
            return  # 点击了面板区域

        if self.state == 'wait_roll' and self.is_human_turn():
            # 点击骰子区域投掷
            if self.dice_rect.collidepoint(mx, my):
                self.roll_dice()
                return

        if self.state == 'choose' and self.is_human_turn():
            # 点击飞机选择
            for p in self.movable:
                px, py = p.get_pixel_pos()
                if dist_sq((mx, my), (px, py)) < CLICK_RADIUS * CLICK_RADIUS:
                    self.execute_move(p, self.dice)
                    w = self.check_winner()
                    if w:
                        self.winner = w
                        self.state = 'game_over'
                        self.message = f'{PLAYER_NAMES[w]} 获胜!'
                    else:
                        self.next_turn()
                    return

    # ── 主循环 ──
    def update(self):
        if self.state == 'game_over':
            return

        # 骰子动画
        if self.state == 'rolling':
            self.roll_anim_val = random.randint(1, 6)
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.roll_anim_val = self.dice
                # 投到6 额外一次
                self.extra_turn = (self.dice == 6)
                # 检查可移动飞机
                self.movable = self.get_movable(self.cur_color, self.dice)
                if not self.movable:
                    self.message = f'{PLAYER_NAMES[self.cur_color]} 无法移动'
                    self.ai_delay = FPS * 2  # 延迟后换人 (约2秒)
                    self.state = 'no_move_wait'
                elif len(self.movable) == 1 and not self.is_human_turn():
                    # AI 只有一架可动
                    self.execute_move(self.movable[0], self.dice)
                    w = self.check_winner()
                    if w:
                        self.winner = w
                        self.state = 'game_over'
                        self.message = f'{PLAYER_NAMES[w]} 获胜!'
                    else:
                        self.ai_delay = FPS
                        self.state = 'ai_wait'
                elif len(self.movable) == 1 and self.is_human_turn():
                    # 人类只有一架，自动移动
                    self.execute_move(self.movable[0], self.dice)
                    w = self.check_winner()
                    if w:
                        self.winner = w
                        self.state = 'game_over'
                        self.message = f'{PLAYER_NAMES[w]} 获胜!'
                    else:
                        self.next_turn()
                else:
                    if self.is_human_turn():
                        self.state = 'choose'
                        self.message = '点击要移动的飞机'
                    else:
                        # AI 选择
                        chosen = self.ai_choose(self.movable)
                        self.execute_move(chosen, self.dice)
                        w = self.check_winner()
                        if w:
                            self.winner = w
                            self.state = 'game_over'
                            self.message = f'{PLAYER_NAMES[w]} 获胜!'
                        else:
                            self.ai_delay = FPS
                            self.state = 'ai_wait'

        # 等待延迟后进入下一回合
        if self.state in ('ai_wait', 'no_move_wait'):
            self.ai_delay -= 1
            if self.ai_delay <= 0:
                self.next_turn()

        # AI 自动投骰
        if self.state == 'wait_roll' and not self.is_human_turn():
            self.ai_delay = FPS
            self.state = 'ai_pre_roll'

        if self.state == 'ai_pre_roll':
            self.ai_delay -= 1
            if self.ai_delay <= 0:
                self.roll_dice()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.state == 'game_over':
                        self.__init__()  # 重新开始

            self.update()
            self.draw_board()
            self.draw_planes()
            self.draw_panel()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
