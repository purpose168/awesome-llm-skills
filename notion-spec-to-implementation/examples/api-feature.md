# 示例：API 功能实施

## 用户请求

> "为用户配置文件 API 规范创建实施计划"

## 工作流程执行

### 步骤 1：获取规范

```
Notion:notion-search
query: "用户配置文件 API 规范"
query_type: "internal"
```

找到：工程规范中的"用户配置文件 API 规范"

```
Notion:notion-fetch
id: "user-profile-api-spec-page-id"
```

### 步骤 2：解析规范

**提取的规范内容：**

```markdown
# 用户配置文件 API 规范

## 概述
用于用户配置文件管理的 RESTful API

## 需求

### 功能需求
- FR-1：按 ID 获取用户配置文件
- FR-2：更新用户配置文件（姓名、简介、头像）
- FR-3：上传配置文件头像
- FR-4：获取用户的公开配置文件（有限字段）
- FR-5：按姓名搜索用户

### 非功能需求
- NFR-1：响应时间 < 200ms (p95)
- NFR-2：支持 1000 个并发用户
- NFR-3：头像上传 < 5MB
- NFR-4：GDPR 合规（数据可移植性）

## API 端点

GET /api/v1/users/:id
PUT /api/v1/users/:id
POST /api/v1/users/:id/avatar
GET /api/v1/users/:id/public
GET /api/v1/users/search

## 数据模型
- id (UUID)
- email (string, unique)
- name (string)
- bio (text, max 500 chars)
- avatar_url (string)
- created_at (timestamp)
- updated_at (timestamp)

## 安全性
- 身份验证：JWT bearer token
- 授权：用户只能更新自己的配置文件
- 速率限制：每用户 100 req/min

## 验收标准
- AC-1：所有端点返回正确的 HTTP 状态代码
- AC-2：验证错误返回 400 并附带错误详细信息
- AC-3：未授权访问返回 401
- AC-4：超过速率限制返回 429
- AC-5：头像图像存储在 S3 中
```

### 步骤 3：创建实施计划

```
Notion:notion-create-pages

parent: { page_id: "engineering-plans-parent-id" }

pages: [{
  properties: {
    "title": "实施计划：用户配置文件 API"
  },
  content: "[实施计划]"
}]
```

**创建的实施计划：**

```markdown
# 实施计划：用户配置文件 API

## 概述
构建用于用户配置文件管理的 RESTful API，包含 CRUD 操作、头像上传和搜索功能。

## 链接规范
<mention-page url="...">用户配置文件 API 规范</mention-page>

## 需求摘要

### 功能需求
- ✅ 获取用户配置文件（已验证）
- ✅ 更新配置文件字段（姓名、简介）
- ✅ 上传头像并处理图像
- ✅ 公开配置文件视图（有限字段）
- ✅ 按姓名搜索用户

### 非功能需求
- **性能**：< 200ms 响应时间 (p95)
- **可扩展性**：1000 个并发用户
- **存储**：头像文件 < 5MB 到 S3
- **合规性**：GDPR 数据可移植性

### 验收标准
- 所有端点具有正确的状态代码
- 输入验证并附带错误详细信息
- 需要 JWT 身份验证
- 强制执行速率限制
- 头像存储在 S3 中

## 技术方法

### 架构
- **框架**：Express.js (Node.js)
- **数据库**：PostgreSQL
- **存储**：AWS S3 用于头像
- **缓存**：Redis 用于配置文件数据
- **搜索**：PostgreSQL 全文搜索

### 关键设计决策
1. **JWT 身份验证**：无状态身份验证，可水平扩展
2. **S3 用于头像**：卸载存储，准备 CDN 集成
3. **Redis 缓存**：减少频繁访问的配置文件的数据库负载
4. **速率限制**：令牌桶算法，每用户限制

## 实施阶段

### 阶段 1：基础（第 1-2 天）
**目标**：设置核心基础设施

**任务**：
- [ ] <mention-page url="...">设置数据库架构</mention-page>
- [ ] <mention-page url="...">配置 S3 存储桶</mention-page>
- [ ] <mention-page url="...">设置 Redis 缓存</mention-page>
- [ ] <mention-page url="...">创建 API 框架</mention-page>

**交付物**：包含数据库、存储、缓存的工作框架  
**估算工作量**：2 天

### 阶段 2：核心端点（第 3-5 天）
**目标**：实施主要 CRUD 操作

**任务**：
- [ ] <mention-page url="...">实施 GET 用户配置文件</mention-page>
- [ ] <mention-page url="...">实施 PUT 更新配置文件</mention-page>
- [ ] <mention-page url="...">添加输入验证</mention-page>
- [ ] <mention-page url="...">添加 JWT 身份验证中间件</mention-page>
- [ ] <mention-page url="...">实施速率限制</mention-page>

**交付物**：带有身份验证的工作 CRUD 操作  
**估算工作量**：3 天

### 阶段 3：头像上传（第 6-7 天）
**目标**：使用 S3 进行头像管理

**任务**：
- [ ] <mention-page url="...">实施头像上传端点</mention-page>
- [ ] <mention-page url="...">添加图像验证（大小、格式）</mention-page>
- [ ] <mention-page url="...">处理和调整图像大小</mention-page>
- [ ] <mention-page url="...">使用签名 URL 上传到 S3</mention-page>

**交付物**：头像上传/更新功能  
**估算工作量**：2 天

### 阶段 4：搜索和公开配置文件（第 8-9 天）
**目标**：完成剩余功能

**任务**：
- [ ] <mention-page url="...">实施用户搜索</mention-page>
- [ ] <mention-page url="...">实施公开配置文件端点</mention-page>
- [ ] <mention-page url="...">添加搜索索引</mention-page>
- [ ] <mention-page url="...">优化搜索查询</mention-page>

**交付物**：搜索和公开配置文件工作正常  
**估算工作量**：2 天

### 阶段 5：测试和优化（第 10-12 天）
**目标**：生产就绪质量

**任务**：
- [ ] <mention-page url="...">编写单元测试</mention-page>
- [ ] <mention-page url="...">编写集成测试</mention-page>
- [ ] <mention-page url="...">性能测试</mention-page>
- [ ] <mention-page url="...">安全审计</mention-page>
- [ ] <mention-page url="...">API 文档</mention-page>

**交付物**：已测试、已文档化、生产就绪的 API  
**估算工作量**：3 天

## 依赖关系

### 外部依赖
- 已创建 AWS S3 存储桶 ✅
- Redis 实例可用 ✅
- 已配置 PostgreSQL 数据库 ✅

### 内部依赖
- JWT 身份验证服务（已存在）
- 用户数据库表（已存在）
- 日志基础设施（已存在）

### 阻碍因素
目前无

## 风险与缓解

### 风险 1：图像处理性能
- **概率**：中等
- **影响**：中等
- **缓解措施**：使用后台作业队列进行处理，立即返回签名上传 URL

### 风险 2：S3 上传失败
- **概率**：低
- **影响**：中等
- **缓解措施**：实施指数退避的重试逻辑，临时回退到本地存储

### 风险 3：速率限制复杂性
- **概率**：低
- **影响**：低
- **缓解措施**：使用经过验证的库（express-rate-limit 和 Redis 存储）

### 风险 4：搜索性能
- **概率**：中等
- **影响**：中等
- **缓解措施**：添加数据库索引，如果需要，稍后考虑 Elasticsearch

## 时间线

| 里程碑 | 目标日期 | 状态 |
|-----------|-------------|--------|
| 阶段 1 完成 | 10 月 16 日 | ⏳ 计划中 |
| 阶段 2 完成 | 10 月 19 日 | ⏳ 计划中 |
| 阶段 3 完成 | 10 月 21 日 | ⏳ 计划中 |
| 阶段 4 完成 | 10 月 23 日 | ⏳ 计划中 |
| 阶段 5 完成 | 10 月 26 日 | ⏳ 计划中 |
| **生产部署** | **10 月 28 日** | ⏳ 计划中 |

**总持续时间**：12 个工作日（约 2.5 周）

## 成功标准

### 技术成功
- [ ] 所有 5 个端点已实施并正常工作
- [ ] 在负载测试中验证响应时间 < 200ms (p95)
- [ ] 处理 1000 个并发用户
- [ ] 满足所有验收标准
- [ ] 测试覆盖率 > 80%
- [ ] 安全扫描通过
- [ ] API 文档完整

### 业务成功
- [ ] 用户配置文件更新功能正常
- [ ] 头像上传可靠工作
- [ ] 搜索在 < 500ms 内返回相关结果
- [ ] 第一周零关键错误

## 资源

### 文档
- <mention-page url="...">用户配置文件 API 规范</mention-page>（原始规范）
- <mention-page url="...">身份验证服务文档</mention-page>
- <mention-page url="...">AWS S3 设置指南</mention-page>

### 相关工作
- <mention-page url="...">用户身份验证 API</mention-page>（类似模式）
- <mention-page url="...">文件上传服务</mention-page>（头像上传参考）

### 外部参考
- Express.js 最佳实践
- AWS S3 SDK 文档
- PostgreSQL 全文搜索指南

## 进度跟踪

### 阶段状态
- 阶段 1：⏳ 未开始
- 阶段 2：⏳ 未开始
- 阶段 3：⏳ 未开始
- 阶段 4：⏳ 未开始
- 阶段 5：⏳ 未开始

**总体进度**：0% 完成

### 最新更新
*实施计划创建于 2025 年 10 月 14 日*
```

### 步骤 4：查找任务数据库

```
Notion:notion-search
query: "任务数据库"
query_type: "internal"
```

找到："工程任务"数据库

### 步骤 5：获取任务数据库架构

```
Notion:notion-fetch
id: "tasks-database-id"
```

**检索到的架构：**
- 数据源：`collection://tasks-db-uuid`
- 属性：名称（标题）、状态（选择）、优先级（选择）、相关任务（关系）、故事点（数字）、标签（多选）

### 步骤 6：创建实施任务

现在为阶段 1 创建任务：

**任务 1：设置数据库架构**

```
Notion:notion-create-pages

parent: { data_source_id: "collection://tasks-db-uuid" }

pages: [{
  properties: {
    "Name": "为用户配置文件 API 设置数据库架构",
    "Status": "待办",
    "Priority": "高",
    "Related Tasks": ["impl-plan-page-id", "spec-page-id"],
    "Story Points": 3,
    "Tags": "backend, database, api"
  },
  content: "## 上下文\n<mention-page url=\"...\">用户配置文件 API 规范</mention-page> 的实施任务\n\n<mention-page url=\"...\">实施计划：用户配置文件 API</mention-page> 的一部分 - 阶段 1\n\n## 目标\n为用户配置文件存储创建数据库架构\n\n## 需求\n基于规范数据模型：\n- id (UUID, primary key)\n- email (string, unique index)\n- name (string, not null)\n- bio (text, max 500 chars)\n- avatar_url (string, nullable)\n- created_at (timestamp)\n- updated_at (timestamp)\n\n## 验收标准\n- [ ] 创建迁移文件\n- [ ] 架构包含所有必需字段\n- [ ] email（唯一）和 name（搜索）上的索引\n- [ ] 验证约束（bio 长度、email 格式）\n- [ ] 在开发数据库上测试迁移\n- [ ] 创建回滚迁移\n\n## 技术方法\n```sql\nCREATE TABLE user_profiles (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  email VARCHAR(255) UNIQUE NOT NULL,\n  name VARCHAR(255) NOT NULL,\n  bio TEXT CHECK (length(bio) <= 500),\n  avatar_url TEXT,\n  created_at TIMESTAMP DEFAULT NOW(),\n  updated_at TIMESTAMP DEFAULT NOW()\n);\n\nCREATE INDEX idx_user_profiles_email ON user_profiles(email);\nCREATE INDEX idx_user_profiles_name ON user_profiles USING gin(to_tsvector('english', name));\n```\n\n## 依赖关系\n- 阻塞于：无\n- 阻塞：所有阶段 2 任务\n\n## 估算工作量\n3 个故事点（半天）\n"
}]
```

*[为所有阶段创建类似任务 - 共 20 个任务]*

### 步骤 7：将计划链接回规范

```
Notion:notion-update-page
page_id: "user-profile-api-spec-page-id"
command: "insert_content_after"
selection_with_ellipsis: "## 验收标准..."
new_str: "

---

## 实施

**实施计划**：<mention-page url=\"...\">实施计划：用户配置文件 API</mention-page>

**实施任务**：查看计划以获取完整任务分解（5 个阶段共 20 个任务）

**状态**：规划完成，准备开始实施
"
```

## 提供给用户的摘要

```markdown
## 实施计划已创建 ✅

### 计划概述
- **功能**：用户配置文件 API
- **持续时间**：12 天（约 2.5 周）
- **阶段**：5 个（基础 → 核心 → 头像 → 搜索 → 测试）
- **任务**：已创建 20 个任务
- **目标发布**：2025 年 10 月 28 日

### 实施阶段

**阶段 1：基础**（2 天）
- 数据库架构
- S3 和 Redis 设置
- API 框架

**阶段 2：核心端点**（3 天）
- GET/PUT 用户配置文件
- 身份验证和验证
- 速率限制

**阶段 3：头像上传**（2 天）
- 图像上传和验证
- S3 集成
- 图像处理

**阶段 4：搜索和公开配置文件**（2 天）
- 用户搜索
- 公开配置文件端点

**阶段 5：测试和优化**（3 天）
- 单元和集成测试
- 性能测试
- 文档

### 关键交付物
- 5 个 REST API 端点
- 头像上传到 S3
- 用户搜索功能
- 综合测试
- API 文档

### 创建的链接
✅ 计划页面：<mention-page url="...">实施计划：用户配置文件 API</mention-page>
✅ 规范已更新并链接到计划
✅ 在任务数据库中创建 20 个任务
✅ 所有任务链接到计划和规范

### 后续步骤
1. 审查并批准计划
2. 将任务分配给团队成员
3. 开始阶段 1（基础）
4. 每日站会以跟踪进度

**准备开始实施！🚀**
```

## 演示的关键功能

### 规范解析
- 提取需求（功能和非功能）
- 识别 API 端点
- 注意数据模型
- 捕获验收标准
- 理解安全要求

### 实施计划
- 分解为逻辑阶段
- 适当排序工作（基础 → 功能 → 测试）
- 识别依赖关系
- 估算每个阶段的工作量
- 创建现实的时间线

### 任务创建
- 生成 20 个具体任务
- 每个任务都有上下文、验收标准、技术方法
- 任务链接到规范和计划
- 注意适当的依赖关系

### 双向链接
- 计划链接到规范
- 规范更新以链接到计划
- 任务链接到两者
- 所有工件之间易于导航

最适用于：功能实施、API 开发、技术项目
