#!/usr/bin/env python3
"""
爆炸动画 - 将对象分解为向外飞行的碎片。

创建爆炸、破碎和粒子爆发效果。
"""

import sys
from pathlib import Path
import math
import random

sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw
import numpy as np
from core.gif_builder import GIFBuilder
from core.frame_composer import create_blank_frame, draw_emoji_enhanced
from core.visual_effects import ParticleSystem
from core.easing import interpolate


def create_explode_animation(
    object_type: str = 'emoji',
    object_data: dict | None = None,
    num_frames: int = 30,
    explode_type: str = 'burst',  # 'burst'（爆发）、'shatter'（破碎）、'dissolve'（溶解）、'implode'（内爆）
    num_pieces: int = 20,
    explosion_speed: float = 5.0,
    center_pos: tuple[int, int] = (240, 240),
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建爆炸动画。

    参数：
        object_type: 'emoji'（表情符号）、'circle'（圆形）、'text'（文本）
        object_data: 对象配置
        num_frames: 帧数
        explode_type: 爆炸类型
        num_pieces: 碎片/粒子数量
        explosion_speed: 爆炸速度
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
            object_data = {'emoji': '💣', 'size': 100}

    # 生成碎片/粒子
    pieces = []
    for _ in range(num_pieces):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(explosion_speed * 0.5, explosion_speed * 1.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.randint(3, 12)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        rotation_speed = random.uniform(-20, 20)

        pieces.append({
            'vx': vx,
            'vy': vy,
            'size': size,
            'color': color,
            'rotation': 0,
            'rotation_speed': rotation_speed
        })

    for i in range(num_frames):
        t = i / (num_frames - 1) if num_frames > 1 else 0
        frame = create_blank_frame(frame_width, frame_height, bg_color)
        draw = ImageDraw.Draw(frame)

        if explode_type == 'burst':
            # 在开始时显示对象，然后爆炸
            if t < 0.2:
                # 对象仍然完整
                scale = interpolate(1.0, 1.2, t / 0.2, 'ease_out')
                if object_type == 'emoji':
                    size = int(object_data['size'] * scale)
                    draw_emoji_enhanced(
                        frame,
                        emoji=object_data['emoji'],
                        position=(center_pos[0] - size // 2, center_pos[1] - size // 2),
                        size=size,
                        shadow=False
                    )
            else:
                # 已爆炸 - 绘制碎片
                explosion_t = (t - 0.2) / 0.8
                for piece in pieces:
                    # 更新位置
                    x = center_pos[0] + piece['vx'] * explosion_t * 50
                    y = center_pos[1] + piece['vy'] * explosion_t * 50 + 0.5 * 300 * explosion_t ** 2  # 重力

                    # 淡出
                    alpha = 1.0 - explosion_t
                    if alpha > 0:
                        color = tuple(int(c * alpha) for c in piece['color'])
                        size = int(piece['size'] * (1 - explosion_t * 0.5))

                        draw.ellipse(
                            [x - size, y - size, x + size, y + size],
                            fill=color
                        )

        elif explode_type == 'shatter':
            # 分解为几何碎片
            if t < 0.15:
                # 对象完整
                if object_type == 'emoji':
                    draw_emoji_enhanced(
                        frame,
                        emoji=object_data['emoji'],
                        position=(center_pos[0] - object_data['size'] // 2,
                                center_pos[1] - object_data['size'] // 2),
                        size=object_data['size'],
                        shadow=False
                    )
            else:
                # 已破碎
                shatter_t = (t - 0.15) / 0.85

                # 绘制三角形碎片
                for piece in pieces[:min(10, len(pieces))]:
                    x = center_pos[0] + piece['vx'] * shatter_t * 30
                    y = center_pos[1] + piece['vy'] * shatter_t * 30 + 0.5 * 200 * shatter_t ** 2

                    # 更新旋转
                    rotation = piece['rotation_speed'] * shatter_t * 100

                    # 绘制三角形碎片
                    shard_size = piece['size'] * 2
                    points = []
                    for j in range(3):
                        angle = (rotation + j * 120) * math.pi / 180
                        px = x + shard_size * math.cos(angle)
                        py = y + shard_size * math.sin(angle)
                        points.append((px, py))

                    alpha = 1.0 - shatter_t
                    if alpha > 0:
                        color = tuple(int(c * alpha) for c in piece['color'])
                        draw.polygon(points, fill=color)

        elif explode_type == 'dissolve':
            # 溶解为粒子
            dissolve_scale = interpolate(1.0, 0.0, t, 'ease_in')

            if dissolve_scale > 0.1:
                # 绘制淡出的对象
                if object_type == 'emoji':
                    size = int(object_data['size'] * dissolve_scale)
                    size = max(12, size)

                    emoji_canvas = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
                    draw_emoji_enhanced(
                        emoji_canvas,
                        emoji=object_data['emoji'],
                        position=(center_pos[0] - size // 2, center_pos[1] - size // 2),
                        size=size,
                        shadow=False
                    )

                    # 应用不透明度
                    from templates.fade import apply_opacity
                    emoji_canvas = apply_opacity(emoji_canvas, dissolve_scale)

                    frame_rgba = frame.convert('RGBA')
                    frame = Image.alpha_composite(frame_rgba, emoji_canvas)
                    frame = frame.convert('RGB')
                    draw = ImageDraw.Draw(frame)

            # 绘制向外移动的粒子
            for piece in pieces:
                x = center_pos[0] + piece['vx'] * t * 40
                y = center_pos[1] + piece['vy'] * t * 40

                alpha = 1.0 - t
                if alpha > 0:
                    color = tuple(int(c * alpha) for c in piece['color'])
                    size = int(piece['size'] * (1 - t * 0.5))
                    draw.ellipse(
                        [x - size, y - size, x + size, y + size],
                        fill=color
                    )

        elif explode_type == 'implode':
            # 反向爆炸 - 碎片向内飞行
            if t < 0.7:
                # 碎片汇聚
                implode_t = 1.0 - (t / 0.7)
                for piece in pieces:
                    x = center_pos[0] + piece['vx'] * implode_t * 50
                    y = center_pos[1] + piece['vy'] * implode_t * 50

                    alpha = 1.0 - (1.0 - implode_t) * 0.5
                    color = tuple(int(c * alpha) for c in piece['color'])
                    size = int(piece['size'] * alpha)

                    draw.ellipse(
                        [x - size, y - size, x + size, y + size],
                        fill=color
                    )
            else:
                # 对象重新形成
                reform_t = (t - 0.7) / 0.3
                scale = interpolate(0.5, 1.0, reform_t, 'elastic_out')

                if object_type == 'emoji':
                    size = int(object_data['size'] * scale)
                    draw_emoji_enhanced(
                        frame,
                        emoji=object_data['emoji'],
                        position=(center_pos[0] - size // 2, center_pos[1] - size // 2),
                        size=size,
                        shadow=False
                    )

        frames.append(frame)

    return frames


def create_particle_burst(
    num_frames: int = 25,
    particle_count: int = 30,
    center_pos: tuple[int, int] = (240, 240),
    colors: list[tuple[int, int, int]] | None = None,
    frame_width: int = 480,
    frame_height: int = 480,
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> list[Image.Image]:
    """
    创建简单的粒子爆发效果。

    参数：
        num_frames: 帧数
        particle_count: 粒子数量
        center_pos: 爆发中心
        colors: 粒子颜色（None表示随机）
        frame_width: 帧宽度
        frame_height: 帧高度
        bg_color: 背景颜色

    返回：
        帧列表
    """
    particles = ParticleSystem()

    # 发射粒子
    if colors is None:
        from core.color_palettes import get_palette
        palette = get_palette('vibrant')
        colors = [palette['primary'], palette['secondary'], palette['accent']]

    for _ in range(particle_count):
        color = random.choice(colors)
        particles.emit(
            center_pos[0], center_pos[1],
            count=1,
            speed=random.uniform(3, 8),
            color=color,
            lifetime=random.uniform(20, 30),
            size=random.randint(3, 8),
            shape='star'
        )

    frames = []
    for _ in range(num_frames):
        frame = create_blank_frame(frame_width, frame_height, bg_color)

        particles.update()
        particles.render(frame)

        frames.append(frame)

    return frames


# 示例用法
if __name__ == '__main__':
    print("创建爆炸动画...")

    builder = GIFBuilder(width=480, height=480, fps=20)

    # 示例1：爆发
    frames = create_explode_animation(
        object_type='emoji',
        object_data={'emoji': '💣', 'size': 100},
        num_frames=30,
        explode_type='burst',
        num_pieces=25
    )
    builder.add_frames(frames)
    builder.save('explode_burst.gif', num_colors=128)

    # 示例2：破碎
    builder.clear()
    frames = create_explode_animation(
        object_type='emoji',
        object_data={'emoji': '🪟', 'size': 100},
        num_frames=30,
        explode_type='shatter',
        num_pieces=12
    )
    builder.add_frames(frames)
    builder.save('explode_shatter.gif', num_colors=128)

    # 示例3：粒子爆发
    builder.clear()
    frames = create_particle_burst(num_frames=25, particle_count=40)
    builder.add_frames(frames)
    builder.save('explode_particles.gif', num_colors=128)

    print("已创建爆炸动画！")
