# Skill Seekers CBC 使用说明

## 项目简介

Skill Seekers CBC 是一个用于从本地仓库和PDF文档生成 Claude AI 技能的工具。它可以智能分析代码仓库，提取关键信息，并生成符合 Claude 格式的技能包。

## 核心功能

### 🏠 本地仓库抓取
- **智能README发现**：自动在各层级查找 README.md、README.rst 等文档文件
- **代码分析**：支持多种深度分析（surface、medium、deep）
- **配置文件识别**：自动提取 YAML、JSON 等配置文件
- **文件结构分析**：生成完整的目录结构树

### 📄 PDF文档抓取
- **内容提取**：提取PDF中的文本内容
- **表格识别**：支持表格数据提取
- **图片处理**：可选的图片内容分析（需要图片识别服务）

### 📦 技能生成
- **自动格式化**：生成符合 Claude 规范的 SKILL.md 文件
- **分类文档**：自动生成 references 目录，包含使用指南、配置说明等
- **质量检验**：自动检查技能完整性并评分
- **打包发布**：生成可直接上传到 Claude 的 zip 包

## 完整操作步骤

### 第一步：准备环境

```bash
# 克隆项目
git clone <项目地址>
cd Skill_Seekers_CBC

# 安装依赖
pip install -r requirements.txt
```

### 第二步：创建配置文件

在 `configs/` 目录下创建配置文件，支持三种类型：

#### 本地仓库配置 (`local_repo.json`)
```json
{
  "name": "my-skill",
  "description": "技能描述",
  "path": "/path/to/your/repository",
  "include_code": true,
  "code_analysis_depth": "surface",
  "include_tests": false,
  "include_configs": true,
  "exclude_dirs_additional": [".DS_Store", "node_modules"]
}
```

#### PDF文档配置 (`pdf_doc.json`)
```json
{
  "name": "pdf-skill",
  "description": "PDF技能描述",
  "pdf_path": "/path/to/document.pdf",
  "extract_tables": true,
  "extract_images": false
}
```

#### 混合源配置 (`unified.json`)
```json
{
  "name": "unified-skill",
  "description": "混合源技能",
  "merge_mode": "rule-based",
  "sources": [
    {
      "type": "local",
      "path": "/path/to/repo",
      "include_code": true,
      "code_analysis_depth": "surface"
    },
    {
      "type": "pdf",
      "path": "/path/to/document.pdf",
      "extract_tables": true
    }
  ],
  "merge_options": {
    "local_weight": 0.6,
    "pdf_weight": 0.4,
    "conflict_resolution": "local_priority"
  }
}
```

### 第三步：执行抓取

#### 本地仓库抓取
```bash
python -m src.skill_seekers.cli.main local --config configs/local_repo.json
```

#### PDF文档抓取
```bash
python -m src.skill_seekers.cli.main pdf --config configs/pdf_doc.json
```

#### 混合源抓取
```bash
python -m src.skill_seekers.cli.main unified --config configs/unified.json
```

### 第四步：构建技能

如果只生成了数据文件（`.json`），需要手动构建技能：

```bash
python src/skill_seekers/cli/build_local_skill.py output/your_data.json
```

### 第五步：AI增强（可选）

```bash
skill-seekers enhance output/trpc-go-examples/ --interactive-enhancement
```

**注意**：此步骤依赖 CodeBuddy Code 服务，如果服务不可用可跳过。

### 第六步：质量检验和打包

```bash
# 打包技能
echo "y" | python -m src.skill_seekers.cli.main package output/your_skill_directory
```

打包成功后会显示质量评分，生成的 `.zip` 文件可直接上传到 Claude。

## 命令参数详解

### 主命令
```bash
python -m src.skill_seekers.cli.main [子命令] [选项]
```

### 子命令说明

#### `local` - 本地仓库抓取
```bash
python -m src.skill_seekers.cli.main local --config CONFIG_FILE
```
- `--config`: 配置文件路径（必需）

#### `pdf` - PDF文档抓取
```bash
python -m src.skill_seekers.cli.main pdf --config CONFIG_FILE
```
- `--config`: 配置文件文件路径（必需）

#### `unified` - 混合源抓取
```bash
python -m src.skill_seekers.cli.main unified --config CONFIG_FILE
```
- `--config`: 配置文件路径（必需）

#### `enhance` - AI增强
```bash
python -m src.skill_seekers.cli.main enhance SKILL_DIRECTORY
```
- `位置参数`: 技能目录路径

#### `package` - 打包发布
```bash
python -m src.skill_seekers.cli.main package SKILL_DIRECTORY
```
- `位置参数`: 技能目录路径

## 配置参数详解

### 通用参数
- `name`: 技能名称（必需）
- `description`: 技能描述（必需）

### 本地仓库特有参数
- `path`: 仓库路径（必需）
- `include_code`: 是否包含代码分析（默认true）
- `code_analysis_depth`: 代码分析深度（surface|medium|deep，默认surface）
- `include_tests`: 是否包含测试文件（默认false）
- `include_configs`: 是否包含配置文件（默认true）
- `exclude_dirs_additional`: 额外排除的目录（列表格式）

### PDF特有参数
- `pdf_path`: PDF文件路径（必需）
- `extract_tables`: 是否提取表格（默认true）
- `extract_images`: 是否提取图片（默认false）

### 混合源特有参数
- `sources`: 数据源列表（必需）
- `merge_mode`: 合并模式（rule-based默认）
- `merge_options`: 合并选项

## 输出结果说明

### 数据文件
抓取完成后会生成 JSON 数据文件，包含：
- `repo_info`: 仓库基本信息
- `readme_files`: README文件列表
- `code_files`: 代码文件列表
- `config_files`: 配置文件列表
- `file_tree`: 文件结构树

### 技能目录结构
```
output/skill_name/
├── SKILL.md          # 主技能文档
├── references/       # 分类参考文档
│   ├── index.md
│   ├── getting_started.md
│   ├── configuration.md
│   ├── features.md
│   └── code_patterns.md
└── assets/          # 资源文件
```

### 质量评分标准
- **90-100分**：Grade A，优秀质量，可直接上传
- **80-89分**：Grade B，良好质量，小幅改进后可用
- **70-79分**：Grade C，一般质量，需要较多改进
- **60-69分**：Grade D，较差质量，需要大幅改进
- **<60分**：Grade F，不合格，无法使用

## 常见问题解决

### 1. 技能目录未生成
**问题**：执行抓取命令后没有生成 output 目录

**解决**：手动构建技能
```bash
python src/skill_seekers/cli/build_local_skill.py output/your_data.json
```

### 2. AI增强失败
**问题**：自动更新到 CodeBuddy Code 版本失败

**解决**：跳过AI增强步骤，直接进行打包。核心功能不受影响。

### 3. 质量评分低
**问题**：质量检验评分不理想

**解决**：检查并改进：
- 确保SKILL.md有YAML前置元数据
- 添加"When to Use This Skill"章节
- 确保reference文件在SKILL.md中有链接
- 改进文件结构展示格式

### 4. PDF处理失败
**问题**：PDF文件无法处理

**解决**：
- 检查PDF文件路径是否正确
- 确保PDF文件没有密码保护
- 检查文件权限

## 最佳实践

### 1. 仓库选择
- 选择有良好文档的仓库
- 确保有清晰的README文件
- 优先选择有结构化配置的项目

### 2. 配置优化
- 合理设置代码分析深度
- 根据需要排除不必要的目录
- 调整混合源的权重比例

### 3. 质量提升
- 完善SKILL.md的描述和示例
- 确保分类文档内容丰富
- 添加实际使用场景

### 4. 迭代改进
- 先生成基础版本
- 根据质量检验结果逐步改进
- 收集用户反馈持续优化

## 示例工作流

### 实例：转换 Go 微服务项目为技能

```bash
# 1. 创建配置
cat > configs/trpc-go-examples.json << EOF
{
  "name": "trpc-go-examples",
  "description": "tRPC-Go framework examples and tutorials",
  "path": "/path/to/trpc-go-example",
  "include_code": true,
  "code_analysis_depth": "surface",
  "include_tests": false,
  "include_configs": true
}
EOF

# 2. 执行抓取
python -m src.skill_seekers.cli.main local --config configs/trpc-go-examples.json

# 3. 构建技能
python src/skill_seekers/cli/build_local_skill.py output/trpc-go-examples_local_data.json

# 4. 打包发布
echo "y" | python -m src.skill_seekers.cli.main package output/trpc-go-examples

# 5. 上传到 Claude
# 访问 https://claude.ai/skills 上传生成的 zip 文件
```

## 技术支持

如遇问题，请检查：
1. Python 环境（建议 Python 3.8+）
2. 依赖包安装完整性
3. 文件路径和权限
4. 配置文件格式正确性

---

**版本**: 1.0.0
**更新日期**: 2025-12-24
**作者**: Skill Seekers Team
