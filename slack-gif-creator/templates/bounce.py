#!/usr/bin/env python3
"""
弹跳动画模板 - 为对象创建弹跳运动。

使用此功能使对象上下弹跳或水平弹跳，具有逼真的物理效果。
"""

import sys
from pathlib import Path

# 将父目录添加到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_circle, draw_emoji
from core.easing import ease_out_bounce, interpolate


def create_bounce_animation(
    object_type: str = 'circle',
    object_data: dict = None,
    num_frames: int = 30,
    bounce_height: int = 150,
    ground_y: int = 350,
    start_x: int = 240,
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list:
    """
    创建弹跳动画的帧。

    参数：
        object_type: 'circle'（圆形）、'emoji'（表情符号）或'custom'（自定义）
        object_data: 对象数据（例如，{'radius': 30, 'color': (255, 0, 0)}）
        num_frames: 动画中的帧数
        bounce_height: 弹跳的最大高度
        ground_y: 地面的Y位置
        start_x: X位置（如果水平移动则为起始X）
        frame_width: 帧宽度
        frame_height: 帧高度
        bg_color: 背景颜色

    返回：
        帧列表
    """
    frames = []

    # 默认对象数据
    if object_data is None:
        if object_type == 'circle':
            object_data = {'radius': 30, 'color': (255, 100, 100)}
        elif object_type == 'emoji':
            object_data = {'emoji': '⚽', 'size': 60}

    for i in range(num_frames):
        # 创建空白帧
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        # 计算进度（0.0到1.0）
        t = i / (num_frames - 1) if num_frames > 1 else 0

        # 使用弹跳缓动计算Y位置
        y = ground_y - int(ease_out_bounce(t) * bounce_height)

        # 绘制对象
        if object_type == 'circle':
            draw_circle(
                frame,
                center=(start_x, y),
                radius=object_data['radius'],
                fill_color=object_data['color']
            )
        elif object_type == 'emoji':
            draw_emoji(
                frame,
                emoji=object_data['emoji'],
                position=(start_x - object_data['size'] // 2, y - object_data['size'] // 2),
                size=object_data['size']
            )

        frames.append(frame)

    return frames


# 示例用法
if __name__ == '__main__':
    print("创建弹跳球GIF...")

    # 创建GIF构建器
    builder = GIFBuilder(width=480, height=480, fps=20)

    # 生成弹跳动画
    frames = create_bounce_animation(
        object_type='circle',
        object_data={'radius': 40, 'color': (255, 100, 100)},
        num_frames=40,
        bounce_height=200
    )

    # 将帧添加到构建器
    builder.add_frames(frames)

    # 保存GIF
    builder.save('bounce_test.gif', num_colors=64)
