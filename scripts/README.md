# SubtitleFormatter Scripts

> **开发者文档** - 如何开发和管理 SubtitleFormatter 的脚本工具

本目录包含 SubtitleFormatter 项目的所有独立脚本工具。这些脚本可以独立运行，也可以通过脚本管理器统一调用。

## 📋 脚本列表

### 📁 diff - 文本差异检测工具
- **功能**: 比较两个文本文件，识别除了格式化差异之外的词汇差异
- **特点**: 智能文本标准化、精确序列对齐、多种输出格式
- **用法**: `scripts_manager.py diff <old_file> <new_file> [options]`
- **输出**: 控制台、JSON、HTML、CSV格式报告
- **依赖**: colorama, rich, click

### 📁 transcript_converter - 字幕格式转换工具
- **功能**: 将非标准格式的字幕文件转换为标准SRT格式和纯文本格式
- **特点**: 支持多种输入格式、自动格式检测
- **用法**: `scripts_manager.py transcript-converter <input_file>`
- **输出**: SRT格式字幕文件和纯文本文件
- **依赖**: 无特殊依赖

## 🔧 脚本分类

### 文本处理类 (text_processing)
- `diff` - 文本差异检测

### 转换类 (converter)
- `transcript-converter` - 字幕格式转换

## 开发新脚本

### 脚本结构
```
scripts/
├── your_script/                    # 脚本目录
│   ├── main.py                    # 主程序文件
│   ├── README.md                  # 脚本说明（可选）
│   └── tests/                     # 测试文件（可选）
```

### 脚本规范
1. **命名规范**: 使用小写字母和下划线
2. **入口文件**: 主程序文件应该可以直接运行
3. **帮助信息**: 支持 `--help` 参数
4. **错误处理**: 适当的错误处理和退出码
5. **文档**: 提供基本的使用说明

### 注册新脚本
在 `scripts_manager.py` 的 `_load_registry()` 方法中添加新脚本：

```python
"your-script": {
    "path": "your_script/main.py",
    "description": "脚本功能描述",
    "usage": "scripts_manager.py your-script <args>",
    "examples": [
        "scripts_manager.py your-script example.txt"
    ],
    "category": "your_category"
}
```

## 依赖管理

### 脚本依赖管理
每个脚本都有独立的依赖组，在 `pyproject.toml` 的 `[dependency-groups]` 中定义：

```toml
[dependency-groups]
# 脚本独立依赖组
diff = [
    "colorama>=0.4.4",
    "rich>=13.0.0", 
    "click>=8.0.0",
]
clean-vtt = [
    "pandas>=1.5.0",
]
release = [
    "tomli-w>=1.0.0",
]
# 无依赖脚本不需要定义group
```

安装特定脚本依赖：
```bash
# 安装diff脚本依赖
uv pip install --group diff

# 安装clean-vtt脚本依赖
uv pip install --group clean-vtt

# 安装release脚本依赖
uv pip install --group release
```

### 安装依赖
```bash
# 安装所有脚本依赖组
uv sync --group diff --group clean-vtt --group release

# 或安装特定脚本依赖
uv pip install --group diff
```

# 安装特定脚本依赖
python scripts_manager.py install diff
```

## 📚 用户文档

### 使用指南
如果你需要了解如何使用这些脚本，请参考：
- [docs/scripts_guide.md](../docs/scripts_guide.md) - 脚本使用指南
- [项目主文档](../README.md) - 核心程序使用说明

## 🔧 开发工具

### 调试模式
```bash
# 显示详细运行信息
python scripts_manager.py run diff Old.txt New.txt --verbose
```

### 测试脚本
```bash
# 测试特定脚本
uv run python scripts/diff/text_diff.py --help

# 运行脚本测试
uv run python -m pytest scripts/diff/tests/
```

---

*最后更新: 2025年10月*
