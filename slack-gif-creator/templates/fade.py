#!/usr/bin/env python3
"""
淡入淡出动画 - 淡入、淡出和交叉淡入淡出效果。

创建用于出现、消失和过渡的平滑不透明度过渡。
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw
import numpy as np
from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_emoji_enhanced
from core.easing import interpolate


def create_fade_animation(
    object_type: str = 'emoji',
    object_data: dict | None = None,
    num_frames: int = 30,
    fade_type: str = 'in',  # 'in'（淡入）、'out'（淡出）、'in_out'（淡入淡出）、'blink'（闪烁）
    easing: str = 'ease_in_out',
    center_pos: tuple[int, int] = (240, 240),
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建淡入淡出动画。

    参数：
        object_type: 'emoji'（表情符号）、'text'（文本）、'image'（图像）
        object_data: 对象配置
        num_frames: 帧数
        fade_type: 淡入淡出效果类型
        easing: 缓动函数
        center_pos: 中心位置
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
            object_data = {'emoji': '✨', 'size': 100}

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0

        # 根据淡入淡出类型计算不透明度
        if fade_type == 'in':
            opacity = interpolate(0, 1, t, easing)
        elif fade_type == 'out':
            opacity = interpolate(1, 0, t, easing)
        elif fade_type == 'in_out':
            if t < 0.5:
                opacity = interpolate(0, 1, t * 2, easing)
            else:
                opacity = interpolate(1, 0, (t - 0.5) * 2, easing)
        elif fade_type == 'blink':
            # 快速淡出并淡入
            if t < 0.2:
                opacity = interpolate(1, 0, t / 0.2, 'ease_in')
            elif t < 0.4:
                opacity = interpolate(0, 1, (t - 0.2) / 0.2, 'ease_out')
            else:
                opacity = 1.0
        else:
            opacity = interpolate(0, 1, t, easing)

        # 创建背景
        frame_bg = create_blank_frame(frame_width, frame_height, bg_color)

        # 创建带有透明度的对象图层
        if object_type == 'emoji':
            # 为表情符号创建RGBA画布
            emoji_canvas = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
            emoji_size = object_data['size']
            draw_emoji_enhanced(
                emoji_canvas,
                emoji=object_data['emoji'],
                position=(center_pos[0] - emoji_size // 2, center_pos[1] - emoji_size // 2),
                size=emoji_size,
                shadow=object_data.get('shadow', False)
            )

            # 应用不透明度
            emoji_canvas = apply_opacity(emoji_canvas, opacity)

            # 合成到背景上
            frame_bg_rgba = frame_bg.convert('RGBA')
            frame = Image.alpha_composite(frame_bg_rgba, emoji_canvas)
            frame = frame.convert('RGB')

        elif object_type == 'text':
            from core.typography import draw_text_with_outline

            # 在单独的图层上创建文本
            text_canvas = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
            text_canvas_rgb = text_canvas.convert('RGB')
            text_canvas_rgb.paste(bg_color, (0, 0, frame_width, frame_height))

            draw_text_with_outline(
                text_canvas_rgb,
                text=object_data.get('text', 'FADE'),
                position=center_pos,
                font_size=object_data.get('font_size', 60),
                text_color=object_data.get('text_color', (0, 0, 0)),
                outline_color=object_data.get('outline_color', (255, 255, 255)),
                outline_width=3,
                centered=True
            )

            # 转换为RGBA并使背景透明
            text_canvas = text_canvas_rgb.convert('RGBA')
            data = text_canvas.getdata()
            new_data = []
            for item in data:
                if item[:3] == bg_color:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            text_canvas.putdata(new_data)

            # 应用不透明度
            text_canvas = apply_opacity(text_canvas, opacity)

            # 合成
            frame_bg_rgba = frame_bg.convert('RGBA')
            frame = Image.alpha_composite(frame_bg_rgba, text_canvas)
            frame = frame.convert('RGB')

        else:
            frame = frame_bg

        frames.append(frame)

    return frames


def apply_opacity(image: Image.Image, opacity: float) -> Image.Image:
    """
    为RGBA图像应用不透明度。

    参数：
        image: RGBA图像
        opacity: 不透明度值（0.0到1.0）

    返回：
        具有调整后不透明度的图像
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 获取alpha通道
    r, g, b, a = image.split()

    # 将alpha乘以不透明度
    a_array = np.array(a, dtype=np.float32)
    a_array = a_array * opacity
    a = Image.fromarray(a_array.astype(np.uint8))

    # 合并回去
    return Image.merge('RGBA', (r, g, b, a))


def create_crossfade(
    object1_data: dict,
    object2_data: dict,
    num_frames: int = 30,
    easing: str = 'ease_in_out',
    object_type: str = 'emoji',
    center_pos: tuple[int, int] = (240, 240),
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    在两个对象之间交叉淡入淡出。

    参数：
        object1_data: 第一个对象配置
        object2_data: 第二个对象配置
        num_frames: 帧数
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

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0

        # 计算不透明度
        opacity1 = interpolate(1, 0, t, easing)
        opacity2 = interpolate(0, 1, t, easing)

        # 创建背景
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        if object_type == 'emoji':
            # 创建第一个表情符号
            emoji1_canvas = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
            size1 = object1_data['size']
            draw_emoji_enhanced(
                emoji1_canvas,
                emoji=object1_data['emoji'],
                position=(center_pos[0] - size1 // 2, center_pos[1] - size1 // 2),
                size=size1,
                shadow=False
            )
            emoji1_canvas = apply_opacity(emoji1_canvas, opacity1)

            # 创建第二个表情符号
            emoji2_canvas = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
            size2 = object2_data['size']
            draw_emoji_enhanced(
                emoji2_canvas,
                emoji=object2_data['emoji'],
                position=(center_pos[0] - size2 // 2, center_pos[1] - size2 // 2),
                size=size2,
                shadow=False
            )
            emoji2_canvas = apply_opacity(emoji2_canvas, opacity2)

            # 合成两者
            frame_rgba = frame.convert('RGBA')
            frame_rgba = Image.alpha_composite(frame_rgba, emoji1_canvas)
            frame_rgba = Image.alpha_composite(frame_rgba, emoji2_canvas)
            frame = frame_rgba.convert('RGB')

        frames.append(frame)

    return frames


def create_fade_to_color(
    start_color: tuple[int, int, int],
    end_color: tuple[int, int, int],
    num_frames: int = 20,
    easing: str = 'linear',
    frame_width: int = 480,
    frame_height: int = 480
) -> list[Image.Image]:
    """
    从一种纯色淡入淡出到另一种纯色。

    参数：
        start_color: 起始RGB颜色
        end_color: 结束RGB颜色
        num_frames: 帧数
        easing: 缓动函数
        frame_width: 帧宽度
        frame_height: 帧高度

    返回：
        帧列表
    """
    frames = []

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0

        # 插值每个颜色通道
        r = int(interpolate(start_color[0], end_color[0], t, easing))
        g = int(interpolate(start_color[1], end_color[1], t, easing))
        b = int(interpolate(start_color[2], end_color[2], t, easing))

        color = (r, g, b)
        frame = create_blank_frame(frame_width, frame_height, color)
        frames.append(frame)

    return frames


# 示例用法
if __name__ == '__main__':
    print("创建淡入淡出动画...")

    builder = GIFBuilder(width=480, height=480, fps=20)

    # 示例1：淡入
    frames = create_fade_animation(
        object_type='emoji',
        object_data={'emoji': '✨', 'size': 120},
        num_frames=30,
        fade_type='in',
        easing='ease_out'
    )
    builder.add_frames(frames)
    builder.save('fade_in.gif', num_colors=128)

    # 示例2：交叉淡入淡出
    builder.clear()
    frames = create_crossfade(
        object1_data={'emoji': '😊', 'size': 100},
        object2_data={'emoji': '😂', 'size': 100},
        num_frames=30,
        object_type='emoji'
    )
    builder.add_frames(frames)
    builder.save('fade_crossfade.gif', num_colors=128)

    # 示例3：闪烁
    builder.clear()
    frames = create_fade_animation(
        object_type='emoji',
        object_data={'emoji': '👀', 'size': 100},
        num_frames=20,
        fade_type='blink'
    )
    builder.add_frames(frames)
    builder.save('fade_blink.gif', num_colors=128)

    print("已创建淡入淡出动画！")
