# 示例：从讨论创建操作指南

**用户请求**："将我们关于部署到生产环境的讨论保存为操作指南"

## 工作流程

### 1. 从聊天中提取内容
从对话中识别：
- 部署先决条件
- 分步程序
- 常见问题和解决方案
- 最佳实践和技巧

### 2. 结构化为操作指南
组织为：
- 概述和先决条件
- 编号部署步骤
- 验证步骤
- 故障排除部分
- 相关资源

### 3. 查找位置
```
Notion:notion-search
query: "部署文档"
```
找到：工程 Wiki → 部署部分

### 4. 创建指南
```
Notion:notion-create-pages
parent: { page_id: "deployment-section-id" }
```

## 输出

```markdown
# 如何部署到生产环境

## 概述
使用 GitHub Actions 进行生产部署，实现零停机滚动更新。
**所需时间**：15-20 分钟 | **复杂度**：中级

## 先决条件
- [ ] PR 已批准并合并到 main 分支
- [ ] 所有 CI 测试通过
- [ ] 数据库迁移已审查
- [ ] 功能标志已配置

## 部署步骤

1. **验证 main 分支已准备就绪**
   ```bash
   git checkout main && git pull
   ```

2. **标记发布版本**
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```

3. **触发部署**
   - GitHub Actions 从标签推送自动启动
   - 监控：https://github.com/org/repo/actions

4. **数据库迁移**（如需要）
   - 在 GitHub Actions 中自动运行
   - 检查日志以确认完成

5. **验证部署**
   - 等待健康检查（2-3 分钟）
   - 测试关键端点
   - 在 Datadog 中检查错误率

## 验证清单
- [ ] k8s 仪表板中所有 pod 健康
- [ ] 过去 10 分钟内错误率 < 0.1%
- [ ] 响应时间 p95 < 500ms
- [ ] 测试登录流程
- [ ] 检查 Slack #alerts 频道

## 故障排除

**健康检查失败**
→ 检查 pod 日志：`kubectl logs -f deployment/api -n production`

**迁移错误**
→ 回滚：恢复标签，迁移自动回滚

**错误率高**
→ 紧急回滚：通过 GitHub Actions 自动部署上一个标签

## 最佳实践
- 在低流量时段部署（太平洋标准时间凌晨 2-4 点）
- 安排 2 名工程师待命
- 部署后监控 30 分钟
- 在 #engineering Slack 频道更新部署通知

## 相关文档
- <mention-page url="...">回滚程序</mention-page>
- <mention-page url="...">数据库迁移指南</mention-page>
```

### 5. 使其可发现
```
Notion:notion-update-page
page_id: "engineering-wiki-homepage"
command: "insert_content_after"
```
在工程 Wiki → 操作指南部分添加链接

## 关键成功因素
- 从讨论中捕获了团队知识
- 结构化为可操作的步骤
- 包括了经验中的故障排除方法
- 通过从 wiki 索引链接使其可发现
- 添加了元数据（时间、复杂度）
