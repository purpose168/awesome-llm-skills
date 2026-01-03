#!/usr/bin/env python3
"""
从PowerPoint演示文稿中提取结构化文本内容。

该模块提供以下功能：
- 从PowerPoint形状中提取所有文本内容
- 保留段落格式（对齐方式、项目符号、字体、间距）
- 递归处理嵌套的GroupShapes，并计算正确的绝对位置
- 按幻灯片上的视觉位置对形状进行排序
- 过滤掉幻灯片编号和非内容占位符
- 导出为JSON格式的清晰结构化数据

类：
    ParagraphData: 表示带有格式的文本段落
    ShapeData: 表示带有位置和文本内容的形状

主要函数：
    extract_text_inventory: 从演示文稿中提取所有文本
    save_inventory: 将提取的数据保存到JSON

用法：
    python inventory.py input.pptx output.json
"""

import argparse
import json
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.shapes.base import BaseShape

# 类型别名，使函数签名更简洁
JsonValue = Union[str, int, float, bool, None]
ParagraphDict = Dict[str, JsonValue]
ShapeDict = Dict[
    str, Union[str, float, bool, List[ParagraphDict], List[str], Dict[str, Any], None]
]
InventoryData = Dict[
    str, Dict[str, "ShapeData"]
]  # 幻灯片ID到{形状ID->ShapeData}的映射字典
InventoryDict = Dict[str, Dict[str, ShapeDict]]  # 可序列化为JSON的目录数据


def main():
    """命令行使用的主入口点。"""
    parser = argparse.ArgumentParser(
        description="从PowerPoint中提取文本目录，支持GroupShape的正确处理。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python inventory.py presentation.pptx inventory.json
    提取文本目录，并为分组形状计算正确的绝对位置

  python inventory.py presentation.pptx inventory.json --issues-only
    仅提取有文本溢出或重叠问题的文本形状

输出的JSON包含：
  - 按幻灯片和形状组织的所有文本内容
  - 组内形状的正确绝对位置
  - 以英寸为单位的视觉位置和大小
  - 段落属性和格式
  - 问题检测：文本溢出和形状重叠
        """,
    )

    parser.add_argument("input", help="输入PowerPoint文件 (.pptx)")
    parser.add_argument("output", help="输出JSON格式的目录文件")
    parser.add_argument(
        "--issues-only",
        action="store_true",
        help="只包含有文本溢出或重叠问题的文本形状",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 找不到输入文件: {args.input}")
        sys.exit(1)

    if not input_path.suffix.lower() == ".pptx":
        print("错误: 输入文件必须是PowerPoint文件 (.pptx)")
        sys.exit(1)

    try:
        print(f"正在从 {args.input} 提取文本目录")
        if args.issues_only:
            print(
                "仅包含有问题的文本形状（溢出/重叠）"
            )
        inventory = extract_text_inventory(input_path, issues_only=args.issues_only)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_inventory(inventory, output_path)

        print(f"输出已保存到: {args.output}")

        # Report statistics
        total_slides = len(inventory)
        total_shapes = sum(len(shapes) for shapes in inventory.values())
        if args.issues_only:
            if total_shapes > 0:
                print(
                    f"在 {total_slides} 张幻灯片中发现 {total_shapes} 个有问题的文本元素"
                )
            else:
                print("未发现任何问题")
        else:
            print(
                f"在 {total_slides} 张幻灯片中发现 {total_shapes} 个文本元素"
            )

    except Exception as e:
        print(f"处理演示文稿时出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


@dataclass
class ShapeWithPosition:
    """带有幻灯片上绝对位置的形状。"""

    shape: BaseShape
    absolute_left: int  # in EMUs
    absolute_top: int  # in EMUs


class ParagraphData:
    """从PowerPoint段落中提取的段落属性数据结构。"""

    def __init__(self, paragraph: Any):
        """从PowerPoint段落对象初始化。

        参数:
            paragraph: PowerPoint段落对象
        """
        self.text: str = paragraph.text.strip()
        self.bullet: bool = False
        self.level: Optional[int] = None
        self.alignment: Optional[str] = None
        self.space_before: Optional[float] = None
        self.space_after: Optional[float] = None
        self.font_name: Optional[str] = None
        self.font_size: Optional[float] = None
        self.bold: Optional[bool] = None
        self.italic: Optional[bool] = None
        self.underline: Optional[bool] = None
        self.color: Optional[str] = None
        self.theme_color: Optional[str] = None
        self.line_spacing: Optional[float] = None

        # Check for bullet formatting
        if (
            hasattr(paragraph, "_p")
            and paragraph._p is not None
            and paragraph._p.pPr is not None
        ):
            pPr = paragraph._p.pPr
            ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
            if (
                pPr.find(f"{ns}buChar") is not None
                or pPr.find(f"{ns}buAutoNum") is not None
            ):
                self.bullet = True
                if hasattr(paragraph, "level"):
                    self.level = paragraph.level

        # Add alignment if not LEFT (default)
        if hasattr(paragraph, "alignment") and paragraph.alignment is not None:
            alignment_map = {
                PP_ALIGN.CENTER: "CENTER",
                PP_ALIGN.RIGHT: "RIGHT",
                PP_ALIGN.JUSTIFY: "JUSTIFY",
            }
            if paragraph.alignment in alignment_map:
                self.alignment = alignment_map[paragraph.alignment]

        # Add spacing properties if set
        if hasattr(paragraph, "space_before") and paragraph.space_before:
            self.space_before = paragraph.space_before.pt
        if hasattr(paragraph, "space_after") and paragraph.space_after:
            self.space_after = paragraph.space_after.pt

        # Extract font properties from first run
        if paragraph.runs:
            first_run = paragraph.runs[0]
            if hasattr(first_run, "font"):
                font = first_run.font
                if font.name:
                    self.font_name = font.name
                if font.size:
                    self.font_size = font.size.pt
                if font.bold is not None:
                    self.bold = font.bold
                if font.italic is not None:
                    self.italic = font.italic
                if font.underline is not None:
                    self.underline = font.underline

                # Handle color - both RGB and theme colors
                try:
                    # Try RGB color first
                    if font.color.rgb:
                        self.color = str(font.color.rgb)
                except (AttributeError, TypeError):
                    # Fall back to theme color
                    try:
                        if font.color.theme_color:
                            self.theme_color = font.color.theme_color.name
                    except (AttributeError, TypeError):
                        pass

        # Add line spacing if set
        if hasattr(paragraph, "line_spacing") and paragraph.line_spacing is not None:
            if hasattr(paragraph.line_spacing, "pt"):
                self.line_spacing = round(paragraph.line_spacing.pt, 2)
            else:
                # Multiplier - convert to points
                font_size = self.font_size if self.font_size else 12.0
                self.line_spacing = round(paragraph.line_spacing * font_size, 2)

    def to_dict(self) -> ParagraphDict:
        """Convert to dictionary for JSON serialization, excluding None values."""
        result: ParagraphDict = {"text": self.text}

        # Add optional fields only if they have values
        if self.bullet:
            result["bullet"] = self.bullet
        if self.level is not None:
            result["level"] = self.level
        if self.alignment:
            result["alignment"] = self.alignment
        if self.space_before is not None:
            result["space_before"] = self.space_before
        if self.space_after is not None:
            result["space_after"] = self.space_after
        if self.font_name:
            result["font_name"] = self.font_name
        if self.font_size is not None:
            result["font_size"] = self.font_size
        if self.bold is not None:
            result["bold"] = self.bold
        if self.italic is not None:
            result["italic"] = self.italic
        if self.underline is not None:
            result["underline"] = self.underline
        if self.color:
            result["color"] = self.color
        if self.theme_color:
            result["theme_color"] = self.theme_color
        if self.line_spacing is not None:
            result["line_spacing"] = self.line_spacing

        return result


class ShapeData:
    """从PowerPoint形状中提取的形状属性数据结构。"""

    @staticmethod
    def emu_to_inches(emu: int) -> float:
        """将EMU（英制公制单位）转换为英寸。"""
        return emu / 914400.0

    @staticmethod
    def inches_to_pixels(inches: float, dpi: int = 96) -> int:
        """在给定DPI下将英寸转换为像素。"""
        return int(inches * dpi)

    @staticmethod
    def get_font_path(font_name: str) -> Optional[str]:
        """获取给定字体名称的字体文件路径。

        参数:
            font_name: 字体名称（例如：'Arial'、'Calibri'）

        返回:
            字体文件的路径，如果找不到则返回None
        """
        system = platform.system()

        # Common font file variations to try
        font_variations = [
            font_name,
            font_name.lower(),
            font_name.replace(" ", ""),
            font_name.replace(" ", "-"),
        ]

        # Define font directories and extensions by platform
        if system == "Darwin":  # macOS
            font_dirs = [
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                "~/Library/Fonts/",
            ]
            extensions = [".ttf", ".otf", ".ttc", ".dfont"]
        else:  # Linux
            font_dirs = [
                "/usr/share/fonts/truetype/",
                "/usr/local/share/fonts/",
                "~/.fonts/",
            ]
            extensions = [".ttf", ".otf"]

        # Try to find the font file
        from pathlib import Path

        for font_dir in font_dirs:
            font_dir_path = Path(font_dir).expanduser()
            if not font_dir_path.exists():
                continue

            # First try exact matches
            for variant in font_variations:
                for ext in extensions:
                    font_path = font_dir_path / f"{variant}{ext}"
                    if font_path.exists():
                        return str(font_path)

            # Then try fuzzy matching - find files containing the font name
            try:
                for file_path in font_dir_path.iterdir():
                    if file_path.is_file():
                        file_name_lower = file_path.name.lower()
                        font_name_lower = font_name.lower().replace(" ", "")
                        if font_name_lower in file_name_lower and any(
                            file_name_lower.endswith(ext) for ext in extensions
                        ):
                            return str(file_path)
            except (OSError, PermissionError):
                continue

        return None

    @staticmethod
    def get_slide_dimensions(slide: Any) -> tuple[Optional[int], Optional[int]]:
        """从幻灯片对象获取幻灯片尺寸。

        参数:
            slide: 幻灯片对象

        返回:
            (width_emu, height_emu)元组，如果未找到则返回(None, None)
        """
        try:
            prs = slide.part.package.presentation_part.presentation
            return prs.slide_width, prs.slide_height
        except (AttributeError, TypeError):
            return None, None

    @staticmethod
    def get_default_font_size(shape: BaseShape, slide_layout: Any) -> Optional[float]:
        """从幻灯片布局中提取占位符形状的默认字体大小。

        参数:
            shape: 占位符形状
            slide_layout: 包含占位符定义的幻灯片布局

        返回:
            默认字体大小（以磅为单位），如果未找到则返回None
        """
        try:
            if not hasattr(shape, "placeholder_format"):
                return None

            shape_type = shape.placeholder_format.type  # type: ignore
            for layout_placeholder in slide_layout.placeholders:
                if layout_placeholder.placeholder_format.type == shape_type:
                    # Find first defRPr element with sz (size) attribute
                    for elem in layout_placeholder.element.iter():
                        if "defRPr" in elem.tag and (sz := elem.get("sz")):
                            return float(sz) / 100.0  # Convert EMUs to points
                    break
        except Exception:
            pass
        return None

    def __init__(
        self,
        shape: BaseShape,
        absolute_left: Optional[int] = None,
        absolute_top: Optional[int] = None,
        slide: Optional[Any] = None,
    ):
        """从PowerPoint形状对象初始化。

        参数:
            shape: PowerPoint形状对象（应预先验证）
            absolute_left: 绝对左位置（以EMU为单位，用于组中的形状）
            absolute_top: 绝对顶位置（以EMU为单位，用于组中的形状）
            slide: 可选的幻灯片对象，用于获取尺寸和布局信息
        """
        self.shape = shape  # Store reference to original shape
        self.shape_id: str = ""  # Will be set after sorting

        # Get slide dimensions from slide object
        self.slide_width_emu, self.slide_height_emu = (
            self.get_slide_dimensions(slide) if slide else (None, None)
        )

        # Get placeholder type if applicable
        self.placeholder_type: Optional[str] = None
        self.default_font_size: Optional[float] = None
        if hasattr(shape, "is_placeholder") and shape.is_placeholder:  # type: ignore
            if shape.placeholder_format and shape.placeholder_format.type:  # type: ignore
                self.placeholder_type = (
                    str(shape.placeholder_format.type).split(".")[-1].split(" ")[0]  # type: ignore
                )

                # Get default font size from layout
                if slide and hasattr(slide, "slide_layout"):
                    self.default_font_size = self.get_default_font_size(
                        shape, slide.slide_layout
                    )

        # Get position information
        # Use absolute positions if provided (for shapes in groups), otherwise use shape's position
        left_emu = (
            absolute_left
            if absolute_left is not None
            else (shape.left if hasattr(shape, "left") else 0)
        )
        top_emu = (
            absolute_top
            if absolute_top is not None
            else (shape.top if hasattr(shape, "top") else 0)
        )

        self.left: float = round(self.emu_to_inches(left_emu), 2)  # type: ignore
        self.top: float = round(self.emu_to_inches(top_emu), 2)  # type: ignore
        self.width: float = round(
            self.emu_to_inches(shape.width if hasattr(shape, "width") else 0),
            2,  # type: ignore
        )
        self.height: float = round(
            self.emu_to_inches(shape.height if hasattr(shape, "height") else 0),
            2,  # type: ignore
        )

        # Store EMU positions for overflow calculations
        self.left_emu = left_emu
        self.top_emu = top_emu
        self.width_emu = shape.width if hasattr(shape, "width") else 0
        self.height_emu = shape.height if hasattr(shape, "height") else 0

        # Calculate overflow status
        self.frame_overflow_bottom: Optional[float] = None
        self.slide_overflow_right: Optional[float] = None
        self.slide_overflow_bottom: Optional[float] = None
        self.overlapping_shapes: Dict[
            str, float
        ] = {}  # Dict of shape_id -> overlap area in sq inches
        self.warnings: List[str] = []
        self._estimate_frame_overflow()
        self._calculate_slide_overflow()
        self._detect_bullet_issues()

    @property
    def paragraphs(self) -> List[ParagraphData]:
        """Calculate paragraphs from the shape's text frame."""
        if not self.shape or not hasattr(self.shape, "text_frame"):
            return []

        paragraphs = []
        for paragraph in self.shape.text_frame.paragraphs:  # type: ignore
            if paragraph.text.strip():
                paragraphs.append(ParagraphData(paragraph))
        return paragraphs

    def _get_default_font_size(self) -> int:
        """Get default font size from theme text styles or use conservative default."""
        try:
            if not (
                hasattr(self.shape, "part") and hasattr(self.shape.part, "slide_layout")
            ):
                return 14

            slide_master = self.shape.part.slide_layout.slide_master  # type: ignore
            if not hasattr(slide_master, "element"):
                return 14

            # Determine theme style based on placeholder type
            style_name = "bodyStyle"  # Default
            if self.placeholder_type and "TITLE" in self.placeholder_type:
                style_name = "titleStyle"

            # Find font size in theme styles
            for child in slide_master.element.iter():
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag == style_name:
                    for elem in child.iter():
                        if "sz" in elem.attrib:
                            return int(elem.attrib["sz"]) // 100
        except Exception:
            pass

        return 14  # Conservative default for body text

    def _get_usable_dimensions(self, text_frame) -> Tuple[int, int]:
        """Get usable width and height in pixels after accounting for margins."""
        # Default PowerPoint margins in inches
        margins = {"top": 0.05, "bottom": 0.05, "left": 0.1, "right": 0.1}

        # Override with actual margins if set
        if hasattr(text_frame, "margin_top") and text_frame.margin_top:
            margins["top"] = self.emu_to_inches(text_frame.margin_top)
        if hasattr(text_frame, "margin_bottom") and text_frame.margin_bottom:
            margins["bottom"] = self.emu_to_inches(text_frame.margin_bottom)
        if hasattr(text_frame, "margin_left") and text_frame.margin_left:
            margins["left"] = self.emu_to_inches(text_frame.margin_left)
        if hasattr(text_frame, "margin_right") and text_frame.margin_right:
            margins["right"] = self.emu_to_inches(text_frame.margin_right)

        # Calculate usable area
        usable_width = self.width - margins["left"] - margins["right"]
        usable_height = self.height - margins["top"] - margins["bottom"]

        # Convert to pixels
        return (
            self.inches_to_pixels(usable_width),
            self.inches_to_pixels(usable_height),
        )

    def _wrap_text_line(self, line: str, max_width_px: int, draw, font) -> List[str]:
        """Wrap a single line of text to fit within max_width_px."""
        if not line:
            return [""]

        # Use textlength for efficient width calculation
        if draw.textlength(line, font=font) <= max_width_px:
            return [line]

        # Need to wrap - split into words
        wrapped = []
        words = line.split(" ")
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if draw.textlength(test_line, font=font) <= max_width_px:
                current_line = test_line
            else:
                if current_line:
                    wrapped.append(current_line)
                current_line = word

        if current_line:
            wrapped.append(current_line)

        return wrapped

    def _estimate_frame_overflow(self) -> None:
        """使用PIL文本测量估算文本是否溢出形状边界。"""
        if not self.shape or not hasattr(self.shape, "text_frame"):
            return

        text_frame = self.shape.text_frame  # type: ignore
        if not text_frame or not text_frame.paragraphs:
            return

        # Get usable dimensions after accounting for margins
        usable_width_px, usable_height_px = self._get_usable_dimensions(text_frame)
        if usable_width_px <= 0 or usable_height_px <= 0:
            return

        # Set up PIL for text measurement
        dummy_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        # Get default font size from placeholder or use conservative estimate
        default_font_size = self._get_default_font_size()

        # Calculate total height of all paragraphs
        total_height_px = 0

        for para_idx, paragraph in enumerate(text_frame.paragraphs):
            if not paragraph.text.strip():
                continue

            para_data = ParagraphData(paragraph)

            # Load font for this paragraph
            font_name = para_data.font_name or "Arial"
            font_size = int(para_data.font_size or default_font_size)

            font = None
            font_path = self.get_font_path(font_name)
            if font_path:
                try:
                    font = ImageFont.truetype(font_path, size=font_size)
                except Exception:
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()

            # Wrap all lines in this paragraph
            all_wrapped_lines = []
            for line in paragraph.text.split("\n"):
                wrapped = self._wrap_text_line(line, usable_width_px, draw, font)
                all_wrapped_lines.extend(wrapped)

            if all_wrapped_lines:
                # Calculate line height
                if para_data.line_spacing:
                    # Custom line spacing explicitly set
                    line_height_px = para_data.line_spacing * 96 / 72
                else:
                    # PowerPoint default single spacing (1.0x font size)
                    line_height_px = font_size * 96 / 72

                # Add space_before (except first paragraph)
                if para_idx > 0 and para_data.space_before:
                    total_height_px += para_data.space_before * 96 / 72

                # Add paragraph text height
                total_height_px += len(all_wrapped_lines) * line_height_px

                # Add space_after
                if para_data.space_after:
                    total_height_px += para_data.space_after * 96 / 72

        # Check for overflow (ignore negligible overflows <= 0.05")
        if total_height_px > usable_height_px:
            overflow_px = total_height_px - usable_height_px
            overflow_inches = round(overflow_px / 96.0, 2)
            if overflow_inches > 0.05:  # Only report significant overflows
                self.frame_overflow_bottom = overflow_inches

    def _calculate_slide_overflow(self) -> None:
        """计算形状是否溢出幻灯片边界。"""
        if self.slide_width_emu is None or self.slide_height_emu is None:
            return

        # Check right overflow (ignore negligible overflows <= 0.01")
        right_edge_emu = self.left_emu + self.width_emu
        if right_edge_emu > self.slide_width_emu:
            overflow_emu = right_edge_emu - self.slide_width_emu
            overflow_inches = round(self.emu_to_inches(overflow_emu), 2)
            if overflow_inches > 0.01:  # Only report significant overflows
                self.slide_overflow_right = overflow_inches

        # Check bottom overflow (ignore negligible overflows <= 0.01")
        bottom_edge_emu = self.top_emu + self.height_emu
        if bottom_edge_emu > self.slide_height_emu:
            overflow_emu = bottom_edge_emu - self.slide_height_emu
            overflow_inches = round(self.emu_to_inches(overflow_emu), 2)
            if overflow_inches > 0.01:  # Only report significant overflows
                self.slide_overflow_bottom = overflow_inches

    def _detect_bullet_issues(self) -> None:
        """检测段落中的项目符号格式问题。"""
        if not self.shape or not hasattr(self.shape, "text_frame"):
            return

        text_frame = self.shape.text_frame  # type: ignore
        if not text_frame or not text_frame.paragraphs:
            return

        # Common bullet symbols that indicate manual bullets
        bullet_symbols = ["•", "●", "○"]

        for paragraph in text_frame.paragraphs:
            text = paragraph.text.strip()
            # Check for manual bullet symbols
            if text and any(text.startswith(symbol + " ") for symbol in bullet_symbols):
                self.warnings.append(
                    "manual_bullet_symbol: use proper bullet formatting"
                )
                break

    @property
    def has_any_issues(self) -> bool:
        """检查形状是否有任何问题（溢出、重叠或警告）。"""
        return (
            self.frame_overflow_bottom is not None
            or self.slide_overflow_right is not None
            or self.slide_overflow_bottom is not None
            or len(self.overlapping_shapes) > 0
            or len(self.warnings) > 0
        )

    def to_dict(self) -> ShapeDict:
        """转换为字典以进行JSON序列化。"""
        result: ShapeDict = {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }

        # Add optional fields if present
        if self.placeholder_type:
            result["placeholder_type"] = self.placeholder_type

        if self.default_font_size:
            result["default_font_size"] = self.default_font_size

        # Add overflow information only if there is overflow
        overflow_data = {}

        # Add frame overflow if present
        if self.frame_overflow_bottom is not None:
            overflow_data["frame"] = {"overflow_bottom": self.frame_overflow_bottom}

        # Add slide overflow if present
        slide_overflow = {}
        if self.slide_overflow_right is not None:
            slide_overflow["overflow_right"] = self.slide_overflow_right
        if self.slide_overflow_bottom is not None:
            slide_overflow["overflow_bottom"] = self.slide_overflow_bottom
        if slide_overflow:
            overflow_data["slide"] = slide_overflow

        # Only add overflow field if there is overflow
        if overflow_data:
            result["overflow"] = overflow_data

        # Add overlap field if there are overlapping shapes
        if self.overlapping_shapes:
            result["overlap"] = {"overlapping_shapes": self.overlapping_shapes}

        # Add warnings field if there are warnings
        if self.warnings:
            result["warnings"] = self.warnings

        # Add paragraphs after placeholder_type
        result["paragraphs"] = [para.to_dict() for para in self.paragraphs]

        return result


def is_valid_shape(shape: BaseShape) -> bool:
    """检查形状是否包含有意义的文本内容。"""
    # Must have a text frame with content
    if not hasattr(shape, "text_frame") or not shape.text_frame:  # type: ignore
        return False

    text = shape.text_frame.text.strip()  # type: ignore
    if not text:
        return False

    # Skip slide numbers and numeric footers
    if hasattr(shape, "is_placeholder") and shape.is_placeholder:  # type: ignore
        if shape.placeholder_format and shape.placeholder_format.type:  # type: ignore
            placeholder_type = (
                str(shape.placeholder_format.type).split(".")[-1].split(" ")[0]  # type: ignore
            )
            if placeholder_type == "SLIDE_NUMBER":
                return False
            if placeholder_type == "FOOTER" and text.isdigit():
                return False

    return True


def collect_shapes_with_absolute_positions(
    shape: BaseShape, parent_left: int = 0, parent_top: int = 0
) -> List[ShapeWithPosition]:
    """递归收集所有带有有效文本的形状，计算绝对位置。

    对于组内的形状，它们的位置是相对于组的。
    该函数通过累积父组偏移量来计算形状在幻灯片上的绝对位置。

    参数:
        shape: 要处理的形状
        parent_left: 从父组累积的左偏移量（以EMU为单位）
        parent_top: 从父组累积的顶偏移量（以EMU为单位）

    返回:
        带有绝对位置的ShapeWithPosition对象列表
    """
    if hasattr(shape, "shapes"):  # GroupShape
        result = []
        # Get this group's position
        group_left = shape.left if hasattr(shape, "left") else 0
        group_top = shape.top if hasattr(shape, "top") else 0

        # Calculate absolute position for this group
        abs_group_left = parent_left + group_left
        abs_group_top = parent_top + group_top

        # Process children with accumulated offsets
        for child in shape.shapes:  # type: ignore
            result.extend(
                collect_shapes_with_absolute_positions(
                    child, abs_group_left, abs_group_top
                )
            )
        return result

    # Regular shape - check if it has valid text
    if is_valid_shape(shape):
        # Calculate absolute position
        shape_left = shape.left if hasattr(shape, "left") else 0
        shape_top = shape.top if hasattr(shape, "top") else 0

        return [
            ShapeWithPosition(
                shape=shape,
                absolute_left=parent_left + shape_left,
                absolute_top=parent_top + shape_top,
            )
        ]

    return []


def sort_shapes_by_position(shapes: List[ShapeData]) -> List[ShapeData]:
    """按视觉位置对形状进行排序（从上到下，从左到右）。

    垂直方向在0.5英寸内的形状被视为同一行。
    """
    if not shapes:
        return shapes

    # Sort by top position first
    shapes = sorted(shapes, key=lambda s: (s.top, s.left))

    # Group shapes by row (within 0.5 inches vertically)
    result = []
    row = [shapes[0]]
    row_top = shapes[0].top

    for shape in shapes[1:]:
        if abs(shape.top - row_top) <= 0.5:
            row.append(shape)
        else:
            # Sort current row by left position and add to result
            result.extend(sorted(row, key=lambda s: s.left))
            row = [shape]
            row_top = shape.top

    # Don't forget the last row
    result.extend(sorted(row, key=lambda s: s.left))
    return result


def calculate_overlap(
    rect1: Tuple[float, float, float, float],
    rect2: Tuple[float, float, float, float],
    tolerance: float = 0.05,
) -> Tuple[bool, float]:
    """计算两个矩形是否重叠以及重叠程度。

    参数:
        rect1: 第一个矩形的（左，上，宽，高），以英寸为单位
        rect2: 第二个矩形的（左，上，宽，高），以英寸为单位
        tolerance: 被视为重叠的最小重叠量（默认：0.05英寸）

    返回:
        (overlaps, overlap_area)元组，其中：
        - overlaps: 如果矩形重叠超过公差，则为True
        - overlap_area: 重叠区域的面积，以平方英寸为单位
    """
    left1, top1, w1, h1 = rect1
    left2, top2, w2, h2 = rect2

    # Calculate overlap dimensions
    overlap_width = min(left1 + w1, left2 + w2) - max(left1, left2)
    overlap_height = min(top1 + h1, top2 + h2) - max(top1, top2)

    # Check if there's meaningful overlap (more than tolerance)
    if overlap_width > tolerance and overlap_height > tolerance:
        # Calculate overlap area in square inches
        overlap_area = overlap_width * overlap_height
        return True, round(overlap_area, 2)

    return False, 0


def detect_overlaps(shapes: List[ShapeData]) -> None:
    """检测重叠的形状并更新它们的overlapping_shapes字典。

    此函数要求每个ShapeData对象已经设置了shape_id。
    它会就地修改形状，添加重叠区域的形状ID（以平方英寸为单位）。

    参数:
        shapes: 带有shape_id属性的ShapeData对象列表
    """
    n = len(shapes)

    # Compare each pair of shapes
    for i in range(n):
        for j in range(i + 1, n):
            shape1 = shapes[i]
            shape2 = shapes[j]

            # Ensure shape IDs are set
            assert shape1.shape_id, f"Shape at index {i} has no shape_id"
            assert shape2.shape_id, f"Shape at index {j} has no shape_id"

            rect1 = (shape1.left, shape1.top, shape1.width, shape1.height)
            rect2 = (shape2.left, shape2.top, shape2.width, shape2.height)

            overlaps, overlap_area = calculate_overlap(rect1, rect2)

            if overlaps:
                # Add shape IDs with overlap area in square inches
                shape1.overlapping_shapes[shape2.shape_id] = overlap_area
                shape2.overlapping_shapes[shape1.shape_id] = overlap_area


def extract_text_inventory(
    pptx_path: Path, prs: Optional[Any] = None, issues_only: bool = False
) -> InventoryData:
    """从PowerPoint演示文稿的所有幻灯片中提取文本内容。

    参数:
        pptx_path: PowerPoint文件的路径
        prs: 可选的Presentation对象。如果未提供，将从pptx_path加载。
        issues_only: 如果为True，仅包含有溢出或重叠问题的形状

    返回嵌套字典：{slide-N: {shape-N: ShapeData}}
    形状按视觉位置（从上到下，从左到右）排序。
    ShapeData对象包含完整的形状信息，可以使用to_dict()方法转换为字典以进行JSON序列化。
    """
    if prs is None:
        prs = Presentation(str(pptx_path))
    inventory: InventoryData = {}

    for slide_idx, slide in enumerate(prs.slides):
        # Collect all valid shapes from this slide with absolute positions
        shapes_with_positions = []
        for shape in slide.shapes:  # type: ignore
            shapes_with_positions.extend(collect_shapes_with_absolute_positions(shape))

        if not shapes_with_positions:
            continue

        # Convert to ShapeData with absolute positions and slide reference
        shape_data_list = [
            ShapeData(
                swp.shape,
                swp.absolute_left,
                swp.absolute_top,
                slide,
            )
            for swp in shapes_with_positions
        ]

        # Sort by visual position and assign stable IDs in one step
        sorted_shapes = sort_shapes_by_position(shape_data_list)
        for idx, shape_data in enumerate(sorted_shapes):
            shape_data.shape_id = f"shape-{idx}"

        # Detect overlaps using the stable shape IDs
        if len(sorted_shapes) > 1:
            detect_overlaps(sorted_shapes)

        # Filter for issues only if requested (after overlap detection)
        if issues_only:
            sorted_shapes = [sd for sd in sorted_shapes if sd.has_any_issues]

        if not sorted_shapes:
            continue

        # Create slide inventory using the stable shape IDs
        inventory[f"slide-{slide_idx}"] = {
            shape_data.shape_id: shape_data for shape_data in sorted_shapes
        }

    return inventory


def get_inventory_as_dict(pptx_path: Path, issues_only: bool = False) -> InventoryDict:
    """提取文本目录并以可JSON序列化的字典形式返回。

    这是extract_text_inventory的便捷包装函数，返回字典而不是ShapeData对象，便于测试和直接JSON序列化。

    参数:
        pptx_path: PowerPoint文件的路径
        issues_only: 如果为True，仅包含有溢出或重叠问题的形状

    返回:
        所有数据都已序列化为JSON的嵌套字典
    """
    inventory = extract_text_inventory(pptx_path, issues_only=issues_only)

    # Convert ShapeData objects to dictionaries
    dict_inventory: InventoryDict = {}
    for slide_key, shapes in inventory.items():
        dict_inventory[slide_key] = {
            shape_key: shape_data.to_dict() for shape_key, shape_data in shapes.items()
        }

    return dict_inventory


def save_inventory(inventory: InventoryData, output_path: Path) -> None:
    """将目录保存到格式正确的JSON文件中。

    将ShapeData对象转换为字典以进行JSON序列化。
    """
    # Convert ShapeData objects to dictionaries
    json_inventory: InventoryDict = {}
    for slide_key, shapes in inventory.items():
        json_inventory[slide_key] = {
            shape_key: shape_data.to_dict() for shape_key, shape_data in shapes.items()
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_inventory, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
