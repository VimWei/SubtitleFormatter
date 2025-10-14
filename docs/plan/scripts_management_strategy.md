# SubtitleFormatter Scripts 管理策略

## 概述

本文档专门讨论 SubtitleFormatter 项目中 `scripts/` 目录的管理策略和未来发展规划。该目录用于存放所有与字幕处理相关的独立脚本工具。

## 当前脚本

### 现有脚本列表
- `Transcript_converter/` - Python 字幕转换工具
  - 功能：将非标准格式的字幕文件转换为标准 SRT 格式和纯文本格式
  - 使用：`python scripts/Transcript_converter/Transcript_converter.py input.transcript`
  
- `general_batch_replace.vim` - Vim 批量替换脚本
  - 功能：批量文本替换工具
  - 使用：`vim -S scripts/general_batch_replace.vim`
  
- `txt-resegment-by-rules.vim` - Vim 文本重分段脚本
  - 功能：按规则重新分段文本
  - 使用：`vim -S scripts/txt-resegment-by-rules.vim`

## 未来可扩展的脚本类型

### 字幕格式转换类
- **SRT 转换器** - 各种格式转 SRT
- **VTT 转换器** - WebVTT 格式支持
- **ASS/SSA 转换器** - 高级字幕格式支持
- **SUB 转换器** - 图形字幕格式支持
- **格式检测器** - 自动识别字幕格式

### 字幕时间轴处理类
- **时间偏移工具** - 调整字幕时间轴
- **同步工具** - 字幕与视频同步
- **分割工具** - 按时间或内容分割字幕
- **合并工具** - 合并多个字幕文件
- **时间轴修复** - 修复时间轴错误

### 字幕文本处理类
- **编码转换** - 字符编码转换
- **字符清理** - 清理特殊字符和格式
- **语言检测** - 自动检测字幕语言
- **翻译工具** - 字幕翻译辅助
- **拼写检查** - 字幕文本纠错

### 批量处理工具类
- **批量转换** - 批量处理多个文件
- **重命名工具** - 批量重命名字幕文件
- **整理工具** - 按规则整理文件结构
- **质量检查** - 批量检查字幕质量
- **统计工具** - 字幕文件统计分析

### 自动化脚本类
- **部署脚本** - 自动化部署工具
- **备份脚本** - 数据备份工具
- **监控脚本** - 文件变化监控
- **定时任务** - 定期执行的任务
- **集成脚本** - 与其他工具集成

## 未来整合策略

### 阶段 1: 独立脚本阶段（当前）

**目标**：保持所有脚本的独立性，便于快速开发和测试

**特点**：
- 所有工具保持独立，通过脚本直接调用
- 每个脚本有独立的文档和使用说明
- 便于快速开发和测试新功能
- 降低维护成本

**目录结构**：
```
scripts/
├── README.md                    # 脚本总览和使用说明
├── Transcript_converter/        # 字幕转换工具
├── general_batch_replace.vim    # Vim 批量替换
├── txt-resegment-by-rules.vim   # Vim 重分段
└── [future_scripts...]         # 未来添加的脚本
```

### 阶段 2: 分类整理阶段

**目标**：按功能分类组织脚本，提供更好的管理

**特点**：
- 按功能分类组织脚本（如 `converters/`, `processors/`, `utilities/`）
- 添加统一的脚本管理工具
- 提供脚本发现和帮助功能
- 建立脚本元数据系统

**目录结构**：
```
scripts/
├── README.md
├── converters/                  # 格式转换类
│   ├── transcript_converter/
│   ├── srt_converter.py
│   └── vtt_converter.py
├── processors/                  # 文本处理类
│   ├── general_batch_replace.vim
│   ├── txt-resegment-by-rules.vim
│   └── text_cleaner.py
├── utilities/                   # 工具类
│   ├── batch_rename.py
│   └── file_organizer.py
└── automation/                  # 自动化类
    ├── deploy.sh
    └── backup.py
```

**新增功能**：
- `scripts/manager.py` - 脚本管理工具
- `scripts/registry.json` - 脚本注册表
- `scripts/help.py` - 脚本帮助系统

### 阶段 3: 渐进集成阶段

**目标**：根据使用频率，将常用脚本集成到主程序

**特点**：
- 根据使用频率，将常用脚本集成到主程序
- 保持脚本的独立性，同时提供统一接口
- 支持 `subtitleformatter script <script_name>` 调用
- 提供脚本发现和帮助功能

**命令行接口**：
```bash
# 主功能
subtitleformatter process input.txt

# 脚本调用
subtitleformatter script transcript-converter input.transcript
subtitleformatter script batch-replace file.txt
subtitleformatter script list                    # 列出所有可用脚本
subtitleformatter script help <script_name>      # 显示脚本帮助
```

**实现方式**：
- 在 `src/subtitleformatter/` 中添加 `scripts/` 模块
- 实现脚本发现和调用机制
- 保持原有脚本的独立性

### 阶段 4: 插件化阶段

**目标**：实现插件系统，支持动态加载和第三方扩展

**特点**：
- 实现插件系统，支持动态加载脚本
- 提供脚本注册和发现机制
- 支持第三方脚本扩展
- 提供脚本开发框架和 API

**插件系统架构**：
```
src/subtitleformatter/
├── plugins/                     # 插件系统
│   ├── __init__.py
│   ├── base.py                 # 插件基类
│   ├── manager.py              # 插件管理器
│   └── registry.py             # 插件注册表
├── scripts/                    # 内置脚本
└── [other_modules...]
```

**插件开发**：
- 提供插件开发框架
- 定义标准插件接口
- 支持插件元数据配置
- 提供插件测试工具

## 脚本开发规范

### 脚本命名规范
- **Python 脚本**：使用下划线命名，如 `transcript_converter.py`
- **Vim 脚本**：使用连字符命名，如 `general-batch-replace.vim`
- **Shell 脚本**：使用下划线命名，如 `batch_deploy.sh`

### 脚本文档规范
每个脚本都应包含：
- 功能描述
- 使用方法
- 参数说明
- 示例
- 依赖要求

### 脚本元数据
```json
{
  "name": "transcript-converter",
  "version": "1.0.0",
  "description": "Convert transcript files to SRT format",
  "author": "VimWei",
  "category": "converter",
  "dependencies": [],
  "usage": "python transcript_converter.py <input_file>",
  "examples": [
    "python transcript_converter.py input.transcript"
  ]
}
```

## 使用方式

### 当前使用方式
```bash
# Python 脚本
python scripts/Transcript_converter/Transcript_converter.py input.transcript

# Vim 脚本
vim -S scripts/general_batch_replace.vim
```

### 未来统一调用方式
```bash
# 通过主程序调用
subtitleformatter script transcript-converter input.transcript
subtitleformatter script batch-replace file.txt

# 脚本管理
subtitleformatter script list
subtitleformatter script install <script_url>
subtitleformatter script uninstall <script_name>
```

## 实施计划

### 短期目标（1-3个月）
- [ ] 整理现有脚本，添加文档
- [ ] 建立脚本命名和文档规范
- [ ] 创建脚本总览文档

### 中期目标（3-6个月）
- [ ] 实现脚本分类整理
- [ ] 开发脚本管理工具
- [ ] 建立脚本注册表

### 长期目标（6-12个月）
- [ ] 实现脚本集成到主程序
- [ ] 开发插件系统
- [ ] 支持第三方脚本扩展

---

*本文档将随着项目发展持续更新*
