# PowerPoint的Office Open XML技术参考

**重要提示：开始前请完整阅读本文档。** 本文档涵盖了关键的XML模式规则和格式要求。不正确的实现可能会创建PowerPoint无法打开的无效PPTX文件。

## 技术指南

### 模式合规性
- **`<p:txBody>`中的元素顺序**：`<a:bodyPr>`、`<a:lstStyle>`、`<a:p>`
- **空白处理**：为带有前导/尾随空格的`<a:t>`元素添加`xml:space='preserve'`
- **Unicode字符**：在ASCII内容中转义字符：`"`变为`&#8220;`
- **图像**：添加到`ppt/media/`，在幻灯片XML中引用，设置尺寸以适应幻灯片边界
- **关系**：更新每张幻灯片资源的`ppt/slides/_rels/slideN.xml.rels`
- **Dirty属性**：向`<a:rPr>`和`<a:endParaRPr>`元素添加`dirty="0"`以指示干净状态

## 演示文稿结构

### 基本幻灯片结构
```xml
<!-- ppt/slides/slide1.xml -->
<p:sld>
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>...</p:nvGrpSpPr>
      <p:grpSpPr>...</p:grpSpPr>
      <!-- 形状放置在此处 -->
    </p:spTree>
  </p:cSld>
</p:sld>
```

### 文本框/带有文本的形状
```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="2" name="Title"/>
    <p:cNvSpPr>
      <a:spLocks noGrp="1"/>
    </p:cNvSpPr>
    <p:nvPr>
      <p:ph type="ctrTitle"/>
    </p:nvPr>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="838200" y="365125"/>
      <a:ext cx="7772400" cy="1470025"/>
    </a:xfrm>
  </p:spPr>
  <p:txBody>
    <a:bodyPr/>
    <a:lstStyle/>
    <a:p>
      <a:r>
        <a:t>幻灯片标题</a:t>
      </a:r>
    </a:p>
  </p:txBody>
</p:sp>
```

### 文本格式化
```xml
<!-- 粗体 -->
<a:r>
  <a:rPr b="1"/>
  <a:t>粗体文本</a:t>
</a:r>

<!-- 斜体 -->
<a:r>
  <a:rPr i="1"/>
  <a:t>斜体文本</a:t>
</a:r>

<!-- 下划线 -->
<a:r>
  <a:rPr u="sng"/>
  <a:t>带下划线的文本</a:t>
</a:r>

<!-- 高亮 -->
<a:r>
  <a:rPr>
    <a:highlight>
      <a:srgbClr val="FFFF00"/>
    </a:highlight>
  </a:rPr>
  <a:t>高亮文本</a:t>
</a:r>

<!-- 字体和大小 -->
<a:r>
  <a:rPr sz="2400" typeface="Arial">
    <a:solidFill>
      <a:srgbClr val="FF0000"/>
    </a:solidFill>
  </a:rPr>
  <a:t>红色Arial 24pt字体</a:t>
</a:r>

<!-- 完整格式化示例 -->
<a:r>
  <a:rPr lang="en-US" sz="1400" b="1" dirty="0">
    <a:solidFill>
      <a:srgbClr val="FAFAFA"/>
    </a:solidFill>
  </a:rPr>
  <a:t>格式化文本</a:t>
</a:r>
```

### 列表
```xml
<!-- 项目符号列表 -->
<a:p>
  <a:pPr lvl="0">
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:t>第一个项目符号点</a:t>
  </a:r>
</a:p>

<!-- 编号列表 -->
<a:p>
  <a:pPr lvl="0">
    <a:buAutoNum type="arabicPeriod"/>
  </a:pPr>
  <a:r>
    <a:t>第一个编号项目</a:t>
  </a:r>
</a:p>

<!-- 第二级缩进 -->
<a:p>
  <a:pPr lvl="1">
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:t>缩进的项目符号</a:t>
  </a:r>
</a:p>
```

### 形状
```xml
<!-- 矩形 -->
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="3" name="Rectangle"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="1000000" y="1000000"/>
      <a:ext cx="3000000" cy="2000000"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
      <a:avLst/>
    </a:prstGeom>
    <a:solidFill>
      <a:srgbClr val="FF0000"/>
    </a:solidFill>
    <a:ln w="25400">
      <a:solidFill>
        <a:srgbClr val="000000"/>
      </a:solidFill>
    </a:ln>
  </p:spPr>
</p:sp>

<!-- 圆角矩形 -->
<p:sp>
  <p:spPr>
    <a:prstGeom prst="roundRect">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:sp>

<!-- 圆形/椭圆形 -->
<p:sp>
  <p:spPr>
    <a:prstGeom prst="ellipse">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:sp>
```

### 图像
```xml
<p:pic>
  <p:nvPicPr>
    <p:cNvPr id="4" name="Picture">
      <a:hlinkClick r:id="" action="ppaction://media"/>
    </p:cNvPr>
    <p:cNvPicPr>
      <a:picLocks noChangeAspect="1"/>
    </p:cNvPicPr>
    <p:nvPr/>
  </p:nvPicPr>
  <p:blipFill>
    <a:blip r:embed="rId2"/>
    <a:stretch>
      <a:fillRect/>
    </a:stretch>
  </p:blipFill>
  <p:spPr>
    <a:xfrm>
      <a:off x="1000000" y="1000000"/>
      <a:ext cx="3000000" cy="2000000"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
      <a:avLst/>
    </a:prstGeom>
  </p:spPr>
</p:pic>
```

### 表格
```xml
<p:graphicFrame>
  <p:nvGraphicFramePr>
    <p:cNvPr id="5" name="Table"/>
    <p:cNvGraphicFramePr>
      <a:graphicFrameLocks noGrp="1"/>
    </p:cNvGraphicFramePr>
    <p:nvPr/>
  </p:nvGraphicFramePr>
  <p:xfrm>
    <a:off x="1000000" y="1000000"/>
    <a:ext cx="6000000" cy="2000000"/>
  </p:xfrm>
  <a:graphic>
    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">
      <a:tbl>
        <a:tblGrid>
          <a:gridCol w="3000000"/>
          <a:gridCol w="3000000"/>
        </a:tblGrid>
        <a:tr h="500000">
          <a:tc>
            <a:txBody>
              <a:bodyPr/>
              <a:lstStyle/>
              <a:p>
                <a:r>
                  <a:t>单元格1</a:t>
                </a:r>
              </a:p>
            </a:txBody>
          </a:tc>
          <a:tc>
            <a:txBody>
              <a:bodyPr/>
              <a:lstStyle/>
              <a:p>
                <a:r>
                  <a:t>单元格2</a:t>
                </a:r>
              </a:p>
            </a:txBody>
          </a:tc>
        </a:tr>
      </a:tbl>
    </a:graphicData>
  </a:graphic>
</p:graphicFrame>
```

### 幻灯片布局

```xml
<!-- 标题幻灯片布局 -->
<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="ctrTitle"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- 标题内容 -->
</p:sp>

<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="subTitle" idx="1"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- 副标题内容 -->
</p:sp>

<!-- 内容幻灯片布局 -->
<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="title"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- 幻灯片标题 -->
</p:sp>

<p:sp>
  <p:nvSpPr>
    <p:nvPr>
      <p:ph type="body" idx="1"/>
    </p:nvPr>
  </p:nvSpPr>
  <!-- 内容主体 -->
</p:sp>
```

## 文件更新

添加内容时，更新以下文件：

**`ppt/_rels/presentation.xml.rels`：**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
```

**`ppt/slides/_rels/slide1.xml.rels`：**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>
```

**`[Content_Types].xml`：**
```xml
<Default Extension="png" ContentType="image/png"/>
<Default Extension="jpg" ContentType="image/jpeg"/>
<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
```

**`ppt/presentation.xml`：**
```xml
<p:sldIdLst>
  <p:sldId id="256" r:id="rId1"/>
  <p:sldId id="257" r:id="rId2"/>
</p:sldIdLst>
```

**`docProps/app.xml`：** 更新幻灯片数量和统计信息
```xml
<Slides>2</Slides>
<Paragraphs>10</Paragraphs>
<Words>50</Words>
```

## 幻灯片操作

### 添加新幻灯片
向演示文稿末尾添加幻灯片时：

1. **创建幻灯片文件** (`ppt/slides/slideN.xml`)
2. **更新`[Content_Types].xml`**：为新幻灯片添加Override
3. **更新`ppt/_rels/presentation.xml.rels`**：为新幻灯片添加关系
4. **更新`ppt/presentation.xml`**：向`<p:sldIdLst>`添加幻灯片ID
5. **创建幻灯片关系**（如果需要）(`ppt/slides/_rels/slideN.xml.rels`)
6. **更新`docProps/app.xml`**：增加幻灯片数量并更新统计信息（如果存在）

### 复制幻灯片
1. 复制源幻灯片XML文件并使用新名称
2. 更新新幻灯片中的所有ID以确保唯一性
3. 按照上述"添加新幻灯片"的步骤操作
4. **关键**：删除或更新`_rels`文件中的任何备注幻灯片引用
5. 删除对未使用媒体文件的引用

### 重新排序幻灯片
1. **更新`ppt/presentation.xml`**：重新排列`<p:sldIdLst>`中的`<p:sldId>`元素
2. `<p:sldId>`元素的顺序决定了幻灯片顺序
3. 保持幻灯片ID和关系ID不变

示例：
```xml
<!-- 原始顺序 -->
<p:sldIdLst>
  <p:sldId id="256" r:id="rId2"/>
  <p:sldId id="257" r:id="rId3"/>
  <p:sldId id="258" r:id="rId4"/>
</p:sldIdLst>

<!-- 将幻灯片3移到位置2后 -->
<p:sldIdLst>
  <p:sldId id="256" r:id="rId2"/>
  <p:sldId id="258" r:id="rId4"/>
  <p:sldId id="257" r:id="rId3"/>
</p:sldIdLst>
```

### 删除幻灯片
1. **从`ppt/presentation.xml`中删除**：删除`<p:sldId>`条目
2. **从`ppt/_rels/presentation.xml.rels`中删除**：删除关系
3. **从`[Content_Types].xml`中删除**：删除Override条目
4. **删除文件**：删除`ppt/slides/slideN.xml`和`ppt/slides/_rels/slideN.xml.rels`
5. **更新`docProps/app.xml`**：减少幻灯片数量并更新统计信息
6. **清理未使用的媒体**：从`ppt/media/`中删除孤立图像

注意：不要重新编号剩余的幻灯片 - 保持它们的原始ID和文件名。


## 需避免的常见错误

- **编码**：在ASCII内容中转义Unicode字符：`"`变为`&#8220;`
- **图像**：添加到`ppt/media/`并更新关系文件
- **列表**：从列表标题中省略项目符号
- **ID**：为UUID使用有效的十六进制值
- **主题**：检查`theme`目录中的所有主题以获取颜色

## 基于模板的演示文稿验证清单

### 打包前始终：
- **清理未使用的资源**：删除未引用的媒体、字体和备注目录
- **修复Content_Types.xml**：声明包中存在的所有幻灯片、布局和主题
- **修复关系ID**：
   - 如果不使用嵌入字体，则删除字体嵌入引用
- **删除损坏的引用**：检查所有`_rels`文件中对已删除资源的引用

### 常见的模板复制陷阱：
- 复制后多个幻灯片引用同一备注幻灯片
- 模板幻灯片中的图像/媒体引用不再存在
- 未包含字体时的字体嵌入引用
- 缺少12-25号布局的slideLayout声明
- docProps目录可能不会解包 - 这是可选的