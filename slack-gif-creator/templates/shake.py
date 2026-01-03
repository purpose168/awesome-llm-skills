#!/usr/bin/env python3
"""
抖动动画模板 - 创建抖动/震动运动。

用于冲击效果、强调或紧张/兴奋的反应。
"""

import sys
import math
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_circle, draw_emoji, draw_text
from core.easing import ease_out_quad


def create_shake_animation(
    object_type: str = 'emoji',
    object_data: dict = None,
    num_frames: int = 20,
    shake_intensity: int = 15,
    center_x: int = 240,
    center_y: int = 240,
    direction: str = 'horizontal',  # 'horizontal'（水平）、'vertical'（垂直）或'both'（双向）
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list:
    """
    创建抖动动画的帧。

    参数：
        object_type: 'circle'（圆形）、'emoji'（表情符号）、'text'（文本）或'custom'（自定义）
        object_data: 对象的数据
        num_frames: 帧数
        shake_intensity: 最大抖动位移（像素）
        center_x: 中心X位置
        center_y: 中心Y位置
        direction: 'horizontal'（水平）、'vertical'（垂直）或'both'（双向）
        frame_width: 帧宽度
        frame_height: 帧高度
        bg_color: 背景颜色

    返回：
        帧列表
    """
    frames = []

    # 默认对象数据
    if object_data is None:
        if object_type == 'emoji':
            object_data = {'emoji': '😱', 'size': 80}
        elif object_type == 'text':
            object_data = {'text': 'SHAKE!', 'font_size': 50, 'color': (255, 0, 0)}

    for i in range(num_frames):
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        # 计算进度
        t = i / (num_frames - 1) if num_frames > 1 else 0

        # 随时间衰减抖动强度
        intensity = shake_intensity * (1 - ease_out_quad(t))

        # 使用正弦波计算抖动偏移以实现平滑振荡
        freq = 3  # 振荡频率
        offset_x = 0
        offset_y = 0

        if direction in ['horizontal', 'both']:
            offset_x = int(math.sin(t * freq * 2 * math.pi) * intensity)

        if direction in ['vertical', 'both']:
            offset_y = int(math.cos(t * freq * 2 * math.pi) * intensity)

        # 应用偏移
        x = center_x + offset_x
        y = center_y + offset_y

        # 绘制对象
        if object_type == 'emoji':
            draw_emoji(
                frame,
                emoji=object_data['emoji'],
                position=(x - object_data['size'] // 2, y - object_data['size'] // 2),
                size=object_data['size']
            )
        elif object_type == 'text':
            draw_text(
                frame,
                text=object_data['text'],
                position=(x, y),
                font_size=object_data['font_size'],
                color=object_data['color'],
                centered=True
            )
        elif object_type == 'circle':
            draw_circle(
                frame,
                center=(x, y),
                radius=object_data.get('radius', 30),
                fill_color=object_data.get('color', (100, 100, 255))
            )

        frames.append(frame)

    return frames


# 示例用法
if __name__ == '__main__':
    print("创建抖动GIF...")

    builder = GIFBuilder(width=480, height=480, fps=24)

    frames = create_shake_animation(
        object_type='emoji',
        object_data={'emoji': '😱', 'size': 100},
        num_frames=30,
        shake_intensity=20,
        direction='both'
    )

    builder.add_frames(frames)
    builder.save('shake_test.gif', num_colors=128)
