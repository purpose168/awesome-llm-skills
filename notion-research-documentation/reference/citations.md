# 引用样式

## 基础页面引用

始终使用 Notion 页面提及（page mentions）来引用来源：

```markdown
<mention-page url="https://notion.so/workspace/Page-Title-uuid">Page Title</mention-page>
```

必须提供 URL。标题是可选的，但可以提高可读性：

```markdown
<mention-page url="https://notion.so/workspace/Page-Title-uuid"/>
```

## 行内引用

在引用的信息后立即引用：

```markdown
Q4 收入环比增长 23%（<mention-page url="...">Q4 财务报告</mention-page>）。
```

## 多个来源

当信息来自多个来源时：

```markdown
客户满意度在所有指标上都有所提升（<mention-page url="...">Q3 调查结果</mention-page>、<mention-page url="...">支持分析</mention-page>）。
```

## 章节级引用

对于来自一个来源的较长章节：

```markdown
### 工程优先级

根据 <mention-page url="...">2025 年工程路线图</mention-page>：

- 专注于 API 可扩展性
- 改善开发者体验
- 迁移到微服务架构
```

## 来源章节

始终在文档末尾包含"来源"（Sources）章节：

```markdown
## 来源

- <mention-page url="...">2025 年战略计划</mention-page>
- <mention-page url="...">市场分析报告</mention-page>
- <mention-page url="...">竞争对手研究：Q3</mention-page>
- <mention-page url="...">客户访谈笔记</mention-page>
```

对于长列表，按类别分组：

```markdown
## 来源

### 主要来源
- <mention-page url="...">官方路线图</mention-page>
- <mention-page url="...">战略文档</mention-page>

### 支持性研究
- <mention-page url="...">市场趋势</mention-page>
- <mention-page url="...">客户反馈</mention-page>

### 背景上下文
- <mention-page url="...">历史分析</mention-page>
```

## 引用内容

当直接引用来源时：

```markdown
产品团队指出："我们需要优先改善移动端体验"（<mention-page url="...">产品会议笔记</mention-page>）。
```

对于块引用（block quotes）：

```markdown
> 我们需要优先改善移动端体验以实现 Q4 目标。这包括性能优化和 UI 刷新。
>
> — <mention-page url="...">产品会议笔记 - 2025 年 10 月</mention-page>
```

## 数据引用

当呈现数据时，引用来源：

```markdown
| 指标 | Q3 | Q4 | 变化 |
|--------|----|----|--------|
| 收入 | $2.3M | $2.8M | +21.7% |
| 用户数 | 12.4K | 15.1K | +21.8% |

来源：<mention-page url="...">财务仪表板</mention-page>
```

## 数据库引用

当引用数据库内容时：

```markdown
基于对 <mention-database url="...">项目数据库</mention-database> 的分析，67% 的项目按计划进行。
```

## 用户引用

当将信息归因于特定人员时：

```markdown
<mention-user url="...">Sarah Chen</mention-user> 在 <mention-page url="...">架构评审</mention-page> 中指出，微服务迁移进度超前。
```

## 引用频率

**过度引用**（每句话）：
```markdown
收入增加（<mention-page url="...">报告</mention-page>）。
成本下降（<mention-page url="...">报告</mention-page>）。
利润率改善（<mention-page url="...">报告</mention-page>）。
```

**引用不足**（无归因）：
```markdown
收入增加，成本下降，利润率改善。
```

**适当平衡**（分组引用）：
```markdown
收入增加，成本下降，利润率改善（<mention-page url="...">Q4 财务报告</mention-page>）。
```

## 过时信息

当来源信息可能过时时进行标注：

```markdown
原始 API 设计（<mention-page url="...">API 规范 v1</mention-page>，最后更新于 2024 年 1 月）已被 <mention-page url="...">API 规范 v2</mention-page> 中的新架构取代。
```

## 交叉引用

链接到相关研究文档：

```markdown
## 相关研究

本研究基于之前的发现：
- <mention-page url="...">市场分析 - 2025 年 Q2</mention-page>
- <mention-page url="...">竞争对手格局评审</mention-page>

有关实施细节，请参阅：
- <mention-page url="...">技术实施指南</mention-page>
```

## 引用验证

在完成研究之前：

✓ 每个关键声明都有来源引用
✓ 所有页面提及都有有效的 URL
✓ 来源章节包含所有引用的页面
✓ 过时的来源已标注
✓ 直接引用已清晰标记
✓ 数据来源已归因

## 引用样式一致性

选择一种引用样式并在全文中使用：

**行内样式**（轻量级）：
```markdown
收入增长 23%（财务报告）。客户数量增加 18%（指标仪表板）。
```

**正式样式**（完整提及）：
```markdown
收入增长 23%（<mention-page url="...">Q4 财务报告</mention-page>）。客户数量增加 18%（<mention-page url="...">指标仪表板</mention-page>）。
```

**推荐使用正式样式**用于大多数研究文档，因为它提供可点击的导航。
