#!/usr/bin/env python3
"""
翻转动画 - 3D风格的卡片翻转和旋转效果。

创建具有透视效果的水平翻转和垂直翻转。
"""

import sys
from pathlib import Path
import math

sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image
from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_emoji_enhanced
from core.easing import interpolate


def create_flip_animation(
    object1_data: dict,
    object2_data: dict | None = None,
    num_frames: int = 30,
    flip_axis: str = 'horizontal',  # 'horizontal'（水平）、'vertical'（垂直）
    easing: str = 'ease_in_out',
    object_type: str = 'emoji',
    center_pos: tuple[int, int] = (240, 240),
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建3D风格的翻转动画。

    参数：
        object1_data: 第一个对象（正面）
        object2_data: 第二个对象（背面，None表示与正面相同）
        num_frames: 帧数
        flip_axis: 翻转轴
        easing: 缓动函数
        object_type: 对象类型
        center_pos: 中心位置
        frame_width: 帧宽度
        frame_height: 帧高度
        bg_color: 背景颜色

    返回：
        帧列表
    """
    frames = []

    if object2_data is None:
        object2_data = object1_data

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        # 计算旋转角度（0到180度）
        angle = interpolate(0, 180, t, easing)

        # 确定哪一面可见并计算缩放
        if angle < 90:
            # 正面可见
            current_object = object1_data
            scale_factor = math.cos(math.radians(angle))
        else:
            # 背面可见
            current_object = object2_data
            scale_factor = abs(math.cos(math.radians(angle)))

        # 当边缘朝向时不绘制（非常薄）
        if scale_factor < 0.05:
            frames.append(frame)
            continue

        if object_type == 'emoji':
            size = current_object['size']

            # 在画布上创建表情符号
            canvas_size = size * 2
            emoji_canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))

            draw_emoji_enhanced(
                emoji_canvas,
                emoji=current_object['emoji'],
                position=(canvas_size // 2 - size // 2, canvas_size // 2 - size // 2),
                size=size,
                shadow=False
            )

            # 应用翻转缩放
            if flip_axis == 'horizontal':
                # 为水平翻转水平缩放
                new_width = max(1, int(canvas_size * scale_factor))
                new_height = canvas_size
            else:
                # 为垂直翻转垂直缩放
                new_width = canvas_size
                new_height = max(1, int(canvas_size * scale_factor))

            # 调整大小以模拟3D旋转
            emoji_scaled = emoji_canvas.resize((new_width, new_height), Image.LANCZOS)

            # 居中定位
            paste_x = center_pos[0] - new_width // 2
            paste_y = center_pos[1] - new_height // 2

            # 合成到帧上
            frame_rgba = frame.convert('RGBA')
            frame_rgba.paste(emoji_scaled, (paste_x, paste_y), emoji_scaled)
            frame = frame_rgba.convert('RGB')

        elif object_type == 'text':
            from core.typography import draw_text_with_outline

            # 在画布上创建文本
            text = current_object.get('text', 'FLIP')
            font_size = current_object.get('font_size', 50)

            canvas_size = max(frame_width, frame_height)
            text_canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))

            # 在RGB上绘制以进行文本渲染
            text_canvas_rgb = text_canvas.convert('RGB')
            text_canvas_rgb.paste(bg_color, (0, 0, canvas_size, canvas_size))

            draw_text_with_outline(
                text_canvas_rgb,
                text=text,
                position=(canvas_size // 2, canvas_size // 2),
                font_size=font_size,
                text_color=current_object.get('text_color', (0, 0, 0)),
                outline_color=current_object.get('outline_color', (255, 255, 255)),
                outline_width=3,
                centered=True
            )

            # 使背景透明
            text_canvas = text_canvas_rgb.convert('RGBA')
            data = text_canvas.getdata()
            new_data = []
            for item in data:
                if item[:3] == bg_color:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            text_canvas.putdata(new_data)

            # 应用翻转缩放
            if flip_axis == 'horizontal':
                new_width = max(1, int(canvas_size * scale_factor))
                new_height = canvas_size
            else:
                new_width = canvas_size
                new_height = max(1, int(canvas_size * scale_factor))

            text_scaled = text_canvas.resize((new_width, new_height), Image.LANCZOS)

            # 居中和裁剪
            if flip_axis == 'horizontal':
                left = (new_width - frame_width) // 2 if new_width > frame_width else 0
                top = (canvas_size - frame_height) // 2
                paste_x = center_pos[0] - min(new_width, frame_width) // 2
                paste_y = 0

                text_cropped = text_scaled.crop((
                    left,
                    top,
                    left + min(new_width, frame_width),
                    top + frame_height
                ))
            else:
                left = (canvas_size - frame_width) // 2
                top = (new_height - frame_height) // 2 if new_height > frame_height else 0
                paste_x = 0
                paste_y = center_pos[1] - min(new_height, frame_height) // 2

                text_cropped = text_scaled.crop((
                    left,
                    top,
                    left + frame_width,
                    top + min(new_height, frame_height)
                ))

            frame_rgba = frame.convert('RGBA')
            frame_rgba.paste(text_cropped, (paste_x, paste_y), text_cropped)
            frame = frame_rgba.convert('RGB')

        frames.append(frame)

    return frames


def create_quick_flip(
    emoji_front: str,
    emoji_back: str,
    num_frames: int = 20,
    frame_size: int = 128
) -> list[Image.Image]:
    """
    为表情符号GIF创建快速翻转。

    参数：
        emoji_front: 正面表情符号
        emoji_back: 背面表情符号
        num_frames: 帧数
        frame_size: 帧大小（正方形）

    返回：
        帧列表
    """
    return create_flip_animation(
        object1_data={'emoji': emoji_front, 'size': 80},
        object2_data={'emoji': emoji_back, 'size': 80},
        num_frames=num_frames,
        flip_axis='horizontal',
        easing='ease_in_out',
        object_type='emoji',
        center_pos=(frame_size // 2, frame_size // 2),
        frame_width=frame_size,
        frame_height=frame_size,
        bg_color=(255, 255, 255)
    )


def create_nope_flip(
    num_frames: int = 25,
    frame_width: int = 480,
    frame_height: int = 480
) -> list[Image.Image]:
    """
    创建"nope"反应翻转（像翻桌子一样）。

    参数：
        num_frames: 帧数
        frame_width: 帧宽度
        frame_height: 帧高度

    返回：
        帧列表
    """
    return create_flip_animation(
        object1_data={'text': 'NOPE', 'font_size': 80, 'text_color': (255, 50, 50)},
        object2_data={'text': 'NOPE', 'font_size': 80, 'text_color': (255, 50, 50)},
        num_frames=num_frames,
        flip_axis='horizontal',
        easing='ease_out',
        object_type='text',
        frame_width=frame_width,
        frame_height=frame_height,
        bg_color=(255, 255, 255)
    )


# 示例用法
if __name__ == '__main__':
    print("创建翻转动画...")

    builder = GIFBuilder(width=480, height=480, fps=20)

    # 示例1：表情符号翻转
    frames = create_flip_animation(
        object1_data={'emoji': '😊', 'size': 120},
        object2_data={'emoji': '😂', 'size': 120},
        num_frames=30,
        flip_axis='horizontal',
        object_type='emoji'
    )
    builder.add_frames(frames)
    builder.save('flip_emoji.gif', num_colors=128)

    # 示例2：文本翻转
    builder.clear()
    frames = create_flip_animation(
        object1_data={'text': 'YES', 'font_size': 80, 'text_color': (100, 200, 100)},
        object2_data={'text': 'NO', 'font_size': 80, 'text_color': (200, 100, 100)},
        num_frames=30,
        flip_axis='vertical',
        object_type='text'
    )
    builder.add_frames(frames)
    builder.save('flip_text.gif', num_colors=128)

    # 示例3：快速翻转（表情符号大小）
    builder = GIFBuilder(width=128, height=128, fps=15)
    frames = create_quick_flip('👍', '👎', num_frames=20)
    builder.add_frames(frames)
    builder.save('flip_quick.gif', num_colors=48, optimize_for_emoji=True)

    print("已创建翻转动画！")
