# Office Open XML 技术参考

**重要提示：开始前请阅读完整文档。** 本文档涵盖：
- [技术指南](#technical-guidelines) - Schema合规性规则和验证要求
- [文档内容模式](#document-content-patterns) - 标题、列表、表格、格式化等的XML模式
- [文档库（Python）](#document-library-python) - 用于OOXML操作的推荐方法，带有自动基础设施设置
- [修订跟踪（红线标注）](#tracked-changes-redlining) - 实现修订跟踪的XML模式

## 技术指南

### Schema合规性
- **`<w:pPr>`中的元素顺序**：`<w:pStyle>`、`<w:numPr>`、`<w:spacing>`、`<w:ind>`、`<w:jc>`
- **空白处理**：对于带有前导/尾随空格的`<w:t>`元素，添加`xml:space='preserve'`属性
- **Unicode编码**：在ASCII内容中转义字符：`"`变为`&#8220;`
  - **字符编码参考**：花引号`""`变为`&#8220;&#8221;`，撇号`'`变为`&#8217;`，长破折号`—`变为`&#8212;`
- **修订跟踪**：在`<w:r>`元素外部使用带有`w:author="Claude"`的`<w:del>`和`<w:ins>`标签
  - **关键**：`<w:ins>`使用`</w:ins>`闭合，`<w:del>`使用`</w:del>`闭合 - 切勿混用
  - **RSID必须为8位十六进制**：使用类似`00AB1234`的值（仅包含0-9、A-F字符）
  - **trackRevisions放置位置**：在settings.xml中，将`<w:trackRevisions/>`添加到`<w:proofState>`之后
- **图像**：添加到`word/media/`目录，在`document.xml`中引用，设置尺寸以防止溢出

## 文档内容模式

### 基本结构
```xml
<w:p>
  <w:r><w:t>文本内容</w:t></w:r>
</w:p>
```

### 标题和样式
```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Title"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>文档标题</w:t></w:r>
</w:p>

<w:p>
  <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
  <w:r><w:t>章节标题</w:t></w:r>
</w:p>
```

### 文本格式化
```xml
<!-- 粗体 -->
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>粗体</w:t></w:r>
<!-- 斜体 -->
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>斜体</w:t></w:r>
<!-- 下划线 -->
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>带下划线</w:t></w:r>
<!-- 高亮 -->
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>高亮</w:t></w:r>
```

### 列表
```xml
<!-- 编号列表 -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>第一项</w:t></w:r>
</w:p>

<!-- 重新开始编号列表（从1开始）- 使用不同的numId -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>新列表项1</w:t></w:r>
</w:p>

<!-- 项目符号列表（级别2） -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
    <w:ind w:left="900"/>
  </w:pPr>
  <w:r><w:t>项目符号项</w:t></w:r>
</w:p>
```

### 表格
```xml
<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="0" w:type="auto"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="4675"/><w:gridCol w:w="4675"/>
  </w:tblGrid>
  <w:tr>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>单元格1</w:t></w:r></w:p>
    </w:tc>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>单元格2</w:t></w:r></w:p>
    </w:tc>
  </w:tr>
</w:tbl>
```

### 布局
```xml
<!-- 新章节前的分页符（常用模式） -->
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
  </w:pPr>
  <w:r>
    <w:t>新章节标题</w:t>
  </w:r>
</w:p>

<!-- 居中段落 -->
<w:p>
  <w:pPr>
    <w:spacing w:before="240" w:after="0"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>居中文本</w:t></w:r>
</w:p>

<!-- 字体更改 - 段落级别（应用于所有文本运行） -->
<w:p>
  <w:pPr>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
  </w:pPr>
  <w:r><w:t>等宽文本</w:t></w:r>
</w:p>

<!-- 字体更改 - 文本运行级别（仅适用于此文本） -->
<w:p>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
    <w:t>这段文本使用Courier New字体</w:t>
  </w:r>
  <w:r><w:t> 而这段文本使用默认字体</w:t></w:r>
</w:p>
```

## 文件更新

添加内容时，需要更新以下文件：

**`word/_rels/document.xml.rels`：**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
```

**`[Content_Types].xml`：**
```xml
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
```

### 图像
**关键提示**：必须计算尺寸以防止页面溢出并保持宽高比。

```xml
<!-- 最小必要结构 -->
<w:p>
  <w:r>
    <w:drawing>
      <wp:inline>
        <wp:extent cx="2743200" cy="1828800"/>
        <wp:docPr id="1" name="图片 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="image1.png"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="rId5"/>
                <!-- 添加此部分以保持宽高比的拉伸填充 -->
                <a:stretch>
                  <a:fillRect/>
                </a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm>
                  <a:ext cx="2743200" cy="1828800"/>
                </a:xfrm>
                <a:prstGeom prst="rect"/>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
```

### 链接（超链接）

**重要提示**：所有超链接（内部和外部）都需要在styles.xml中定义Hyperlink样式。没有此样式，链接将显示为普通文本而不是蓝色下划线的可点击链接。

**外部链接：**
```xml
<!-- 在document.xml中 -->
<w:hyperlink r:id="rId5">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>链接文本</w:t>
  </w:r>
</w:hyperlink>

<!-- 在word/_rels/document.xml.rels中 -->
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" 
              Target="https://www.example.com/" TargetMode="External"/>
```

**内部链接：**

```xml
<!-- 链接到书签 -->
<w:hyperlink w:anchor="myBookmark">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>链接文本</w:t>
  </w:r>
</w:hyperlink>

<!-- 书签目标 -->
<w:bookmarkStart w:id="0" w:name="myBookmark"/>
<w:r><w:t>目标内容</w:t></w:r>
<w:bookmarkEnd w:id="0"/>
```

**超链接样式（在styles.xml中是必需的）：**
```xml
<w:style w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/>
  <w:basedOn w:val="DefaultParagraphFont"/>
  <w:uiPriority w:val="99"/>
  <w:unhideWhenUsed/>
  <w:rPr>
    <w:color w:val="467886" w:themeColor="hyperlink"/>
    <w:u w:val="single"/>
  </w:rPr>
</w:style>
```

## 文档库（Python）

所有修订跟踪和注释操作都使用`scripts/document.py`中的Document类。它自动处理基础设施设置（people.xml、RSID、settings.xml、注释文件、关系、内容类型）。仅在库不支持的复杂场景下才使用直接XML操作。

**处理Unicode和实体：**
- **搜索**：实体表示法和Unicode字符都有效 - `contains="&#8220;Company"`和`contains="\u201cCompany"`可以找到相同的文本
- **替换**：可以使用实体（`&#8220;`）或Unicode（`\u201c`）- 两者都有效，并且会根据文件的编码自动转换（ascii → 实体，utf-8 → Unicode）

### 初始化

**查找docx技能根目录**（包含`scripts/`和`ooxml/`的目录）：
```bash
# 搜索document.py以定位技能根目录
# 注意：这里使用/mnt/skills作为示例；请根据实际情况检查您的上下文
find /mnt/skills -name "document.py" -path "*/docx/scripts/*" 2>/dev/null | head -1
# 示例输出：/mnt/skills/docx/scripts/document.py
# 技能根目录是：/mnt/skills/docx
```

**使用设置为docx技能根目录的PYTHONPATH运行脚本：**
```bash
PYTHONPATH=/mnt/skills/docx python your_script.py
```

**在您的脚本中**，从技能根目录导入：
```python
from scripts.document import Document, DocxXMLEditor

# 基本初始化（自动创建临时副本并设置基础设施）
doc = Document('unpacked')

# 自定义作者和缩写
doc = Document('unpacked', author="John Doe", initials="JD")

# 启用修订跟踪模式
doc = Document('unpacked', track_revisions=True)

# 指定自定义RSID（如果未提供则自动生成）
doc = Document('unpacked', rsid="07DC5ECB")
```

### 创建修订跟踪

**关键提示**：只标记实际更改的文本。将所有未更改的文本保留在`<w:del>`/`<w:ins>`标签之外。标记未更改的文本会使编辑看起来不专业且难以审阅。

**属性处理**：Document类会自动将属性（w:id、w:date、w:rsidR、w:rsidDel、w16du:dateUtc、xml:space）注入到新元素中。当保留原始文档中未更改的文本时，复制原始`<w:r>`元素及其现有属性以保持文档完整性。

**方法选择指南**：
- **向常规文本添加您自己的更改**：使用带有`<w:del>`/`<w:ins>`标签的`replace_node()`，或使用`suggest_deletion()`删除整个`<w:r>`或`<w:p>`元素
- **部分修改其他作者的修订**：使用`replace_node()`将您的更改嵌套在他们的`<w:ins>`/`<w:del>`内部
- **完全拒绝其他作者的插入**：在`<w:ins>`元素上使用`revert_insertion()`（不要使用`suggest_deletion()`）
- **完全拒绝其他作者的删除**：在`<w:del>`元素上使用`revert_deletion()`以使用修订跟踪恢复已删除的内容

```python
# 最小修改 - 更改一个单词："The report is monthly" → "The report is quarterly"
# 原始：<w:r w:rsidR="00AB12CD"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>The report is monthly</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="The report is monthly")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00AB12CD">{rpr}<w:t>The report is </w:t></w:r><w:del><w:r>{rpr}<w:delText>monthly</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>quarterly</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 最小修改 - 更改数字："within 30 days" → "within 45 days"
# 原始：<w:r w:rsidR="00XYZ789"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>within 30 days</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="within 30 days")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00XYZ789">{rpr}<w:t>within </w:t></w:r><w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>45</w:t></w:r></w:ins><w:r w:rsidR="00XYZ789">{rpr}<w:t> days</w:t></w:r>'
doc["word/document.xml"].replace_node(node, replacement)

# 完全替换 - 即使替换所有文本也保留格式
node = doc["word/document.xml"].get_node(tag="w:r", contains="apple")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:del><w:r>{rpr}<w:delText>apple</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>banana orange</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 插入新内容（不需要属性 - 自动注入）
node = doc["word/document.xml"].get_node(tag="w:r", contains="existing text")
doc["word/document.xml"].insert_after(node, '<w:ins><w:r><w:t>new text</w:t></w:r></w:ins>')

# 部分删除其他作者的插入内容
# 原始：<w:ins w:author="Jane Smith" w:date="..."><w:r><w:t>quarterly financial report</w:t></w:r></w:ins>
# 目标：仅删除"financial"，使其变为"quarterly report"
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
# 重要提示：保留外部<w:ins>上的w:author="Jane Smith"以保持作者身份
replacement = '''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>quarterly </w:t></w:r>
  <w:del><w:r><w:delText>financial </w:delText></w:r></w:del>
  <w:r><w:t>report</w:t></w:r>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# 更改其他作者插入内容的一部分
# 原始：<w:ins w:author="Jane Smith"><w:r><w:t>in silence, safe and sound</w:t></w:r></w:ins>
# 目标：将"safe and sound"更改为"soft and unbound"
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "8"})
replacement = f'''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>in silence, </w:t></w:r>
</w:ins>
<w:ins>
  <w:r><w:t>soft and unbound</w:t></w:r>
</w:ins>
<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:del><w:r><w:delText>safe and sound</w:delText></w:r></w:del>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# 删除整个文本运行（仅在删除所有内容时使用；部分删除使用replace_node）
node = doc["word/document.xml"].get_node(tag="w:r", contains="text to delete")
doc["word/document.xml"].suggest_deletion(node)

# 删除整个段落（原地删除，处理常规和编号列表段落）
para = doc["word/document.xml"].get_node(tag="w:p", contains="paragraph to delete")
doc["word/document.xml"].suggest_deletion(para)

# 添加新的编号列表项
target_para = doc["word/document.xml"].get_node(tag="w:p", contains="existing list item")
pPr = tags[0].toxml() if (tags := target_para.getElementsByTagName("w:pPr")) else ""
new_item = f'<w:p>{pPr}<w:r><w:t>New item</w:t></w:r></w:p>'
tracked_para = DocxXMLEditor.suggest_paragraph(new_item)
doc["word/document.xml"].insert_after(target_para, tracked_para)
# 可选：在内容前添加间距段落以获得更好的视觉分隔
# spacing = DocxXMLEditor.suggest_paragraph('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr></w:p>')
# doc["word/document.xml"].insert_after(target_para, spacing + tracked_para)
```

### 添加注释

```python
# 添加跨越两个现有修订的注释
# 注意：w:id是自动生成的。只有在通过XML检查知道w:id时，才可以通过它搜索
start_node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
end_node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "2"})
doc.add_comment(start=start_node, end=end_node, text="此更改的说明")

# 在段落上添加注释
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
doc.add_comment(start=para, end=para, text="对该段落的评论")

# 在新创建的修订上添加注释
# 首先创建修订
node = doc["word/document.xml"].get_node(tag="w:r", contains="old")
new_nodes = doc["word/document.xml"].replace_node(
    node,
    '<w:del><w:r><w:delText>old</w:delText></w:r></w:del><w:ins><w:r><w:t>new</w:t></w:r></w:ins>'
)
# 然后在新创建的元素上添加注释
# new_nodes[0] 是 <w:del>，new_nodes[1] 是 <w:ins>
doc.add_comment(start=new_nodes[0], end=new_nodes[1], text="根据要求将旧内容更改为新内容")

# 回复现有注释
doc.reply_to_comment(parent_comment_id=0, text="我同意此更改")
```

### 拒绝修订

**重要提示**：使用 `revert_insertion()` 拒绝插入内容，使用 `revert_deletion()` 恢复被删除的内容（使用修订跟踪）。仅对常规未标记内容使用 `suggest_deletion()`。

```python
# 拒绝插入（将其包装在删除标记中）
# 当其他作者插入了你想要删除的文本时使用此方法
ins = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
nodes = doc["word/document.xml"].revert_insertion(ins)  # 返回 [ins]

# 拒绝删除（创建插入以恢复被删除的内容）
# 当其他作者删除了你想要恢复的文本时使用此方法
del_elem = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "3"})
nodes = doc["word/document.xml"].revert_deletion(del_elem)  # 返回 [del_elem, new_ins]

# 拒绝段落中的所有插入
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
nodes = doc["word/document.xml"].revert_insertion(para)  # 返回 [para]

# 拒绝段落中的所有删除
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
nodes = doc["word/document.xml"].revert_deletion(para)  # 返回 [para]
```

### 插入图片

**关键提示**：Document类在 `doc.unpacked_path` 位置使用临时副本。请始终将图片复制到此临时目录，而不是原始解包文件夹。

```python
from PIL import Image
import shutil, os

# 先初始化文档
doc = Document('unpacked')

# 复制图片并按比例计算全宽尺寸
media_dir = os.path.join(doc.unpacked_path, 'word/media')
os.makedirs(media_dir, exist_ok=True)
shutil.copy('image.png', os.path.join(media_dir, 'image1.png'))
img = Image.open(os.path.join(media_dir, 'image1.png'))
width_emus = int(6.5 * 914400)  # 6.5" 可用宽度，914400 EMUs/英寸
height_emus = int(width_emus * img.size[1] / img.size[0])

# 添加关系和内容类型
rels_editor = doc['word/_rels/document.xml.rels']
next_rid = rels_editor.get_next_rid()
rels_editor.append_to(rels_editor.dom.documentElement,
    f'<Relationship Id="{next_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>')
doc['[Content_Types].xml'].append_to(doc['[Content_Types].xml'].dom.documentElement,
    '<Default Extension="png" ContentType="image/png"/>')

# 插入图片
node = doc["word/document.xml"].get_node(tag="w:p", line_number=100)
doc["word/document.xml"].insert_after(node, f'''<w:p>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{width_emus}" cy="{height_emus}"/>
        <wp:docPr id="1" name="Picture 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr><pic:cNvPr id="1" name="image1.png"/><pic:cNvPicPr/></pic:nvPicPr>
              <pic:blipFill><a:blip r:embed="{next_rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
              <pic:spPr><a:xfrm><a:ext cx="{width_emus}" cy="{height_emus}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>''')
```

### 获取节点

```python
# 通过文本内容获取
node = doc["word/document.xml"].get_node(tag="w:p", contains="特定文本")

# 通过行范围获取
para = doc["word/document.xml"].get_node(tag="w:p", line_number=range(100, 150))

# 通过属性获取
node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})

# 通过精确行号获取（必须是标签开始的行号）
para = doc["word/document.xml"].get_node(tag="w:p", line_number=42)

# 组合筛选条件
node = doc["word/document.xml"].get_node(tag="w:r", line_number=range(40, 60), contains="文本")

# 当文本多次出现时消除歧义 - 添加行号范围
node = doc["word/document.xml"].get_node(tag="w:r", contains="Section", line_number=range(2400, 2500))
```

### 保存

```python
# 保存并自动验证（复制回原始目录）
doc.save()  # 默认验证，如果验证失败则抛出错误

# 保存到不同位置
doc.save('modified-unpacked')

# 跳过验证（仅用于调试 - 在生产环境中需要此功能表明XML存在问题）
doc.save(validate=False)
```

### 直接DOM操作

对于库未覆盖的复杂场景：

```python
# 访问任何XML文件
editor = doc["word/document.xml"]
editor = doc["word/comments.xml"]

# 直接DOM访问（defusedxml.minidom.Document）
node = doc["word/document.xml"].get_node(tag="w:p", line_number=5)
parent = node.parentNode
parent.removeChild(node)
parent.appendChild(node)  # 移动到末尾

# 常规文档操作（不带修订跟踪）
old_node = doc["word/document.xml"].get_node(tag="w:p", contains="原始文本")
doc["word/document.xml"].replace_node(old_node, "<w:p><w:r><w:t>替换文本</w:t></w:r></w:p>")

# 多次插入 - 使用返回值来维护顺序
node = doc["word/document.xml"].get_node(tag="w:r", line_number=100)
nodes = doc["word/document.xml"].insert_after(node, "<w:r><w:t>A</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>B</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>C</w:t></w:r>")
# 结果：original_node, A, B, C
```

## 修订跟踪（红线标注）

**所有修订跟踪操作请使用上面的Document类。** 以下模式仅供构建替换XML字符串时参考。

### 验证规则
验证器会检查在还原Claude的更改后，文档文本是否与原始文本匹配。这意味着：
- **切勿修改其他作者的`<w:ins>`或`<w:del>`标签内的文本**
- **始终使用嵌套删除**来移除其他作者的插入内容
- **每次编辑都必须使用`<w:ins>`或`<w:del>`标签进行正确跟踪**

### 修订模式

**关键规则**：
1. 永远不要修改其他作者的修订内容内部。始终使用嵌套删除。
2. **XML结构**：始终将`<w:del>`和`<w:ins>`放在包含完整`<w:r>`元素的段落级别。切勿在`<w:r>`元素内部嵌套 - 这会创建无效的XML，破坏文档处理。

**文本插入：**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidR="00792858">
    <w:t>插入的文本</w:t>
  </w:r>
</w:ins>
```

**文本删除：**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidDel="00792858">
    <w:delText>删除的文本</w:delText>
  </w:r>
</w:del>
```

**删除其他作者的插入内容（必须使用嵌套结构）：**
```xml
<!-- 在原始插入内容内嵌套删除 -->
<w:ins w:author="Jane Smith" w:id="16">
  <w:del w:author="Claude" w:id="40">
    <w:r><w:delText>monthly</w:delText></w:r>
  </w:del>
</w:ins>
<w:ins w:author="Claude" w:id="41">
  <w:r><w:t>weekly</w:t></w:r>
</w:ins>
```

**恢复其他作者删除的内容：**
```xml
<!-- 保持他们的删除不变，在其后添加新的插入 -->
<w:del w:author="Jane Smith" w:id="50">
  <w:r><w:delText>within 30 days</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="51">
  <w:r><w:t>within 30 days</w:t></w:r>
</w:ins>
```