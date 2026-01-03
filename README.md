<h1 align="center">Awesome LLM 技能集</h1>

<p align="center">
  <a href="url">
  <img width="1280" height="640" alt="Awesome LLM 技能集" src="https://github.com/user-attachments/assets/fb10b4c7-4155-4026-95b9-b4b979a14921" />
  </a>

</p>


<p align="center">
  精心策划的 LLM 技能、资源和工具列表，用于在 Claude Code、Codex、Gemini CLI、通义千问代码、OpenCode 等工具上自定义 AI 工作流程。
</p>


<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome" />
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="欢迎提交 PR" />
  </a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=flat-square" alt="许可证: Apache-2.0" />
  </a>
</p>


## 目录

- [什么是 LLM 技能？](#what-are-llm-skills)
- [快速开始](#quick-start)
- [技能列表](#skills)
- [平台](#platforms)
  - [Claude Code (Anthropic)](#claude-code-anthropic)
  - [Claude Desktop (Anthropic)](#claude-desktop-anthropic)
  - [Codex CLI (OpenAI)](#codex-cli-openai)
  - [Gemini CLI (Google)](#gemini-cli-google)
  - [OpenCode (开源 CLI)](#opencode-open-source-cli)
  - [通义千问代码 (阿里巴巴)](#qwen-code-alibaba)
- [贡献](#contributing)
  - [快速贡献步骤](#quick-contribution-steps)
- [资源](#resources)
  - [官方文档](#official-documentation)
  - [社区资源](#community-resources)
- [许可证](#license)


## 什么是 LLM 技能？

LLM 技能是可自定义的工作流程，用于教授 LLM 如何根据您的独特需求执行特定任务。技能使 LLM 能够在所有 LLM 平台上以可重复、标准化的方式执行任务。

## 快速开始

1. **创建项目级或用户级技能文件夹**
   使用以下发现路径之一，让 Claude Code 自动找到它：

   * 项目级：`.claude/skills/webapp-testing/`
   * 用户级：`~/.claude/skills/webapp-testing/`

2. **添加 `SKILL.md`**（必需）

  基本技能模板：
  
  ```markdown
  ---
  name: my-skill-name
  description: A clear description of what this skill does and when to use it.
  ---
  
  # My Skill Name
  
  Detailed description of the skill's purpose and capabilities.
  
  ## When to Use This Skill
  
  - Use case 1
  - Use case 2
  - Use case 3
  
  ## Instructions
  
  [Detailed instructions for LLMs on how to execute this skill]
  
  ## Examples
  
  [Real-world examples showing the skill in action]
  ```
  <!-- 技能模板说明：
  - 以YAML格式的元数据开头，包含技能名称和描述
  - 技能名称部分提供详细的用途和能力描述
  - 使用场景部分列出适用的具体情况
  - 指令部分提供LLM执行技能的详细步骤
  - 示例部分展示技能在实际场景中的应用
  -->

  - 专注于特定、可重复的任务
  - 包含清晰的示例和边缘情况
  - 为LLM编写指令，而非终端用户
  - 记录前提条件和依赖项
  - 包含错误处理指导

3. **保持支持文件精简**
   只添加必要的文件（例如，`resources/` 中的小型测试数据、辅助脚本）。这可以使技能加载更快，也更容易让 Claude 应用。

4. **加载技能**

   * **Claude（网页版或桌面版）：** 通过 **设置 → 功能 → 技能** → **上传技能** 上传 ZIP 文件。
   * **Claude Code（终端）：** 将文件夹放在 `.claude/skills/`（项目级）或 `~/.claude/skills/`（用户级）下。Claude Code 会从这些位置发现技能。
   * **其他 CLI（Codex、Gemini、OpenCode、通义千问代码）：** 它们不原生支持 Anthropic 的技能格式，请在提示中引用您的 `SKILL.md`（Gemini CLI 支持 `@` 文件/上下文附件）。
  
5. **使用技能**
   只需用自然语言提问，可选地提及技能名称——例如："使用 **Webapp 测试** 技能验证结账流程并生成 `report.md`。" Claude 可以根据您的请求自动调用相关技能。

6. **（可选）在 Claude Code 中启动仓库会话**
   支持斜杠命令；许多用户在开始工作前运行 `/init` 来生成 `CLAUDE.md` 并引导上下文。

## 技能列表

### 支持 MCP 的技能

- [Notion 知识捕获](./notion-knowledge-capture/) - 将聊天和决策转换为结构化的 Notion 页面和数据库条目，并提供适当的链接。
- [Notion 会议智能](./notion-meeting-intelligence/) - 从 Notion 上下文中准备会议，并创建内部预读材料和外部议程。
- [Notion 研究文档](./notion-research-documentation/) - 搜索 Notion，综合多个页面，并将引用的研究文档写回到 Notion。
- [Notion 规范到实现](./notion-spec-to-implementation/) - 将 Notion 规范转换为带有验收标准和进度跟踪的任务计划。

### 文档处理

- [docx](https://github.com/anthropics/skills/tree/main/document-skills/docx) - 创建、编辑、分析带有修订记录、评论和格式的 Word 文档。
- [pdf](https://github.com/anthropics/skills/tree/main/document-skills/pdf) - 提取文本、表格、元数据，合并和注释 PDF。
- [pptx](https://github.com/anthropics/skills/tree/main/document-skills/pptx) - 读取、生成和调整幻灯片、布局、模板。
- [xlsx](https://github.com/anthropics/skills/tree/main/document-skills/xlsx) - 电子表格操作：公式、图表、数据转换。
- [Markdown 转 EPUB 转换器](https://github.com/smerchek/claude-epub-skill) - 将 Markdown 文档和聊天摘要转换为专业的 EPUB 电子书文件。*由 [@smerchek](https://github.com/smerchek) 开发*

### 开发与代码工具

- [artifacts-builder](https://github.com/anthropics/skills/tree/main/artifacts-builder) - 使用现代前端 Web 技术（React、Tailwind CSS、shadcn/ui）创建复杂、多组件 claude.ai HTML 工件的工具套件。
- [aws-skills](https://github.com/zxkane/aws-skills) - 包含 CDK 最佳实践、成本优化的 MCP 服务器和无服务器/事件驱动架构模式的 AWS 开发工具。
- [变更日志生成器](./changelog-generator/) - 通过分析历史记录并将技术提交转换为用户友好的发布说明，自动从 git 提交创建面向用户的变更日志。
- [D3.js 可视化](https://github.com/chrisvoncsefalvay/claude-d3js-skill) - 教 Claude 生成 D3 图表和交互式数据可视化。*由 [@chrisvoncsefalvay](https://github.com/chrisvoncsefalvay) 开发*
- [FFUF Web 模糊测试](https://github.com/jthack/ffuf_claude_skill) - 集成 ffuf Web 模糊测试工具，使 Claude 能够运行模糊测试任务并分析结果中的漏洞。*由 [@jthack](https://github.com/jthack) 开发*
- [完成开发分支](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) - 通过提供清晰的选项和处理选定的工作流程来指导完成开发工作。
- [iOS 模拟器](https://github.com/conorluddy/ios-simulator-skill) - 使 Claude 能够与 iOS 模拟器交互，用于测试和调试 iOS 应用程序。*由 [@conorluddy](https://github.com/conorluddy) 开发*
- [MCP 构建器](./mcp-builder/) - 指导使用 Python 或 TypeScript 创建高质量的 MCP（模型上下文协议）服务器，用于将外部 API 和服务与 LLM 集成。
- [move-code-quality-skill](https://github.com/1NickPappas/move-code-quality-skill) - 根据官方 Move Book 代码质量检查清单分析 Move 语言包，确保符合 Move 2024 版标准和最佳实践。
- [Playwright 浏览器自动化](https://github.com/lackeyjb/playwright-skill) - 模型调用的 Playwright 自动化，用于测试和验证 Web 应用程序。*由 [@lackeyjb](https://github.com/lackeyjb) 开发*
- [pypict-claude-skill](https://github.com/omkamal/pypict-claude-skill) - 使用 PICT（成对独立组合测试）为需求或代码设计全面的测试用例，生成具有成对覆盖率的优化测试套件。
- [技能创建器](./skill-creator/) - 提供创建有效 Claude 技能的指导，通过专业知识、工作流程和工具集成来扩展功能。
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) - 在几分钟内自动将任何文档网站转换为 Claude AI 技能。*由 [@yusufkaraaslan](https://github.com/yusufkaraaslan) 开发*
- [测试驱动开发](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - 在编写实现代码之前，用于实现任何功能或修复错误。
- [使用 git worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/) - 创建隔离的 git worktrees，具有智能目录选择和安全验证功能。
- [Webapp 测试](./webapp-testing/) - 使用 Playwright 测试本地 Web 应用程序，验证前端功能、调试 UI 行为并捕获屏幕截图。

### 数据与分析

- [CSV 数据摘要工具](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) - 无需用户提示，自动分析 CSV 文件并生成带有可视化的综合见解。*由 [@coffeefuelbump](https://github.com/coffeefuelbump) 开发*
- [postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres) - 对 PostgreSQL 数据库执行安全的只读 SQL 查询，支持多连接和深度防御安全机制。*由 [@sanjay3290](https://github.com/sanjay3290) 开发*
- [根本原因追踪](https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing) - 当执行过程中出现深层错误且需要追溯查找原始触发因素时使用。

### 商业与营销

- [品牌指南](./brand-guidelines/) - 将 Anthropic 官方品牌颜色和排版应用于工件，确保一致的视觉标识和专业设计标准。
- [竞争对手广告提取器](./competitive-ads-extractor/) - 从广告库中提取和分析竞争对手的广告，以了解产生共鸣的信息和创意方法。
- [域名创意生成器](./domain-name-brainstormer/) - 生成创意域名 ideas，并检查包括 .com、.io、.dev 和 .ai 在内的多个 TLD 的可用性。
- [内部沟通](./internal-comms/) - 帮助编写内部沟通内容，包括 3P 更新、公司通讯、常见问题解答、状态报告和项目更新，使用公司特定格式。
- [潜在客户研究助手](./lead-research-assistant/) - 通过分析您的产品、搜索目标公司并提供可操作的外展策略，识别和筛选高质量的潜在客户。

### 沟通与写作

- [article-extractor](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor) - 从网页中提取完整的文章文本和元数据。
- [brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) - 通过结构化提问和替代方案探索，将粗略的想法转化为完整的设计。
- [内容研究写作助手](./content-research-writer/) - 通过进行研究、添加引用、改进钩子并提供逐节反馈来协助撰写高质量内容。
- [家族历史研究](https://github.com/emaynard/claude-family-history-research-skill) - 为规划家族历史和家谱研究项目提供帮助。
- [会议洞察分析器](./meeting-insights-analyzer/) - 分析会议记录，揭示行为模式，包括冲突避免、发言比例、填充词和领导风格。
- [NotebookLM 集成](https://github.com/PleasePrompto/notebooklm-skill) - 让 Claude Code 直接与 NotebookLM 聊天，获取完全基于上传文档的有来源依据的答案。*由 [@PleasePrompto](https://github.com/PleasePrompto) 开发*

### 创意与媒体

- [Canvas 设计](./canvas-design/) - 使用设计理念和美学原则在 PNG 和 PDF 文档中创建精美的视觉艺术，用于海报、设计和静态作品。
- [imagen](https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen) - 使用 Google Gemini 的图像生成 API 生成图像，用于 UI 原型、图标、插图和视觉资产。*由 [@sanjay3290](https://github.com/sanjay3290) 开发*
- [图像增强器](./image-enhancer/) - 通过提高分辨率、锐度和清晰度来改善图像和截图质量，用于专业演示和文档。
- [Slack GIF 创建器](./slack-gif-creator/) - 创建针对 Slack 优化的动画 GIF，具有尺寸限制验证器和可组合的动画原语。
- [主题工厂](./theme-factory/) - 将专业字体和颜色主题应用于工件，包括幻灯片、文档、报告和 HTML 登录页面，提供 10 种预设主题。
- [视频下载器](./video-downloader/) - 从 YouTube 和其他平台下载视频，用于离线观看、编辑或存档，支持各种格式和质量选项。
- [youtube-transcript](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/youtube-transcript) - 从 YouTube 视频获取字幕并准备摘要。

### 生产力与组织

- [文件整理器](./file-organizer/) - 通过理解上下文、查找重复项并建议更好的组织结构，智能地组织文件和文件夹。
- [发票整理器](./invoice-organizer/) - 通过读取文件、提取信息并一致地重命名，自动组织发票和收据以准备纳税。
- [抽奖获胜者选择器](./raffle-winner-picker/) - 使用加密安全的随机性从列表、电子表格或 Google Sheets 中随机选择赠品和竞赛的获胜者。
- [ship-learn-next](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/ship-learn-next) - 基于反馈循环帮助迭代确定下一步要构建或学习内容的技能。
- [tapestry](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/tapestry) - 将相关文档相互链接并总结为知识网络。

### 协作与项目管理

- [git-pushing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/git-pushing) - 自动化 git 操作和仓库交互。
- [review-implementing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/review-implementing) - 评估代码实现计划并与规范保持一致。
- [test-fixing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/test-fixing) - 检测失败的测试并提出补丁或修复方案。

### 安全与系统

- [computer-forensics](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/computer-forensics) - 数字取证分析和调查技术。
- [file-deletion](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/file-deletion) - 安全文件删除和数据清理方法。
- [metadata-extraction](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/metadata-extraction) - 提取和分析文件元数据用于取证目的。
- [threat-hunting-with-sigma-rules](https://github.com/jthack/threat-hunting-with-sigma-rules-skill) - 使用 Sigma 检测规则来搜索威胁并分析安全事件。

## 平台

### Claude Code (Anthropic)

**设置和启用技能**

* **安装：** 确保已安装 Node 20+ 和 Visual Studio Code。Claude Code 通过运行时访问、终端支持和代码生成来增强 Claude 的编码能力。
* **入门：** 从 VS Code 或终端启动 Claude Code。Claude Code 会自动从 `.claude/skills/`（项目级）或 `~/.claude/skills/`（用户级）目录发现技能。
* **使用技能：** 只需用自然语言描述您的需求。Claude Code 会根据您的请求上下文自动激活相关技能。

### Claude Desktop (Anthropic)

**设置和启用技能**

* Claude Desktop 为 Claude 提供跨 Windows、macOS 和 Linux 平台的原生应用体验。
* 通过设置 → 功能 → 技能访问技能。以 ZIP 文件形式上传自定义技能或从可用的社区技能中选择。
* 桌面应用支持所有 Claude 功能，包括文件上传、代码生成和实时协作。

### Codex CLI (OpenAI)

**设置和启用技能**

* OpenAI 的 Codex 为 GitHub Copilot 提供支持，可通过 CLI 工具访问，用于代码生成和自动化。
* 虽然 Codex 不原生支持 Anthropic 的技能格式，但您可以通过在提示或配置文件中包含指令来适应技能。
* 最适合代码补全、重构和跨多种编程语言生成样板代码。

### Gemini CLI (Google)

**设置和启用技能**

* 安装 Node 20+，然后通过 `npm install -g @google/gemini-cli` 安装 Gemini CLI，或使用 `npx @google/gemini-cli` 按需运行。
* 运行 `gemini` 并使用您的 Google 账号登录；会打开一个浏览器窗口进行身份验证。Gemini CLI 目前没有内置支持 Anthropic 技能，但您可以通过加载自己的 `SKILL.md` 文件并在提示中引用它来遵循技能指令。使用 `@` 符号上传包含技能指令的文件。

### OpenCode (开源 CLI)

**设置和启用技能**

* 使用单行脚本安装 OpenCode：`curl -fsSL https://opencode.ai/install | bash`。
* 运行 `opencode auth login` 并选择您的提供商（例如，Cerebras）来配置您的 API 密钥。
* 使用 `opencode` 启动界面，并使用 `/init` 初始化您的项目上下文。
* OpenCode 不原生加载 Anthropic 技能，但您可以在项目中放置一个 `skills/` 文件夹，并要求 OpenCode 读取 `SKILL.md` 文件；这近似于技能功能，允许您跨工具重用指令。

### 通义千问代码 (阿里巴巴)

**设置和启用技能**

* 确保已安装 Node 20+，然后使用 `npm install -g @qwen-code/qwen-code@latest` 安装通义千问代码，并使用 `qwen --version` 验证。或者，克隆仓库并在本地安装。
* 通过运行 `qwen` 启动会话。通义千问代码目前不直接支持 Anthropic 技能，但您仍然可以通过创建 `skills/` 目录并提示通义千问代码遵循您的 `SKILL.md` 文件中的指令来采用技能模式。



## 贡献

我们欢迎您的贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解详情：

- 如何提交新技能
- 技能质量标准
- 拉取请求流程
- 行为准则

### 快速贡献步骤

1. 确保您的技能基于真实用例
2. 检查现有技能中是否有重复项
3. 遵循技能结构模板
4. 在多个平台上测试您的技能
5. 提交包含清晰文档的拉取请求

## 资源

### 官方文档

- [LLM 技能概述](https://www.anthropic.com/news/skills) - 官方公告和功能介绍
- [技能用户指南](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - 如何在 LLM 中使用技能
- [创建自定义技能](https://support.claude.com/en/articles/12512198-creating-custom-skills) - 技能开发指南
- [技能 API 文档](https://docs.claude.com/en/api/skills-guide) - API 集成指南
- [代理技能博客文章](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - 工程深度解析

### 社区资源

- [Anthropic 技能仓库](https://github.com/anthropics/skills) - 官方示例技能
- [Claude 社区](https://community.anthropic.com) - 与其他用户讨论技能
- [技能市场](https://claude.ai/marketplace) - 发现和分享技能
- [Notion 技能](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0) - Notion 集成技能

## 许可证

本仓库采用 Apache License 2.0 许可证。

各个技能可能有不同的许可证 - 请检查每个技能文件夹以获取特定的许可证信息。

---
