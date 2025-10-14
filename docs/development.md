# 开发指南（src 架构）

本文档面向当前基于 src 目录的项目结构，描述开发环境、项目结构、运行与调试、依赖管理以及常见开发任务。

## 项目结构
```
SubtitleFormatter/
├── src/
│   └── subtitleformatter/
│       ├── __init__.py
│       ├── __main__.py              # 入口：读取 config.yaml 运行
│       ├── config.py                # 配置加载与路径处理
│       ├── core/                    # 核心处理模块
│       │   ├── text_cleaner.py
│       │   ├── sentence_handler.py
│       │   ├── filler_remover.py
│       │   └── line_breaker.py
│       ├── models/                  # 模型管理
│       │   └── model_manager.py
│       ├── utils/                   # 工具/调试
│       │   └── debug_output.py
│       └── processors/              # 流程协调器
│           └── text_processor.py
├── scripts/                         # 独立脚本（Vim/Shell/Python 等）
├── config.yaml                      # 运行配置
├── pyproject.toml                   # 依赖与入口点（uv）
├── README.md
└── docs/
    ├── development.md               # 本文档
    └── Archive/                     # 旧文档
```

## 开发环境
- Python 3.11+
- 使用 uv 管理依赖与虚拟环境

初始化：
```bash
uv sync
```

运行（基于 config.yaml）：
```bash
uv run subtitleformatter
```

可选：直接以模块方式运行（同样读取 config.yaml）：
```bash
uv run python -m subtitleformatter
```

## 配置说明（config.yaml）
- `input_file`: 输入文件路径
- `output_file`: 输出文件路径，支持占位符 `{timestamp}`、`{input_file_basename}`
- `max_width`: 最大片宽
- `language`: `auto|en|zh`
- `model_size`: `sm|md|lg`
- `debug.enabled`: 是否启用调试输出
- `debug.temp_dir`: 调试输出目录

## 核心模块职责
- `core/text_cleaner.py`: 基础清理与规范化
- `core/sentence_handler.py`: 智能断句（spaCy）
- `core/filler_remover.py`: 停顿词与重复词处理
- `core/line_breaker.py`: 智能断行（语法断点）
- `models/model_manager.py`: 语言模型加载与下载
- `utils/debug_output.py`: 步骤结果与日志记录
- `processors/text_processor.py`: 串联完整流程

## 常见开发任务

### 1. 新增处理步骤
- 在 `core/` 中添加新模块
- 在 `processors/text_processor.py` 中插入调用
- 更新调试输出（可选）

### 2. 修改配置项
- 在 `config.yaml` 中定义
- 如需流程内可用：在 `config.py: load_config` 中做解析与目录准备

### 3. 模型相关改动
- 在 `models/model_manager.py` 添加/修改模型选择逻辑
- 注意首次运行需要下载相应 spaCy 模型

### 4. 调试
- 在 `config.yaml` 中启用 `debug.enabled: true`
- 输出位于 `debug.temp_dir`（默认 `data/debug`）

## 依赖与打包
- 依赖由 `pyproject.toml` 管理
- 可执行入口点（基于 config.yaml）：
```toml
[project.scripts]
subtitleformatter = "subtitleformatter.__main__:main"

[tool.uv]
package = true
```
- 安装/更新依赖：`uv sync`
- 运行：`uv run subtitleformatter`

## 测试建议
- 为核心模块编写单元测试（建议使用 pytest）
- 对 `processors/text_processor.py` 进行集成测试（可使用小型输入样例）

## 代码风格
- 保持命名清晰、函数短小
- 仅为非显而易见的逻辑添加精炼注释
- 避免过深嵌套，优先早返回

---
如需新增脚本的组织与集成策略，请参阅 `docs/scripts_management_strategy.md`（若存在）。
