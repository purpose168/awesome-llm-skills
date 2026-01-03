import json
import sys

from pypdf import PdfReader


# 提取PDF中可填写表单字段的数据，并输出JSON格式供Claude用于填充字段。请参见forms.md。


# 此函数匹配PdfReader的`get_fields`和`update_page_form_field_values`方法使用的格式。
def get_full_annotation_field_id(annotation):
    components = []
    while annotation:
        field_name = annotation.get('/T')
        if field_name:
            components.append(field_name)
        annotation = annotation.get('/Parent')
    return ".".join(reversed(components)) if components else None


def make_field_dict(field, field_id):
    field_dict = {"field_id": field_id}
    ft = field.get('/FT')
    if ft == "/Tx":
        field_dict["type"] = "text"
    elif ft == "/Btn":
        field_dict["type"] = "checkbox"  # 单选按钮组单独处理
        states = field.get("/_States_", [])
        if len(states) == 2:
            # "/Off"似乎总是未选中的值，如以下文档所示：
            # https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=448
            # 它可以是"/_States_"列表中的第一个或第二个。
            if "/Off" in states:
                field_dict["checked_value"] = states[0] if states[0] != "/Off" else states[1]
                field_dict["unchecked_value"] = "/Off"
            else:
                print(f"复选框 `${field_id}` 的状态值意外。其选中和未选中的值可能不正确；如果您尝试勾选它，请直观验证结果。")
                field_dict["checked_value"] = states[0]
                field_dict["unchecked_value"] = states[1]
    elif ft == "/Ch":
        field_dict["type"] = "choice"
        states = field.get("/_States_", [])
        field_dict["choice_options"] = [{
            "value": state[0],
            "text": state[1],
        } for state in states]
    else:
        field_dict["type"] = f"unknown ({ft})"
    return field_dict


# 返回可填写PDF字段的列表：
# [
#   {
#     "field_id": "name",
#     "page": 1,
#     "type": ("text", "checkbox", "radio_group", or "choice")
#     // 每种类型的附加字段在forms.md中描述
#   },
# ]
def get_field_info(reader: PdfReader):
    fields = reader.get_fields()

    field_info_by_id = {}
    possible_radio_names = set()

    for field_id, field in fields.items():
        # 如果这是带有子项的容器字段，则跳过，除非它可能是单选按钮选项的父组。
        if field.get("/Kids"):
            if field.get("/FT") == "/Btn":
                possible_radio_names.add(field_id)
            continue
        field_info_by_id[field_id] = make_field_dict(field, field_id)

    # 边界矩形存储在页面对象的注释中。

    # 单选按钮选项为每个选择都有一个单独的注释；
    # 所有选择都具有相同的字段名称。
    # 请参见 https://westhealth.github.io/exploring-fillable-forms-with-pdfrw.html
    radio_fields_by_id = {}

    for page_index, page in enumerate(reader.pages):
        annotations = page.get('/Annots', [])
        for ann in annotations:
            field_id = get_full_annotation_field_id(ann)
            if field_id in field_info_by_id:
                field_info_by_id[field_id]["page"] = page_index + 1
                field_info_by_id[field_id]["rect"] = ann.get('/Rect')
            elif field_id in possible_radio_names:
                try:
                    # ann['/AP']['/N'] 应该有两个项。其中一个是 '/Off'，
                    # 另一个是激活值。
                    on_values = [v for v in ann["/AP"]["/N"] if v != "/Off"]
                except KeyError:
                    continue
                if len(on_values) == 1:
                    rect = ann.get("/Rect")
                    if field_id not in radio_fields_by_id:
                        radio_fields_by_id[field_id] = {
                            "field_id": field_id,
                            "type": "radio_group",
                            "page": page_index + 1,
                            "radio_options": [],
                        }
                    # 注意：至少在 macOS 15.7 上，Preview.app 不能正确显示选中的单选按钮。
                    # （如果从值中删除前导斜杠，它可以正常工作，但这会导致它们在
                    # Chrome/Firefox/Acrobat 等中显示不正确）。
                    radio_fields_by_id[field_id]["radio_options"].append({
                        "value": on_values[0],
                        "rect": rect,
                    })

    # 有些PDF有表单字段定义但没有相应的注释，
    # 所以我们无法确定它们的位置。现在暂时忽略这些字段。
    fields_with_location = []
    for field_info in field_info_by_id.values():
        if "page" in field_info:
            fields_with_location.append(field_info)
        else:
            print(f"无法确定字段ID的位置: {field_info.get('field_id')}, 忽略")

    # 按页码排序，然后按Y位置（PDF坐标系中翻转）排序，然后按X位置排序。
    def sort_key(f):
        if "radio_options" in f:
            rect = f["radio_options"][0]["rect"] or [0, 0, 0, 0]
        else:
            rect = f.get("rect") or [0, 0, 0, 0]
        adjusted_position = [-rect[1], rect[0]]
        return [f.get("page"), adjusted_position]
    
    sorted_fields = fields_with_location + list(radio_fields_by_id.values())
    sorted_fields.sort(key=sort_key)

    return sorted_fields


def write_field_info(pdf_path: str, json_output_path: str):
    reader = PdfReader(pdf_path)
    field_info = get_field_info(reader)
    with open(json_output_path, "w") as f:
        json.dump(field_info, f, indent=2)
    print(f"已将 {len(field_info)} 个字段写入 {json_output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: extract_form_field_info.py [输入PDF文件] [输出JSON文件]")
        sys.exit(1)
    write_field_info(sys.argv[1], sys.argv[2])
