# 统一日志系统使用指南

## 概述

统一日志系统将终端输出和GUI日志面板连接起来，让您能够像使用`print`一样简单地添加日志，同时自动同步到GUI界面。

## 基本用法

### 1. 导入日志函数

```python
from subtitleformatter.utils.unified_logger import (
    log_info, log_warning, log_error, log_debug,
    log_step, log_stats, log_progress
)
```

### 2. 基本日志输出

```python
# 信息日志
log_info("这是一条信息")

# 警告日志
log_warning("这是一条警告")

# 错误日志
log_error("这是一条错误")

# 调试日志
log_debug("这是一条调试信息")
```

### 3. 步骤日志

```python
# 简单步骤
log_step("正在处理文件")

# 带消息的步骤
log_step("正在处理文件", "开始读取输入文件")
```

### 4. 统计日志

```python
stats = {
    "处理文件": 1,
    "清理操作": {
        "移除BOM": 1,
        "统一空格": 1
    },
    "断句结果": {
        "总句子数": 88,
        "平均长度": 371.2
    }
}
log_stats("处理统计", stats)
```

### 5. 进度日志

```python
# 进度日志
log_progress(50, 100, "处理中...")
```

## 高级用法

### 直接使用logger实例

```python
from subtitleformatter.utils.unified_logger import logger

# 设置GUI回调（通常在GUI初始化时设置）
logger.set_gui_callback(gui_log_callback)

# 启用/禁用终端输出
logger.enable_terminal(True)

# 启用/禁用GUI输出
logger.enable_gui(True)
```

## 在GUI中的使用

在GUI应用中，统一日志系统会自动将日志输出到日志面板。您只需要像使用`print`一样使用日志函数：

```python
# 在TextProcessor中
log_step("正在初始化处理环境")
log_info("已加载语言模型: en_core_web_md")
log_stats("文本清理统计", clean_stats)
```

## 输出格式

统一日志系统会输出带时间戳的格式化日志：

```
[10:33:34] INFO: 正在初始化处理环境...
[10:33:34] WARNING: 这是一条警告
[10:33:34] ERROR: 这是一条错误
```

## 优势

1. **简单易用**：像使用`print`一样简单
2. **统一输出**：同时输出到终端和GUI
3. **格式化**：自动添加时间戳和日志级别
4. **灵活配置**：可以独立控制终端和GUI输出
5. **线程安全**：支持多线程环境

## 注意事项

- 在GUI应用中，日志会自动显示在日志面板中
- 在命令行应用中，日志会输出到终端
- 日志级别包括：INFO、WARNING、ERROR、DEBUG
- 时间戳格式为：HH:MM:SS
