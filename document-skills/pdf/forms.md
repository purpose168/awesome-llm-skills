**重要提示：您必须按顺序完成这些步骤。请勿跳过直接编写代码。**

如果您需要填写PDF表单，请首先检查PDF是否包含可填充的表单字段。从该文件所在目录运行以下脚本：
`python scripts/check_fillable_fields <file.pdf>`，然后根据结果选择进入「可填充字段」或「不可填充字段」部分并按照说明操作。

# 可填充字段
如果PDF包含可填充的表单字段：
- 从该文件所在目录运行以下脚本：`python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`。该脚本会创建一个JSON文件，包含以下格式的字段列表：
```
[
  {
    "field_id": (字段的唯一ID),
    "page": (页码，从1开始计数),
    "rect": ([左, 下, 右, 上] PDF坐标中的边界框，y=0为页面底部),
    "type": ("text" 文本, "checkbox" 复选框, "radio_group" 单选按钮组, 或 "choice" 选择字段),
  },
  // 复选框具有 "checked_value" 和 "unchecked_value" 属性：
  {
    "field_id": (字段的唯一ID),
    "page": (页码，从1开始计数),
    "type": "checkbox",
    "checked_value": (将字段设置为此值以选中复选框),
    "unchecked_value": (将字段设置为此值以取消选中复选框),
  },
  // 单选按钮组具有包含可能选项的 "radio_options" 列表。
  {
    "field_id": (字段的唯一ID),
    "page": (页码，从1开始计数),
    "type": "radio_group",
    "radio_options": [
      {
        "value": (将字段设置为此值以选择此单选按钮选项),
        "rect": (此选项单选按钮的边界框)
      },
      // 其他单选按钮选项
    ]
  },
  // 多选字段具有包含可能选项的 "choice_options" 列表：
  {
    "field_id": (字段的唯一ID),
    "page": (页码，从1开始计数),
    "type": "choice",
    "choice_options": [
      {
        "value": (将字段设置为此值以选择此选项),
        "text": (选项的显示文本)
      },
      // 其他选择选项
    ],
  }
]
```
- 使用此脚本将PDF转换为PNG图像（每页一个图像）（从该文件所在目录运行）：
`python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
然后分析图像以确定每个表单字段的用途（确保将边界框的PDF坐标转换为图像坐标）。
- 创建一个 `field_values.json` 文件，包含要为每个字段输入的值，格式如下：
```
[
  {
    "field_id": "last_name", // 必须与 `extract_form_field_info.py` 中的 field_id 匹配
    "description": "用户的姓氏",
    "page": 1, // 必须与 field_info.json 中的 "page" 值匹配
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "如果用户年满18岁则需要勾选的复选框",
    "page": 1,
    "value": "/On" // 如果是复选框，使用其 "checked_value" 值来勾选。如果是单选按钮组，使用 "radio_options" 中的一个 "value" 值。
  },
  // 更多字段
]
```
- 从该文件所在目录运行 `fill_fillable_fields.py` 脚本以创建填写好的PDF：
`python scripts/fill_fillable_fields.py <input pdf> <field_values.json> <output pdf>`
此脚本将验证您提供的字段ID和值是否有效；如果打印错误消息，请纠正相应的字段并重试。

# 不可填充字段
如果PDF没有可填充的表单字段，您需要通过视觉方式确定应添加数据的位置并创建文本注释。请**严格按照以下步骤操作**。您必须执行所有这些步骤，以确保表单被准确填写。每个步骤的详细信息如下。
- 将PDF转换为PNG图像并确定字段边界框。
- 创建包含字段信息和显示边界框的验证图像的JSON文件。
- 验证边界框。
- 使用边界框填写表单。

## 步骤1：视觉分析（必填）
- 将PDF转换为PNG图像。从该文件所在目录运行以下脚本：
`python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
该脚本将为PDF中的每一页创建一个PNG图像。
- 仔细检查每张PNG图像，识别所有表单字段和用户应输入数据的区域。对于每个用户应输入文本的表单字段，确定表单字段标签和用户应输入文本区域的边界框。标签和输入边界框**不得相交**；文本输入框应仅包含应输入数据的区域。通常，此区域将位于其标签的旁边、上方或下方。输入边界框必须足够高和宽以容纳其文本。

以下是您可能会看到的一些表单结构示例：

*框内标签*
```
┌────────────────────────┐
│ Name:                  │
└────────────────────────┘
```
输入区域应位于"Name"标签的右侧，并延伸到框的边缘。

*行前标签*
```
Email: _______________________
```
输入区域应位于行上方，并包含其整个宽度。

*行下标签*
```
_________________________
Name
```
输入区域应位于行上方，并包含行的整个宽度。这在签名和日期字段中很常见。

*行上标签*
```
Please enter any special requests:
________________________________________________
```
输入区域应从标签底部延伸到行，并包含行的整个宽度。

*复选框*
```
Are you a US citizen? Yes □  No □
```
对于复选框：
- 寻找小正方形框（□）- 这些是实际需要定位的复选框。它们可能位于其标签的左侧或右侧。
- 区分标签文本（"Yes"、"No"）和可点击的复选框正方形。
- 输入边界框应**仅**覆盖小正方形，而不是文本标签。

### 步骤2：创建fields.json和验证图像（必填）
- 创建一个名为 `fields.json` 的文件，包含表单字段和边界框信息，格式如下：
```
{
  "pages": [
    {
      "page_number": 1,
      "image_width": (第一页图像的宽度，像素),
      "image_height": (第一页图像的高度，像素),
    },
    {
      "page_number": 2,
      "image_width": (第二页图像的宽度，像素),
      "image_height": (第二页图像的高度，像素),
    }
    // 更多页面
  ],
  "form_fields": [
    // 文本字段示例。
    {
      "page_number": 1,
      "description": "此处应输入用户的姓氏",
      // 边界框格式为 [左, 上, 右, 下]。标签和文本输入的边界框不应重叠。
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "text": "Johnson", // 此文本将作为注释添加到 entry_bounding_box 位置
        "font_size": 14, // 可选，默认为 14
        "font_color": "000000", // 可选，RRGGBB 格式，默认为 000000（黑色）
      }
    },
    // 复选框示例。输入边界框应**仅**定位到正方形，而不是文本
    {
      "page_number": 2,
      "description": "如果用户年满18岁应勾选的复选框",
      "entry_bounding_box": [140, 525, 155, 540],  // 复选框正方形上方的小框
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],  // 包含 "Yes" 文本的框
      // 使用 "X" 来勾选复选框。
      "entry_text": {
        "text": "X",
      }
    }
    // 更多表单字段条目
  ]
}
```

通过从该文件所在目录运行以下脚本为每页创建验证图像：
`python scripts/create_validation_image.py <page_number> <path_to_fields.json> <input_image_path> <output_image_path>`

验证图像将在应输入文本的位置显示红色矩形，并在标签文本上显示蓝色矩形。

### 步骤3：验证边界框（必填）
#### 自动交集检查
- 通过使用 `check_bounding_boxes.py` 脚本检查 fields.json 文件（从该文件所在目录运行），验证边界框是否有交集，以及输入边界框是否足够高：
`python scripts/check_bounding_boxes.py <JSON file>`

如果有错误，请重新分析相关字段，调整边界框，并重复此过程直到没有剩余错误。请记住：标签（蓝色）边界框应包含文本标签，输入（红色）框不应包含。

#### 手动图像检查
**重要提示：在没有目视检查验证图像的情况下，请勿继续操作**
- 红色矩形必须**仅**覆盖输入区域
- 红色矩形**不得**包含任何文本
- 蓝色矩形应包含标签文本
- 对于复选框：
  - 红色矩形必须位于复选框正方形的中心
  - 蓝色矩形应覆盖复选框的文本标签

- 如果任何矩形看起来有问题，请修复 fields.json，重新生成验证图像，并再次验证。重复此过程，直到边界框完全准确。


### 步骤4：向PDF添加注释
从该文件所在目录运行此脚本，使用 fields.json 中的信息创建填写好的PDF：
`python scripts/fill_pdf_form_with_annotations.py <input_pdf_path> <path_to_fields.json> <output_pdf_path>`
