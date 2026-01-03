# DOCX 库教程

使用 JavaScript/TypeScript 生成 .docx 文件。

**重要提示：在开始前请阅读整个文档。** 本文档涵盖了关键的格式规则和常见陷阱 - 跳过部分内容可能导致文件损坏或渲染问题。

## 设置
假设 docx 已全局安装
如果未安装：`npm install -g docx`

```javascript
// 导入所需的所有组件
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Media, 
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink, 
        InternalHyperlink, TableOfContents, HeadingLevel, BorderStyle, WidthType, TabStopType, 
        TabStopPosition, UnderlineType, ShadingType, VerticalAlign, SymbolRun, PageNumber,
        FootnoteReferenceRun, Footnote, PageBreak } = require('docx');

// 创建文档并保存
const doc = new Document({ sections: [{ children: [/* 内容 */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer)); // Node.js 环境
Packer.toBlob(doc).then(blob => { /* 下载逻辑 */ }); // 浏览器环境
```

## 文本和格式
```javascript
// 重要提示：切勿使用 \n 换行 - 始终使用单独的 Paragraph 元素
// ❌ 错误：new TextRun("第一行\n第二行")
// ✅ 正确：new Paragraph({ children: [new TextRun("第一行")] }), new Paragraph({ children: [new TextRun("第二行")] })

// 包含所有格式选项的基本文本
new Paragraph({
  alignment: AlignmentType.CENTER, // 居中对齐
  spacing: { before: 200, after: 200 }, // 段落前后间距
  indent: { left: 720, right: 720 }, // 左右缩进
  children: [
    new TextRun({ text: "粗体", bold: true }), // 粗体文本
    new TextRun({ text: "斜体", italics: true }), // 斜体文本
    new TextRun({ text: "双下划线", underline: { type: UnderlineType.DOUBLE, color: "FF0000" } }), // 红色双下划线
    new TextRun({ text: "红色文本", color: "FF0000", size: 28, font: "Arial" }), // 红色 14pt Arial 文本
    new TextRun({ text: "黄色高亮", highlight: "yellow" }), // 黄色高亮
    new TextRun({ text: "删除线", strike: true }), // 删除线
    new TextRun({ text: "x2", superScript: true }), // 上标
    new TextRun({ text: "H2O", subScript: true }), // 下标
    new TextRun({ text: "小型大写字母", smallCaps: true }), // 小型大写字母
    new SymbolRun({ char: "2022", font: "Symbol" }), // 项目符号 •
    new SymbolRun({ char: "00A9", font: "Arial" })   // 版权符号 © - 符号使用 Arial 字体
  ]
})
```

## 样式和专业格式

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }, // 默认 12pt 字体
    paragraphStyles: [
      // 文档标题样式 - 覆盖内置的 Title 样式
      { id: "Title", name: "标题", basedOn: "Normal",
        run: { size: 56, bold: true, color: "000000", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      // 重要提示：通过使用确切的 ID 覆盖内置标题样式
      { id: "Heading1", name: "标题 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "000000", font: "Arial" }, // 16pt
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } }, // 目录需要此设置
      { id: "Heading2", name: "标题 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000", font: "Arial" }, // 14pt
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
      // 自定义样式使用您自己的 ID
      { id: "myStyle", name: "我的样式", basedOn: "Normal",
        run: { size: 28, bold: true, color: "000000" },
        paragraph: { spacing: { after: 120 }, alignment: AlignmentType.CENTER } }
    ],
    characterStyles: [{ id: "myCharStyle", name: "我的字符样式",
      run: { color: "FF0000", bold: true, underline: { type: UnderlineType.SINGLE } } }] // 红色粗体单下划线
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } }, // 1 英寸边距
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("文档标题")] }), // 使用覆盖的 Title 样式
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("标题 1")] }), // 使用覆盖的 Heading1 样式
      new Paragraph({ style: "myStyle", children: [new TextRun("自定义段落样式")] }), // 使用自定义样式
      new Paragraph({ children: [
        new TextRun("普通文本与"),
        new TextRun({ text: "自定义字符样式", style: "myCharStyle" }) // 应用自定义字符样式
      ]})
    ]
  }]
});
```

**专业字体组合：**
- **Arial (标题) + Arial (正文)** - 最广泛支持，干净专业
- **Times New Roman (标题) + Arial (正文)** - 经典衬线标题与现代无衬线正文
- **Georgia (标题) + Verdana (正文)** - 优化屏幕阅读，优雅对比

**关键样式原则：**
- **覆盖内置样式**：使用确切的 ID 如 "Heading1"、"Heading2"、"Heading3" 覆盖 Word 的内置标题样式
- **HeadingLevel 常量**：`HeadingLevel.HEADING_1` 使用 "Heading1" 样式，`HeadingLevel.HEADING_2` 使用 "Heading2" 样式，依此类推
- **包含 outlineLevel**：为 H1 设置 `outlineLevel: 0`，为 H2 设置 `outlineLevel: 1` 等，以确保目录正常工作
- **使用自定义样式** 而非内联格式以保持一致性
- **设置默认字体**：使用 `styles.default.document.run.font`，推荐使用 Arial
- **建立视觉层次**：使用不同的字体大小（标题 > 页眉 > 正文）
- **添加适当的间距**：使用段落的 `before` 和 `after` 间距
- **谨慎使用颜色**：标题和页眉默认使用黑色 (000000) 和灰色阴影
- **设置一致的边距**：1440 = 1 英寸（标准边距）


## 列表（始终使用正确的列表 - 切勿使用 Unicode 项目符号）
```javascript
// 项目符号 - 始终使用编号配置，而不是 Unicode 符号
// 关键：使用 LevelFormat.BULLET 常量，而不是字符串 "bullet"
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullet-list", // 项目符号列表引用
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }, // 悬挂缩进
      { reference: "first-numbered-list", // 第一个编号列表引用
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }, // 十进制编号 1., 2., 3.
      { reference: "second-numbered-list", // 第二个编号列表引用（不同引用 = 重新从 1 开始）
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    children: [
      // 项目符号列表项
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("第一个项目符号点")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("第二个项目符号点")] }),
      // 编号列表项
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("第一个编号项")] }),
      new Paragraph({ numbering: { reference: "first-numbered-list", level: 0 },
        children: [new TextRun("第二个编号项")] }),
      // ⚠️ 关键：不同引用 = 独立列表，从 1 重新开始
      // 相同引用 = 继续之前的编号
      new Paragraph({ numbering: { reference: "second-numbered-list", level: 0 },
        children: [new TextRun("再次从 1 开始（因为使用了不同的引用）")] })
    ]
  }]
});

// ⚠️ 关键编号规则：每个引用创建一个独立的编号列表
// - 相同引用 = 继续编号（1, 2, 3... 然后 4, 5, 6...）
// - 不同引用 = 重新从 1 开始（1, 2, 3... 然后 1, 2, 3...）
// 为每个单独的编号部分使用唯一的引用名称！

// ⚠️ 关键：切勿使用 Unicode 项目符号 - 它们会创建无法正常工作的假列表
// new TextRun("• 项")           // 错误
// new SymbolRun({ char: "2022" }) // 错误
// ✅ 始终使用带有 LevelFormat.BULLET 的编号配置创建真正的 Word 列表
```

## 表格
```javascript
// 完整的表格，包含边距、边框、表头和项目符号点
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }; // 表格边框样式
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder }; // 单元格边框

new Table({
  columnWidths: [4680, 4680], // ⚠️ 关键：在表格级别设置列宽 - 值以 DXA（点的二十分之一）为单位
  margins: { top: 100, bottom: 100, left: 180, right: 180 }, // 为所有单元格设置一次边距
  rows: [
    new TableRow({ // 表头行
      tableHeader: true, // 标记为表头
      children: [
        new TableCell({
          borders: cellBorders, // 应用边框
          width: { size: 4680, type: WidthType.DXA }, // 同时在每个单元格上设置宽度
          // ⚠️ 关键：始终使用 ShadingType.CLEAR 以防止 Word 中出现黑色背景
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, 
          verticalAlign: VerticalAlign.CENTER, // 垂直居中
          children: [new Paragraph({ 
            alignment: AlignmentType.CENTER, // 水平居中
            children: [new TextRun({ text: "表头", bold: true, size: 22 })] // 加粗文本
          })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 同时在每个单元格上设置宽度
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          children: [new Paragraph({ 
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "项目符号点", bold: true, size: 22 })]
          })]
        })
      ]
    }),
    new TableRow({ // 数据行
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 同时在每个单元格上设置宽度
          children: [new Paragraph({ children: [new TextRun("常规数据")] })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA }, // 同时在每个单元格上设置宽度
          children: [
            new Paragraph({ 
              numbering: { reference: "bullet-list", level: 0 }, // 使用之前定义的项目符号列表
              children: [new TextRun("第一个项目符号点")] 
            }),
            new Paragraph({ 
              numbering: { reference: "bullet-list", level: 0 },
              children: [new TextRun("第二个项目符号点")] 
            })
          ]
        })
      ]
    })
  ]
})
```

**重要提示：表格宽度和边框**
- 同时使用 `columnWidths: [width1, width2, ...]` 数组和每个单元格上的 `width: { size: X, type: WidthType.DXA }`
- DXA（点的二十分之一）单位：1440 = 1 英寸，Letter 尺寸可用宽度 = 9360 DXA（带 1" 边距）
- 将边框应用于单个 `TableCell` 元素，而不是 `Table` 本身

**预计算列宽（带 1" 边距的 Letter 尺寸 = 总宽度 9360 DXA）：**
- **2 列：** `columnWidths: [4680, 4680]`（等宽）
- **3 列：** `columnWidths: [3120, 3120, 3120]`（等宽）

## 链接和导航
```javascript
// 目录（需要标题）- 关键：仅使用 HeadingLevel，不使用自定义样式
// ❌ 错误：new Paragraph({ heading: HeadingLevel.HEADING_1, style: "customHeader", children: [new TextRun("标题")] })
// ✅ 正确：new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("标题")] })
new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }), // 包含 1-3 级标题的目录

// 外部链接
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "谷歌", style: "Hyperlink" })], // 使用内置的 Hyperlink 样式
    link: "https://www.google.com" // 链接 URL
  })]
}),

// 内部链接和书签
new Paragraph({
  children: [new InternalHyperlink({
    children: [new TextRun({ text: "跳转到章节", style: "Hyperlink" })],
    anchor: "section1" // 书签 ID
  })]
}),
new Paragraph({
  children: [new TextRun("章节内容")],
  bookmark: { id: "section1", name: "section1" } // 定义书签
}),
```

## 图片和媒体
```javascript
// 带大小和定位的基本图片
// 关键：始终指定 'type' 参数 - ImageRun 必需此参数
new Paragraph({
  alignment: AlignmentType.CENTER, // 图片居中
  children: [new ImageRun({
    type: "png", // 新要求：必须指定图片类型（png, jpg, jpeg, gif, bmp, svg）
    data: fs.readFileSync("image.png"), // 读取图片数据
    transformation: { width: 200, height: 150, rotation: 0 }, // 宽度、高度和旋转角度（度）
    altText: { title: "Logo", description: "公司标志", name: "名称" } // 重要：所有三个字段都需要
  })]
})
```

## 分页符
```javascript
// 手动分页符
new Paragraph({ children: [new PageBreak()] }),

// 段落前分页
new Paragraph({
  pageBreakBefore: true, // 在段落前插入分页符
  children: [new TextRun("这从新页面开始")]
})

// ⚠️ 关键：切勿单独使用 PageBreak - 它会创建 Word 无法打开的无效 XML
// ❌ 错误：new PageBreak() 
// ✅ 正确：new Paragraph({ children: [new PageBreak()] })
```

## 页眉/页脚和页面设置
```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1440 = 1 英寸边距
        size: { orientation: PageOrientation.LANDSCAPE }, // 横向页面
        pageNumbers: { start: 1, formatType: "decimal" } // 页码从 1 开始，十进制格式
        // 可选格式："upperRoman"（大写罗马数字）、"lowerRoman"（小写罗马数字）、"upperLetter"（大写字母）、"lowerLetter"（小写字母）
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT, // 右对齐页眉
        children: [new TextRun("页眉文本")]
      })] })        
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER, // 居中页脚
        children: [
          new TextRun("第 "), 
          new TextRun({ children: [PageNumber.CURRENT] }), // 当前页码
          new TextRun(" 页，共 "), 
          new TextRun({ children: [PageNumber.TOTAL_PAGES] }) // 总页数
        ]
      })] })        
    },
    children: [/* 内容 */]
  }]
});
```

## 制表符
```javascript
new Paragraph({
  tabStops: [ // 定义制表位
    { type: TabStopType.LEFT, position: TabStopPosition.MAX / 4 }, // 左对齐，25% 宽度位置
    { type: TabStopType.CENTER, position: TabStopPosition.MAX / 2 }, // 居中对齐，50% 宽度位置
    { type: TabStopType.RIGHT, position: TabStopPosition.MAX * 3 / 4 } // 右对齐，75% 宽度位置
  ],
  children: [new TextRun("左\t中\t右")] // 使用 \t 分隔制表位内容
})
```

## 常量和快速参考
- **下划线：** `SINGLE`（单下划线）、`DOUBLE`（双下划线）、`WAVY`（波浪线）、`DASH`（虚线）
- **边框：** `SINGLE`（单实线）、`DOUBLE`（双实线）、`DASHED`（虚线）、`DOTTED`（点线）  
- **编号：** `DECIMAL`（1,2,3）、`UPPER_ROMAN`（I,II,III）、`LOWER_LETTER`（a,b,c）
- **制表符：** `LEFT`（左对齐）、`CENTER`（居中对齐）、`RIGHT`（右对齐）、`DECIMAL`（小数对齐）
- **符号：** `"2022"`（•）、`"00A9"`（©）、`"00AE"`（®）、`"2122"`（™）、`"00B0"`（°）、`"F070"`（✓）、`"F0FC"`（✗）

## 关键问题和常见错误
- **关键：PageBreak 必须始终位于 Paragraph 内部** - 单独的 PageBreak 会创建 Word 无法打开的无效 XML
- **始终为表格单元格底纹使用 ShadingType.CLEAR** - 切勿使用 ShadingType.SOLID（会导致黑色背景）
- 测量单位为 DXA（1440 = 1 英寸）| 每个表格单元格需要 ≥1 个 Paragraph | 目录仅需要 HeadingLevel 样式
- **始终使用自定义样式** 并使用 Arial 字体，以获得专业外观和适当的视觉层次
- **始终设置默认字体**：使用 `styles.default.document.run.font`，推荐使用 Arial
- **始终为表格使用 columnWidths 数组** + 单个单元格宽度以提高兼容性
- **切勿为项目符号使用 Unicode 符号** - 始终使用带有 `LevelFormat.BULLET` 常量（不是字符串 "bullet"）的正确编号配置
- **切勿在任何地方使用 \n 换行** - 始终为每行使用单独的 Paragraph 元素
- **始终在 Paragraph 的 children 中使用 TextRun 对象** - 切勿直接在 Paragraph 上使用 text 属性
- **图片的关键要求**：ImageRun 需要 `type` 参数 - 始终指定 "png"、"jpg"、"jpeg"、"gif"、"bmp" 或 "svg"
- **项目符号的关键要求**：必须使用 `LevelFormat.BULLET` 常量，而不是字符串 "bullet"，并为项目符号字符包含 `text: "•"`
- **编号的关键要求**：每个编号引用创建一个独立的列表。相同引用 = 继续编号（1,2,3 然后 4,5,6）。不同引用 = 重新从 1 开始（1,2,3 然后 1,2,3）。为每个单独的编号部分使用唯一的引用名称！
- **目录的关键要求**：使用 TableOfContents 时，标题必须仅使用 HeadingLevel - 切勿在标题段落中添加自定义样式，否则目录会失效
- **表格**：设置 `columnWidths` 数组 + 单个单元格宽度，将边框应用于单元格而不是表格
- **在表格级别设置表格边距**：以获得一致的单元格填充（避免每个单元格重复设置）