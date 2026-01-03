---
name: docx
description: "全面的文档创建、编辑和分析功能，支持修订跟踪、注释、格式保留和文本提取。当Claude需要处理专业文档（.docx文件）时，适用于：(1) 创建新文档，(2) 修改或编辑内容，(3) 处理修订跟踪，(4) 添加注释或其他文档任务"
license: 专有。LICENSE.txt包含完整条款
---

# DOCX创建、编辑和分析

## 概览

用户可能会要求您创建、编辑或分析.docx文件的内容。.docx文件本质上是一个包含XML文件和其他资源的ZIP归档文件，您可以读取或编辑这些内容。针对不同的任务，您可以使用不同的工具和工作流。

## 工作流决策树

### 读取/分析内容
使用下面的"文本提取"或"原始XML访问"部分

### 创建新文档
使用"创建新Word文档"工作流

### 编辑现有文档
- **自己的文档 + 简单修改**
  使用"基本OOXML编辑"工作流

- **他人的文档**
  使用**"红线工作流"**（推荐默认选项）

- **法律、学术、商业或政府文档**
  使用**"红线工作流"**（必须）

## 读取和分析内容

### 文本提取
如果您只需要读取文档的文本内容，应该使用pandoc将文档转换为markdown格式。Pandoc提供了出色的文档结构保留支持，并且可以显示修订跟踪：

```bash
# 将文档转换为带有修订跟踪的markdown格式
pandoc --track-changes=all path-to-file.docx -o output.md
# 选项：--track-changes=accept/reject/all（接受/拒绝/全部修订）
```

### 原始XML访问
您需要原始XML访问以获取以下内容：注释、复杂格式、文档结构、嵌入媒体和元数据。要使用这些功能，您需要解压文档并读取其原始XML内容。

#### 解压文件
`python ooxml/scripts/unpack.py <office_file> <output_directory>`

#### 关键文件结构
* `word/document.xml` - 主要文档内容
* `word/comments.xml` - document.xml中引用的注释
* `word/media/` - 嵌入的图像和媒体文件
* 修订跟踪使用`<w:ins>`（插入）和`<w:del>`（删除）标签

## 创建新Word文档

当从头开始创建新的Word文档时，请使用**docx-js**，它允许您使用JavaScript/TypeScript创建Word文档。

### 工作流
1. **必须 - 阅读整个文件**：完整阅读[`docx-js.md`](docx-js.md)（约500行），从头读到尾。**绝不要设置任何行范围限制**。在开始创建文档之前，请阅读完整的文件内容，以了解详细的语法、关键格式规则和最佳实践。
2. 使用Document、Paragraph、TextRun组件创建JavaScript/TypeScript文件（您可以假设所有依赖项已安装，否则请参考下面的依赖项部分）
3. 使用Packer.toBuffer()导出为.docx格式

## 编辑现有Word文档

当编辑现有Word文档时，请使用**Document库**（一个用于OOXML操作的Python库）。该库会自动处理基础设施设置，并提供文档操作的方法。对于复杂场景，您可以通过该库直接访问底层DOM。

### 工作流
1. **必须 - 阅读整个文件**：完整阅读[`ooxml.md`](ooxml.md)（约600行），从头读到尾。**绝不要设置任何行范围限制**。阅读完整的文件内容，以了解Document库API和直接编辑文档文件的XML模式。
2. 解压文档：`python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. 使用Document库创建并运行Python脚本（请参阅ooxml.md中的"Document Library"部分）
4. 打包最终文档：`python ooxml/scripts/pack.py <input_directory> <office_file>`

Document库既提供了用于常见操作的高级方法，也提供了用于复杂场景的直接DOM访问。

## 文档审阅的红线工作流

此工作流允许您在OOXML中实现修订跟踪之前，使用markdown规划全面的修订跟踪。**关键**：对于完整的修订跟踪，您必须系统地实现所有更改。

**批处理策略**：将相关更改分组为3-10个更改的批次。这使得调试易于管理，同时保持效率。在进入下一批之前测试每一批。

**原则：最小化、精确编辑**
在实现修订跟踪时，只标记实际更改的文本。重复不变的文本会使编辑更难审阅，显得不专业。将替换内容分解为：[不变文本] + [删除内容] + [插入内容] + [不变文本]。通过从原始文本中提取`<w:r>`元素并重新使用它，来保留不变文本的原始运行RSID。

示例 - 将句子中的"30 days"改为"60 days"：
```python
# 不好的做法 - 替换整个句子
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del><w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# 好的做法 - 只标记更改的内容，为不变文本保留原始<w:r>
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r><w:del><w:r><w:delText>30</w:delText></w:r></w:del><w:ins><w:r><w:t>60</w:t></w:r></w:ins><w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

### 修订跟踪工作流

1. **获取markdown表示**：将文档转换为保留修订跟踪的markdown：
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md
   ```

2. **识别并分组更改**：审阅文档并识别所有需要的更改，将它们组织成逻辑批次：

   **定位方法**（用于在XML中查找更改）：
   - 章节/标题编号（例如，"Section 3.2"，"Article IV"）
   - 带编号的段落标识符
   - 带有唯一周围文本的grep模式
   - 文档结构（例如，"第一段"，"签名块"）
   - **不要使用markdown行号** - 它们与XML结构不对应

   **批次组织**（每批分组3-10个相关更改）：
   - 按章节："批次1：第2节修订"，"批次2：第5节更新"
   - 按类型："批次1：日期修正"，"批次2：当事人名称更改"
   - 按复杂度：先进行简单的文本替换，然后处理复杂的结构更改
   - 按顺序："批次1：第1-3页"，"批次2：第4-6页"

3. **阅读文档并解压**：
   - **必须 - 阅读整个文件**：完整阅读[`ooxml.md`](ooxml.md)（约600行），从头读到尾。**绝不要设置任何行范围限制**。特别注意"Document Library"和"Tracked Change Patterns"部分。
   - **解压文档**：`python ooxml/scripts/unpack.py <file.docx> <dir>`
   - **记录建议的RSID**：解压脚本会建议用于您的修订跟踪的RSID。复制此RSID，在步骤4b中使用。

4. **分批实现更改**：将更改按逻辑分组（按章节、类型或位置），并在单个脚本中一起实现。这种方法：
   - 使调试更容易（较小的批次=更容易隔离错误）
   - 允许渐进式进展
   - 保持效率（3-10个更改的批次大小效果良好）

   **建议的批次分组**：
   - 按文档章节（例如，"第3节更改"，"定义"，"终止条款"）
   - 按更改类型（例如，"日期更改"，"当事人名称更新"，"法律术语替换"）
   - 按位置（例如，"第1-3页更改"，"文档前半部分的更改"）

   对于每一批相关更改：

   **a. 将文本映射到XML**：在`word/document.xml`中grep文本，以验证文本如何跨`<w:r>`元素拆分。

   **b. 创建并运行脚本**：使用`get_node`查找节点，实现更改，然后使用`doc.save()`保存。
   有关模式，请参阅ooxml.md中的**"Document Library"**部分。

   **注意**：在编写脚本之前，始终立即grep `word/document.xml`以获取当前行号并验证文本内容。每次脚本运行后，行号都会改变。

5. **打包文档**：所有批次完成后，将解压的目录转换回.docx：
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **最终验证**：对完整文档进行全面检查：
   - 将最终文档转换为markdown：
     ```bash
     pandoc --track-changes=all reviewed-document.docx -o verification.md
     ```
   - 验证所有更改都已正确应用：
     ```bash
     grep "original phrase" verification.md  # 不应找到
     grep "replacement phrase" verification.md  # 应找到
     ```
   - 检查是否引入了意外更改


## 将文档转换为图片

要直观分析Word文档，请使用两步法将其转换为图片：

1. **将DOCX转换为PDF**：
   ```bash
   soffice --headless --convert-to pdf document.docx
   ```

2. **将PDF页面转换为JPEG图片**：
   ```bash
   pdftoppm -jpeg -r 150 document.pdf page
   ```
   这将创建`page-1.jpg`、`page-2.jpg`等文件。

选项说明：
- `-r 150`：将分辨率设置为150 DPI（可根据质量/大小平衡进行调整）
- `-jpeg`：输出JPEG格式（如果需要PNG格式，请使用`-png`）
- `-f N`：要转换的第一页（例如，`-f 2`从第2页开始）
- `-l N`：要转换的最后一页（例如，`-l 5`到第5页结束）
- `page`：输出文件的前缀

特定范围的示例：
```bash
pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page  # 仅转换第2-5页
```

## 代码风格指南
**重要**：在为DOCX操作生成代码时：
- 编写简洁的代码
- 避免冗长的变量名和冗余操作
- 避免不必要的打印语句

## 依赖项

所需依赖项（如果不可用，请安装）：

- **pandoc**：`sudo apt-get install pandoc`（用于文本提取）
- **docx**：`npm install -g docx`（用于创建新文档）
- **LibreOffice**：`sudo apt-get install libreoffice`（用于PDF转换）
- **Poppler**：`sudo apt-get install poppler-utils`（用于pdftoppm将PDF转换为图片）
- **defusedxml**：`pip install defusedxml`（用于安全XML解析）