# 开发指南

## 项目结构 

```
SmartTextFormatter/
├── modules/           # 核心功能模块
│   ├── __init__.py
│   ├── text_cleaner.py     # 文本清理
│   ├── sentence_handler.py  # 智能断句
│   ├── filler_remover.py   # 停顿词处理
│   ├── line_breaker.py     # 智能断行
│   ├── model_manager.py    # 模型管理
│   └── debug_output.py     # 调试输出
├── data/             # 输入输出文件
│   ├── input.txt     # 输入文本示例
│   └── output.txt    # 输出结果示例
├── docs/             # 项目文档
├── temp/             # 调试输出目录
├── config.yaml       # 配置文件
└── main.py          # 程序入口
```

## 核心模块说明

- `text_cleaner.py`: 基础文本清理，统一空白字符、处理空行等
- `sentence_handler.py`: 使用语言模型进行智能断句
- `filler_remover.py`: 识别和处理文本中的停顿词
- `line_breaker.py`: 基于语法结构进行智能断行
- `model_manager.py`: 统一管理语言模型的加载和使用
- `debug_output.py`: 处理调试信息的输出和保存

## 处理流程

### 1. 配置加载 (`main.py: load_config`)
- 读取 YAML 配置文件
- 处理文件路径（包括时间戳替换）
- 创建必要目录（输出目录、调试目录）

### 2. 文件处理 (`main.py: process_file`)

#### 2.1 初始化处理环境
- 创建调试输出器
  - 配置调试模式
  - 准备调试输出目录
- 加载语言模型
  - 通过 ModelManager 统一管理
  - 根据配置选择合适的模型

#### 2.2 文本处理流程
1. 基础文本清理 (TextCleaner)
   - 统一空白字符处理
   - 处理多余空行
   - 基本格式规范化
   - 不依赖语言模型

2. 智能断句 (SentenceHandler)
   - 使用 spaCy 语言模型分析
   - 识别自然句子边界
   - 保持语义完整性
   - 支持多语言处理

3. 停顿词处理 (FillerRemover)
   - 识别语言特定的停顿词
   - 处理语气词和填充词
   - 优化语言流畅度
   - 使用语言模型分析上下文

4. 智能断行 (LineBreaker)
   - 基于语法结构智能分析
   - 控制最大行宽
   - 在合适的语法位置断行
   - 保持文本可读性

#### 2.3 结果输出
- 保存处理后的文本
- 生成调试信息（如果启用）
- 清理临时文件（如果有）

## 调试支持

建议启用调试模式进行开发启用调试模式可以查看详细的处理过程：

1. 在配置文件中启用调试：
```yaml
debug:
  enabled: true
  temp_dir: temp
```

2. 查看调试输出：
   - 每个处理步骤的结果都会保存在 temp 目录
   - 可以查看详细的处理过程
   - 便于定位问题和优化效果