# MCP 服务器开发最佳实践和指南

## 概述

本文档汇总了构建模型上下文协议（MCP）服务器的关键最佳实践和指南。它涵盖了命名约定、工具设计、响应格式、分页、错误处理、安全性和合规性要求。

---

## 快速参考

### 服务器命名
- **Python**: `{service}_mcp`（例如，`slack_mcp`）
- **Node/TypeScript**: `{service}-mcp-server`（例如，`slack-mcp-server`）

### 工具命名
- 使用带服务前缀的 snake_case 命名法
- 格式：`{service}_{action}_{resource}`
- 示例：`slack_send_message`、`github_create_issue`

### 响应格式
- 同时支持 JSON 和 Markdown 格式
- JSON 用于程序化处理
- Markdown 用于人类可读性

### 分页
- 始终遵循 `limit` 参数
- 返回 `has_more`、`next_offset`、`total_count`
- 默认值为 20-50 项

### 字符限制
- 设置 CHARACTER_LIMIT 常量（通常为 25,000）
- 使用清晰的消息进行优雅截断
- 提供过滤指导

---

## 目录
1. 服务器命名约定
2. 工具命名与设计
3. 响应格式指南
4. 分页最佳实践
5. 字符限制与截断
6. 工具开发最佳实践
7. 传输最佳实践
8. 测试要求
9. OAuth 和安全最佳实践
10. 资源管理最佳实践
11. 提示管理最佳实践
12. 错误处理标准
13. 文档要求
14. 合规与监控

---

## 1. 服务器命名约定

为MCP服务器遵循以下标准化命名模式：

**Python**：使用 `{service}_mcp` 格式（小写带下划线）
- 示例：`slack_mcp`、`github_mcp`、`jira_mcp`、`stripe_mcp`

**Node/TypeScript**：使用 `{service}-mcp-server` 格式（小写带连字符）
- 示例：`slack-mcp-server`、`github-mcp-server`、`jira-mcp-server`

名称应该：
- 通用（不与特定功能绑定）
- 描述正在集成的服务/API
- 易于从任务描述中推断
- 不包含版本号或日期

---

## 2. 工具命名与设计

### 工具命名最佳实践

1. **使用 snake_case**：`search_users`、`create_project`、`get_channel_info`
2. **包含服务前缀**：预计您的MCP服务器可能与其他MCP服务器一起使用
   - 使用 `slack_send_message` 而不是仅 `send_message`
   - 使用 `github_create_issue` 而不是仅 `create_issue`
   - 使用 `asana_list_tasks` 而不是仅 `list_tasks`
3. **以动作为导向**：以动词开头（get、list、search、create等）
4. **保持具体**：避免可能与其他服务器冲突的通用名称
5. **保持一致性**：在服务器内部使用一致的命名模式

### 工具设计指南

- 工具描述必须狭窄且明确地描述功能
- 描述必须与实际功能精确匹配
- 不应与其他MCP服务器产生混淆
- 应提供工具注释（readOnlyHint、destructiveHint、idempotentHint、openWorldHint）
- 保持工具操作的专注性和原子性

---

## 3. 响应格式指南

所有返回数据的工具都应支持多种格式以提高灵活性：

### JSON 格式（`response_format="json"`）
- 机器可读的结构化数据
- 包含所有可用字段和元数据
- 一致的字段名称和类型
- 适合程序化处理
- 用于LLM需要进一步处理数据的情况

### Markdown 格式（`response_format="markdown"`，通常为默认格式）
- 人类可读的格式化文本
- 使用标题、列表和格式以提高清晰度
- 将时间戳转换为人类可读格式（例如，使用 "2024-01-15 10:30:00 UTC" 而非时间戳）
- 显示带ID的显示名称（例如，"@john.doe (U123456)"）
- 省略冗长的元数据（例如，只显示一个头像URL，而非所有尺寸）
- 逻辑上分组相关信息
- 用于向用户呈现信息的情况

---

## 4. 分页最佳实践

对于列出资源的工具：

- **始终遵循 `limit` 参数**：指定限制时切勿加载所有结果
- **实现分页**：使用 `offset` 或基于游标（cursor）的分页
- **返回分页元数据**：包含 `has_more`、`next_offset`/`next_cursor`、`total_count`
- **切勿将所有结果加载到内存中**：对于大型数据集尤其重要
- **使用合理的默认限制**：通常为20-50项
- **在响应中包含清晰的分页信息**：使LLM能够轻松请求更多数据

分页响应结构示例：
```json
{
  "total": 150,
  "count": 20,
  "offset": 0,
  "items": [...],
  "has_more": true,
  "next_offset": 20
}
```

---

## 5. 字符限制与截断

为防止响应数据过多导致过载：

- **定义 CHARACTER_LIMIT 常量**：通常在模块级别设置为25,000个字符
- **在返回前检查响应大小**：测量最终响应长度
- **使用清晰的指示器优雅截断**：让LLM知道数据已被截断
- **提供过滤指导**：建议如何使用参数减少结果
- **包含截断元数据**：显示什么内容被截断以及如何获取更多数据

截断处理示例：
```python
CHARACTER_LIMIT = 25000

if len(result) > CHARACTER_LIMIT:
    truncated_data = data[:max(1, len(data) // 2)]
    response["truncated"] = True
    response["truncation_message"] = (
        f"响应已从 {len(data)} 项截断为 {len(truncated_data)} 项。 "
        f"使用 'offset' 参数或添加过滤器查看更多结果。"
    )
```

---

## 6. 传输选项

MCP服务器支持多种传输机制，适用于不同的部署场景：

### Stdio 传输

**最适用于**：命令行工具、本地集成、子进程执行

**特性**：
- 标准输入/输出流通信
- 设置简单，无需网络配置
- 作为客户端的子进程运行
- 非常适合桌面应用程序和CLI工具

**使用场景**：
- 为本地开发环境构建工具
- 与桌面应用程序集成（例如，Claude Desktop）
- 创建命令行实用程序
- 单用户、单会话场景

### HTTP 传输

**最适用于**：Web服务、远程访问、多客户端场景

**特性**：
- 基于HTTP的请求-响应模式
- 支持多个并发客户端
- 可以部署为Web服务
- 需要网络配置和安全考虑

**使用场景**：
- 同时为多个客户端提供服务
- 部署为云服务
- 与Web应用程序集成
- 需要负载均衡或扩展

### 服务器发送事件（SSE）传输

**最适用于**：实时更新、推送通知、流数据

**特性**：
- 基于HTTP的单向服务器到客户端流
- 无需轮询即可实现实时更新
- 用于持续数据流的长连接
- 构建在标准HTTP基础设施上

**使用场景**：
- 客户端需要实时数据更新
- 实现推送通知
- 流日志或监控数据
- 长时间操作的渐进式结果交付

### 传输选择标准

| 标准 | Stdio | HTTP | SSE |
|------|-------|------|-----|
| **部署方式** | 本地 | 远程 | 远程 |
| **客户端** | 单个 | 多个 | 多个 |
| **通信模式** | 双向 | 请求-响应 | 服务器推送 |
| **复杂度** | 低 | 中等 | 中等-高 |
| **实时性** | 否 | 否 | 是 |

---

## 7. 工具开发最佳实践

### 通用指南
1. 工具名称应具有描述性且以动作为导向
2. 使用带有详细JSON模式的参数验证
3. 在工具描述中包含示例
4. 实现适当的错误处理和验证
5. 对长时间操作使用进度报告
6. 保持工具操作的专注性和原子性
7. 记录预期的返回值结构
8. 实现适当的超时机制
9. 为资源密集型操作考虑速率限制
10. 记录工具使用情况以进行调试和监控

### 工具的安全考虑

#### 输入验证
- 根据模式验证所有参数
- 清理文件路径和系统命令
- 验证URL和外部标识符
- 检查参数大小和范围
- 防止命令注入

#### 访问控制
- 在需要的地方实现身份验证
- 使用适当的授权检查
- 审计工具使用情况
- 限制请求速率
- 监控滥用情况

#### 错误处理
- 不要向客户端暴露内部错误
- 记录与安全相关的错误
- 适当处理超时
- 错误发生后清理资源
- 验证返回值

### 工具注释
- 提供readOnlyHint和destructiveHint注释
- 记住注释只是提示，不是安全保证
- 客户端不应仅基于注释做出安全关键决策

---

## 8. 传输最佳实践

### 通用传输指南
1. 正确处理连接生命周期
2. 实现适当的错误处理
3. 使用适当的超时值
4. 实现连接状态管理
5. 断开连接时清理资源

### 传输的安全最佳实践
- 遵循针对DNS重新绑定攻击的安全考虑
- 实现适当的身份验证机制
- 验证消息格式
- 优雅处理格式错误的消息

### Stdio传输特定指南
- 本地MCP服务器不应记录到stdout（会干扰协议）
- 使用stderr进行日志记录
- 正确处理标准I/O流

---

## 9. 测试要求

全面的测试策略应涵盖以下方面：

### 功能测试
- 验证使用有效/无效输入时的正确执行

### 集成测试
- 测试与外部系统的交互

### 安全测试
- 验证身份验证、输入清理、速率限制

### 性能测试
- 检查负载下的行为、超时情况

### 错误处理
- 确保适当的错误报告和清理

---

## 10. OAuth 和安全最佳实践

### 身份验证和授权

连接到外部服务的MCP服务器应实现适当的身份验证：

**OAuth 2.1 实现：**
- 使用来自认可机构的证书的安全OAuth 2.1
- 处理请求前验证访问令牌
- 仅接受专门为您的服务器设计的令牌
- 拒绝没有适当受众声明的令牌
- 绝不要传递从MCP客户端接收的令牌

**API密钥管理：**
- 将API密钥存储在环境变量中，切勿存储在代码中
- 服务器启动时验证密钥
- 身份验证失败时提供清晰的错误消息
- 对敏感凭据使用安全传输

### 输入验证和安全

**始终验证输入：**
- 清理文件路径以防止目录遍历
- 验证URL和外部标识符
- 检查参数大小和范围
- 防止系统调用中的命令注入
- 对所有输入使用模式验证（Pydantic/Zod）

**错误处理安全：**
- 不要向客户端暴露内部错误
- 在服务器端记录与安全相关的错误
- 提供有帮助但不暴露内部信息的错误消息
- 错误发生后清理资源

### 隐私和数据保护

**数据收集原则：**
- 仅收集功能所需的严格必要数据
- 不收集无关的对话数据
- 除非工具目的明确需要，否则不收集PII（个人身份信息）
- 提供有关访问哪些数据的清晰信息

**数据传输：**
- 未经披露，不要将数据发送到组织外部的服务器
- 对所有网络通信使用安全传输（HTTPS）
- 验证外部服务的证书

---

## 11. 资源管理最佳实践

1. 仅建议必要的资源
2. 为根资源使用清晰、描述性的名称
3. 正确处理资源边界
4. 尊重客户端对资源的控制
5. 使用模型控制的原语（工具）进行自动数据暴露

---

## 12. 提示管理最佳实践

- 客户端应向用户显示建议的提示
- 用户应能够修改或拒绝提示
- 客户端应向用户显示完成结果
- 用户应能够修改或拒绝完成结果
- 使用采样时考虑成本

---

## 13. 错误处理标准

- 使用标准JSON-RPC错误代码
- 在结果对象内报告工具错误（而非协议级别）
- 提供有帮助的、具体的错误消息
- 不暴露内部实现细节
- 错误发生时正确清理资源

---

## 14. 文档要求

- 提供所有工具和功能的清晰文档
- 包含工作示例（每个主要功能至少3个）
- 记录安全考虑因素
- 指定所需的权限和访问级别
- 记录速率限制和性能特征

---

## 15. 合规与监控

- 实现日志记录以进行调试和监控
- 跟踪工具使用模式
- 监控潜在的滥用情况
- 为与安全相关的操作维护审计跟踪
- 准备好进行持续的合规审查

---

## 总结

这些最佳实践代表了构建安全、高效且合规的MCP服务器的全面指南，这些服务器能在生态系统中良好运行。开发人员应遵循这些指南，以确保他们的MCP服务器符合纳入MCP目录的标准，并为用户提供安全、可靠的体验。


----------


# 工具

> 使LLM能够通过您的服务器执行操作

工具是模型上下文协议（MCP）中的强大原语，使服务器能够向客户端公开可执行功能。通过工具，LLM可以与外部系统交互、执行计算并在现实世界中采取行动。

<Note>
  工具被设计为**模型控制**的，这意味着工具从服务器向客户端公开，目的是让AI模型能够自动调用它们（有人类在回路中批准）。
</Note>

## 概述

MCP中的工具允许服务器公开可执行函数，这些函数可以被客户端调用，并被LLM用于执行操作。工具的关键方面包括：

* **发现**：客户端可以通过发送`tools/list`请求获取可用工具列表
* **调用**：工具使用`tools/call`请求调用，服务器执行请求的操作并返回结果
* **灵活性**：工具可以从简单计算到复杂API交互不等

与[资源](/docs/concepts/resources)类似，工具通过唯一名称标识，并可以包含描述来指导其使用。然而，与资源不同的是，工具代表可以修改状态或与外部系统交互的动态操作。

## 工具定义结构

每个工具使用以下结构定义：

```typescript
{
  name: string;          // 工具的唯一标识符
  description?: string;  // 人类可读的描述
  inputSchema: {         // 工具参数的JSON Schema
    type: "object",
    properties: { ... }  // 工具特定的参数
  },
  annotations?: {        // 关于工具行为的可选提示
    title?: string;      // 工具的人类可读标题
    readOnlyHint?: boolean;    // 如果为true，工具不修改其环境
    destructiveHint?: boolean; // 如果为true，工具可能执行破坏性更新
    idempotentHint?: boolean;  // 如果为true，使用相同参数重复调用没有额外效果
    openWorldHint?: boolean;   // 如果为true，工具与外部实体交互
  }
}
```

## 实现工具

以下是在MCP服务器中实现基本工具的示例：

<Tabs>
  <Tab title="TypeScript">
    ```typescript
    const server = new Server({
      name: "example-server",
      version: "1.0.0"
    }, {
      capabilities: {
        tools: {}
      }
    });

    // 定义可用工具
    server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [{
          name: "calculate_sum",
          description: "将两个数字相加",
          inputSchema: {
            type: "object",
            properties: {
              a: { type: "number" },
              b: { type: "number" }
            },
            required: ["a", "b"]
          }
        }]
      };
    });

    // 处理工具执行
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name === "calculate_sum") {
        const { a, b } = request.params.arguments;
        return {
          content: [
            {
              type: "text",
              text: String(a + b)
            }
          ]
        };
      }
      throw new Error("未找到工具");
    });
    ```
  </Tab>

  <Tab title="Python">
    ```python
    app = Server("example-server")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="calculate_sum",
                description="将两个数字相加",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            )
        ]

    @app.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "calculate_sum":
            a = arguments["a"]
            b = arguments["b"]
            result = a + b
            return [types.TextContent(type="text", text=str(result))]
        raise ValueError(f"未找到工具: {name}")
    ```
  </Tab>
</Tabs>

## 工具模式示例

以下是服务器可以提供的工具类型示例：

### 系统操作

与本地系统交互的工具：

```typescript
{
  name: "execute_command",
  description: "运行shell命令",
  inputSchema: {
    type: "object",
    properties: {
      command: { type: "string" },
      args: { type: "array", items: { type: "string" } }
    }
  }
}
```

### API集成

包装外部API的工具：

```typescript
{
  name: "github_create_issue",
  description: "创建GitHub问题",
  inputSchema: {
    type: "object",
    properties: {
      title: { type: "string" },
      body: { type: "string" },
      labels: { type: "array", items: { type: "string" } }
    }
  }
}
```

### 数据处理

转换或分析数据的工具：

```typescript
{
  name: "analyze_csv",
  description: "分析CSV文件",
  inputSchema: {
    type: "object",
    properties: {
      filepath: { type: "string" },
      operations: {
        type: "array",
        items: {
          enum: ["sum", "average", "count"]
        }
      }
    }
  }
}
```

## 最佳实践

实现工具时：

1. 提供清晰、描述性的名称和描述
2. 对参数使用详细的JSON Schema定义
3. 在工具描述中包含示例，以演示模型应如何使用它们
4. 实现适当的错误处理和验证
5. 对长时间操作使用进度报告
6. 保持工具操作的专注性和原子性
7. 记录预期的返回值结构
8. 实现适当的超时机制
9. 为资源密集型操作考虑速率限制
10. 记录工具使用情况以进行调试和监控

### 工具名称冲突

MCP客户端应用程序和MCP服务器代理在构建自己的工具列表时可能会遇到工具名称冲突。例如，两个连接的MCP服务器`web1`和`web2`可能都公开一个名为`search_web`的工具。

应用程序可以使用以下策略之一来消除工具歧义（以下只是部分策略，并非详尽列表）：

* 将用户定义的唯一服务器名称与工具名称连接起来，例如`web1___search_web`和`web2___search_web`。当配置文件中已经提供了用户定义的唯一服务器名称时，此策略可能更可取。
* 为工具名称生成随机前缀，例如`jrwxs___search_web`和`6cq52___search_web`。在服务器代理中，当用户定义的唯一名称不可用时，此策略可能更可取。
* 使用服务器URI作为工具名称的前缀，例如`web1.example.com:search_web`和`web2.example.com:search_web`。在使用远程MCP服务器时，此策略可能适合。

请注意，初始化流程中服务器提供的名称不保证是唯一的，通常不适合用于消歧目的。

## 安全考虑

公开工具时：

### 输入验证

* 根据模式验证所有参数
* 清理文件路径和系统命令
* 验证URL和外部标识符
* 检查参数大小和范围
* 防止命令注入

### 访问控制

* 在需要的地方实现身份验证
* 使用适当的授权检查
* 审计工具使用情况
* 限制请求速率
* 监控滥用情况

### 错误处理

* 不要向客户端暴露内部错误
* 记录与安全相关的错误
* 适当处理超时
* 错误发生后清理资源
* 验证返回值

## 工具发现和更新

MCP支持动态工具发现：

1. 客户端可以随时列出可用工具
2. 服务器可以使用`notifications/tools/list_changed`通知客户端工具发生变化
3. 可以在运行时添加或删除工具
4. 可以更新工具定义（尽管应谨慎操作）

## 错误处理

工具错误应在结果对象内报告，而不是作为MCP协议级错误。这允许LLM看到错误并可能处理它。当工具遇到错误时：

1. 在结果中将`isError`设置为`true`
2. 在`content`数组中包含错误详情

Here's an example of proper error handling for tools:

<Tabs>
  <Tab title="TypeScript">
    ```typescript
    try {
      // Tool operation
      const result = performOperation();
      return {
        content: [
          {
            type: "text",
            text: `Operation successful: ${result}`
          }
        ]
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Error: ${error.message}`
          }
        ]
      };
    }
    ```
  </Tab>

  <Tab title="Python">
    ```python
    try:
        # Tool operation
        result = perform_operation()
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Operation successful: {result}"
                )
            ]
        )
    except Exception as error:
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"Error: {str(error)}"
                )
            ]
        )
    ```
  </Tab>
</Tabs>

这个方法允许LLM看到发生了错误，并可能采取纠正措施或请求人工干预。

## 工具注释

工具注释提供有关工具行为的额外元数据，帮助客户端了解如何呈现和管理工具。这些注释是描述工具性质和影响的提示，但不应依赖它们做出安全决策。

### 工具注释的目的

工具注释有几个关键目的：

1. 提供特定于UX的信息，不影响模型上下文
2. 帮助客户端适当地分类和呈现工具
3. 传达有关工具潜在副作用的信息
4. 协助开发直观的工具批准界面

### 可用的工具注释

MCP规范为工具定义了以下注释：

| 注释              | 类型    | 默认值 | 描述                                                                                                                          |
| ----------------- | ------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `title`           | string  | -       | 工具的人类可读标题，对UI显示很有用                                                                           |
| `readOnlyHint`    | boolean | false   | 如果为true，表示工具不修改其环境                                                                          |
| `destructiveHint` | boolean | true    | 如果为true，工具可能执行破坏性更新（仅当`readOnlyHint`为false时有意义）                                     |
| `idempotentHint`  | boolean | false   | 如果为true，使用相同参数重复调用工具没有额外效果（仅当`readOnlyHint`为false时有意义） |
| `openWorldHint`   | boolean | true    | 如果为true，工具可能与外部实体的"开放世界"交互                                                             |

### 示例用法

以下是如何为不同场景定义带有注释的工具：

```typescript
// 一个只读搜索工具
{
  name: "web_search",
  description: "Search the web for information",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string" }
    },
    required: ["query"]
  },
  annotations: {
    title: "Web Search",
    readOnlyHint: true,
    openWorldHint: true
  }
}

// 一个破坏性文件删除工具
{
  name: "delete_file",
  description: "Delete a file from the filesystem",
  inputSchema: {
    type: "object",
    properties: {
      path: { type: "string" }
    },
    required: ["path"]
  },
  annotations: {
    title: "Delete File",
    readOnlyHint: false,
    destructiveHint: true,
    idempotentHint: true,
    openWorldHint: false
  }
}

// 一个非破坏性数据库记录创建工具
{
  name: "create_record",
  description: "Create a new record in the database",
  inputSchema: {
    type: "object",
    properties: {
      table: { type: "string" },
      data: { type: "object" }
    },
    required: ["table", "data"]
  },
  annotations: {
    title: "Create Database Record",
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: false
  }
}
```

### 在服务器实现中集成注释

<Tabs>
  <Tab title="TypeScript">
    ```typescript
    server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [{
          name: "calculate_sum",
          description: "将两个数字相加",
          inputSchema: {
            type: "object",
            properties: {
              a: { type: "number" },
              b: { type: "number" }
            },
            required: ["a", "b"]
          },
          annotations: {
            title: "计算求和",
            readOnlyHint: true,
            openWorldHint: false
          }
        }]
      };
    });
    ```
  </Tab>

  <Tab title="Python">
    ```python
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("example-server")

    @mcp.tool(
        annotations={
            "title": "计算求和",
            "readOnlyHint": True,
            "openWorldHint": False
        }
    )
    async def calculate_sum(a: float, b: float) -> str:
        """将两个数字相加。

        参数：
            a: 要相加的第一个数字
            b: 要相加的第二个数字
        """
        result = a + b
        return str(result)
    ```
  </Tab>
</Tabs>

### 工具注释的最佳实践

1. **准确说明副作用**：清楚地表明工具是否修改其环境以及这些修改是否具有破坏性。

2. **使用描述性标题**：提供清晰描述工具用途的人性化标题。

3. **正确指示幂等性**：只有当使用相同参数重复调用确实没有额外效果时，才将工具标记为幂等。

4. **设置适当的开放/封闭世界提示**：指示工具是与封闭系统（如数据库）还是开放系统（如Web）交互。

5. **记住注释只是提示**：ToolAnnotations中的所有属性都是提示，不保证提供工具行为的真实描述。客户端永远不应仅基于注释做出安全关键决策。

## 测试工具

MCP工具的全面测试策略应涵盖：

* **功能测试**：验证工具使用有效输入时能正确执行，并适当处理无效输入
* **集成测试**：测试工具与外部系统的交互，使用真实和模拟的依赖项
* **安全测试**：验证身份验证、授权、输入清理和速率限制
* **性能测试**：检查负载下的行为、超时处理和资源清理
* **错误处理**：确保工具通过MCP协议正确报告错误并清理资源
