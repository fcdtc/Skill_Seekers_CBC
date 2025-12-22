# 🚀 Skill Seekers GitHub 仓库生成 Skill 指南

## 📋 从 GitHub 仓库生成 Skill 的完整命令

### 方案1：使用 GitHub Token（推荐，避免 API 限制）
```bash
# 1. 设置 GitHub Token（如果还没有）
export GITHUB_TOKEN=your_github_personal_access_token

# 2. 生成 skill（会从 GitHub API 获取）
skill-seekers github --repo https://github.com/trpc-group/trpc-agent-go --name trpc-agent-go

# 3. 增强生成的 skill（使用 CodeBuddy Code）
skill-seekers enhance output/trpc-agent-go/

# 4. 打包成 .zip 文件
skill-seekers package output/trpc-agent-go/
```

### 方案2：使用本地克隆（绕过 API 限制，最快）
```bash
# 1. 先克隆仓库到本地（如果还没有）
git clone https://github.com/trpc-group/trpc-agent-go.git /tmp/trpc-agent-go

# 2. 直接分析本地仓库生成 skill
skill-seekers github --local-repo /tmp/trpc-agent-go --name trpc-agent-go

# 3. 增强 skill
skill-seekers enhance output/trpc-agent-go/

# 4. 打包
skill-seekers package output/trpc-agent-go/
```

### 方案3：一键完整流程
```bash
# 使用 install 命令：fetch → scrape → enhance → package → upload
skill-seekers install --config trpc-agent-go --no-upload
```

---

## 📖 Skill Seekers 所有命令详解

### 🔥 核心工作流命令

#### **1. `scrape` - 文档网站抓取**
```bash
skill-seekers scrape --config configs/react.json --enhance-local
```
**作用**：从文档网站抓取内容并生成 skill
- 输入：配置文件（JSON格式）
- 输出：`output/{name}/` 目录包含 SKILL.md 和参考资料
- 支持本地增强（`--enhance-local`）

#### **2. `github` - GitHub 仓库分析**
```bash
skill-seekers github --repo user/repo --name myskill
skill-seekers github --local-repo /path/to/repo --name myskill
```
**作用**：分析 GitHub 仓库的代码结构和文档
- 两种模式：API 抓取或本地分析
- 输出代码模式、API 定义、README 等

#### **3. `enhance` - AI 增强**
```bash
skill-seekers enhance output/react/
```
**作用**：使用 CodeBuddy Code 增强 SKILL.md 质量
- 读取参考资料，生成更好的示例和指导
- 30-60秒完成，无需 API key

#### **4. `unified` - 多源合并**
```bash
skill-seekers unified --config configs/react_unified.json --merge-mode codebuddy-enhanced
```
**作用**：合并文档、GitHub、PDF 等多个数据源
- 检测冲突并智能合并
- 支持 rule-based 和 codebuddy-enhanced 模式

---

### 📦 打包和分发命令

#### **5. `package` - 打包技能**
```bash
skill-seekers package output/react/
skill-seekers package output/react/ --upload
```
**作用**：将 skill 目录打包成 `.zip` 文件
- 可选择自动上传到 Claude
- 生成可分享的技能包

#### **6. `upload` - 上传技能**
```bash
skill-seekers upload output/react.zip
```
**作用**：上传已打包的 `.zip` 文件到 Claude
- 需要 ANTHROPIC_API_KEY

---

### 🛠️ 辅助工具命令

#### **7. `estimate` - 页面估算**
```bash
skill-seekers estimate configs/react.json
```
**作用**：估算文档网站的页面数量和抓取时间
- 快速验证配置是否正确
- 帮助设置合理的 max_pages 参数

#### **8. `pdf` - PDF 提取**
```bash
skill-seekers pdf --input document.pdf --name myskill
```
**作用**：从 PDF 文件提取内容和代码
- 支持文字、图片、表格提取
- 生成结构化 skill

#### **9. `install-agent` - 安装到 AI 工具**
```bash
skill-seekers install-agent output/react/ --agent claude
skill-seekers install-agent output/react/ --agent all
```
**作用**：将 skill 安装到各种 AI 开发工具
- 支持 Claude、Cursor、VS Code、Amp 等
- 全局或项目级安装

---

### 🚀 自动化命令

#### **10. `install` - 一键完整流程**
```bash
skill-seekers install --config react  # 使用预设配置
skill-seekers install --config configs/custom.json  # 使用配置文件
skill-seekers install --config react --no-upload  # 不自动上传
```
**作用**：完整的自动化工作流
- Phase 1: 获取配置
- Phase 2: 抓取文档
- Phase 3: AI 增强（必需）
- Phase 4: 打包 skill
- Phase 5: 上传到 Claude（可选）

---

## 🎯 推荐流程：GitHub repository → skill

**推荐使用这个流程：**

```bash
# Step 1: 设置 GitHub Token（一次设置，永久使用）
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Step 2: 从 GitHub 生成 skill（分析代码结构 + API）
skill-seekers github --repo https://github.com/trpc-group/trpc-agent-go --name trpc-agent-go

# Step 3: 增强 skill 质量（使用 CodeBuddy Code）
skill-seekers enhance output/trpc-agent-go/

# Step 4: 打包成可分享的 .zip 文件
skill-seekers package output/trpc-agent-go/

# 结果：output/trpc-agent-go.zip 文件，可直接上传到 Claude
```

如果遇到 API 限制，用 `--local-repo` 替代 `--repo` 参数即可！

---

## 🎯 最终推荐方案

对于 GitHub 仓库生成 skill，推荐使用：

```bash
# 如果没有 GitHub Token 或遇到 API 限制
git clone https://github.com/trpc-group/trpc-agent-go.git /tmp/trpc-agent-go
skill-seekers github --local-repo /tmp/trpc-agent-go --name trpc-agent-go
skill-seekers enhance output/trpc-agent-go/
skill-seekers package output/trpc-agent-go/
```

这样就能完整分析 trpc-agent-go 仓库的代码结构、API 设计、文档等，并生成高质量的 CodeBuddy skill！🚀

---

## 📚 常见问题

### Q: GitHub Token 如何获取？
A: 访问 https://github.com/settings/tokens → "Generate new token (classic)" → 选择权限：至少勾选 "public_repo"

### Q: 遇到 GitHub API 限制怎么办？
A: 使用 `--local-repo` 参数改为本地分析模式，完全绕过 API 限制

### Q: CodeBuddy Code 增强需要 API key 吗？
A: 不需要！现在项目已配置为使用 CodeBuddy Code，无需额外的 AI API key

### Q: 生成的 skill 文件在哪里？
A: 在 `output/{name}/` 目录下，最终的 `.zip` 文件在 `output/` 目录下

---

## 🔄 CodeBuddy Code 支持

本项目的本地 AI 增强功能已完全支持 **CodeBuddy Code**，无需额外配置即可使用！所有 `--enhance-local` 功能都将通过 CodeBuddy Code 进行处理。