---
name: notion-research-documentation
description: 在您的 Notion 工作区中搜索，综合多个页面的发现，并创建保存为新 Notion 页面的综合研究文档。将分散的信息转化为带有适当引用和可操作见解的结构化报告。
---

# 研究与文档

启用综合研究工作流程：在您的 Notion 工作区中搜索信息，获取并分析相关页面，综合发现，并创建结构良好的文档。

## 快速开始

当被要求研究和记录主题时：

1. **搜索相关内容**：使用 `Notion:notion-search` 查找页面
2. **获取详细信息**：使用 `Notion:notion-fetch` 读取完整页面内容
3. **综合发现**：分析和组合来自多个来源的信息
4. **创建结构化输出**：使用 `Notion:notion-create-pages` 编写文档

## 研究工作流程

### 步骤 1：搜索相关信息

```
使用 Notion:notion-search 和研究主题
如果范围已知，按团队空间过滤
审查搜索结果以识别最相关的页面
```

### 步骤 2：获取页面内容

```
对每个相关页面 URL 使用 Notion:notion-fetch
从所有相关来源收集内容
记录关键发现、引用和数据点
```

### 步骤 3：综合发现

分析收集的信息：
- 识别关键主题和模式
- 连接来源之间的相关概念
- 注意空白或冲突信息
- 逻辑组织发现

### 步骤 4：创建结构化文档

使用适当的文档模板（参见 [reference/format-selection-guide.md](reference/format-selection-guide.md)）来构建输出：
- 清晰的标题和执行摘要
- 带有标题的良好组织章节
- 链接回来源页面的引用
- 可操作的结论或后续步骤

## 输出格式

根据请求选择适当的格式：

**研究摘要**：参见 [reference/research-summary-format.md](reference/research-summary-format.md)
**综合报告**：参见 [reference/comprehensive-report-format.md](reference/comprehensive-report-format.md)
**快速简报**：参见 [reference/quick-brief-format.md](reference/quick-brief-format.md)

## 最佳实践

1. **先广泛搜索**：从广泛的搜索开始，然后缩小范围
2. **引用来源**：始终使用提及链接回来源页面
3. **验证时效性**：检查页面最后编辑日期以获取当前信息
4. **交叉参考**：在多个来源中验证发现
5. **清晰结构**：使用标题、项目符号和格式提高可读性

## 页面放置

默认情况下，将研究文档创建为独立页面。如果用户指定：
- 父页面 → 使用 `page_id` 父级
- 数据库 → 先获取数据库，然后使用适当的 `data_source_id`
- 团队空间 → 在该上下文中创建

## 高级功能

**搜索过滤**：参见 [reference/advanced-search.md](reference/advanced-search.md)
**引用样式**：参见 [reference/citations.md](reference/citations.md)

## 常见问题

**"未找到结果"**：尝试更广泛的搜索术语或不同的团队空间
**"结果太多"**：添加过滤器或在特定页面内搜索
**"无法访问页面"**：用户可能没有权限，请他们验证访问权限

## 示例

参见 [examples/](examples/) 获取完整的工作流程演示：
- [examples/market-research.md](examples/market-research.md) - 研究市场趋势
- [examples/technical-investigation.md](examples/technical-investigation.md) - 技术深入分析
- [examples/competitor-analysis.md](examples/competitor-analysis.md) - 多来源综合
