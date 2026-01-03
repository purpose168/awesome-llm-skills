---
name: mcp-builder
description: 用于创建高质量MCP（模型上下文协议，Model Context Protocol）服务器的指南，使LLM能够通过精心设计的工具与外部服务交互。在构建MCP服务器以集成外部API或服务时使用，无论是使用Python（FastMCP）还是Node/TypeScript（MCP SDK）。
license: Complete terms in LICENSE.txt
---

# MCP服务器开发指南

## 概述

要创建高质量的MCP（模型上下文协议，Model Context Protocol）服务器，使LLM能够有效地与外部服务交互，请使用此技能。MCP服务器提供工具，允许LLM访问外部服务和API。MCP服务器的质量取决于它能在多大程度上使LLM使用提供的工具完成现实世界的任务。

---

# 流程

## 🚀 高级工作流

创建高质量的MCP服务器涉及四个主要阶段：

### 阶段1：深入研究与规划

#### 1.1 理解以智能体为中心的设计原则

在开始实施之前，请通过回顾以下原则来理解如何为AI智能体设计工具：

**为工作流而非仅API端点构建：**
- 不要简单包装现有的API端点 - 构建深思熟虑、高影响力的工作流工具
- 整合相关操作（例如，`schedule_event`既检查可用性又创建事件）
- 专注于支持完成完整任务的工具，而不仅仅是单个API调用
- 考虑智能体实际需要完成哪些工作流

**针对有限上下文进行优化：**
- 智能体的上下文窗口有限 - 让每个标记都发挥作用
- 返回高信号信息，而非详尽的数据转储
- 提供"简洁"与"详细"的响应格式选项
- 默认使用人类可读的标识符而非技术代码（使用名称而非ID）
- 将智能体的上下文预算视为稀缺资源

**设计可操作的错误消息：**
- 错误消息应引导智能体采用正确的使用模式
- 建议具体的后续步骤："尝试使用filter='active_only'来减少结果"
- 让错误具有教育意义，而不仅仅是诊断性的
- 通过清晰的反馈帮助智能体学习正确的工具使用方法

**遵循自然任务细分：**
- 工具名称应反映人类对任务的思考方式
- 使用一致的前缀对相关工具进行分组，以提高可发现性
- 围绕自然工作流设计工具，而不仅仅是API结构

**使用评估驱动的开发：**
- 尽早创建真实的评估场景
- 让智能体反馈驱动工具改进
- 快速原型设计并根据智能体的实际性能进行迭代

#### 1.3 研究MCP协议文档

**获取最新的MCP协议文档：**

使用WebFetch加载：`https://modelcontextprotocol.io/llms-full.txt`

这份全面的文档包含完整的MCP规范和指南。

#### 1.4 研究框架文档

**加载并阅读以下参考文件：**

- **MCP最佳实践**：[📋 查看最佳实践](./reference/mcp_best_practices.md) - 所有MCP服务器的核心指南

**对于Python实现，还需加载：**
- **Python SDK文档**：使用WebFetch加载 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python实现指南](./reference/python_mcp_server.md) - Python特定的最佳实践和示例

**对于Node/TypeScript实现，还需加载：**
- **TypeScript SDK文档**：使用WebFetch加载 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript实现指南](./reference/node_mcp_server.md) - Node/TypeScript特定的最佳实践和示例

#### 1.5 全面研究API文档

要集成服务，请阅读**所有**可用的API文档：
- 官方API参考文档
- 认证和授权要求
- 速率限制和分页模式
- 错误响应和状态码
- 可用端点及其参数
- 数据模型和架构

**根据需要使用网络搜索和WebFetch工具收集全面信息。**

#### 1.6 创建全面的实施计划

基于您的研究，创建一个详细计划，包括：

**工具选择：**
- 列出最有价值的端点/操作来实现
- 优先考虑支持最常见和最重要用例的工具
- 考虑哪些工具可以协同工作以实现复杂的工作流

**共享工具和辅助函数：**
- 识别常见的API请求模式
- 规划分页辅助函数
- 设计过滤和格式化工具
- 规划错误处理策略

**输入/输出设计：**
- 定义输入验证模型（Python使用Pydantic，TypeScript使用Zod）
- 设计一致的响应格式（例如JSON或Markdown），以及可配置的详细程度（例如详细或简洁）
- 为大规模使用（数千用户/资源）进行规划
- 实现字符限制和截断策略（例如25,000 tokens）

**错误处理策略：**
- 规划优雅的故障模式
- 设计清晰、可操作、LLM友好的自然语言错误消息，提示进一步操作
- 考虑速率限制和超时场景
- 处理认证和授权错误

---

### 阶段2：实施

现在您有了全面的计划，可以按照特定语言的最佳实践开始实施。

#### 2.1 设置项目结构

**对于Python：**
- 创建单个`.py`文件，复杂情况下可组织为模块（参见[🐍 Python指南](./reference/python_mcp_server.md)）
- 使用MCP Python SDK进行工具注册
- 定义Pydantic模型用于输入验证

**对于Node/TypeScript：**
- 创建适当的项目结构（参见[⚡ TypeScript指南](./reference/node_mcp_server.md)）
- 设置`package.json`和`tsconfig.json`
- 使用MCP TypeScript SDK
- 定义Zod模式用于输入验证

#### 2.2 首先实现核心基础设施

**开始实施时，先创建共享工具，然后再实现具体工具：**
- API请求辅助函数
- 错误处理工具
- 响应格式化函数（JSON和Markdown）
- 分页辅助函数
- 认证/令牌管理

#### 2.3 系统地实现工具

对于计划中的每个工具：

**定义输入架构：**
- 使用Pydantic（Python）或Zod（TypeScript）进行验证
- 包含适当的约束（最小/最大长度、正则表达式模式、最小/最大值、范围）
- 提供清晰、描述性的字段说明
- 在字段说明中包含多样化的示例

**编写全面的文档字符串/描述：**
- 一行概括工具的功能
- 详细说明目的和功能
- 带有示例的显式参数类型
- 完整的返回类型架构
- 使用示例（何时使用，何时不使用）
- 错误处理文档，概述在给定特定错误时如何进行下一步

**实现工具逻辑：**
- 使用共享工具避免代码重复
- 对所有I/O操作遵循async/await模式
- 实现适当的错误处理
- 支持多种响应格式（JSON和Markdown）
- 尊重分页参数
- 检查字符限制并适当截断

**添加工具注释：**
- `readOnlyHint`: true（对于只读操作）
- `destructiveHint`: false（对于非破坏性操作）
- `idempotentHint`: true（如果重复调用具有相同效果）
- `openWorldHint`: true（如果与外部系统交互）

#### 2.4 遵循特定语言的最佳实践

**此时，加载适当的语言指南：**

**对于Python：加载[🐍 Python实现指南](./reference/python_mcp_server.md)并确保以下内容：**
- 使用MCP Python SDK并正确注册工具
- 使用带`model_config`的Pydantic v2模型
- 全程使用类型提示
- 对所有I/O操作使用async/await
- 正确组织导入
- 模块级常量（CHARACTER_LIMIT, API_BASE_URL）

**对于Node/TypeScript：加载[⚡ TypeScript实现指南](./reference/node_mcp_server.md)并确保以下内容：**
- 正确使用`server.registerTool`
- 使用带`.strict()`的Zod模式
- 启用TypeScript严格模式
- 不使用`any`类型 - 使用适当的类型
- 显式的Promise<T>返回类型
- 配置构建过程（`npm run build`）

---

### 阶段3：审查和优化

初始实现后：

#### 3.1 代码质量审查

为确保质量，请审查代码是否符合以下要求：
- **DRY原则**：工具之间没有重复代码
- **可组合性**：共享逻辑被提取为函数
- **一致性**：类似操作返回类似格式
- **错误处理**：所有外部调用都有错误处理
- **类型安全**：完整的类型覆盖（Python类型提示，TypeScript类型）
- **文档**：每个工具都有全面的文档字符串/描述

#### 3.2 测试和构建

**重要提示：** MCP服务器是长时间运行的进程，通过stdio/stdin或sse/http等待请求。直接在主进程中运行它们（例如`python server.py`或`node dist/index.js`）会导致进程无限挂起。

**安全测试服务器的方法：**
- 使用评估工具（见阶段4）- 推荐方法
- 在tmux中运行服务器，使其保持在主进程之外
- 测试时使用超时：`timeout 5s python server.py`

**对于Python：**
- 验证Python语法：`python -m py_compile your_server.py`
- 通过审查文件检查导入是否正常工作
- 手动测试：在tmux中运行服务器，然后在主进程中使用评估工具测试
- 或直接使用评估工具（它会为stdio传输管理服务器）

**对于Node/TypeScript：**
- 运行`npm run build`并确保完成时没有错误
- 验证是否创建了dist/index.js
- 手动测试：在tmux中运行服务器，然后在主进程中使用评估工具测试
- 或直接使用评估工具（它会为stdio传输管理服务器）

#### 3.3 使用质量检查清单

要验证实现质量，请从特定语言指南中加载适当的检查清单：
- Python：参见[🐍 Python指南](./reference/python_mcp_server.md)中的"质量检查清单"
- Node/TypeScript：参见[⚡ TypeScript指南](./reference/node_mcp_server.md)中的"质量检查清单"

---

### 阶段4：创建评估

在实现MCP服务器后，创建全面的评估来测试其有效性。

**加载[✅ 评估指南](./reference/evaluation.md)获取完整的评估指南。**

#### 4.1 理解评估目的

评估测试LLM是否能有效地使用您的MCP服务器来回答真实、复杂的问题。

#### 4.2 创建10个评估问题

要创建有效的评估，请按照评估指南中概述的流程进行：

1. **工具检查**：列出可用工具并了解其功能
2. **内容探索**：使用只读操作探索可用数据
3. **问题生成**：创建10个复杂、真实的问题
4. **答案验证**：自己解决每个问题以验证答案

#### 4.3 评估要求

每个问题必须：
- **独立**：不依赖于其他问题
- **只读**：只需要非破坏性操作
- **复杂**：需要多个工具调用和深入探索
- **真实**：基于人类关心的真实用例
- **可验证**：单一、清晰的答案，可以通过字符串比较验证
- **稳定**：答案不会随时间变化

#### 4.4 输出格式

创建具有以下结构的XML文件：

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# 参考文件

## 📚 文档库

在开发过程中根据需要加载这些资源：

### 核心MCP文档（首先加载）
- **MCP协议**：从`https://modelcontextprotocol.io/llms-full.txt`获取 - 完整的MCP规范
- [📋 MCP最佳实践](./reference/mcp_best_practices.md) - 通用MCP指南，包括：
  - 服务器和工具命名约定
  - 响应格式指南（JSON vs Markdown）
  - 分页最佳实践
  - 字符限制和截断策略
  - 工具开发指南
  - 安全和错误处理标准

### SDK文档（在阶段1/2加载）
- **Python SDK**：从`https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`获取
- **TypeScript SDK**：从`https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`获取

### 特定语言实现指南（在阶段2加载）
- [🐍 Python实现指南](./reference/python_mcp_server.md) - 完整的Python/FastMCP指南，包括：
  - 服务器初始化模式
  - Pydantic模型示例
  - 使用`@mcp.tool`进行工具注册
  - 完整的工作示例
  - 质量检查清单

- [⚡ TypeScript实现指南](./reference/node_mcp_server.md) - 完整的TypeScript指南，包括：
  - 项目结构
  - Zod模式示例
  - 使用`server.registerTool`进行工具注册
  - 完整的工作示例
  - 质量检查清单

### 评估指南（在阶段4加载）
- [✅ 评估指南](./reference/evaluation.md) - 完整的评估创建指南，包括：
  - 问题创建指南
  - 答案验证策略
  - XML格式规范
  - 示例问题和答案
  - 使用提供的脚本运行评估
