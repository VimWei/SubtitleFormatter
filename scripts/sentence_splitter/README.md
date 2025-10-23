# 句子拆分工具 (Sentence Splitter)

## 功能描述

句子拆分工具是一个基于规则和启发式方法的文本处理工具，专门用于将长句和复合句拆分为更短的句子。**无需LLM即可实现智能拆分**，通过分析句子结构、连接词和标点符号来做出拆分决策。

## 核心特性

### 🧠 智能拆分策略
- **连接词识别**: 自动识别并列连接词（and, or, but等）和从属连接词（because, since, if等）
- **标点符号分析**: 基于分号、冒号、逗号的优先级进行拆分
- **上下文感知**: 排除数字格式（如1,000）和简单并列（如apple, banana, orange）的误拆分
- **递归拆分**: 支持对复杂复合句进行多次拆分

### 🎯 拆分规则
1. **长度阈值**: 只拆分长度超过80字符的句子
2. **连接词优先**: 在连接词前进行拆分
3. **标点符号优先级**: 分号 > 冒号 > 逗号
4. **智能排除**: 自动排除数字分隔符和简单词汇并列

### 📊 处理效果
- 原始句子: 1个长句
- 拆分后: 2-4个短句（根据句子复杂度）
- 保持语义完整性
- 提高可读性

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
- **命名**: 自动添加 `.smart_split.txt` 后缀
- **位置**: 默认保存到 `data/output/` 目录

## 拆分示例

### 输入句子（长句）
```
So given an invoice like this, you might want to write software to extract the most important fields, which for this application, let's say is the biller, that would be tech flow solutions, the biller address, the amount due, which is $3,000, and the due date, which looks like it is August 20th, 2025.
```

### 输出结果（拆分后）
```
So given an invoice like this, you might want to write software to extract the most important fields
which for this application, let's say is the biller, that would be tech flow solutions, the biller address, the amount due, which is $3,000, and the due date, which looks like it is August 20th, 2025
```

### 更复杂的拆分示例

**输入**:
```
If you were to implement this with an agentic workflow, you might do so like this, and you write input an invoice, then call a PDF to text conversion API to turn the PDF into maybe formatted text, such as markdown text for the LLM to ingest, and then the LLM will look at the PDF and figure out, is this actually an invoice or is this some other type of document that they should just ignore?
```

**输出**:
```
If you were to implement this with an agentic workflow, you might do so like this
and you write input an invoice, then call a PDF to text conversion API to turn the PDF into maybe formatted text, such as markdown text for the LLM to ingest
and then the LLM will look at the PDF and figure out, is this actually an invoice or is this some other type of document that they should just ignore?
```

## 技术实现

### 核心算法
1. **句子分析**: 检查句子长度和复杂度
2. **拆分点识别**: 查找连接词和标点符号
3. **优先级排序**: 基于语法重要性排序拆分点
4. **上下文过滤**: 排除数字和简单并列
5. **递归拆分**: 对拆分后的部分继续处理

### 连接词库
- **并列连接词**: and, or, but, yet, so, for, nor
- **从属连接词**: because, since, as, if, when, while, although, though, unless, until, before, after
- **其他连接词**: however, therefore, moreover, furthermore, nevertheless, meanwhile, consequently

### 智能排除规则
- **数字格式**: 1,000,000, $3,000, 3.14
- **简单并列**: apple, banana, orange
- **缩写识别**: Mr., Mrs., Dr., Inc., Ltd.

## 使用场景

### 适用场景
- ✅ 字幕文本处理
- ✅ 转录文本优化
- ✅ 长句可读性提升
- ✅ 复合句结构化
- ✅ 文档预处理

### 不适用场景
- ❌ 需要深度语义理解的文本
- ❌ 诗歌或文学性文本
- ❌ 需要保持原始格式的文档

## 性能特点

- **处理速度**: 快速，基于正则表达式和字符串操作
- **内存占用**: 低，逐行处理
- **准确性**: 高，基于语法规则和启发式方法
- **可扩展性**: 易于添加新的拆分规则

## 注意事项

1. **语言支持**: 目前主要支持英文
2. **句子质量**: 输入应为完整的句子
3. **格式要求**: 每行一个句子
4. **输出覆盖**: 会覆盖已存在的同名文件
5. **编码要求**: 确保输入文件使用UTF-8编码

## 版本信息

- **版本**: v1.0.0
- **依赖**: 无外部依赖
- **Python版本**: >= 3.11
- **开发状态**: 稳定版

## 开发说明

该工具采用**规则+启发式**的方法，无需LLM即可实现智能拆分：

1. **规则基础**: 基于英语语法规则和标点符号使用规范
2. **启发式优化**: 通过上下文分析和模式识别提高准确性
3. **可扩展设计**: 易于添加新的拆分规则和连接词
4. **性能优化**: 使用正则表达式和高效字符串操作

相比LLM方案，这种方法具有：
- ✅ 更快的处理速度
- ✅ 更低的资源消耗
- ✅ 更可预测的结果
- ✅ 更易于调试和优化
