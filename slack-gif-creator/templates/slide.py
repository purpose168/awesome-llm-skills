#!/usr/bin/env python3
"""
滑动动画 - 从边缘滑入元素，带有过冲/弹跳效果。

创建平滑的进入和退出动画。
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image
from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_emoji_enhanced
from core.easing import interpolate


def create_slide_animation(
    object_type: str = 'emoji',
    object_data: dict | None = None,
    num_frames: int = 30,
    direction: str = 'left',  # 'left'（左）、'right'（右）、'top'（上）、'bottom'（下）
    slide_type: str = 'in',  # 'in'（进入）、'out'（退出）、'across'（横穿）
    easing: str = 'ease_out',
    overshoot: bool = False,
    final_pos: tuple[int, int] | None = None,
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建滑动动画。

    参数：
        object_type: 'emoji'（表情符号）、'text'（文本）
        object_data: 对象配置
        num_frames: 帧数
        direction: 滑动方向
        slide_type: 滑动类型（进入/退出/横穿）
        easing: 缓动函数
        overshoot: 在末尾添加过冲/弹跳
        final_pos: 最终位置（None = 中心）
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
            object_data = {'emoji': '➡️', 'size': 100}

    if final_pos is None:
        final_pos = (frame_width // 2, frame_height // 2)

    # 根据方向计算起始和结束位置
    size = object_data.get('size', 100) if object_type == 'emoji' else 100
    margin = size

    if direction == 'left':
        start_pos = (-margin, final_pos[1])
        end_pos = final_pos if slide_type == 'in' else (frame_width + margin, final_pos[1])
    elif direction == 'right':
        start_pos = (frame_width + margin, final_pos[1])
        end_pos = final_pos if slide_type == 'in' else (-margin, final_pos[1])
    elif direction == 'top':
        start_pos = (final_pos[0], -margin)
        end_pos = final_pos if slide_type == 'in' else (final_pos[0], frame_height + margin)
    elif direction == 'bottom':
        start_pos = (final_pos[0], frame_height + margin)
        end_pos = final_pos if slide_type == 'in' else (final_pos[0], -margin)
    else:
        start_pos = (-margin, final_pos[1])
        end_pos = final_pos

    # 对于'out'类型，交换起始和结束位置
    if slide_type == 'out':
        start_pos, end_pos = final_pos, end_pos
    elif slide_type == 'across':
        # 全程滑动
        if direction == 'left':
            start_pos = (-margin, final_pos[1])
            end_pos = (frame_width + margin, final_pos[1])
        elif direction == 'right':
            start_pos = (frame_width + margin, final_pos[1])
            end_pos = (-margin, final_pos[1])
        elif direction == 'top':
            start_pos = (final_pos[0], -margin)
            end_pos = (final_pos[0], frame_height + margin)
        elif direction == 'bottom':
            start_pos = (final_pos[0], frame_height + margin)
            end_pos = (final_pos[0], -margin)

    # 如果请求，使用过冲缓动
    if overshoot and slide_type == 'in':
        easing = 'back_out'

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        # 计算当前位置
        x = int(interpolate(start_pos[0], end_pos[0], t, easing))
        y = int(interpolate(start_pos[1], end_pos[1], t, easing))

        # 绘制对象
        if object_type == 'emoji':
            size = object_data['size']
            draw_emoji_enhanced(
                frame,
                emoji=object_data['emoji'],
                position=(x - size // 2, y - size // 2),
                size=size,
                shadow=object_data.get('shadow', True)
            )

        elif object_type == 'text':
            from core.typography import draw_text_with_outline
            draw_text_with_outline(
                frame,
                text=object_data.get('text', 'SLIDE'),
                position=(x, y),
                font_size=object_data.get('font_size', 50),
                text_color=object_data.get('text_color', (0, 0, 0)),
                outline_color=object_data.get('outline_color', (255, 255, 255)),
                outline_width=3,
                centered=True
            )

        frames.append(frame)

    return frames


def create_multi_slide(
    objects: list[dict],
    num_frames: int = 30,
    stagger_delay: int = 3,
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建多个对象按顺序滑入的动画。

    参数：
        objects: 对象配置列表，包含'type'（类型）、'data'（数据）、'direction'（方向）、'final_pos'（最终位置）
        num_frames: 帧数
        stagger_delay: 每个对象开始之间的帧数
        frame_width: 帧宽度
        frame_height: 帧高度
        bg_color: 背景颜色

    返回：
        帧列表
    """
    frames = []

    for i in range(num_frames):
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        for idx, obj in enumerate(objects):
            # 计算此对象何时开始移动
            start_frame = idx * stagger_delay
            if i < start_frame:
                continue  # 对象尚未开始

            # 计算此对象的进度
            obj_frame = i - start_frame
            obj_duration = num_frames - start_frame
            if obj_duration <= 0:
                continue

            t = obj_frame / obj_duration

            # 获取对象属性
            obj_type = obj.get('type', 'emoji')
            obj_data = obj.get('data', {'emoji': '➡️', 'size': 80})
            direction = obj.get('direction', 'left')
            final_pos = obj.get('final_pos', (frame_width // 2, frame_height // 2))
            easing = obj.get('easing', 'back_out')

            # 计算位置
            size = obj_data.get('size', 80)
            margin = size

            if direction == 'left':
                start_x = -margin
                end_x = final_pos[0]
                y = final_pos[1]
            elif direction == 'right':
                start_x = frame_width + margin
                end_x = final_pos[0]
                y = final_pos[1]
            elif direction == 'top':
                x = final_pos[0]
                start_y = -margin
                end_y = final_pos[1]
            elif direction == 'bottom':
                x = final_pos[0]
                start_y = frame_height + margin
                end_y = final_pos[1]
            else:
                start_x = -margin
                end_x = final_pos[0]
                y = final_pos[1]

            # 插值位置
            if direction in ['left', 'right']:
                x = int(interpolate(start_x, end_x, t, easing))
            else:
                y = int(interpolate(start_y, end_y, t, easing))

            # 绘制对象
            if obj_type == 'emoji':
                draw_emoji_enhanced(
                    frame,
                    emoji=obj_data['emoji'],
                    position=(x - size // 2, y - size // 2),
                    size=size,
                    shadow=False
                )

        frames.append(frame)

    return frames


# 示例用法
if __name__ == '__main__':
    print("创建滑动动画...")

    builder = GIFBuilder(width=480, height=480, fps=20)

    # 示例1：从左侧滑入，带过冲
    frames = create_slide_animation(
        object_type='emoji',
        object_data={'emoji': '➡️', 'size': 100},
        num_frames=30,
        direction='left',
        slide_type='in',
        overshoot=True
    )
    builder.add_frames(frames)
    builder.save('slide_in_left.gif', num_colors=128)

    # 示例2：横穿滑动
    builder.clear()
    frames = create_slide_animation(
        object_type='emoji',
        object_data={'emoji': '🚀', 'size': 80},
        num_frames=40,
        direction='left',
        slide_type='across',
        easing='ease_in_out'
    )
    builder.add_frames(frames)
    builder.save('slide_across.gif', num_colors=128)

    # 示例3：多个对象滑入
    builder.clear()
    objects = [
        {
            'type': 'emoji',
            'data': {'emoji': '🎯', 'size': 60},
            'direction': 'left',
            'final_pos': (120, 240)
        },
        {
            'type': 'emoji',
            'data': {'emoji': '🎪', 'size': 60},
            'direction': 'right',
            'final_pos': (240, 240)
        },
        {
            'type': 'emoji',
            'data': {'emoji': '🎨', 'size': 60},
            'direction': 'top',
            'final_pos': (360, 240)
        }
    ]
    frames = create_multi_slide(objects, num_frames=50, stagger_delay=5)
    builder.add_frames(frames)
    builder.save('slide_multi.gif', num_colors=128)

    print("已创建滑动动画！")
