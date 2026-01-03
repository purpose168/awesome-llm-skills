# 示例：从对话到常见问题

## 用户请求

> "将这次关于部署故障排除的对话保存到常见问题中"

**上下文**：用户刚刚进行了一次对话，解释了如何排查常见的部署错误。

## 对话摘要

对话涵盖了：
1. **问题**："为什么部署失败并出现'端口已被占用'错误？"
2. **回答**：上一次部署的进程仍在运行，需要终止它
3. **问题**："我如何找到并终止进程？"
4. **分享的命令**：`lsof -ti:3000 | xargs kill -9` 或使用 `pm2 restart app`
5. **问题**："关于'无法连接到数据库'错误呢？"
6. **回答**：检查数据库凭据，验证数据库是否正在运行，检查网络连接
7. **最佳实践**：始终首先检查日志（`pm2 logs` 或 `docker logs`）

## 工作流程执行

### 步骤 1：识别内容类型

这是问答内容 → **常见问题条目**格式是适当的

### 步骤 2：结构化常见问题条目

从对话中提取不同的问答对：

**常见问题 1**：端口已被占用错误
**常见问题 2**：无法连接到数据库错误
**常见问题 3**：一般故障排除方法

### 步骤 3：确定目标位置

```
Notion:notion-search
query: "FAQ deployment"
query_type: "internal"
```

找到：工程文档中的"部署常见问题"数据库

```
Notion:notion-fetch
id: "deployment-faq-database-id"
```

**模式**：
- 问题（标题）
- 类别（选择）：部署、配置、故障排除等
- 标签（多选）
- 最后审查（日期）

### 步骤 4：创建常见问题条目

**常见问题条目 1：端口已被占用**

```
Notion:notion-create-pages

parent: { data_source_id: "collection://faq-db-uuid" }

pages: [{
  properties: {
    "Question": "为什么部署失败并出现'端口已被占用'错误？",
    "Category": "故障排除",
    "Tags": "部署, 错误, 端口",
    "date:Last Reviewed:start": "2025-10-14",
    "date:Last Reviewed:is_datetime": 0
  },
  content: "## 简短回答\n\n部署端口（通常是 3000）仍被上一次部署的进程占用。在重新部署之前，您需要终止现有进程。\n\n## 详细解释\n\n当您部署应用程序时，它会尝试绑定到特定端口（例如端口 3000）。如果上一次部署没有正常关闭，该进程可能仍在运行并占用端口。这会阻止新部署启动。\n\n**常见原因**：\n- 上一次部署崩溃且未清理\n- 手动启动的 `node` 进程被遗忘\n- PM2 或其他进程管理器未正确重启\n- 同时尝试多次部署\n\n## 解决方案\n\n### 选项 1：终止使用该端口的进程\n\n```bash\n# 查找并终止端口 3000 上的进程\nlsof -ti:3000 | xargs kill -9\n```\n\n将 `3000` 替换为您的应用程序端口号。\n\n### 选项 2：如果使用 PM2\n\n```bash\n# 重启应用程序\npm2 restart app\n\n# 或删除并重启\npm2 delete app\npm2 start app.js --name app\n```\n\n### 选项 3：检查所有 node 进程\n\n```bash\n# 列出所有 node 进程\nps aux | grep node\n\n# 通过 PID 终止特定进程\nkill -9 <PID>\n```\n\n## 预防\n\n1. **使用进程管理器**：PM2、systemd 或 Docker 自动处理清理\n2. **优雅关闭**：在应用程序中实现适当的关闭处理程序\n3. **健康检查**：在启动新部署之前监控上一次部署是否已关闭\n\n```javascript\n// 优雅关闭示例\nprocess.on('SIGTERM', () => {\n  server.close(() => {\n    console.log('服务器已关闭');\n    process.exit(0);\n  });\n});\n```\n\n## 验证\n\n终止进程后，验证端口是否空闲：\n\n```bash\nlsof -ti:3000\n# 如果端口空闲，应该不返回任何内容\n```\n\n## 相关问题\n- <mention-page url=\"...\">如何检查什么在使用端口？</mention-page>\n- <mention-page url=\"...\">如何配置应用程序端口？</mention-page>\n- <mention-page url=\".[... 87 个字符省略 ...]
}]
```

**常见问题条目 2：数据库连接错误**

```
Notion:notion-create-pages

parent: { data_source_id: "collection://faq-db-uuid" }

pages: [{
  properties: {
    "Question": "为什么在部署期间会出现'无法连接到数据库'错误？",
    "Category": "故障排除",
    "Tags": "部署, 数据库, 错误",
    "date:Last Reviewed:start": "2025-10-14",
    "date:Last Reviewed:is_datetime": 0
  },
  content: "## 简短回答\n\n数据库连接错误通常意味着数据库未运行、凭据不正确或存在网络连接问题。检查数据库状态，验证凭据并测试连接性。\n\n## 详细解释\n\n应用程序在启动期间无法建立与数据库的连接。这会阻止应用程序正常初始化。\n\n**常见原因**：\n- 数据库服务未运行\n- 连接凭据不正确\n- 网络连接问题（防火墙、安全组）\n- 数据库主机/端口配置错误\n- 数据库达到连接限制\n- SSL/TLS 配置不匹配\n\n## 故障排除步骤\n\n### 步骤 1：检查数据库状态\n\n```bash\n# 对于本地 PostgreSQL\npg_isready -h localhost -p 5432\n\n# 对于 Docker\ndocker ps | grep postgres\n\n# 对于 MongoDB\nmongosh --eval \"db.adminCommand('ping')\"\n```\n\n### 步骤 2：验证凭据\n\n检查您的 `.env` 或配置文件：\n\n```bash\n# 常见环境变量\nDB_HOST=localhost\nDB_PORT=5432\nDB_NAME=myapp_production\nDB_USER=myapp_user\nDB_PASSWORD=***********\n```\n\n手动测试连接：\n\n```bash\n# PostgreSQL\npsql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME\n\n# MongoDB\nmongosh \"mongodb://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME\"\n```\n\n### 步骤 3：检查网络连接\n\n```bash\n# 测试端口是否可达\ntelnet $DB_HOST $DB_PORT\n\n# 或使用 nc\nnc -zv $DB_HOST $DB_PORT\n\n# 检查防火墙规则（如果适用）\nsudo iptables -L\n```\n\n### 步骤 4：检查应用程序日志\n\n```bash\n# PM2 日志\npm2 logs app\n\n# Docker 日志\ndocker logs container-name\n\n# 应用程序日志\ntail -f /var/log/app/error.log\n```\n\n查找特定错误消息：\n- `ECONNREFUSED`：数据库未运行或主机/端口错误\n- `Authentication failed`：凭据错误\n- `Timeout`：网络/防火墙问题\n- `Too many connections`：达到数据库连接限制\n\n## 按错误类型的解决方案\n\n#[... 1753 个字符省略 ...]
}]
```

**常见问题条目 3：一般故障排除**

```
Notion:notion-create-pages

parent: { data_source_id: "collection://faq-db-uuid" }

pages: [{
  properties: {
    "Question": "当部署失败时，我应该首先检查什么？",
    "Category": "故障排除",
    "Tags": "部署, 调试, 最佳实践",
    "date:Last Reviewed:start": "2025-10-14",
    "date:Last Reviewed:is_datetime": 0
  },
  content: "## 简短回答\n\n**始终首先检查日志。** 日志包含直接指向问题的错误消息。使用 `pm2 logs`、`docker logs` 或检查应用程序的日志文件。\n\n## 详细解释\n\n日志是您最重要且首要的调试工具。它们显示：\n- 确切的错误消息\n- 堆栈跟踪\n- 时间信息\n- 配置问题\n- 依赖问题\n\n大多数部署问题都可以通过仔细阅读日志来诊断和修复。\n\n## 如何检查日志\n\n### PM2\n\n```bash\n# 查看所有日志\npm2 logs\n\n# 查看特定应用程序的日志\npm2 logs app-name\n\n# 仅查看错误\npm2 logs --err\n\n# 实时跟踪日志\npm2 logs --lines 100\n```\n\n### Docker\n\n```bash\n# 查看日志\ndocker logs container-name\n\n# 跟踪日志\ndocker logs -f container-name\n\n# 最后 100 行\ndocker logs --tail 100 container-name\n\n# 带时间戳\ndocker logs -t container-name\n```\n\n### 应用程序日志\n\n```bash\n# 跟踪应用程序日志\ntail -f /var/log/app/app.log\ntail -f /var/log/app/error.log\n\n# 在日志中搜索错误\ngrep -i error /var/log/app/*.log\n\n# 查看带上下文的日志\ngrep -B 5 -A 5 \"ERROR\" app.log\n```\n\n## 系统性故障排除方法\n\n### 1. 检查日志\n- 仔细阅读错误消息\n- 记录确切的错误类型和消息\n- 检查时间戳以查找错误发生的时间\n\n### 2. 验证配置\n- 环境变量设置正确吗？\n- 配置文件存在且有效吗？\n- 路径和文件权限正确吗？\n\n### 3. 检查依赖\n- 所有包都安装了吗？（`node_modules` 存在吗？）\n- 安装了正确的版本吗？\n- 有任何本机模块编译错误吗？\n\n### 4. 验证环境\n- 所需服务正在运行吗（数据库、Redis 等）？\n- 端口可用吗？\n- 网络连接正常吗？\n\n### 5. 单独测试组件\n- 您可以手动连接到数据库吗？\n- 您可以在本地运行应用程序吗？\n- 健康检查端点工作吗？\n\n### 6. 检查最近的变[... 2073 个字符省略 ...]
}]
```

### 步骤 5：更新常见问题索引

```
Notion:notion-fetch
id: "faq-index-page-id"
```

```
Notion:notion-update-page
page_id: "faq-index-page-id"
command: "insert_content_after"
selection_with_ellipsis: "## 部署和故障排除..."
new_str: "
- <mention-page url=\"...\">为什么部署失败并出现'端口已被占用'错误？</mention-page>
- <mention-page url=\"...\">为什么会出现'无法连接到数据库'错误？</mention-page>
- <mention-page url=\"...\">当部署失败时，我应该首先检查什么？</mention-page>
"
```

## 提供给用户的摘要

```markdown
## 已创建的常见问题条目 ✅

### 已捕获的对话
将部署故障排除对话转换为 3 个全面的常见问题条目。

### 已创建的常见问题条目

1. **端口已被占用错误**
   - 问题：由于端口被占用导致部署失败
   - 解决方案：终止进程、使用 PM2、检查 node 进程
   - 预防：使用进程管理器、优雅关闭
   - 链接：<mention-page url="...">端口已被占用常见问题</mention-page>

2. **数据库连接错误**
   - 问题：部署期间无法连接到数据库
   - 故障排除：4 步系统性方法
   - 解决方案：按错误类型（凭据、网络、限制）
   - 预防：连接池、健康检查、重试逻辑
   - 链接：<mention-page url="...">数据库连接常见问题</mention-page>

3. **一般故障排除方法**
   - 最佳实践：始终首先检查日志
   - 工具：PM2 日志、Docker 日志、应用程序日志
   - 系统性方法：6 步调试过程
   - 常见错误：模块未找到、权限、端口
   - 链接：<mention-page url="...">故障排除第一步常见问题</mention-page>

### 内容结构

每个常见问题包括：
✅ 简短回答（快速参考）
✅ 详细解释（完整上下文）
✅ 多个解决方案选项
✅ 代码示例和命令
✅ 预防策略
✅ 链接到相关问题
✅ 最后更新日期

### 数据库集成

- ✅ 添加到常见问题数据库（不是独立页面）
- ✅ 设置属性：类别（故障排除）、标签、日期
- ✅ 常见问题索引页面已更新链接
- ✅ 相关问题之间的交叉引用

### 添加的价值

**从对话** → **到结构化知识**：
- 随意问答 → 专业常见问题条目
- 隐式知识 → 显式文档
- 一次性帮助 → 可重用资源
- 5 分钟对话 → 永久团队知识

**未来收益**：
- 团队可以在常见问题上自助服务
- 新团队成员可以更快入职
- 减少重复问题
- 提高故障排除速度

**知识已捕获并保存！📚**
```

## 演示的关键功能

### 内容提取
- 从对话中识别不同的问答对
- 提取命令、解决方案和最佳实践
- 保留故障排除工作流程

### 常见问题结构
- 简短回答以便快速参考
- 详细解释以便理解
- 多个解决方案（选项 1、2、3）
- 带注释的代码示例
- 预防策略
- 相关问题链接

### 数据库集成
- 在常见问题数据库中创建（不是独立页面）
- 设置适当的属性（类别、标签、日期）
- 更新索引页面并添加链接
- 交叉引用相关问题

### 价值转换
- 将非正式对话转换为专业文档
- 添加结构、示例和预防提示
- 使知识可搜索和可发现
- 创建永久团队资源

适用于：常见问题创建、知识保存、团队文档
