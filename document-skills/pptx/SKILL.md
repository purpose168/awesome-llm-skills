---
name: pptx
description: "演示文稿创建、编辑和分析。当Claude需要处理演示文稿（.pptx文件）时使用，包括：(1) 创建新演示文稿，(2) 修改或编辑内容，(3) 使用布局，(4) 添加注释或演讲者备注，或执行其他任何演示文稿相关任务"
license: 专有。LICENSE.txt包含完整条款
---

# PPTX 创建、编辑和分析

## 概述

用户可能会要求您创建、编辑或分析.pptx文件的内容。.pptx文件本质上是一个包含XML文件和其他资源的ZIP归档文件，您可以读取或编辑这些文件。针对不同的任务，您可以使用不同的工具和工作流程。

## 内容读取和分析

### 文本提取
如果您只需要读取演示文稿的文本内容，您应该将文档转换为markdown格式：

```bash
# 将文档转换为markdown
python -m markitdown path-to-file.pptx
```

### 原始XML访问
您需要原始XML访问来获取以下内容：注释、演讲者备注、幻灯片布局、动画、设计元素和复杂格式。对于这些功能中的任何一个，您都需要解包演示文稿并读取其原始XML内容。

#### 解包文件
`python ooxml/scripts/unpack.py <office_file> <output_dir>`

**注意**：unpack.py脚本位于项目根目录下的`skills/pptx/ooxml/scripts/unpack.py`。如果该脚本不存在于此路径，请使用`find . -name "unpack.py"`命令定位它。

#### 关键文件结构
* `ppt/presentation.xml` - 主演示文稿元数据和幻灯片引用
* `ppt/slides/slide{N}.xml` - 单个幻灯片内容（slide1.xml、slide2.xml等）
* `ppt/notesSlides/notesSlide{N}.xml` - 每张幻灯片的演讲者备注
* `ppt/comments/modernComment_*.xml` - 特定幻灯片的注释
* `ppt/slideLayouts/` - 幻灯片布局模板
* `ppt/slideMasters/` - 母版幻灯片模板
* `ppt/theme/` - 主题和样式信息
* `ppt/media/` - 图像和其他媒体文件

#### 排版和颜色提取
**当需要模仿示例设计时**：始终首先使用以下方法分析演示文稿的排版和颜色：
1. **读取主题文件**：检查`ppt/theme/theme1.xml`中的颜色（`<a:clrScheme>`）和字体（`<a:fontScheme>`）
2. **样本幻灯片内容**：检查`ppt/slides/slide1.xml`中的实际字体使用（`<a:rPr>`）和颜色
3. **搜索模式**：使用grep命令查找所有XML文件中的颜色（`<a:solidFill>`、`<a:srgbClr>`）和字体引用

## 从头创建新的PowerPoint演示文稿 **（无模板）**

当从头创建新的PowerPoint演示文稿时，使用**html2pptx**工作流程将HTML幻灯片转换为PowerPoint，以实现精确定位。

### 设计原则

**关键提示**：在创建任何演示文稿之前，分析内容并选择适当的设计元素：
1. **考虑主题**：这个演示文稿是关于什么的？它暗示了什么基调、行业或情绪？
2. **检查品牌标识**：如果用户提到公司/组织，考虑他们的品牌颜色和标识
3. **根据内容匹配调色板**：选择能反映主题的颜色
4. **说明您的方法**：在编写代码之前解释您的设计选择

**要求**：
- ✅ 在编写代码之前说明基于内容的设计方法
- ✅ 仅使用网页安全字体：Arial、Helvetica、Times New Roman、Georgia、Courier New、Verdana、Tahoma、Trebuchet MS、Impact
- ✅ 通过大小、粗细和颜色创建清晰的视觉层次
- ✅ 确保可读性：强烈的对比度、适当大小的文本、清晰的对齐方式
- ✅ 保持一致性：在幻灯片之间重复使用模式、间距和视觉语言

#### 颜色调色板选择

**创造性地选择颜色**：
- **超越默认值**：什么颜色真正匹配这个特定主题？避免自动选择。
- **考虑多个角度**：主题、行业、情绪、能量水平、目标受众、品牌标识（如果提到）
- **勇于尝试**：尝试意想不到的组合 - 医疗保健演示文稿不一定要是绿色，金融演示文稿不一定要是深蓝色
- **构建您的调色板**：选择3-5种协同工作的颜色（主导色+辅助色+强调色）
- **确保对比度**：文本在背景上必须清晰可读

**示例颜色调色板**（使用这些来激发创造力 - 选择一个、调整它或创建您自己的）：

1. **经典蓝色**：深蓝色 (#1C2833)、板岩灰色 (#2E4053)、银色 (#AAB7B8)、米白色 (#F4F6F6)
2. **青绿色与珊瑚色**：青绿色 (#5EA8A7)、深青绿色 (#277884)、珊瑚色 (#FE4447)、白色 (#FFFFFF)
3. **大胆红色**：红色 (#C0392B)、亮红色 (#E74C3C)、橙色 (#F39C12)、黄色 (#F1C40F)、绿色 (#2ECC71)
4. **温暖腮红**：淡紫色 (#A49393)、腮红 (#EED6D3)、玫瑰色 (#E8B4B8)、奶油色 (#FAF7F2)
5. **勃艮第奢华**：勃艮第 (#5D1D2E)、深红色 (#951233)、铁锈色 (#C15937)、金色 (#997929)
6. **深紫色与祖母绿**：紫色 (#B165FB)、深蓝色 (#181B24)、祖母绿 (#40695B)、白色 (#FFFFFF)
7. **奶油色与森林绿**：奶油色 (#FFE1C7)、森林绿 (#40695B)、白色 (#FCFCFC)
8. **粉色与紫色**：粉色 (#F8275B)、珊瑚色 (#FF574A)、玫瑰色 (#FF737D)、紫色 (#3D2F68)
9. **酸橙绿与李子色**：酸橙绿 (#C5DE82)、李子色 (#7C3A5F)、珊瑚色 (#FD8C6E)、蓝灰色 (#98ACB5)
10. **黑色与金色**：金色 (#BF9A4A)、黑色 (#000000)、奶油色 (#F4F6F6)
11. **鼠尾草绿与赤陶色**：鼠尾草绿 (#87A96B)、赤陶色 (#E07A5F)、奶油色 (#F4F1DE)、炭灰色 (#2C2C2C)
12. **炭灰色与红色**：炭灰色 (#292929)、红色 (#E33737)、浅灰色 (#CCCBCB)
13. **充满活力的橙色**：橙色 (#F96D00)、浅灰色 (#F2F2F2)、炭灰色 (#222831)
14. **森林绿**：黑色 (#191A19)、绿色 (#4E9F3D)、深绿色 (#1E5128)、白色 (#FFFFFF)
15. **复古彩虹**：紫色 (#722880)、粉色 (#D72D51)、橙色 (#EB5C18)、琥珀色 (#F08800)、金色 (#DEB600)
16. **复古土色**：芥末色 (#E3B448)、鼠尾草绿 (#CBD18F)、森林绿 (#3A6B35)、奶油色 (#F4F1DE)
17. **海岸玫瑰**：旧玫瑰色 (#AD7670)、海狸色 (#B49886)、蛋壳色 (#F3ECDC)、灰绿色 (#BFD5BE)
18. **橙色与绿松石色**：浅橙色 (#FC993E)、灰绿松石色 (#667C6F)、白色 (#FCFCFC)

#### 视觉细节选项

**几何图案**：
- 使用对角线分隔符而不是水平线
- 不对称列宽（30/70、40/60、25/75）
- 90°或270°旋转的文本标题
- 图像的圆形/六边形框架
- 角落的三角形强调形状
- 重叠形状以增加深度

**边框与框架处理**：
- 仅在一侧使用粗单色边框（10-20pt）
- 双线条边框，使用对比色
- 角落括号代替完整框架
- L形边框（顶部+左侧或底部+右侧）
- 标题下方的下划线强调（3-5pt粗）

**排版处理**：
- 极端大小对比（72pt标题与11pt正文）
- 全大写标题，字母间距宽
- 超大显示类型的编号部分
- 数据/统计/技术内容使用等宽字体（Courier New）
- 密集信息使用紧凑字体（Arial Narrow）
- 轮廓文字用于强调

**图表与数据样式**：
- 单色图表，关键数据使用单一强调色
- 水平条形图代替垂直条形图
- 点图代替条形图
- 最少的网格线或完全没有
- 数据标签直接放在元素上（无图例）
- 关键指标使用超大数字

**布局创新**：
- 全屏图像与文本叠加
- 侧边栏列（20-30%宽度）用于导航/上下文
- 模块化网格系统（3×3、4×4块）
- Z型或F型内容流
- 彩色形状上的浮动文本框
- 杂志风格的多列布局

**背景处理**：
- 占幻灯片40-60%的纯色块
- 渐变填充（仅垂直或对角线）
- 分割背景（两种颜色，对角线或垂直）
- 从边缘到边缘的色带
- 负空间作为设计元素

### 布局技巧
**创建包含图表或表格的幻灯片时**：
- **两列布局（首选）**：使用横跨整个宽度的标题，然后是下方的两列 - 一列用于文本/项目符号，另一列用于特色内容。这提供了更好的平衡，使图表/表格更易读。使用不等宽的弹性布局（例如40%/60%分割）为每种内容类型优化空间。
- **全屏布局**：让特色内容（图表/表格）占据整个幻灯片，以获得最大的影响力和可读性
- **绝不要垂直堆叠**：不要将图表/表格放在文本下方的单列中 - 这会导致可读性差和布局问题

### 工作流程
1. **必须 - 阅读整个文件**：完整阅读[`html2pptx.md`](html2pptx.md)文件的内容。**阅读此文件时绝不要设置任何范围限制**。在继续创建演示文稿之前，阅读完整的文件内容以了解详细语法、关键格式规则和最佳实践。
2. 为每张幻灯片创建一个具有适当尺寸的HTML文件（例如16:9比例使用720pt × 405pt）
   - 使用`<p>`、`<h1>`-`<h6>`、`<ul>`、`<ol>`用于所有文本内容
   - 使用`class="placeholder"`标记将添加图表/表格的区域（渲染时使用灰色背景以提高可见性）
   - **关键提示**：首先使用Sharp将渐变和图标光栅化为PNG图像，然后在HTML中引用
   - **布局**：对于包含图表/表格/图像的幻灯片，使用全屏布局或两列布局以提高可读性
3. 使用[`html2pptx.js`](scripts/html2pptx.js)库创建并运行JavaScript文件，将HTML幻灯片转换为PowerPoint并保存演示文稿
   - 使用`html2pptx()`函数处理每个HTML文件
   - 使用PptxGenJS API将图表和表格添加到占位符区域
   - 使用`pptx.writeFile()`保存演示文稿
4. **视觉验证**：生成缩略图并检查布局问题
   - 创建缩略图网格：`python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - 读取并仔细检查缩略图，查看：
     - **文本截断**：文本被标题栏、形状或幻灯片边缘截断
     - **文本重叠**：文本与其他文本或形状重叠
     - **定位问题**：内容离幻灯片边界或其他元素太近
     - **对比度问题**：文本和背景之间的对比度不足
   - 如果发现问题，调整HTML边距/间距/颜色并重新生成演示文稿
   - 重复此过程，直到所有幻灯片在视觉上都正确

## 编辑现有PowerPoint演示文稿

当编辑现有PowerPoint演示文稿中的幻灯片时，您需要处理原始Office Open XML (OOXML)格式。这包括解包.pptx文件、编辑XML内容，然后重新打包。

### 工作流程
1. **必须 - 阅读整个文件**：完整阅读[`ooxml.md`](ooxml.md)（约500行）的内容。**阅读此文件时绝不要设置任何范围限制**。在进行任何演示文稿编辑之前，阅读完整的文件内容以了解OOXML结构和编辑工作流程的详细指导。
2. 解包演示文稿：`python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. 编辑XML文件（主要是`ppt/slides/slide{N}.xml`和相关文件）
4. **关键提示**：每次编辑后立即验证并修复所有验证错误，然后再继续：`python ooxml/scripts/validate.py <dir> --original <file>`
5. 打包最终演示文稿：`python ooxml/scripts/pack.py <input_directory> <office_file>`

## 使用模板创建新的PowerPoint演示文稿

当您需要创建一个遵循现有模板设计的演示文稿时，您需要先复制和重新排列模板幻灯片，然后替换占位符内容。

### 工作流程
1. **提取模板文本并创建视觉缩略图网格**：
   * 提取文本：`python -m markitdown template.pptx > template-content.md`
   * 读取`template-content.md`：阅读整个文件以了解模板演示文稿的内容。**阅读此文件时绝不要设置任何范围限制**。
   * 创建缩略图网格：`python scripts/thumbnail.py template.pptx`
   * 有关更多详细信息，请参见[创建缩略图网格](#创建缩略图网格)部分

2. **分析模板并将清单保存到文件**：
   * **视觉分析**：查看缩略图网格以了解幻灯片布局、设计模式和视觉结构
   * 创建并保存一个位于`template-inventory.md`的模板清单文件，包含：
     ```markdown
     # 模板清单分析
     **总幻灯片数：[count]**
     **重要提示：幻灯片采用0索引（第一张幻灯片=0，最后一张幻灯片=count-1）**

     ## [类别名称]
     - 幻灯片0：[可用的布局代码] - 描述/用途
     - 幻灯片1：[布局代码] - 描述/用途
     - 幻灯片2：[布局代码] - 描述/用途
     [... 每一张幻灯片都必须单独列出其索引 ...]
     ```
   * **使用缩略图网格**：参考视觉缩略图以识别：
     - 布局模式（标题幻灯片、内容布局、节分隔符）
     - 图像占位符的位置和数量
     - 幻灯片组之间的设计一致性
     - 视觉层次和结构
   * 此清单文件是下一步选择合适模板的必需文件

3. **基于模板清单创建演示文稿大纲**：
   * 查看步骤2中可用的模板
   * 为第一张幻灯片选择介绍或标题模板。这应该是前几个模板之一
   * 为其他幻灯片选择安全的、基于文本的布局
   * **关键提示：将布局结构与实际内容匹配**：
     - 单列布局：用于统一的叙述或单一主题
     - 两列布局：仅在您有恰好2个不同项目/概念时使用
     - 三列布局：仅在您有恰好3个不同项目/概念时使用
     - 图像+文本布局：仅在您有实际要插入的图像时使用
     - 引用布局：仅用于来自人的实际引用（带出处），绝不要用于强调
     - 永远不要使用占位符数量多于您拥有的内容的布局
     - 如果您有2个项目，不要强行将它们放入3列布局
     - 如果您有4个或更多项目，请考虑分成多张幻灯片或使用列表格式
   * 在选择布局之前先计算您的实际内容块数量
   * 验证所选布局中的每个占位符都将填充有意义的内容
   * 为每个内容部分选择代表**最佳**布局的选项
   * 保存包含内容和模板映射的`outline.md`，利用可用的设计
   * 示例模板映射：
      ```
      # 要使用的模板幻灯片（0索引）
      # 警告：验证索引是否在范围内！包含73张幻灯片的模板索引为0-72
      # 映射：大纲中的幻灯片编号 -> 模板幻灯片索引
      template_mapping = [
          0,   # 使用幻灯片0（标题/封面）
          34,  # 使用幻灯片34（B1：标题和正文）
          34,  # 再次使用幻灯片34（为第二个B1重复）
          50,  # 使用幻灯片50（E1：引用）
          54,  # 使用幻灯片54（F2：结尾+文本）
      ]
      ```

4. **使用`rearrange.py`复制、重新排序和删除幻灯片**：
   * 使用`scripts/rearrange.py`脚本创建一个包含所需顺序幻灯片的新演示文稿：
     ```bash
     python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
     ```
   * 该脚本自动处理重复幻灯片、删除未使用的幻灯片和重新排序
   * 幻灯片索引采用0索引（第一张幻灯片是0，第二张是1，依此类推）
   * 相同的幻灯片索引可以多次出现以复制该幻灯片

5. **使用`inventory.py`脚本提取所有文本**：
   * **运行清单提取**：
     ```bash
     python scripts/inventory.py working.pptx text-inventory.json
     ```
   * **读取text-inventory.json**：阅读整个text-inventory.json文件以了解所有形状及其属性。**阅读此文件时绝不要设置任何范围限制**。

   * 清单JSON结构：
      ```json
        {
          "slide-0": {
            "shape-0": {
              "placeholder_type": "TITLE",  // 或null表示非占位符
              "left": 1.5,                  // 位置（英寸）
              "top": 2.0,
              "width": 7.5,
              "height": 1.2,
              "paragraphs": [
                {
                  "text": "Paragraph text",
                  // 可选属性（仅当非默认值时包含）：
                  "bullet": true,           // 检测到显式项目符号
                  "level": 0,               // 仅当bullet为true时包含
                  "alignment": "CENTER",    // CENTER、RIGHT（不包括LEFT）
                  "space_before": 10.0,     // 段落前间距（磅）
                  "space_after": 6.0,       // 段落后间距（磅）
                  "line_spacing": 22.4,     // 行间距（磅）
                  "font_name": "Arial",     // 来自第一个run
                  "font_size": 14.0,        // 磅
                  "bold": true,
                  "italic": false,
                  "underline": false,
                  "color": "FF0000"         // RGB颜色
                }
              ]
            }
          }
        }
      ```

   * 关键特性：
     - **幻灯片**：命名为"slide-0"、"slide-1"等
     - **形状**：按视觉位置（从上到下、从左到右）排序，命名为"shape-0"、"shape-1"等
     - **占位符类型**：TITLE、CENTER_TITLE、SUBTITLE、BODY、OBJECT或null
     - **默认字体大小**：`default_font_size`（从布局占位符中提取的磅值，当可用时）
     - **幻灯片编号被过滤**：具有SLIDE_NUMBER占位符类型的形状会自动从清单中排除
     - **项目符号**：当`bullet: true`时，`level`总是包含（即使为0）
     - **间距**：`space_before`、`space_after`和`line_spacing`（以磅为单位，仅当设置时包含）
     - **颜色**：RGB使用`color`（例如"FF0000"），主题颜色使用`theme_color`（例如"DARK_1"）
     - **属性**：仅包含非默认值

6. **生成替换文本并将数据保存到JSON文件**
   基于上一步的文本清单：
   - **关键提示**：首先验证清单中存在哪些形状 - 仅引用实际存在的形状
   - **验证**：replace.py脚本将验证替换JSON中的所有形状是否都存在于清单中
     - 如果您引用了不存在的形状，您将收到错误，显示可用的形状
     - 如果您引用了不存在的幻灯片，您将收到错误，表明幻灯片不存在
     - 所有验证错误都会在脚本退出前一次性显示
   - **重要提示**：replace.py脚本内部使用inventory.py来识别所有文本形状
   - **自动清除**：清单中的所有文本形状将被清除，除非您为它们提供"paragraphs"
   - 为需要内容的形状添加"paragraphs"字段（不是"replacement_paragraphs"）
   - 替换JSON中没有"paragraphs"的形状将自动清除其文本
   - 带有项目符号的段落将自动左对齐。当`"bullet": true`时，不要设置`alignment`属性
   - 为占位符文本生成适当的替换内容
   - 使用形状大小确定适当的内容长度
   - **关键提示**：包含原始清单中的段落属性 - 不要只提供文本
   - **重要提示**：当bullet: true时，不要在文本中包含项目符号符号（•、-、*） - 它们会自动添加
   - **基本格式规则**：
     - 标题通常应具有`"bold": true`
     - 列表项应具有`"bullet": true, "level": 0`（当bullet为true时需要level）
     - 保留任何对齐属性（例如，居中文本使用`"alignment": "CENTER"`）
     - 当与默认不同时，包含字体属性（例如，`"font_size": 14.0`、`"font_name": "Lora"`）
     - 颜色：RGB使用`"color": "FF0000"`，主题颜色使用`"theme_color": "DARK_1"`
     - 替换脚本需要**格式正确的段落**，而不仅仅是文本字符串
     - **重叠形状**：优先选择具有更大default_font_size或更合适placeholder_type的形状
   - 将带有替换内容的更新清单保存到`replacement-text.json`
   - **警告**：不同的模板布局具有不同的形状数量 - 在创建替换内容之前始终检查实际清单

   显示正确格式的示例paragraphs字段：
   ```json
   "paragraphs": [
     {
       "text": "New presentation title text",
       "alignment": "CENTER",
       "bold": true
     },
     {
       "text": "Section Header",
       "bold": true
     },
     {
       "text": "First bullet point without bullet symbol",
       "bullet": true,
       "level": 0
     },
     {
       "text": "Red colored text",
       "color": "FF0000"
     },
     {
       "text": "Theme colored text",
       "theme_color": "DARK_1"
     },
     {
       "text": "Regular paragraph text without special formatting"
     }
   ]
   ```

   **替换JSON中未列出的形状会被自动清除**：
   ```json
   {
     "slide-0": {
       "shape-0": {
         "paragraphs": [...] // 此形状获取新文本
       }
       // 清单中的shape-1和shape-2会被自动清除
     }
   }
   ```

   **演示文稿的常见格式模式**：
   - 标题幻灯片：粗体文本，有时居中
   - 幻灯片内的节标题：粗体文本
   - 项目符号列表：每个项目需要 `"bullet": true, "level": 0`
   - 正文文本：通常不需要特殊属性
   - 引用：可能有特殊的对齐或字体属性

7. **使用`replace.py`脚本应用替换**
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```

   该脚本将：
   - 首先使用inventory.py中的函数提取所有文本形状的清单
   - 验证替换JSON中的所有形状是否存在于清单中
   - 清除清单中标识的所有形状的文本
   - 仅将新文本应用于替换JSON中定义了"paragraphs"的形状
   - 通过应用JSON中的段落属性来保留格式
   - 自动处理项目符号、对齐方式、字体属性和颜色
   - 保存更新后的演示文稿

   示例验证错误：
   ```
   ERROR: 替换JSON中的无效形状：
     - 在'slide-0'上未找到形状'shape-99'。可用形状：shape-0, shape-1, shape-4
     - 清单中未找到幻灯片'slide-999'
   ```

   ```
   ERROR: 替换文本使这些形状的溢出情况更糟：
     - slide-0/shape-2: 溢出增加了1.25"（原0.00"，现1.25"）
   ```

## 创建缩略图网格

创建PowerPoint幻灯片的视觉缩略图网格，用于快速分析和参考：

```bash
python scripts/thumbnail.py template.pptx [output_prefix]
```

**功能**：
- 创建：`thumbnails.jpg`（对于大型演示文稿，使用`thumbnails-1.jpg`、`thumbnails-2.jpg`等）
- 默认：5列，每个网格最多30张幻灯片（5×6）
- 自定义前缀：`python scripts/thumbnail.py template.pptx my-grid`
  - 注意：如果要在特定目录输出，输出前缀应包含路径（例如：`workspace/my-grid`）
- 调整列数：`--cols 4`（范围：3-6，影响每个网格的幻灯片数量）
- 网格限制：3列=每个网格12张幻灯片，4列=20，5列=30，6列=42
- 幻灯片采用0索引（Slide 0, Slide 1等）

**用例**：
- 模板分析：快速了解幻灯片布局和设计模式
- 内容审查：演示文稿的视觉概览
- 导航参考：通过视觉外观查找特定幻灯片
- 质量检查：验证所有幻灯片是否格式正确

**示例**：
```bash
# 基本用法
python scripts/thumbnail.py presentation.pptx

# 组合选项：自定义名称、列数
python scripts/thumbnail.py template.pptx analysis --cols 4
```

## 将幻灯片转换为图像

要可视化分析PowerPoint幻灯片，请使用两步过程将它们转换为图像：

1. **将PPTX转换为PDF**：
   ```bash
   soffice --headless --convert-to pdf template.pptx
   ```

2. **将PDF页面转换为JPEG图像**：
   ```bash
   pdftoppm -jpeg -r 150 template.pdf slide
   ```
   这将创建`slide-1.jpg`、`slide-2.jpg`等文件。

选项：
- `-r 150`：将分辨率设置为150 DPI（根据质量/大小平衡调整）
- `-jpeg`：输出JPEG格式（如果需要PNG，使用`-png`）
- `-f N`：要转换的第一页（例如，`-f 2`从第2页开始）
- `-l N`：要转换的最后一页（例如，`-l 5`在第5页停止）
- `slide`：输出文件的前缀

特定范围的示例：
```bash
pdftoppm -jpeg -r 150 -f 2 -l 5 template.pdf slide  # 仅转换第2-5页
```

## 代码风格指南
**重要**：在生成用于PPTX操作的代码时：
- 编写简洁的代码
- 避免冗长的变量名和冗余操作
- 避免不必要的打印语句

## 依赖项

所需依赖项（应已安装）：

- **markitdown**：`pip install "markitdown[pptx]"`（用于从演示文稿中提取文本）
- **pptxgenjs**：`npm install -g pptxgenjs`（用于通过html2pptx创建演示文稿）
- **playwright**：`npm install -g playwright`（用于html2pptx中的HTML渲染）
- **react-icons**：`npm install -g react-icons react react-dom`（用于图标）
- **sharp**：`npm install -g sharp`（用于SVG光栅化和图像处理）
- **LibreOffice**：`sudo apt-get install libreoffice`（用于PDF转换）
- **Poppler**：`sudo apt-get install poppler-utils`（用于pdftoppm将PDF转换为图像）
- **defusedxml**：`pip install defusedxml`（用于安全的XML解析）