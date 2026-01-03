#!/usr/bin/env python3
"""
颜色调色板 - 用于GIF的专业、和谐配色方案。

使用一致、精心设计的调色板可以使GIF看起来专业且精致，
而不是随机和业余。
"""

from typing import Optional
import colorsys


# 专业调色板 - 为GIF压缩和视觉吸引力精心挑选

VIBRANT = {
    'primary': (255, 68, 68),      # 亮红色
    'secondary': (255, 168, 0),     # 亮橙色
    'accent': (0, 168, 255),        # 亮蓝色
    'success': (68, 255, 68),       # 亮绿色
    'background': (240, 248, 255),  # 爱丽丝蓝
    'text': (30, 30, 30),           # 接近黑色
    'text_light': (255, 255, 255),  # 白色
}

PASTEL = {
    'primary': (255, 179, 186),     # 柔和粉色
    'secondary': (255, 223, 186),   # 柔和桃色
    'accent': (186, 225, 255),      # 柔和蓝色
    'success': (186, 255, 201),     # 柔和绿色
    'background': (255, 250, 240),  # 花卉白
    'text': (80, 80, 80),           # 深灰色
    'text_light': (255, 255, 255),  # 白色
}

DARK = {
    'primary': (255, 100, 100),     # 柔和红色
    'secondary': (100, 200, 255),   # 柔和蓝色
    'accent': (255, 200, 100),      # 柔和金色
    'success': (100, 255, 150),     # 柔和绿色
    'background': (30, 30, 35),     # 接近黑色
    'text': (220, 220, 220),        # 浅灰色
    'text_light': (255, 255, 255),  # 白色
}

NEON = {
    'primary': (255, 16, 240),      # 霓虹粉色
    'secondary': (0, 255, 255),     # 青色
    'accent': (255, 255, 0),        # 黄色
    'success': (57, 255, 20),       # 霓虹绿色
    'background': (20, 20, 30),     # 深蓝黑色
    'text': (255, 255, 255),        # 白色
    'text_light': (255, 255, 255),  # 白色
}

PROFESSIONAL = {
    'primary': (0, 122, 255),       # 系统蓝色
    'secondary': (88, 86, 214),     # 系统紫色
    'accent': (255, 149, 0),        # 系统橙色
    'success': (52, 199, 89),       # 系统绿色
    'background': (255, 255, 255),  # 白色
    'text': (0, 0, 0),              # 黑色
    'text_light': (255, 255, 255),  # 白色
}

WARM = {
    'primary': (255, 107, 107),     # 珊瑚红色
    'secondary': (255, 159, 64),    # 橙色
    'accent': (255, 218, 121),      # 黄色
    'success': (106, 176, 76),      # 橄榄绿色
    'background': (255, 246, 229),  # 暖白色
    'text': (51, 51, 51),           # 炭黑色
    'text_light': (255, 255, 255),  # 白色
}

COOL = {
    'primary': (107, 185, 240),     # 天蓝色
    'secondary': (130, 202, 157),   # 薄荷色
    'accent': (162, 155, 254),      # 薰衣草色
    'success': (86, 217, 150),      # 水绿色
    'background': (240, 248, 255),  # 爱丽丝蓝
    'text': (45, 55, 72),           # 深板岩色
    'text_light': (255, 255, 255),  # 白色
}

MONOCHROME = {
    'primary': (80, 80, 80),        # 深灰色
    'secondary': (130, 130, 130),   # 中灰色
    'accent': (180, 180, 180),      # 浅灰色
    'success': (100, 100, 100),     # 灰色
    'background': (245, 245, 245),  # 近白色
    'text': (30, 30, 30),           # 接近黑色
    'text_light': (255, 255, 255),  # 白色
}

# 调色板名称映射
PALETTES = {
    'vibrant': VIBRANT,
    'pastel': PASTEL,
    'dark': DARK,
    'neon': NEON,
    'professional': PROFESSIONAL,
    'warm': WARM,
    'cool': COOL,
    'monochrome': MONOCHROME,
}


def get_palette(name: str = 'vibrant') -> dict:
    """
    按名称获取调色板。

    参数：
        name: 调色板名称（vibrant、pastel、dark、neon、professional、warm、cool、monochrome）

    返回：
        颜色角色到RGB元组的字典
    """
    return PALETTES.get(name.lower(), VIBRANT)


def get_text_color_for_background(bg_color: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    为给定背景获取最佳文本颜色（黑色或白色）。

    使用亮度计算以确保可读性。

    参数：
        bg_color: 背景RGB颜色

    返回：
        对比度好的文本颜色（黑色或白色）
    """
    # 计算相对亮度
    r, g, b = bg_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # 浅色背景返回黑色，深色背景返回白色
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)


def get_complementary_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    获取色轮上的互补（相反）颜色。

    参数：
        color: RGB颜色元组

    返回：
        互补RGB颜色
    """
    # 转换为HSV
    r, g, b = [x / 255.0 for x in color]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # 将色相旋转180度（0-1比例中的0.5）
    h_comp = (h + 0.5) % 1.0

    # 转换回RGB
    r_comp, g_comp, b_comp = colorsys.hsv_to_rgb(h_comp, s, v)
    return (int(r_comp * 255), int(g_comp * 255), int(b_comp * 255))


def lighten_color(color: tuple[int, int, int], amount: float = 0.3) -> tuple[int, int, int]:
    """
    按给定量使颜色变亮。

    参数：
        color: RGB颜色元组
        amount: 变亮的量（0.0-1.0）

    返回：
        变亮的RGB颜色
    """
    r, g, b = color
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return (r, g, b)


def darken_color(color: tuple[int, int, int], amount: float = 0.3) -> tuple[int, int, int]:
    """
    按给定量使颜色变暗。

    参数：
        color: RGB颜色元组
        amount: 变暗的量（0.0-1.0）

    返回：
        变暗的RGB颜色
    """
    r, g, b = color
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return (r, g, b)


def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int],
                 ratio: float = 0.5) -> tuple[int, int, int]:
    """
    将两种颜色混合在一起。

    参数：
        color1: 第一种RGB颜色
        color2: 第二种RGB颜色
        ratio: 混合比例（0.0 = 全部color1，1.0 = 全部color2）

    返回：
        混合的RGB颜色
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2

    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)

    return (r, g, b)


def create_gradient_colors(start_color: tuple[int, int, int],
                           end_color: tuple[int, int, int],
                           steps: int) -> list[tuple[int, int, int]]:
    """
    在两种颜色之间创建渐变色。

    参数：
        start_color: 起始RGB颜色
        end_color: 结束RGB颜色
        steps: 渐变步数

    返回：
        形成渐变的RGB颜色列表
    """
    colors = []
    for i in range(steps):
        ratio = i / (steps - 1) if steps > 1 else 0
        colors.append(blend_colors(start_color, end_color, ratio))
    return colors


# 在调色板中效果良好的冲击/强调颜色
IMPACT_COLORS = {
    'flash': (255, 255, 240),       # 亮闪光（奶油色）
    'explosion': (255, 150, 0),     # 橙色爆炸
    'electricity': (100, 200, 255), # 电蓝色
    'fire': (255, 100, 0),          # 火焰橙红色
    'success': (50, 255, 100),      # 成功绿色
    'error': (255, 50, 50),         # 错误红色
    'warning': (255, 200, 0),       # 警告黄色
    'magic': (200, 100, 255),       # 魔法紫色
}


def get_impact_color(effect_type: str = 'flash') -> tuple[int, int, int]:
    """
    获取冲击/强调效果的颜色。

    参数：
        effect_type: 效果类型（flash、explosion、electricity等）

    返回：
        效果的RGB颜色
    """
    return IMPACT_COLORS.get(effect_type, IMPACT_COLORS['flash'])


# 表情符号安全调色板（在128x128尺寸下配合32-64种颜色效果良好）
EMOJI_PALETTES = {
    'simple': [
        (255, 255, 255),  # 白色
        (0, 0, 0),        # 黑色
        (255, 100, 100),  # 红色
        (100, 255, 100),  # 绿色
        (100, 100, 255),  # 蓝色
        (255, 255, 100),  # 黄色
    ],
    'vibrant_emoji': [
        (255, 255, 255),  # 白色
        (30, 30, 30),     # 黑色
        (255, 68, 68),    # 红色
        (68, 255, 68),    # 绿色
        (68, 68, 255),    # 蓝色
        (255, 200, 68),   # 金色
        (255, 68, 200),   # 粉色
        (68, 255, 200),   # 青色
    ]
}


def get_emoji_palette(name: str = 'simple') -> list[tuple[int, int, int]]:
    """
    获取针对表情符号GIF优化的有限调色板（<64KB）。

    参数：
        name: 调色板名称（simple、vibrant_emoji）

    返回：
        RGB颜色列表（6-8种颜色）
    """
    return EMOJI_PALETTES.get(name, EMOJI_PALETTES['simple'])
