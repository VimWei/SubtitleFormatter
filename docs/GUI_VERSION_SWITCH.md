# GUI 版本切换说明

## 概述

SubtitleFormatter 现在默认启动新版 GUI (V2)，同时保留了旧版 GUI (V1) 作为参考。

## 启动方式

### 默认启动（新版 V2 GUI）
```bash
uv run subtitleformatter
```
或者使用 VBScript：
```bash
SubtitleFormatter.vbs
```

### 启动旧版 GUI（V1 Legacy）
```bash
uv run subtitleformatter --legacy
```

### CLI 模式
```bash
uv run subtitleformatter --cli
```

### 备用方式（直接运行脚本）

#### 旧版 GUI（V1 Legacy）- 备用方式
```bash
uv run python test_gui_v1.py
```

#### 新版 GUI（V2）- 备用方式
```bash
uv run python test_gui_v2.py
```

## 版本差异

### V1 (旧版)
- 简单的标签页布局
- 传统配置管理
- 所有功能集中在一个窗口
- 较小的窗口尺寸 (800x520)

### V2 (新版)
- 插件化架构
- 最大化窗口布局
- 插件管理和可视化
- 分离的配置管理面板
- 更大的窗口尺寸 (最小 1200x800)

## 文件结构

```
SubtitleFormatter/
├── src/subtitleformatter/
│   ├── __main__.py              # 主入口（默认使用 V2）
│   └── gui/
│       ├── main_window.py       # V1 GUI (旧版)
│       └── main_window_v2.py    # V2 GUI (新版)
├── test_gui_v1.py               # V1 GUI 启动脚本
├── test_gui_v2.py               # V2 GUI 启动脚本
└── SubtitleFormatter.vbs        # Windows VBScript 启动器
```

## 技术细节

### 参数说明

新增了 `--legacy` 参数来选择 GUI 版本：

- `uv run subtitleformatter` - 默认启动 V2 GUI（新版）
- `uv run subtitleformatter --legacy` - 启动 V1 GUI（旧版）
- `uv run subtitleformatter --cli` - 启动 CLI 模式
- `uv run subtitleformatter --cli --config <path>` - CLI 模式 + 自定义配置

### 入口点实现

在 `src/subtitleformatter/__main__.py` 中，`run_gui()` 函数现在支持版本选择：

```python
def run_gui(use_legacy: bool = False):
    """Run SubtitleFormatter in GUI mode."""
    if use_legacy:
        from subtitleformatter.gui.main_window import run_gui as run_gui_legacy
        run_gui_legacy()
    else:
        from subtitleformatter.gui.main_window_v2 import run_gui_v2
        run_gui_v2()
```

可以通过 `--legacy` 参数来切换 GUI 版本。

### 配置兼容性

- V1 和 V2 使用相同的配置文件格式
- V2 使用新的配置协调器 (`ConfigCoordinator`)
- V1 使用传统的配置管理器 (`ConfigManager`)

## 迁移建议

如果需要在两个版本之间切换测试：

1. **使用 V2**: 直接运行 `uv run subtitleformatter`
2. **使用 V1**: 运行 `uv run python test_gui_v1.py`

## 注意事项

- 旧版 GUI 保留作为参考，不建议删除
- 新版 GUI 仍在开发中，可能存在未完成的功能
- 配置文件在两个版本之间是兼容的
- 建议在使用前备份配置文件

## 更新记录

- 2024-XX-XX: 切换到 V2 GUI 作为默认版本

