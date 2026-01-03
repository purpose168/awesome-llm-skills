# 数据库最佳实践

创建和维护知识捕获数据库的一般指导。

## 核心原则

### 1. 保持简单
- 从核心属性开始
- 仅在需要时添加更多
- 不要过度设计

### 2. 使用一致的命名
- 标题属性作为主要标识符
- 状态用于生命周期跟踪
- 标签用于灵活分类
- 所有者用于问责

### 3. 包含元数据
- 创建/更新时间戳
- 所有者或维护者
- 最后审查日期
- 状态指示器

### 4. 启用发现
- 自由使用标签
- 创建有用的视图
- 链接相关内容
- 使用清晰的标题

### 5. 为扩展做规划
- 尽早考虑过滤器
- 使用关系进行连接
- 考虑搜索
- 用类别组织

## 创建数据库

### 使用 `Notion:notion-create-database`

文档数据库示例：

```javascript
{
  "parent": {"page_id": "wiki-page-id"},
  "title": [{"text": {"content": "团队文档"}}],
  "properties": {
    "Type": {
      "select": {
        "options": [
          {"name": "操作指南", "color": "blue"},
          {"name": "概念", "color": "green"},
          {"name": "参考", "color": "gray"},
          {"name": "常见问题", "color": "yellow"}
        ]
      }
    },
    "Category": {
      "select": {
        "options": [
          {"name": "工程", "color": "red"},
          {"name": "产品", "color": "purple"},
          {"name": "设计", "color": "pink"}
        ]
      }
    },
    "Tags": {"multi_select": {"options": []}},
    "Owner": {"people": {}},
    "Status": {
      "select": {
        "options": [
          {"name": "草稿", "color": "gray"},
          {"name": "最终", "color": "green"},
          {"name": "已弃用", "color": "red"}
        ]
      }
    }
  }
}
```

### 获取数据库模式

在创建页面之前，始终获取数据库以获取模式：

```
Notion:notion-fetch
id: "database-url-or-id"
```

这将返回要使用的确切属性名称和类型。

## 数据库选择指南

| 需求 | 使用此数据库 |
|------|-------------------|
| 通用文档 | [文档数据库](documentation-database.md) |
| 跟踪决策 | [决策日志](decision-log-database.md) |
| 问答知识库 | [常见问题数据库](faq-database.md) |
| 团队特定内容 | [团队 Wiki](team-wiki-database.md) |
| 分步指南 | [操作指南数据库](how-to-guide-database.md) |
| 事故/项目学习 | [学习数据库](learning-database.md) |

## 提示

1. **从通用文档数据库开始** - 最灵活
2. **添加专用数据库**，随着需求出现（常见问题、决策）
3. **使用关系**连接相关文档
4. **创建视图**用于常见用例
5. **每季度审查属性** - 删除未使用的属性
6. **在数据库描述中记录模式**
7. **培训团队**关于属性使用和约定
