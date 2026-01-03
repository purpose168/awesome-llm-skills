# Node/TypeScript MCP 服务器实现指南

## 概述

本文档提供了使用 MCP TypeScript SDK 实现 MCP 服务器的 Node/TypeScript 特定最佳实践和示例。它涵盖了项目结构、服务器设置、工具注册模式、使用 Zod 进行输入验证、错误处理以及完整的工作示例。

---

## 快速参考

### 关键导入
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"; // 导入 MCP 服务器核心类
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"; // 导入标准输入输出传输
import { z } from "zod"; // 导入 Zod 用于输入验证
import axios, { AxiosError } from "axios"; // 导入 Axios 用于 HTTP 请求
```

### 服务器初始化
```typescript
const server = new McpServer({
  name: "service-mcp-server", // 服务器名称，格式为 {service}-mcp-server
  version: "1.0.0" // 服务器版本号
});
```

### 工具注册模式
```typescript
server.registerTool("tool_name", {...config}, async (params) => {
  // 工具实现代码
});
```

---

## MCP TypeScript SDK

官方 MCP TypeScript SDK 提供以下功能：
- `McpServer` 类用于服务器初始化
- `registerTool` 方法用于工具注册
- Zod 模式集成用于运行时输入验证
- 类型安全的工具处理器实现

有关完整详细信息，请参阅参考资料中的 MCP SDK 文档。

## 服务器命名约定

Node/TypeScript MCP 服务器必须遵循以下命名模式：
- **格式**：`{service}-mcp-server`（小写，使用连字符分隔）
- **示例**：`github-mcp-server`、`jira-mcp-server`、`stripe-mcp-server`

服务器名称应具备以下特点：
- 通用性（不与特定功能绑定）
- 能够描述所集成的服务/API
- 易于从任务描述中推断
- 不包含版本号或日期

## 项目结构

为 Node/TypeScript MCP 服务器创建以下结构：

```
{service}-mcp-server/          # 项目根目录
├── package.json              # 项目依赖和脚本配置
├── tsconfig.json             # TypeScript 配置文件
├── README.md                 # 项目文档
├── src/                      # 源代码目录
│   ├── index.ts              # 主入口文件，包含 McpServer 初始化
│   ├── types.ts              # TypeScript 类型定义和接口
│   ├── tools/                # 工具实现（按领域划分文件）
│   ├── services/             # API 客户端和共享工具
│   ├── schemas/              # Zod 验证模式
│   └── constants.ts          # 共享常量（API_URL、CHARACTER_LIMIT 等）
└── dist/                     # 构建后的 JavaScript 文件（入口点：dist/index.js）
```

## 工具实现

### 工具命名

工具名称使用 snake_case 格式（例如 "search_users"、"create_project"、"get_channel_info"），并采用清晰、面向动作的名称。

**避免命名冲突**：包含服务上下文以防止重叠：
- 使用 "slack_send_message" 而不是仅使用 "send_message"
- 使用 "github_create_issue" 而不是仅使用 "create_issue"
- 使用 "asana_list_tasks" 而不是仅使用 "list_tasks"

### 工具结构

使用 `registerTool` 方法注册工具时需满足以下要求：
- 使用 Zod 模式进行运行时输入验证和类型安全
- 必须显式提供 `description` 字段 - JSDoc 注释不会自动提取
- 显式提供 `title`、`description`、`inputSchema` 和 `annotations`
- `inputSchema` 必须是 Zod 模式对象（不是 JSON 模式）
- 明确为所有参数和返回值指定类型

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// 创建 MCP 服务器实例
const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// 用户搜索输入的 Zod 验证模式
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "查询字符串至少需要2个字符")
    .max(200, "查询字符串不能超过200个字符")
    .describe("用于匹配姓名/邮箱的搜索字符串"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("返回结果的最大数量"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("分页跳过的结果数量"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("输出格式：'markdown' 用于人类可读或 'json' 用于机器可读")
}).strict(); // 使用 .strict() 禁止额外字段

// 从 Zod 模式推断 TypeScript 类型
type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

// 注册用户搜索工具
server.registerTool(
  "example_search_users", // 工具名称，使用 snake_case 格式
  {
    title: "搜索示例用户", // 工具标题
    description: `在 Example 系统中按姓名、邮箱或团队搜索用户。

此工具搜索 Example 平台上的所有用户配置文件，支持部分匹配和各种搜索筛选器。它不会创建或修改用户，仅搜索现有用户。

参数：
  - query (string)：用于匹配姓名/邮箱的搜索字符串
  - limit (number)：返回结果的最大数量，范围1-100（默认：20）
  - offset (number)：分页跳过的结果数量（默认：0）
  - response_format ('markdown' | 'json')：输出格式（默认：'markdown'）

返回值：
  JSON 格式：结构化数据，具有以下 schema：
  {
    "total": number,           // 找到的匹配总数
    "count": number,           // 当前响应中的结果数量
    "offset": number,          // 当前分页偏移量
    "users": [
      {
        "id": string,          // 用户 ID（例如："U123456789"）
        "name": string,        // 全名（例如："John Doe"）
        "email": string,       // 邮箱地址
        "team": string,        // 团队名称（可选）
        "active": boolean      // 用户是否活跃
      }
    ],
    "has_more": boolean,       // 是否还有更多结果
    "next_offset": number      // 下一页的偏移量（如果 has_more 为 true）
  }

示例：
  - 使用场景："查找所有营销团队成员" -> 参数 query="team:marketing"
  - 使用场景："搜索 John 的账户" -> 参数 query="john"
  - 不适合场景：需要创建用户时（请改用 example_create_user）

错误处理：
  - 如果请求过多（429 状态），返回 "Error: Rate limit exceeded"
  - 如果搜索结果为空，返回 "No users found matching '<query>'"`,
    inputSchema: UserSearchInputSchema, // 输入验证模式
    annotations: { // 工具属性注释
      readOnlyHint: true,       // 只读操作（不修改数据）
      destructiveHint: false,   // 非破坏性操作
      idempotentHint: true,     // 幂等操作（多次调用效果相同）
      openWorldHint: true       // 开放世界操作（结果可能随时间变化）
    }
  },
  // 工具实现函数
  async (params: UserSearchInput) => {
    try {
      // 输入验证由 Zod 模式自动处理
      // 使用验证后的参数发出 API 请求
      const data = await makeApiRequest<any>(
        "users/search",
        "GET",
        undefined,
        {
          q: params.query,
          limit: params.limit,
          offset: params.offset
        }
      );

      const users = data.users || [];
      const total = data.total || 0;

      // 如果没有找到用户
      if (!users.length) {
        return {
          content: [{
            type: "text",
            text: `未找到匹配 '${params.query}' 的用户`
          }]
        };
      }

      // 根据请求的格式格式化响应
      let result: string;

      if (params.response_format === ResponseFormat.MARKDOWN) {
        // 人类可读的 Markdown 格式
        const lines: string[] = [`# 用户搜索结果: '${params.query}'`, ""];
        lines.push(`找到 ${total} 个用户（显示 ${users.length} 个）`);
        lines.push("");

        for (const user of users) {
          lines.push(`## ${user.name} (${user.id})`);
          lines.push(`- **邮箱**: ${user.email}`);
          if (user.team) {
            lines.push(`- **团队**: ${user.team}`);
          }
          lines.push("");
        }

        result = lines.join("\n");

      } else {
        // 机器可读的 JSON 格式
        const response: any = {
          total,
          count: users.length,
          offset: params.offset,
          users: users.map((user: any) => ({
            id: user.id,
            name: user.name,
            email: user.email,
            ...(user.team ? { team: user.team } : {}),
            active: user.active ?? true // 使用空值合并运算符设置默认值
          }))
        };

        // 如果有更多结果，添加分页信息
        if (total > params.offset + users.length) {
          response.has_more = true;
          response.next_offset = params.offset + users.length;
        }

        result = JSON.stringify(response, null, 2); // 格式化 JSON 输出
      }

      // 返回响应内容
      return {
        content: [{
          type: "text",
          text: result
        }]
      };
    } catch (error) {
      // 处理错误并返回错误消息
      return {
        content: [{
          type: "text",
          text: handleApiError(error)
        }]
      };
    }
  }
);
```

## Zod 输入验证模式

Zod 提供运行时类型验证功能：

```typescript
import { z } from "zod"; // 导入 Zod 库

// 基础验证模式
const CreateUserSchema = z.object({
  name: z.string()
    .min(1, "姓名是必填项")
    .max(100, "姓名不能超过100个字符"),
  email: z.string()
    .email("无效的邮箱格式"),
  age: z.number()
    .int("年龄必须是整数")
    .min(0, "年龄不能为负数")
    .max(150, "年龄不能超过150岁")
}).strict();  // 使用 .strict() 禁止额外字段

// 枚举类型
enum ResponseFormat {
  MARKDOWN = "markdown", // Markdown 格式
  JSON = "json" // JSON 格式
}

// 使用枚举的模式
const SearchSchema = z.object({
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN) // 默认使用 Markdown 格式
    .describe("输出格式")
});

// 带默认值的可选字段
const PaginationSchema = z.object({
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20) // 默认返回20条结果
    .describe("返回结果的最大数量"),
  offset: z.number()
    .int()
    .min(0)
    .default(0) // 默认从第0条结果开始
    .describe("跳过的结果数量")
});
```

## 响应格式选项

支持多种输出格式以提高灵活性：

```typescript
enum ResponseFormat {
  MARKDOWN = "markdown", // Markdown 格式（人类可读）
  JSON = "json" // JSON 格式（机器可读）
}

const inputSchema = z.object({
  query: z.string(),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN) // 默认使用 Markdown 格式
    .describe("输出格式：'markdown' 用于人类可读或 'json' 用于机器可读")
});
```

**Markdown 格式**：
- 使用标题、列表和格式化来提高清晰度
- 将时间戳转换为人类可读的格式
- 显示显示名称并在括号中包含 ID
- 省略冗长的元数据
- 逻辑上对相关信息进行分组

**JSON 格式**：
- 返回完整、结构化的数据，适合程序处理
- 包含所有可用字段和元数据
- 使用一致的字段名称和类型

## 分页实现

对于列出资源的工具：

```typescript
// 分页参数的验证模式
const ListSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20), // 每页最大结果数
  offset: z.number().int().min(0).default(0) // 跳过的结果数
});

// 实现分页逻辑的函数
async function listItems(params: z.infer<typeof ListSchema>) {
  // 调用API获取数据
  const data = await apiRequest(params.limit, params.offset);

  // 构建包含分页信息的响应
  const response = {
    total: data.total, // 总结果数
    count: data.items.length, // 当前页结果数
    offset: params.offset, // 当前偏移量
    items: data.items, // 结果数据
    has_more: data.total > params.offset + data.items.length, // 是否还有更多结果
    next_offset: data.total > params.offset + data.items.length
      ? params.offset + data.items.length // 下一页的偏移量
      : undefined
  };

  // 返回格式化的JSON响应
  return JSON.stringify(response, null, 2);
}
```

## 字符限制和截断

添加一个 CHARACTER_LIMIT 常量来防止响应内容过大：

```typescript
// 在 constants.ts 模块级别定义
export const CHARACTER_LIMIT = 25000;  // 响应的最大字符数

async function searchTool(params: SearchInput) {
  let result = generateResponse(data);

  // 检查字符限制并在需要时截断
  if (result.length > CHARACTER_LIMIT) {
    // 截断数据，至少保留1项
    const truncatedData = data.slice(0, Math.max(1, data.length / 2));
    response.data = truncatedData;
    response.truncated = true; // 标记响应已被截断
    response.truncation_message =
      `响应从 ${data.length} 项截断到 ${truncatedData.length} 项。 ` +
      `请使用 'offset' 参数或添加筛选条件查看更多结果。`;
    result = JSON.stringify(response, null, 2);
  }

  return result;
}
```

## 错误处理

提供清晰、可操作的错误消息：

```typescript
import axios, { AxiosError } from "axios";

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "错误：资源未找到。请检查ID是否正确。";
        case 403:
          return "错误：权限被拒绝。您没有访问此资源的权限。";
        case 429:
          return "错误：请求频率超过限制。请稍后再试。";
        default:
          return `错误：API请求失败，状态码 ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "错误：请求超时。请重试。";
    }
  }
  return `错误：发生意外错误：${error instanceof Error ? error.message : String(error)}`;
}
```

## 共享工具

将通用功能提取到可重用的函数中：

```typescript
// 共享的API请求函数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}
```

## Async/Await 最佳实践

始终对网络请求和I/O操作使用async/await：

```typescript
// 良好：异步网络请求
async function fetchData(resourceId: string): Promise<ResourceData> {
  const response = await axios.get(`${API_URL}/resource/${resourceId}`);
  return response.data;
}

// 不佳：Promise链
function fetchData(resourceId: string): Promise<ResourceData> {
  return axios.get(`${API_URL}/resource/${resourceId}`)
    .then(response => response.data);  // 可读性和可维护性较差
}
```

## TypeScript 最佳实践

1. **使用严格的TypeScript**：在tsconfig.json中启用严格模式
2. **定义接口**：为所有数据结构创建清晰的接口定义
3. **避免使用`any`**：使用适当的类型或`unknown`代替`any`
4. **使用Zod进行运行时验证**：使用Zod模式验证外部数据
5. **类型守卫**：为复杂类型检查创建类型守卫函数
6. **错误处理**：始终使用try-catch并进行适当的错误类型检查
7. **空值安全**：使用可选链（`?.`）和空值合并（`??`）

```typescript
// 良好：使用Zod和接口实现类型安全
interface UserResponse {
  id: string;
  name: string;
  email: string;
  team?: string;
  active: boolean;
}

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  team: z.string().optional(),
  active: z.boolean()
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const data = await apiCall(`/users/${id}`);
  return UserSchema.parse(data);  // 运行时验证
}

// 不佳：使用any类型
async function getUser(id: string): Promise<any> {
  return await apiCall(`/users/${id}`);  // 没有类型安全
}
```

## 包配置

### package.json

```json
{
  "name": "{service}-mcp-server",
  "version": "1.0.0",
  "description": "用于{Service} API集成的MCP服务器",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.6.1",
    "axios": "^1.7.9",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 完整示例

```typescript
#!/usr/bin/env node
/**
 * Example服务的MCP服务器。
 *
 * 该服务器提供与Example API交互的工具，包括用户搜索、
 * 项目管理和数据导出功能。
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios, { AxiosError } from "axios";

// 常量
const API_BASE_URL = "https://api.example.com/v1";
const CHARACTER_LIMIT = 25000;

// 枚举
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

// Zod模式
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "查询字符串至少需要2个字符")
    .max(200, "查询字符串不能超过200个字符")
    .describe("用于匹配姓名/邮箱的搜索字符串"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("返回结果的最大数量"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("分页跳过的结果数量"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("输出格式：'markdown' 用于人类可读或 'json' 用于机器可读")
}).strict();

type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

// 共享工具函数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "错误：资源未找到。请检查ID是否正确。";
        case 403:
          return "错误：权限被拒绝。您没有访问此资源的权限。";
        case 429:
          return "错误：请求频率超过限制。请稍后再试。";
        default:
          return `错误：API请求失败，状态码 ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "错误：请求超时。请重试。";
    }
  }
  return `错误：发生意外错误：${error instanceof Error ? error.message : String(error)}`;
}

// 创建MCP服务器实例
const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// 注册工具
server.registerTool(
  "example_search_users",
  {
    title: "搜索示例用户",
    description: `[完整描述如上所示]`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    // 实现如上所示
  }
);

// 主函数
async function main() {
  // 验证所需的环境变量
  if (!process.env.EXAMPLE_API_KEY) {
    console.error("错误：需要EXAMPLE_API_KEY环境变量");
    process.exit(1);
  }

  // 创建传输
  const transport = new StdioServerTransport();

  // 将服务器连接到传输
  await server.connect(transport);

  console.error("示例MCP服务器通过stdio运行中");
}

// 运行服务器
main().catch((error) => {
  console.error("服务器错误：", error);
  process.exit(1);
});
```

---

## 高级MCP特性

### 资源注册

将数据作为资源公开，以实现高效的基于URI的访问：

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/sdk/types.js";

// 使用URI模板注册资源
server.registerResource(
  {
    uri: "file://documents/{name}",
    name: "文档资源",
    description: "通过名称访问文档",
    mimeType: "text/plain"
  },
  async (uri: string) => {
    // 从URI中提取参数
    const match = uri.match(/^file:\/\/documents\/(.+)$/);
    if (!match) {
      throw new Error("无效的URI格式");
    }

    const documentName = match[1];
    const content = await loadDocument(documentName);

    return {
      contents: [{
        uri,
        mimeType: "text/plain",
        text: content
      }]
    };
  }
);

// 动态列出可用资源
server.registerResourceList(async () => {
  const documents = await getAvailableDocuments();
  return {
    resources: documents.map(doc => ({
      uri: `file://documents/${doc.name}`,
      name: doc.name,
      mimeType: "text/plain",
      description: doc.description
    }))
  };
});
```

**何时使用资源vs工具：**
- **资源**：用于使用简单基于URI的参数进行数据访问
- **工具**：用于需要验证和业务逻辑的复杂操作
- **资源**：当数据相对静态或基于模板时
- **工具**：当操作具有副作用或复杂工作流时

### 多种传输选项

TypeScript SDK支持不同的传输机制：

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

// Stdio传输（默认 - 用于CLI工具）
const stdioTransport = new StdioServerTransport();
await server.connect(stdioTransport);

// SSE传输（用于实时Web更新）
const sseTransport = new SSEServerTransport("/message", response);
await server.connect(sseTransport);

// HTTP传输（用于Web服务）
// 根据你的HTTP框架集成进行配置
```

**传输选择指南：**
- **Stdio**：命令行工具、子进程集成、本地开发
- **HTTP**：Web服务、远程访问、多个同时客户端
- **SSE**：实时更新、服务器推送通知、Web仪表板

### 通知支持

当服务器状态发生变化时通知客户端：

```typescript
// 当工具列表变更时通知
server.notification({
  method: "notifications/tools/list_changed"
});

// 当资源变更时通知
server.notification({
  method: "notifications/resources/list_changed"
});
```

请谨慎使用通知 - 仅在服务器功能确实发生变化时使用。

---

## 代码最佳实践

### 代码可组合性和可重用性

你的实现必须优先考虑可组合性和代码重用：

1. **提取通用功能**：
   - 为跨多个工具使用的操作创建可重用的辅助函数
   - 构建共享的API客户端用于HTTP请求，而不是重复代码
   - 将错误处理逻辑集中在工具函数中
   - 将业务逻辑提取到可以组合的专用函数中
   - 提取共享的markdown或JSON字段选择和格式化功能

2. **避免重复**：
   - 永远不要在工具之间复制粘贴相似的代码
   - 如果你发现自己在写两次相似的逻辑，将其提取为函数
   - 分页、过滤、字段选择和格式化等常见操作应该共享
   - 身份验证/授权逻辑应该集中管理

## 构建和运行

在运行之前，请务必先构建你的TypeScript代码：

```bash
# 构建项目
npm run build

# 运行服务器
npm start

# 带自动重载的开发模式
npm run dev
```

在认为实现完成之前，请务必确保 `npm run build` 能够成功完成。

## 质量检查清单

在完成Node/TypeScript MCP服务器实现之前，请确保：

### 战略设计
- [ ] 工具支持完整的工作流程，而不仅仅是API端点包装器
- [ ] 工具名称反映自然的任务细分
- [ ] 响应格式针对代理上下文效率进行了优化
- [ ] 在适当的地方使用人类可读的标识符
- [ ] 错误消息指导代理正确使用

### 实现质量
- [ ] 聚焦实现：实现了最重要和最有价值的工具
- [ ] 所有工具都使用 `registerTool` 进行注册，并带有完整配置
- [ ] 所有工具都包含 `title`、`description`、`inputSchema` 和 `annotations`
- [ ] 正确设置了注释（readOnlyHint、destructiveHint、idempotentHint、openWorldHint）
- [ ] 所有工具使用Zod模式进行运行时输入验证，并带有 `.strict()` 强制约束
- [ ] 所有Zod模式都有适当的约束条件和描述性错误消息
- [ ] 所有工具都有全面的描述，包含明确的输入/输出类型
- [ ] 描述中包含返回值示例和完整的模式文档
- [ ] 错误消息清晰、可操作且具有教育意义

### TypeScript质量
- [ ] 为所有数据结构定义了TypeScript接口
- [ ] 在tsconfig.json中启用了严格的TypeScript模式
- [ ] 不使用 `any` 类型 - 改用 `unknown` 或适当的类型
- [ ] 所有异步函数都有明确的Promise<T>返回类型
- [ ] 错误处理使用适当的类型守卫（例如：`axios.isAxiosError`、`z.ZodError`）

### 高级特性（如适用）
- [ ] 为适当的数据端点注册了资源
- [ ] 配置了适当的传输方式（stdio、HTTP、SSE）
- [ ] 为动态服务器功能实现了通知
- [ ] 使用SDK接口实现类型安全

### 项目配置
- [ ] Package.json包含所有必要的依赖
- [ ] 构建脚本在dist/目录中生成可工作的JavaScript
- [ ] 主入口点已正确配置为dist/index.js
- [ ] 服务器名称遵循格式：`{service}-mcp-server`
- [ ] tsconfig.json已正确配置了严格模式

### 代码质量
- [ ] 在适用的地方正确实现了分页
- [ ] 大型响应会检查CHARACTER_LIMIT常量并使用清晰的消息进行截断
- [ ] 为潜在的大型结果集提供了过滤选项
- [ ] 所有网络操作都能优雅地处理超时和连接错误
- [ ] 通用功能被提取到可重用的函数中
- [ ] 相似操作的返回类型保持一致

### 测试和构建
- [ ] `npm run build` 能够成功完成且无错误
- [ ] 创建了可执行的dist/index.js
- [ ] 服务器可以运行：`node dist/index.js --help`
- [ ] 所有导入都能正确解析
- [ ] 示例工具调用能够正常工作