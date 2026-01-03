#!/usr/bin/env python3
"""
GIF构建器 - 用于将帧组装成针对Slack优化的GIF的核心模块。

该模块提供了从程序生成的帧创建GIF的主要接口，并自动针对Slack的要求进行优化。
"""

from pathlib import Path
from typing import Optional
import imageio.v3 as imageio
from PIL import Image
import numpy as np


class GIFBuilder:
    """用于从帧创建优化GIF的构建器。"""

    def __init__(self, width: int = 480, height: int = 480, fps: int = 15):
        """
        初始化GIF构建器。

        参数：
            width: 帧宽度（像素）
            height: 帧高度（像素）
            fps: 每秒帧数
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.frames: list[np.ndarray] = []

    def add_frame(self, frame: np.ndarray | Image.Image):
        """
        向GIF添加一帧。

        参数：
            frame: 帧作为numpy数组或PIL图像（将转换为RGB）
        """
        if isinstance(frame, Image.Image):
            frame = np.array(frame.convert('RGB'))

        # 确保帧大小正确
        if frame.shape[:2] != (self.height, self.width):
            pil_frame = Image.fromarray(frame)
            pil_frame = pil_frame.resize((self.width, self.height), Image.Resampling.LANCZOS)
            frame = np.array(pil_frame)

        self.frames.append(frame)

    def add_frames(self, frames: list[np.ndarray | Image.Image]):
        """一次添加多帧。"""
        for frame in frames:
            self.add_frame(frame)

    def optimize_colors(self, num_colors: int = 128, use_global_palette: bool = True) -> list[np.ndarray]:
        """
        使用量化减少所有帧的颜色。

        参数：
            num_colors: 目标颜色数（8-256）
            use_global_palette: 对所有帧使用单一调色板（更好的压缩）

        返回：
            颜色优化后的帧列表
        """
        optimized = []

        if use_global_palette and len(self.frames) > 1:
            # 从所有帧创建全局调色板
            # 采样帧以构建调色板
            sample_size = min(5, len(self.frames))
            sample_indices = [int(i * len(self.frames) / sample_size) for i in range(sample_size)]
            sample_frames = [self.frames[i] for i in sample_indices]

            # 将采样帧组合成单个图像以生成调色板
            # 展平每个帧以获取所有像素，然后堆叠它们
            all_pixels = np.vstack([f.reshape(-1, 3) for f in sample_frames])  # (total_pixels, 3)

            # 从像素数据创建正确形状的RGB图像
            # 我们将从所有像素创建一个大致为正方形的图像
            total_pixels = len(all_pixels)
            width = min(512, int(np.sqrt(total_pixels)))  # 合理的宽度，最大512
            height = (total_pixels + width - 1) // width  # 向上取整

            # 如有必要，填充以填充矩形
            pixels_needed = width * height
            if pixels_needed > total_pixels:
                padding = np.zeros((pixels_needed - total_pixels, 3), dtype=np.uint8)
                all_pixels = np.vstack([all_pixels, padding])

            # 重塑为正确的RGB图像格式（H, W, 3）
            img_array = all_pixels[:pixels_needed].reshape(height, width, 3).astype(np.uint8)
            combined_img = Image.fromarray(img_array, mode='RGB')

            # 生成全局调色板
            global_palette = combined_img.quantize(colors=num_colors, method=2)

            # 将全局调色板应用于所有帧
            for frame in self.frames:
                pil_frame = Image.fromarray(frame)
                quantized = pil_frame.quantize(palette=global_palette, dither=1)
                optimized.append(np.array(quantized.convert('RGB')))
        else:
            # 使用逐帧量化
            for frame in self.frames:
                pil_frame = Image.fromarray(frame)
                quantized = pil_frame.quantize(colors=num_colors, method=2, dither=1)
                optimized.append(np.array(quantized.convert('RGB')))

        return optimized

    def deduplicate_frames(self, threshold: float = 0.995) -> int:
        """
        删除重复或近乎重复的连续帧。

        参数：
            threshold: 相似度阈值（0.0-1.0）。越高越严格（0.995 = 非常相似）。

        返回：
            删除的帧数
        """
        if len(self.frames) < 2:
            return 0

        deduplicated = [self.frames[0]]
        removed_count = 0

        for i in range(1, len(self.frames)):
            # 与前一帧比较
            prev_frame = np.array(deduplicated[-1], dtype=np.float32)
            curr_frame = np.array(self.frames[i], dtype=np.float32)

            # 计算相似度（归一化）
            diff = np.abs(prev_frame - curr_frame)
            similarity = 1.0 - (np.mean(diff) / 255.0)

            # 如果足够不同则保留帧
            # 高阈值（0.995）意味着只删除真正相同的帧
            if similarity < threshold:
                deduplicated.append(self.frames[i])
            else:
                removed_count += 1

        self.frames = deduplicated
        return removed_count

    def save(self, output_path: str | Path, num_colors: int = 128,
             optimize_for_emoji: bool = False, remove_duplicates: bool = True) -> dict:
        """
        将帧保存为针对Slack优化的GIF。

        参数：
            output_path: 保存GIF的位置
            num_colors: 使用的颜色数（越少 = 文件越小）
            optimize_for_emoji: 如果为True，则优化为<64KB的表情符号大小
            remove_duplicates: 删除重复的连续帧

        返回：
            包含文件信息的字典（路径、大小、尺寸、帧数）
        """
        if not self.frames:
            raise ValueError("没有帧可保存。请先使用add_frame()添加帧。")

        output_path = Path(output_path)
        original_frame_count = len(self.frames)

        # 删除重复帧以减小文件大小
        if remove_duplicates:
            removed = self.deduplicate_frames(threshold=0.98)
            if removed > 0:
                print(f"  删除了{removed}个重复帧")

        # 如果请求，优化表情符号
        if optimize_for_emoji:
            if self.width > 128 or self.height > 128:
                print(f"  将尺寸从{self.width}x{self.height}调整为128x128以用于表情符号")
                self.width = 128
                self.height = 128
                # 调整所有帧的大小
                resized_frames = []
                for frame in self.frames:
                    pil_frame = Image.fromarray(frame)
                    pil_frame = pil_frame.resize((128, 128), Image.Resampling.LANCZOS)
                    resized_frames.append(np.array(pil_frame))
                self.frames = resized_frames
            num_colors = min(num_colors, 48)  # 对表情符号使用更激进的颜色限制

            # 对表情符号进行更激进的FPS降低
            if len(self.frames) > 12:
                print(f"  将帧数从{len(self.frames)}减少到约12以用于表情符号大小")
                # 保留每第n帧以接近12帧
                keep_every = max(1, len(self.frames) // 12)
                self.frames = [self.frames[i] for i in range(0, len(self.frames), keep_every)]

        # 使用全局调色板优化颜色
        optimized_frames = self.optimize_colors(num_colors, use_global_palette=True)

        # 计算帧持续时间（毫秒）
        frame_duration = 1000 / self.fps

        # 保存GIF
        imageio.imwrite(
            output_path,
            optimized_frames,
            duration=frame_duration,
            loop=0  # 无限循环
        )

        # 获取文件信息
        file_size_kb = output_path.stat().st_size / 1024
        file_size_mb = file_size_kb / 1024

        info = {
            'path': str(output_path),
            'size_kb': file_size_kb,
            'size_mb': file_size_mb,
            'dimensions': f'{self.width}x{self.height}',
            'frame_count': len(optimized_frames),
            'fps': self.fps,
            'duration_seconds': len(optimized_frames) / self.fps,
            'colors': num_colors
        }

        # 打印信息
        print(f"\n✓ GIF创建成功！")
        print(f"  路径：{output_path}")
        print(f"  大小：{file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")
        print(f"  尺寸：{self.width}x{self.height}")
        print(f"  帧数：{len(optimized_frames)} @ {self.fps} fps")
        print(f"  持续时间：{info['duration_seconds']:.1f}s")
        print(f"  颜色数：{num_colors}")

        # 警告
        if optimize_for_emoji and file_size_kb > 64:
            print(f"\n⚠️  警告：表情符号文件大小（{file_size_kb:.1f} KB）超过64 KB限制")
            print("   尝试：减少帧数、减少颜色或简化设计")
        elif not optimize_for_emoji and file_size_kb > 2048:
            print(f"\n⚠️  警告：文件大小（{file_size_kb:.1f} KB）对于Slack来说很大")
            print("   尝试：减少帧数、减小尺寸或减少颜色")

        return info

    def clear(self):
        """清除所有帧（对于创建多个GIF很有用）。"""
        self.frames = []
