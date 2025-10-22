# SubtitleFormatter 脚本使用指南

> **用户使用指南** - 如何使用 SubtitleFormatter 的脚本管理器

## 🚀 快速开始

### 基本命令
```bash
# 列出所有脚本
uv run python scripts_manager.py list

# 运行脚本（推荐方式）
uv run python scripts_manager.py <script_name> <arguments>

# 显示帮助
uv run python scripts_manager.py help <script_name>
```

## 📋 使用示例

### 文本差异检测
```bash
# 比较两个文本文件
uv run python scripts_manager.py text-diff old.txt new.txt --json
```

### 句子分割
```bash
# 将文本按句分割
uv run python scripts_manager.py sentence-splitter input.txt
```

## 📁 默认路径处理

脚本管理器支持智能默认路径，简化文件操作：

### 输入文件处理
- **自动检测**: 如果文件在 `data/input/` 目录中，只需提供文件名
- **完整路径**: 如果文件在其他位置，使用完整路径
- **自动创建**: 如果 `data/input/` 目录不存在，会自动创建

### 输出文件处理
- **自动输出**: 大多数脚本会自动将输出保存到 `data/output/` 目录
- **智能命名**: 根据输入文件名自动生成输出文件名
- **目录创建**: 如果 `data/output/` 目录不存在，会自动创建

### 使用示例
```bash
# 简单使用 - 文件在 data/input/ 中
uv run python scripts_manager.py sentence-splitter input.txt
# 输出自动保存到 data/output/input.txt

# 指定输出文件名
uv run python scripts_manager.py sentence-splitter input.txt -o result.txt
# 输出保存到 data/output/result.txt

# 使用完整路径
uv run python scripts_manager.py text-diff /path/to/old.txt /path/to/new.txt
```

## 📚 更多信息

### 具体脚本用法
每个脚本的详细用法请查阅：
- `scripts/` 下每个脚本目录的 `README.md`

### 脚本开发
如需开发新脚本，请查阅：
- `scripts/README.md` - 脚本开发规范