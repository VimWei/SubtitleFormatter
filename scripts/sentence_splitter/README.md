# 句子拆分工具 (Sentence Splitter)

## 功能描述

句子拆分工具是一个基于规则和启发式方法的文本处理工具，专门用于将长句和复合句拆分为更短的句子。**无需LLM即可实现智能拆分**，通过分析句子结构、连接词和标点符号来做出拆分决策。

## 核心特性

- **智能拆分**: 基于连接词和标点符号的优先级进行拆分
- **上下文感知**: 排除数字格式和简单并列的误拆分
- **多轮弱化**: 确保复杂长句能够被合理拆分
- **递归处理**: 支持对复合句进行多次拆分
- **格式保持**: 逗号和冒号及其空格保留在上一行

## 使用方法

### 基本用法

```bash
# 自动保存到 data/output/ 目录（推荐）
uv run python scripts/sentence_splitter/main.py input.txt

# 自定义输出文件
uv run python scripts/sentence_splitter/main.py input.txt -o output.txt
uv run python scripts/sentence_splitter/main.py input.txt --output output.txt
```

### 通过脚本管理器使用

```bash
# 自动保存到 data/output/ 目录（推荐）
uv run python scripts_manager.py sentence-splitter input.txt

# 自定义输出文件
uv run python scripts_manager.py sentence-splitter input.txt -o output.txt
```

## 输入输出格式

### 输入格式
- **文件格式**: 文本文件，每行一个句子
- **编码**: UTF-8
- **内容**: 支持英文长句和复合句

### 输出格式
- **格式**: 每行一个拆分后的句子
- **命名**: 自动添加 `.split.txt` 后缀
- **位置**: 默认保存到 `data/output/` 目录，注意会覆盖已存在的同名文件
