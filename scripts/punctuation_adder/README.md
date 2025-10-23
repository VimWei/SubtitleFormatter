# Punctuation Adder

> **自动标点恢复工具** - 使用机器学习模型为英文文本自动添加标点符号

## 📋 功能描述

使用 `deepmultilingualpunctuation` 模型为英文文本自动添加标点符号，支持句子分割和首字母大写，支持单文件和通配符批量处理。

## 🚀 快速开始

### 安装依赖
```bash
uv sync --group punctuation-adder
```

### 基本使用
```bash
# 处理单个文件
uv run scripts_manager.py punctuation-adder file.txt

# 批量处理
uv run scripts_manager.py punctuation-adder *.txt

# 指定输出文件名
uv run scripts_manager.py punctuation-adder file.txt -o output.txt
```

## 📖 使用说明

### 默认路径处理
- **输入**: 优先查找 `data/input/` 目录，支持完整路径
- **输出**: 自动保存到 `data/output/` 目录，添加 `.punctuated.txt` 后缀

### 处理示例
**输入** (data/input/example.txt):
```
hello world this is a test without punctuation
```

**输出** (data/output/example.punctuated.txt):
```
Hello world, this is a test without punctuation.
```

## ⚙️ 技术实现

- **模型**: `deepmultilingualpunctuation` (RNN-based)
- **编码**: UTF-8-SIG 输入，UTF-8 输出
- **处理**: 标点恢复 → 后处理（句子分割、首字母大写、破折号转逗号）

## ⚠️ 注意事项

- 模型基于政治演讲数据训练，对技术文本准确性可能较低
- 主要专注于标点恢复，大小写纠正能力有限
- 建议处理完成后人工检查重要文档

## 🔍 故障排除

**模型加载失败**: 检查网络连接，首次运行需要下载模型
**权限错误**: 确保脚本有写入 `data/output/` 目录的权限