# 文本转句子工具 (Text to Sentences)

## 功能描述

将包含标点符号的连续文本按句分割，每句一行输出。这是一个简单的文本处理工具，专门用于处理类似字幕或转录文本的格式化需求。

## 特点

- **简单高效**: 基于正则表达式的句子分割
- **保持原样**: 只进行句子分割，不做其他文本处理
- **自动保存**: 默认自动保存到 data/output/ 目录
- **智能命名**: 使用原文件名添加 `.sentence.txt` 后缀
- **无依赖**: 仅使用Python标准库

## 使用方法

### 基本用法

```bash
# 自动保存到 data/output/ 目录（推荐）
uv run python scripts/text_to_sentences/main.py input.txt

# 自定义输出文件
uv run python scripts/text_to_sentences/main.py input.txt -o output.txt
uv run python scripts/text_to_sentences/main.py input.txt --output output.txt
```

### 通过脚本管理器使用

```bash
# 自动保存到 data/output/ 目录（推荐）
uv run python scripts_manager.py text-to-sentences input.txt

# 自定义输出文件
uv run python scripts_manager.py text-to-sentences input.txt -o output.txt
```

## 输入输出格式

### 输入格式
- 支持任意包含标点符号的文本文件
- 文件编码：UTF-8
- 句子以句号(.)、问号(?)、感叹号(!)结尾

### 输出格式
- 每行一个句子
- 保持原文本内容不变
- 自动去除多余空白字符
- 默认保存到 `data/output/` 目录
- 使用原文件名添加 `.sentence.txt` 后缀

## 示例

### 输入文件 (input.txt)
```
Let's take a look at some examples of Agentic AI applications. One task that many businesses carry out is invoice processing. So given an invoice like this, you might want to write software to extract the most important fields.
```

### 输出结果
```
Let's take a look at some examples of Agentic AI applications.
One task that many businesses carry out is invoice processing.
So given an invoice like this, you might want to write software to extract the most important fields.
```

## 技术实现

- **句子识别**: 使用正则表达式 `([.!?]+)\s+` 识别句子结束
- **文本处理**: 自动去除首尾空白字符，统一换行符处理
- **错误处理**: 完善的错误处理和用户友好的错误信息

## 注意事项

1. 该工具仅进行句子分割，不进行其他文本处理
2. 对于复杂的文本格式，可能需要预处理
3. 输出文件会覆盖已存在的同名文件
4. 确保输入文件使用UTF-8编码
5. 默认自动保存到 `data/output/` 目录，无需指定输出路径

## 版本信息

- 版本: v1.0.0
- 依赖: 无外部依赖
- Python版本: >= 3.11
