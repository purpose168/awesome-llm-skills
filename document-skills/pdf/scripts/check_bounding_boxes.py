from dataclasses import dataclass
import json
import sys


# 检查Claude分析PDF时创建的`fields.json`文件是否包含重叠边界框的脚本。请参阅forms.md。


@dataclass
class RectAndField:
    rect: list[float]
    rect_type: str
    field: dict


# 返回打印到stdout以便Claude读取的消息列表。
def get_bounding_box_messages(fields_json_stream) -> list[str]:
    messages = []
    fields = json.load(fields_json_stream)
    messages.append(f"已读取 {len(fields['form_fields'])} 个字段")

    def rects_intersect(r1, r2):
        disjoint_horizontal = r1[0] >= r2[2] or r1[2] <= r2[0]
        disjoint_vertical = r1[1] >= r2[3] or r1[3] <= r2[1]
        return not (disjoint_horizontal or disjoint_vertical)

    rects_and_fields = []
    for f in fields["form_fields"]:
        rects_and_fields.append(RectAndField(f["label_bounding_box"], "label", f))
        rects_and_fields.append(RectAndField(f["entry_bounding_box"], "entry", f))

    has_error = False
    for i, ri in enumerate(rects_and_fields):
        # 这是O(N^2)复杂度；如果成为问题，我们可以优化。
        for j in range(i + 1, len(rects_and_fields)):
            rj = rects_and_fields[j]
            if ri.field["page_number"] == rj.field["page_number"] and rects_intersect(ri.rect, rj.rect):
                has_error = True
                if ri.field is rj.field:
                    messages.append(f"FAILURE: `{ri.field['description']}`的标签和输入框边界框相交 ({ri.rect}, {rj.rect})")
                else:
                    messages.append(f"FAILURE: `{ri.field['description']}`的{ri.rect_type.replace('label', '标签').replace('entry', '输入框')}边界框 ({ri.rect}) 与 `{rj.field['description']}`的{rj.rect_type.replace('label', '标签').replace('entry', '输入框')}边界框 ({rj.rect}) 相交")
                if len(messages) >= 20:
                    messages.append("Aborting: 中止进一步检查；修复边界框并重试")
                    return messages
        if ri.rect_type == "entry":
            if "entry_text" in ri.field:
                font_size = ri.field["entry_text"].get("font_size", 14)
                entry_height = ri.rect[3] - ri.rect[1]
                if entry_height < font_size:
                    has_error = True
                    messages.append(f"FAILURE: `{ri.field['description']}`的输入框高度 ({entry_height}) 对于文本内容来说太小 (字体大小: {font_size})。请增加框高度或减小字体大小。")
                    if len(messages) >= 20:
                        messages.append("Aborting: 中止进一步检查；修复边界框并重试")
                        return messages

    if not has_error:
        messages.append("SUCCESS: 所有边界框都有效")
    return messages

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_bounding_boxes.py [fields.json]")
        sys.exit(1)
    # 输入文件应该是forms.md中描述的`fields.json`格式。
    with open(sys.argv[1]) as f:
        messages = get_bounding_box_messages(f)
    for msg in messages:
        print(msg)
