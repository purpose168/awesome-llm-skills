#!/usr/bin/env python3
"""
根据索引序列重新排列PowerPoint幻灯片。

使用方法：
    python rearrange.py template.pptx output.pptx 0,34,34,50,52

这将使用template.pptx中的幻灯片创建output.pptx，幻灯片顺序由指定的索引序列决定。
幻灯片可以重复（例如，索引34出现两次）。
"""

import argparse
import shutil
import sys
from copy import deepcopy
from pathlib import Path

import six
from pptx import Presentation


def main():
    parser = argparse.ArgumentParser(
        description="根据索引序列重新排列PowerPoint幻灯片。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python rearrange.py template.pptx output.pptx 0,34,34,50,52
    使用template.pptx中的幻灯片0、34（两次）、50和52创建output.pptx

  python rearrange.py template.pptx output.pptx 5,3,1,2,4
    创建按指定顺序重新排列幻灯片的output.pptx

注意：幻灯片索引从0开始（第一张幻灯片为0，第二张为1，依此类推）
        """,
    )

    parser.add_argument("template", help="模板PPTX文件路径")
    parser.add_argument("output", help="输出PPTX文件路径")
    parser.add_argument(
        "sequence", help="逗号分隔的幻灯片索引序列（从0开始）"
    )

    args = parser.parse_args()

    # Parse the slide sequence
    try:
        slide_sequence = [int(x.strip()) for x in args.sequence.split(",")]
    except ValueError:
        print(
            "错误: 序列格式无效。请使用逗号分隔的整数（例如：0,34,34,50,52）"
        )
        sys.exit(1)

    # Check template exists
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"错误: 找不到模板文件: {args.template}")
        sys.exit(1)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        rearrange_presentation(template_path, output_path, slide_sequence)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"处理演示文稿时出错: {e}")
        sys.exit(1)


def duplicate_slide(pres, index):
    """在演示文稿中复制幻灯片。"""
    source = pres.slides[index]

    # Use source's layout to preserve formatting
    new_slide = pres.slides.add_slide(source.slide_layout)

    # Collect all image and media relationships from the source slide
    image_rels = {}
    for rel_id, rel in six.iteritems(source.part.rels):
        if "image" in rel.reltype or "media" in rel.reltype:
            image_rels[rel_id] = rel

    # CRITICAL: Clear placeholder shapes to avoid duplicates
    for shape in new_slide.shapes:
        sp = shape.element
        sp.getparent().remove(sp)

    # Copy all shapes from source
    for shape in source.shapes:
        el = shape.element
        new_el = deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(new_el, "p:extLst")

        # Handle picture shapes - need to update the blip reference
        # Look for all blip elements (they can be in pic or other contexts)
        # Using the element's own xpath method without namespaces argument
        blips = new_el.xpath(".//a:blip[@r:embed]")
        for blip in blips:
            old_rId = blip.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if old_rId in image_rels:
                # Create a new relationship in the destination slide for this image
                old_rel = image_rels[old_rId]
                # get_or_add returns the rId directly, or adds and returns new rId
                new_rId = new_slide.part.rels.get_or_add(
                    old_rel.reltype, old_rel._target
                )
                # Update the blip's embed reference to use the new relationship ID
                blip.set(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed",
                    new_rId,
                )

    # Copy any additional image/media relationships that might be referenced elsewhere
    for rel_id, rel in image_rels.items():
        try:
            new_slide.part.rels.get_or_add(rel.reltype, rel._target)
        except Exception:
            pass  # Relationship might already exist

    return new_slide


def delete_slide(pres, index):
    """从演示文稿中删除幻灯片。"""
    rId = pres.slides._sldIdLst[index].rId
    pres.part.drop_rel(rId)
    del pres.slides._sldIdLst[index]


def reorder_slides(pres, slide_index, target_index):
    """将幻灯片从一个位置移动到另一个位置。"""
    slides = pres.slides._sldIdLst

    # Remove slide element from current position
    slide_element = slides[slide_index]
    slides.remove(slide_element)

    # Insert at target position
    slides.insert(target_index, slide_element)


def rearrange_presentation(template_path, output_path, slide_sequence):
    """
    使用模板中的幻灯片按指定顺序创建新演示文稿。

    参数：
        template_path: 模板PPTX文件路径
        output_path: 输出PPTX文件路径
        slide_sequence: 要包含的幻灯片索引列表（从0开始）
    """
    # Copy template to preserve dimensions and theme
    if template_path != output_path:
        shutil.copy2(template_path, output_path)
        prs = Presentation(output_path)
    else:
        prs = Presentation(template_path)

    total_slides = len(prs.slides)

    # Validate indices
    for idx in slide_sequence:
        if idx < 0 or idx >= total_slides:
            raise ValueError(f"Slide index {idx} out of range (0-{total_slides - 1})")

    # Track original slides and their duplicates
    slide_map = []  # List of actual slide indices for final presentation
    duplicated = {}  # Track duplicates: original_idx -> [duplicate_indices]

    # Step 1: DUPLICATE repeated slides
    print(f"正在处理模板中的 {len(slide_sequence)} 张幻灯片...")
    for i, template_idx in enumerate(slide_sequence):
        if template_idx in duplicated and duplicated[template_idx]:
            # Already duplicated this slide, use the duplicate
            slide_map.append(duplicated[template_idx].pop(0))
            print(f"  [{i}] 使用幻灯片 {template_idx} 的副本")
        elif slide_sequence.count(template_idx) > 1 and template_idx not in duplicated:
            # First occurrence of a repeated slide - create duplicates
            slide_map.append(template_idx)
            duplicates = []
            count = slide_sequence.count(template_idx) - 1
            print(
                f"  [{i}] 使用原始幻灯片 {template_idx}，创建 {count} 个副本"
            )
            for _ in range(count):
                duplicate_slide(prs, template_idx)
                duplicates.append(len(prs.slides) - 1)
            duplicated[template_idx] = duplicates
        else:
            # Unique slide or first occurrence already handled, use original
            slide_map.append(template_idx)
            print(f"  [{i}] 使用原始幻灯片 {template_idx}")

    # Step 2: DELETE unwanted slides (work backwards)
    slides_to_keep = set(slide_map)
    print(f"\n正在删除 {len(prs.slides) - len(slides_to_keep)} 张未使用的幻灯片...")
    for i in range(len(prs.slides) - 1, -1, -1):
        if i not in slides_to_keep:
            delete_slide(prs, i)
            # Update slide_map indices after deletion
            slide_map = [idx - 1 if idx > i else idx for idx in slide_map]

    # Step 3: REORDER to final sequence
    print(f"正在将 {len(slide_map)} 张幻灯片重新排序为最终序列...")
    for target_pos in range(len(slide_map)):
        # Find which slide should be at target_pos
        current_pos = slide_map[target_pos]
        if current_pos != target_pos:
            reorder_slides(prs, current_pos, target_pos)
            # Update slide_map: the move shifts other slides
            for i in range(len(slide_map)):
                if slide_map[i] > current_pos and slide_map[i] <= target_pos:
                    slide_map[i] -= 1
                elif slide_map[i] < current_pos and slide_map[i] >= target_pos:
                    slide_map[i] += 1
            slide_map[target_pos] = target_pos

    # Save the presentation
    prs.save(output_path)
    print(f"\n已将重新排列的演示文稿保存到: {output_path}")
    print(f"最终演示文稿包含 {len(prs.slides)} 张幻灯片")


if __name__ == "__main__":
    main()
