# 示例：市场研究

**用户请求**："研究 AI 编码助手市场的当前状态并在 Notion 中创建摘要文档"

## 工作流程

### 1. 搜索
```
Notion:notion-search
query: "AI coding assistants market"
```
在工程、策略和产品团队空间中找到 3 个相关页面。

### 2. 获取和分析
```
Notion:notion-fetch (3x)
```
从源页面提取市场规模、竞争格局和技术趋势。

### 3. 创建文档
```
Notion:notion-create-pages
```

## 输出（精简版）

```markdown
# AI 编码助手市场研究 - 2025年10月

## 执行摘要
AI 编码助手市场正经历 150%+ 的同比增长。GitHub Copilot 以 60% 的份额占据主导地位，但专业工具在特定细分领域正在获得关注。

## 关键发现

### 市场规模和增长
2024 年 $8 亿 → 2026 年预计 $25 亿。开发者采用率：23%（2023 年）→ 47%（2024 年）。
来源：<mention-page url="...">市场趋势 Q3 2025</mention-page>

### 竞争格局
- GitHub Copilot：60%（强大的 IDE 集成）
- Cursor：15%（快速增长，完整 IDE）
- Tabnine：10%（企业，本地部署）
- Cody：5%（代码库感知）
- CodeWhisperer：8%（AWS 集成）
来源：<mention-page url="...">AI 工具竞争分析</mention-page>

### 技术趋势
关键差异化因素：上下文感知、定制化、多模态界面、代码验证。
来源：<mention-page url="...">开发者工具格局</mention-page>

## 后续步骤
1. 监控 Cursor 的增长和功能发布
2. 评估 Cody 的代码库感知能力
3. 记录企业安全/合规要求
4. 跟踪定价趋势
```

## 关键要点
- 在多个团队空间中找到相关页面
- 综合了竞争、市场和技术视角
- 使用适当的引用链接到源页面
- 创建了可操作的建议
