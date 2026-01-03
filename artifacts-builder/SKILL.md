---
name: artifacts-builder
description: 用于使用现代前端Web技术（React、Tailwind CSS、shadcn/ui）创建复杂、多组件claude.ai HTML工件的工具套件。适用于需要状态管理、路由或shadcn/ui组件的复杂工件 - 不适用于简单的单文件HTML/JSX工件。
license: 完整条款见LICENSE.txt
---

# Artifacts Builder（工件构建器）

要构建功能强大的前端claude.ai工件，请按照以下步骤操作：
1. 使用`scripts/init-artifact.sh`初始化前端仓库
2. 通过编辑生成的代码开发您的工件
3. 使用`scripts/bundle-artifact.sh`将所有代码打包到单个HTML文件中
4. 向用户展示工件
5. （可选）测试工件

**技术栈**：React 18 + TypeScript + Vite + Parcel（打包） + Tailwind CSS + shadcn/ui

## 设计与风格指南

非常重要：为避免所谓的"AI劣质设计"，请避免使用过多的居中布局、紫色渐变、统一的圆角和Inter字体。

## 快速开始

### 步骤1：初始化项目

运行初始化脚本创建一个新的React项目：
```bash
# 使用脚本初始化新的React项目
bash scripts/init-artifact.sh <project-name>
# 进入项目目录
cd <project-name>
```

这将创建一个完全配置好的项目，包含：
- ✅ React + TypeScript（通过Vite）
- ✅ Tailwind CSS 3.4.1 带 shadcn/ui 主题系统
- ✅ 配置了路径别名 (`@/`)
- ✅ 预安装了40+个shadcn/ui组件
- ✅ 包含所有Radix UI依赖项
- ✅ 配置了用于打包的Parcel（通过.parcelrc）
- ✅ 兼容Node 18+（自动检测并固定Vite版本）

### 步骤2：开发您的工件

要构建工件，请编辑生成的文件。有关指导，请参阅下面的**常见开发任务**。

### 步骤3：打包为单个HTML文件

要将React应用打包为单个HTML工件：
```bash
# 将React应用打包为单个HTML文件
bash scripts/bundle-artifact.sh
```

这将创建`bundle.html` - 一个自包含的工件，所有JavaScript、CSS和依赖项都内联其中。该文件可以直接在Claude对话中作为工件共享。

**要求**：您的项目根目录中必须有一个`index.html`文件。

**脚本功能**：
- 安装打包依赖项（parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline）
- 创建带路径别名支持的`.parcelrc`配置
- 使用Parcel构建（无源代码映射）
- 使用html-inline将所有资产内联到单个HTML中

### 步骤4：与用户共享工件

最后，在与用户的对话中共享打包好的HTML文件，以便他们可以将其作为工件查看。

### 步骤5：测试/可视化工件（可选）

注意：这是一个完全可选的步骤。仅在必要或请求时执行。

要测试/可视化工件，请使用可用工具（包括其他技能或内置工具，如Playwright或Puppeteer）。一般来说，避免预先测试工件，因为这会增加请求与完成的工件可见之间的延迟。如果有请求或出现问题，在展示工件后再进行测试。

## 参考

- **shadcn/ui组件**：https://ui.shadcn.com/docs/components