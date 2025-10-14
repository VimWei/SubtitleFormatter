# SubtitleFormatter 重构为 src 架构规划

## 项目概述

SubtitleFormatter 是一个智能字幕处理工具，使用 NLP 模型对文本进行清理、分割和格式化。当前项目采用传统的 Python 项目结构，需要重构为标准的 src 架构以提高可维护性和可扩展性。

## 当前项目结构分析

### 现有文件组织
```
SubtitleFormatter/
├── main.py                    # 主程序入口
├── modules/                   # 核心处理模块
│   ├── __init__.py
│   ├── text_cleaner.py       # 文本清理
│   ├── sentence_handler.py   # 智能断句
│   ├── filler_remover.py     # 停顿词处理
│   ├── line_breaker.py       # 智能断行
│   ├── model_manager.py      # 模型管理
│   └── debug_output.py       # 调试输出
├── tools/                     # 独立工具（保持独立）
│   ├── general_batch_replace.vim
│   ├── Transcript_converter/
│   └── txt-resegment-by-rules.vim
├── data/                      # 数据目录
├── config.yaml               # 配置文件
├── pyproject.toml
└── README.md
```

### 核心功能模块分析

1. **文本清理** (`text_cleaner.py`)
   - 统一空白字符、换行符、标点符号
   - 清理多余空行
   - 规范化中英文混排

2. **智能断句** (`sentence_handler.py`)
   - 基于 spaCy NLP 模型的句子分割
   - 处理缩写词和标点符号
   - 智能句子边界识别

3. **停顿词处理** (`filler_remover.py`)
   - 移除口语停顿词（um, uh, well 等）
   - 处理重复词
   - 支持中英文停顿词

4. **智能断行** (`line_breaker.py`)
   - 基于语法结构的智能换行
   - 支持最大行宽限制
   - 语法边界识别

5. **模型管理** (`model_manager.py`)
   - spaCy 语言模型加载和管理
   - 支持多种语言和模型大小
   - 自动模型下载

6. **调试输出** (`debug_output.py`)
   - 处理步骤可视化
   - 统计信息收集
   - 调试文件生成

## 目标 src 架构设计

### 脚本处理策略

当前 `tools/` 目录包含各种独立脚本工具，重构时将：
1. **重命名** → `tools/` 重命名为 `scripts/`
2. **保持独立** → 所有脚本暂时保持独立，便于开发
3. **未来整合** → 详细的整合策略请参考 `scripts_management_strategy.md`

### 新的目录结构
```
SubtitleFormatter/
├── src/
│   └── subtitleformatter/
│       ├── __init__.py           # 包初始化
│       ├── __main__.py           # 主入口点 (python -m subtitleformatter)
│       ├── cli.py                # 命令行接口
│       ├── config.py             # 配置管理
│       ├── core/                 # 核心处理模块
│       │   ├── __init__.py
│       │   ├── text_cleaner.py
│       │   ├── sentence_handler.py
│       │   ├── filler_remover.py
│       │   └── line_breaker.py
│       ├── models/               # 模型管理
│       │   ├── __init__.py
│       │   └── model_manager.py
│       ├── utils/                # 工具函数
│       │   ├── __init__.py
│       │   └── debug_output.py
│       └── processors/           # 处理器协调器
│           ├── __init__.py
│           └── text_processor.py
├── scripts/                      # 独立脚本（Vim、Shell 等）
├── data/                         # 数据目录
├── config.yaml                   # 配置文件
├── pyproject.toml
└── README.md
```

### 架构设计原则

1. **清晰的职责分离**
   - `core/` - 核心文本处理逻辑，每个模块专注单一职责
   - `models/` - 模型管理相关功能
   - `utils/` - 通用工具函数和调试功能
   - `processors/` - 处理流程协调和编排

2. **保持向后兼容**
   - 保持 `tools/` 目录独立，不纳入 src 结构
   - 保持配置文件和数据目录位置
   - 保持现有的 API 接口

3. **易于扩展和维护**
   - 模块化设计便于添加新功能
   - 清晰的接口便于单元测试
   - 标准化的包结构便于分发

## 重构实施计划

### 阶段 1: 目录结构创建
- [ ] 创建 `src/subtitleformatter/` 主包目录
- [ ] 创建子包目录：`core/`, `models/`, `utils/`, `processors/`
- [ ] 创建所有必要的 `__init__.py` 文件

### 阶段 2: 核心模块迁移
- [ ] 迁移 `modules/text_cleaner.py` → `src/subtitleformatter/core/text_cleaner.py`
- [ ] 迁移 `modules/sentence_handler.py` → `src/subtitleformatter/core/sentence_handler.py`
- [ ] 迁移 `modules/filler_remover.py` → `src/subtitleformatter/core/filler_remover.py`
- [ ] 迁移 `modules/line_breaker.py` → `src/subtitleformatter/core/line_breaker.py`

### 阶段 3: 支持模块迁移
- [ ] 迁移 `modules/model_manager.py` → `src/subtitleformatter/models/model_manager.py`
- [ ] 迁移 `modules/debug_output.py` → `src/subtitleformatter/utils/debug_output.py`

### 阶段 4: 主程序重构
- [ ] 创建 `src/subtitleformatter/__main__.py` 作为主入口点
- [ ] 创建 `src/subtitleformatter/cli.py` 命令行接口
- [ ] 创建 `src/subtitleformatter/config.py` 配置管理
- [ ] 创建 `src/subtitleformatter/processors/text_processor.py` 处理协调器

### 阶段 4.5: 脚本目录整理
- [ ] 将 `tools/` 重命名为 `scripts/`
- [ ] 参考 `scripts_management_strategy.md` 进行脚本整理

### 阶段 5: 导入语句更新
- [ ] 更新所有模块的导入语句
- [ ] 确保相对导入正确
- [ ] 更新包级别的 `__init__.py` 文件

### 阶段 6: 项目配置更新
- [ ] 更新 `pyproject.toml` 支持新的包结构
- [ ] 添加命令行入口点
- [ ] 更新依赖配置

### 阶段 7: 测试和验证
- [ ] 测试新的包结构是否正常工作
- [ ] 验证所有功能保持原有行为
- [ ] 更新文档和示例

## 详细实施步骤

### 1. 创建新的包结构

```bash
# 创建主包目录
mkdir -p src/subtitleformatter

# 创建子包目录
mkdir -p src/subtitleformatter/{core,models,utils,processors}

# 创建 __init__.py 文件
touch src/subtitleformatter/__init__.py
touch src/subtitleformatter/core/__init__.py
touch src/subtitleformatter/models/__init__.py
touch src/subtitleformatter/utils/__init__.py
touch src/subtitleformatter/processors/__init__.py
```

### 2. 模块迁移策略

#### 核心模块迁移
- 保持原有类名和方法签名
- 更新导入路径
- 确保功能完全一致

#### 配置管理重构
- 将 `main.py` 中的配置加载逻辑提取到 `config.py`
- 支持环境变量和配置文件
- 提供配置验证功能

#### 主程序重构
- `__main__.py`: 提供 `python -m subtitleformatter` 入口
- `cli.py`: 提供命令行参数解析
- `text_processor.py`: 协调整个处理流程

### 3. 导入语句更新

#### 包内导入
```python
# 从 core 模块导入
from .core.text_cleaner import TextCleaner
from .core.sentence_handler import SentenceHandler

# 从 models 模块导入
from .models.model_manager import ModelManager

# 从 utils 模块导入
from .utils.debug_output import DebugOutput
```

#### 外部导入
```python
# 在 __main__.py 中
from subtitleformatter.cli import main
from subtitleformatter.config import load_config
```

### 4. 命令行接口设计

重构后的命令行接口专注于核心功能：

```bash
# 主功能 - 智能文本处理
subtitleformatter process input.txt
subtitleformatter process input.txt --output output.txt --max-width 80

# 帮助信息
subtitleformatter --help
subtitleformatter process --help

# 独立脚本使用（保持现有方式）
python scripts/Transcript_converter/Transcript_converter.py input.transcript
vim -S scripts/general_batch_replace.vim
```

### 5. pyproject.toml 更新

```toml
[project]
name = "subtitleformatter"
version = "0.1.0"
description = "An intelligent subtitle processing tool"
# ... 其他配置

[project.scripts]
subtitleformatter = "subtitleformatter.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

## 相关文档

- **脚本管理策略** - 详见 `scripts_management_strategy.md`
- **开发指南** - 详见 `Development_Guide.md`
- **使用说明** - 详见 `usage.md`

---

*本文档将随着重构进展持续更新*
