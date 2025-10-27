# 统一日志系统使用指南

## 概述

统一日志系统是SubtitleFormatter的核心日志管理组件，负责所有终端和GUI输出。它提供了简洁模式和详细模式，让您能够像使用`print`一样简单地添加日志，同时自动同步到GUI界面。

## 架构设计

### 职责分离
- **统一日志系统** (`UnifiedLogger`)：负责所有终端和GUI输出
- **调试输出系统** (`DebugOutput`)：专注于调试文件保存功能
- **清晰的职责分离**：避免重复输出，提高代码可维护性

## 基本用法

### 1. 导入日志函数

```python
from subtitleformatter.utils.unified_logger import (
    log_info, log_warning, log_error, log_debug,
    log_step, log_stats, log_progress,
    log_debug_info, log_debug_step
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

### 5. 调试模式日志

```python
# 调试信息 - 仅在调试模式下显示
log_debug_info("文本长度: 32669 字符")

# 调试步骤 - 仅在调试模式下显示
log_debug_step("详细处理步骤", "开始详细分析")
```

### 6. 进度日志

```python
# 进度日志
log_progress(50, 100, "处理中...")
```

## 调试模式控制

### 简洁模式 vs 详细模式

统一日志系统支持两种模式：

**简洁模式**（debug = false）：
- 只显示基本处理步骤
- 不显示详细统计信息
- 适合日常使用

**详细模式**（debug = true）：
- 显示所有处理步骤
- 显示详细统计信息（文本长度、句子数量、停顿词统计等）
- 适合调试和分析

### 模式控制

```python
from subtitleformatter.utils.unified_logger import logger

# 设置调试模式
logger.set_debug_mode(True)   # 启用详细模式
logger.set_debug_mode(False)  # 启用简洁模式
```

## 日志级别配置

### 概述

统一日志系统支持可配置的日志级别，允许您根据需要过滤日志输出。

### 配置方法

日志级别配置位于 `data/configs/config_latest.toml` 文件中的 `[logging]` 部分：

```toml
[logging]
# 日志级别: DEBUG, INFO, WARNING, ERROR
# DEBUG: 显示所有日志（包括调试信息）
# INFO: 显示普通信息和警告错误（推荐）
# WARNING: 只显示警告和错误
# ERROR: 只显示错误
level = "INFO"
```

### 日志级别说明

#### DEBUG（调试级别）
- **显示内容**: 所有日志（包括 DEBUG、INFO、WARNING、ERROR）
- **使用场景**: 开发调试、排查问题
- **特点**: 最详细的日志输出
- **示例**: 会显示 "Loaded plugin chain from..." 这样的 DEBUG 日志

```toml
[logging]
level = "DEBUG"
```

#### INFO（信息级别，推荐）
- **显示内容**: INFO、WARNING、ERROR
- **使用场景**: 日常使用（默认）
- **特点**: 显示重要的操作和信息
- **隐藏**: DEBUG 级别的详细信息

```toml
[logging]
level = "INFO"
```

#### WARNING（警告级别）
- **显示内容**: WARNING、ERROR
- **使用场景**: 只关注警告和错误
- **特点**: 更简洁的输出
- **隐藏**: DEBUG 和 INFO 信息

```toml
[logging]
level = "WARNING"
```

#### ERROR（错误级别）
- **显示内容**: 只显示 ERROR
- **使用场景**: 仅关注严重问题
- **特点**: 最简洁的输出
- **隐藏**: DEBUG、INFO、WARNING

```toml
[logging]
level = "ERROR"
```

### 使用示例

#### 查看详细日志（调试模式）

如果您想看到所有日志，包括内部的调试信息：

1. 打开 `data/configs/config_latest.toml`
2. 修改 `[logging]` 部分：

```toml
[logging]
level = "DEBUG"
```

3. 重启应用程序

现在您会看到所有日志，包括 DEBUG 级别的详细信息。

#### 简化日志输出

如果您只想看到错误信息：

1. 打开 `data/configs/config_latest.toml`
2. 修改 `[logging]` 部分：

```toml
[logging]
level = "ERROR"
```

3. 重启应用程序

现在只会显示错误信息，所有其他日志都会被过滤掉。

### 编程接口

#### 设置日志级别

```python
from subtitleformatter.utils.unified_logger import set_log_level

# 设置日志级别
set_log_level("DEBUG")   # 显示所有日志
set_log_level("INFO")    # 显示 INFO 及以上
set_log_level("WARNING") # 只显示警告和错误
set_log_level("ERROR")   # 只显示错误
```

#### 运行时修改日志级别

```python
from subtitleformatter.utils.unified_logger import logger

# 设置特定日志级别
logger.set_log_level("DEBUG")
```

### 日志级别优先级

```
DEBUG (0) < INFO (1) < WARNING (2) < ERROR (3)
```

日志会显示 **等于或高于** 设置的级别的所有日志。

例如：
- 设置 `level = "INFO"`：会显示 INFO、WARNING、ERROR
- 设置 `level = "WARNING"`：只显示 WARNING、ERROR
- 设置 `level = "ERROR"`：只显示 ERROR

### 常见问题

#### Q: 为什么我看不到 "Loaded plugin chain from..." 这样的日志？

A: 这些是 DEBUG 级别的日志。如果您设置的是 INFO 级别，这些日志会被过滤掉。将日志级别设置为 DEBUG 即可看到。

#### Q: 如何知道我当前的日志级别？

A: 日志级别会显示在每一条日志的前面，例如：
- `[18:37:28] DEBUG: ...`
- `[18:37:28] INFO: ...`

#### Q: 修改配置后需要重启吗？

A: 是的，需要重启应用程序才能生效。日志级别在应用程序启动时从配置文件读取。

#### Q: 可以在代码中动态修改日志级别吗？

A: 可以，使用 `logger.set_log_level("DEBUG")` 等方法可以在运行时修改日志级别。

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

# 设置调试模式
logger.set_debug_mode(True)
```

## 在GUI中的使用

在GUI应用中，统一日志系统会自动将日志输出到日志面板。您只需要像使用`print`一样使用日志函数：

```python
# 在TextProcessor中
log_step("正在初始化处理环境")
log_info("已加载语言模型: en_core_web_md")
log_stats("文本清理统计", clean_stats)

# 调试模式下的详细信息
log_debug_info("文本长度: 32669 字符")
log_debug_info("共拆分出 88 个句子")
```

### GUI集成

```python
# 在GUI主窗口中设置回调
from subtitleformatter.utils.unified_logger import logger

# 设置GUI日志回调
logger.set_gui_callback(self.log_panel.append_log)
```

## 输出格式

统一日志系统会输出带时间戳的格式化日志：

### 简洁模式输出
```
[11:06:25] INFO: 正在初始化处理环境...
[11:06:25] INFO: 正在加载语言模型...
[11:06:25] INFO: 已加载语言模型: en_core_web_md
[11:06:25] INFO: 开始处理文件...
[11:06:25] INFO: 已读入文件 Bee hunting.txt
[11:06:25] INFO: 正在进行文本清理...
[11:06:25] INFO: 正在进行智能断句...
[11:06:27] INFO: 正在处理停顿词...
[11:06:27] INFO: 正在进行智能断行...
[11:06:29] INFO: 正在保存结果到文件...
```

### 详细模式输出
```
[11:06:07] INFO: 正在初始化处理环境...
[11:06:07] INFO: 正在加载语言模型...
[11:06:07] INFO: 已加载语言模型: en_core_web_md
[11:06:07] INFO: 开始处理文件...
[11:06:07] INFO: 已读入文件 Bee hunting.txt
[11:06:07] INFO: 文本长度: 32669 字符
[11:06:07] INFO: 正在进行文本清理...
[11:06:07] INFO: 文本清理统计:
[11:06:07] INFO: ----------------------------------------
[11:06:07] INFO:   - special_chars: 1
[11:06:07] INFO:   - spaces: 1
[11:06:07] INFO: ----------------------------------------
[11:06:07] INFO: 正在进行智能断句...
[11:06:09] INFO: 共拆分出 88 个句子
[11:06:09] INFO: 最长句子: 3059 字符
[11:06:09] INFO: 最短句子: 3 字符
[11:06:09] INFO: 平均句长: 371.2 字符
... (更多详细统计信息)
```

## 优势

1. **简单易用**：像使用`print`一样简单
2. **统一输出**：同时输出到终端和GUI
3. **格式化**：自动添加时间戳和日志级别
4. **灵活配置**：可以独立控制终端和GUI输出
5. **线程安全**：支持多线程环境
6. **模式控制**：支持简洁模式和详细模式
7. **职责分离**：清晰的架构设计，避免重复输出

## 架构优势

### 职责分离
- **统一日志系统**：负责所有用户界面输出
- **调试输出系统**：专注于文件保存功能
- **避免重复**：消除了终端输出的重复问题

### 模式支持
- **简洁模式**：适合日常使用，输出简洁
- **详细模式**：适合调试分析，输出丰富
- **自动切换**：根据配置自动选择模式

## 总结

通过统一日志系统，您可以：
- ✅ 减少日志噪音，只关注重要信息
- ✅ 在调试时看到详细信息
- ✅ 在生产环境中隐藏敏感调试信息
- ✅ 根据需要灵活调整日志详细程度
- ✅ 像使用`print`一样简单易用
- ✅ 统一输出到终端和GUI
- ✅ 自动格式化和时间戳

## 注意事项

- 在GUI应用中，日志会自动显示在日志面板中
- 在命令行应用中，日志会输出到终端
- 日志级别包括：INFO、WARNING、ERROR、DEBUG
- 时间戳格式为：HH:MM:SS
- 调试模式通过配置文件控制：`[debug] enabled = true/false`
- 日志级别通过配置文件控制：`[logging] level = "INFO"`
- 修改配置后需要重启应用程序才能生效
- 调试文件仍然正常生成，不受统一日志系统影响
