#!/usr/bin/env python3
"""向PowerPoint演示文稿应用文本替换。

使用方法：
    python replace.py <input.pptx> <replacements.json> <output.pptx>

替换JSON应具有inventory.py输出的结构。
除非在该形状的替换中指定了"paragraphs"，否则inventory.py识别的所有文本形状都将清除其文本。
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from inventory import InventoryData, extract_text_inventory
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Pt


def clear_paragraph_bullets(paragraph):
    """清除段落的项目符号格式。"""
    pPr = paragraph._element.get_or_add_pPr()

    # Remove existing bullet elements
    for child in list(pPr):
        if (
            child.tag.endswith("buChar")
            or child.tag.endswith("buNone")
            or child.tag.endswith("buAutoNum")
            or child.tag.endswith("buFont")
        ):
            pPr.remove(child)

    return pPr


def apply_paragraph_properties(paragraph, para_data: Dict[str, Any]):
    """向段落应用格式属性。"""
    # Get the text but don't set it on paragraph directly yet
    text = para_data.get("text", "")

    # Get or create paragraph properties
    pPr = clear_paragraph_bullets(paragraph)

    # Handle bullet formatting
    if para_data.get("bullet", False):
        level = para_data.get("level", 0)
        paragraph.level = level

        # Calculate font-proportional indentation
        font_size = para_data.get("font_size", 18.0)
        level_indent_emu = int((font_size * (1.6 + level * 1.6)) * 12700)
        hanging_indent_emu = int(-font_size * 0.8 * 12700)

        # Set indentation
        pPr.attrib["marL"] = str(level_indent_emu)
        pPr.attrib["indent"] = str(hanging_indent_emu)

        # Add bullet character
        buChar = OxmlElement("a:buChar")
        buChar.set("char", "•")
        pPr.append(buChar)

        # Default to left alignment for bullets if not specified
        if "alignment" not in para_data:
            paragraph.alignment = PP_ALIGN.LEFT
    else:
        # Remove indentation for non-bullet text
        pPr.attrib["marL"] = "0"
        pPr.attrib["indent"] = "0"

        # Add buNone element
        buNone = OxmlElement("a:buNone")
        pPr.insert(0, buNone)

    # Apply alignment
    if "alignment" in para_data:
        alignment_map = {
            "LEFT": PP_ALIGN.LEFT,
            "CENTER": PP_ALIGN.CENTER,
            "RIGHT": PP_ALIGN.RIGHT,
            "JUSTIFY": PP_ALIGN.JUSTIFY,
        }
        if para_data["alignment"] in alignment_map:
            paragraph.alignment = alignment_map[para_data["alignment"]]

    # Apply spacing
    if "space_before" in para_data:
        paragraph.space_before = Pt(para_data["space_before"])
    if "space_after" in para_data:
        paragraph.space_after = Pt(para_data["space_after"])
    if "line_spacing" in para_data:
        paragraph.line_spacing = Pt(para_data["line_spacing"])

    # Apply run-level formatting
    if not paragraph.runs:
        run = paragraph.add_run()
        run.text = text
    else:
        run = paragraph.runs[0]
        run.text = text

    # Apply font properties
    apply_font_properties(run, para_data)


def apply_font_properties(run, para_data: Dict[str, Any]):
    """向文本运行应用字体属性。"""
    if "bold" in para_data:
        run.font.bold = para_data["bold"]
    if "italic" in para_data:
        run.font.italic = para_data["italic"]
    if "underline" in para_data:
        run.font.underline = para_data["underline"]
    if "font_size" in para_data:
        run.font.size = Pt(para_data["font_size"])
    if "font_name" in para_data:
        run.font.name = para_data["font_name"]

    # Apply color - prefer RGB, fall back to theme_color
    if "color" in para_data:
        color_hex = para_data["color"].lstrip("#")
        if len(color_hex) == 6:
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            run.font.color.rgb = RGBColor(r, g, b)
    elif "theme_color" in para_data:
        # Get theme color by name (e.g., "DARK_1", "ACCENT_1")
        theme_name = para_data["theme_color"]
        try:
            run.font.color.theme_color = getattr(MSO_THEME_COLOR, theme_name)
        except AttributeError:
            print(f"  警告: 未知的主题颜色名称 '{theme_name}'")


def detect_frame_overflow(inventory: InventoryData) -> Dict[str, Dict[str, float]]:
    """检测形状中的文本溢出（文本超出形状边界）。

    返回 slide_key -> shape_key -> overflow_inches 的字典。
    仅包含存在文本溢出的形状。
    """
    overflow_map = {}

    for slide_key, shapes_dict in inventory.items():
        for shape_key, shape_data in shapes_dict.items():
            # Check for frame overflow (text exceeding shape bounds)
            if shape_data.frame_overflow_bottom is not None:
                if slide_key not in overflow_map:
                    overflow_map[slide_key] = {}
                overflow_map[slide_key][shape_key] = shape_data.frame_overflow_bottom

    return overflow_map


def validate_replacements(inventory: InventoryData, replacements: Dict) -> List[str]:
    """验证替换中的所有形状是否都存在于目录中。

    返回错误消息列表。
    """
    errors = []

    for slide_key, shapes_data in replacements.items():
        if not slide_key.startswith("slide-"):
            continue

        # Check if slide exists
        if slide_key not in inventory:
            errors.append(f"Slide '{slide_key}' not found in inventory")
            continue

        # Check each shape
        for shape_key in shapes_data.keys():
            if shape_key not in inventory[slide_key]:
                # Find shapes without replacements defined and show their content
                unused_with_content = []
                for k in inventory[slide_key].keys():
                    if k not in shapes_data:
                        shape_data = inventory[slide_key][k]
                        # Get text from paragraphs as preview
                        paragraphs = shape_data.paragraphs
                        if paragraphs and paragraphs[0].text:
                            first_text = paragraphs[0].text[:50]
                            if len(paragraphs[0].text) > 50:
                                first_text += "..."
                            unused_with_content.append(f"{k} ('{first_text}')")
                        else:
                            unused_with_content.append(k)

                errors.append(
                    f"Shape '{shape_key}' not found on '{slide_key}'. "
                    f"Shapes without replacements: {', '.join(sorted(unused_with_content)) if unused_with_content else 'none'}"
                )

    return errors


def check_duplicate_keys(pairs):
    """在加载JSON时检查重复键。"""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"在JSON中发现重复键: '{key}'")
        result[key] = value
    return result


def apply_replacements(pptx_file: str, json_file: str, output_file: str):
    """将JSON中的文本替换应用到PowerPoint演示文稿。"""

    # Load presentation
    prs = Presentation(pptx_file)

    # Get inventory of all text shapes (returns ShapeData objects)
    # Pass prs to use same Presentation instance
    inventory = extract_text_inventory(Path(pptx_file), prs)

    # Detect text overflow in original presentation
    original_overflow = detect_frame_overflow(inventory)

    # Load replacement data with duplicate key detection
    with open(json_file, "r") as f:
        replacements = json.load(f, object_pairs_hook=check_duplicate_keys)

    # Validate replacements
    errors = validate_replacements(inventory, replacements)
    if errors:
        print("错误: 替换JSON中的形状无效:")
        for error in errors:
            print(f"  - {error}")
        print("\n请检查目录并更新您的替换JSON。")
        print(
            "您可以使用以下命令重新生成目录: python inventory.py <input.pptx> <output.json>"
        )
        raise ValueError(f"Found {len(errors)} validation error(s)")

    # Track statistics
    shapes_processed = 0
    shapes_cleared = 0
    shapes_replaced = 0

    # Process each slide from inventory
    for slide_key, shapes_dict in inventory.items():
        if not slide_key.startswith("slide-"):
            continue

        slide_index = int(slide_key.split("-")[1])

        if slide_index >= len(prs.slides):
            print(f"警告: 未找到幻灯片 {slide_index}")
            continue

        # Process each shape from inventory
        for shape_key, shape_data in shapes_dict.items():
            shapes_processed += 1

            # Get the shape directly from ShapeData
            shape = shape_data.shape
            if not shape:
                print(f"警告: {shape_key} 没有形状引用")
                continue

            # ShapeData already validates text_frame in __init__
            text_frame = shape.text_frame  # type: ignore

            text_frame.clear()  # type: ignore
            shapes_cleared += 1

            # Check for replacement paragraphs
            replacement_shape_data = replacements.get(slide_key, {}).get(shape_key, {})
            if "paragraphs" not in replacement_shape_data:
                continue

            shapes_replaced += 1

            # Add replacement paragraphs
            for i, para_data in enumerate(replacement_shape_data["paragraphs"]):
                if i == 0:
                    p = text_frame.paragraphs[0]  # type: ignore
                else:
                    p = text_frame.add_paragraph()  # type: ignore

                apply_paragraph_properties(p, para_data)

    # Check for issues after replacements
    # Save to a temporary file and reload to avoid modifying the presentation during inventory
    # (extract_text_inventory accesses font.color which adds empty <a:solidFill/> elements)
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        prs.save(str(tmp_path))

    try:
        updated_inventory = extract_text_inventory(tmp_path)
        updated_overflow = detect_frame_overflow(updated_inventory)
    finally:
        tmp_path.unlink()  # Clean up temp file

    # Check if any text overflow got worse
    overflow_errors = []
    for slide_key, shape_overflows in updated_overflow.items():
        for shape_key, new_overflow in shape_overflows.items():
            # Get original overflow (0 if there was no overflow before)
            original = original_overflow.get(slide_key, {}).get(shape_key, 0.0)

            # Error if overflow increased
            if new_overflow > original + 0.01:  # Small tolerance for rounding
                increase = new_overflow - original
                overflow_errors.append(
                    f'{slide_key}/{shape_key}: overflow worsened by {increase:.2f}" '
                    f'(was {original:.2f}", now {new_overflow:.2f}")'
                )

    # Collect warnings from updated shapes
    warnings = []
    for slide_key, shapes_dict in updated_inventory.items():
        for shape_key, shape_data in shapes_dict.items():
            if shape_data.warnings:
                for warning in shape_data.warnings:
                    warnings.append(f"{slide_key}/{shape_key}: {warning}")

    # Fail if there are any issues
    if overflow_errors or warnings:
        print("\n错误: 在替换输出中检测到问题:")
        if overflow_errors:
            print("\n文本溢出情况恶化:")
            for error in overflow_errors:
                print(f"  - {error}")
        if warnings:
            print("\n格式警告:")
            for warning in warnings:
                print(f"  - {warning}")
        print("\n请在保存前修复这些问题。")
        raise ValueError(
            f"Found {len(overflow_errors)} overflow error(s) and {len(warnings)} warning(s)"
        )

    # Save the presentation
    prs.save(output_file)

    # Report results
    print(f"已将更新的演示文稿保存到: {output_file}")
    print(f"处理了 {len(prs.slides)} 张幻灯片")
    print(f"  - 处理的形状数: {shapes_processed}")
    print(f"  - 清除的形状数: {shapes_cleared}")
    print(f"  - 替换的形状数: {shapes_replaced}")


def main():
    """命令行使用的主入口点。"""
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    input_pptx = Path(sys.argv[1])
    replacements_json = Path(sys.argv[2])
    output_pptx = Path(sys.argv[3])

    if not input_pptx.exists():
        print(f"错误: 未找到输入文件 '{input_pptx}'")
        sys.exit(1)

    if not replacements_json.exists():
        print(f"错误: 未找到替换JSON文件 '{replacements_json}'")
        sys.exit(1)

    try:
        apply_replacements(str(input_pptx), str(replacements_json), str(output_pptx))
    except Exception as e:
        print(f"应用替换时出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
