# Transcript Converter Plugin

字幕格式转换插件，将非标准格式的字幕文件（`.transcript`）转换为标准的 SRT 和 TXT 格式。

## 功能特点

- ✅ 自动识别时间戳格式（如 `0:02`, `1:30`）
- ✅ 智能计算字幕的结束时间
- ✅ 生成标准 SRT 格式文件（适用于视频播放器）
- ✅ 生成纯文本 TXT 文件（去除时间轴信息）
- ✅ 支持中英文内容
- ✅ 可配置输出格式（SRT/TXT 可独立控制）

## 输入格式

插件支持的输入文件格式示例：

```
0:02
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw
0:05
as an important and rapidly growing trend in how people were building on-base applications,
0:10
what I did not realize was that a bunch of marketers would get hold of this term
1:30
这是一段中文示例内容。
```

### 时间戳格式

- 格式：`m:ss`（分钟:秒，秒数必须是两位数）
- 示例：`0:02`、`1:30`、`10:45`

### 文件结构

- 每段字幕以时间戳开头
- 时间戳后跟随一行或多行文本
- 空行会被忽略

## 输出格式

### SRT 格式文件

生成标准的 SRT 字幕文件，包含完整的时间轴信息：

```
1
00:00:02,000 --> 00:00:05,000
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw

2
00:00:05,000 --> 00:00:10,000
as an important and rapidly growing trend in how people were building on-base applications,

3
00:01:30,000 --> 00:01:33,000
这是一段中文示例内容。
```

### TXT 格式文件

生成纯文本文件，去除时间轴信息，仅保留字幕文本：

```
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw
as an important and rapidly growing trend in how people were building on-base applications,
这是一段中文示例内容。
```

## 配置选项

插件支持以下配置选项（在 `plugin.json` 或 GUI 插件配置面板中设置）：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | `boolean` | `true` | 是否启用插件 |
| `emit_srt` | `boolean` | `true` | 是否输出 SRT 文件 |
| `emit_txt` | `boolean` | `true` | 是否输出 TXT 文件 |

### 配置示例

```json
{
  "enabled": true,
  "emit_srt": true,
  "emit_txt": false
}
```

此配置将：
- 启用插件
- 生成 SRT 文件
- 不生成 TXT 文件

## 使用方法

### 通过 GUI 使用

1. 在 **Basic** 标签页中：
   - 设置 **Input mode** 为 `File`、`Files` 或 `Directory`
   - 选择或输入 `.transcript` 文件路径
   - 设置 **Output mode** 为 `Directory`
   - 选择输出目录

2. 在插件链中添加 `builtin/transcript_converter` 插件

3. 在插件配置面板中：
   - 启用插件（`enabled: true`）
   - 选择输出格式（`emit_srt`、`emit_txt`）

4. 点击 **Run** 执行转换

### 输入/输出示例

**输入文件**：`data/input/sample.transcript`

**输出文件**（在 `data/output/` 目录下）：
- `sample.srt` - SRT 格式字幕文件
- `sample.txt` - 纯文本文件

## 工作原理

### 时间戳转换

- 输入格式：`m:ss`（如 `0:02`、`1:30`）
- 转换规则：
  - 解析分钟和秒数
  - 计算总秒数
  - 转换为标准格式：`00:00:00,000`

### 结束时间计算

- **有下一段字幕**：使用下一段字幕的开始时间作为当前段的结束时间
- **最后一段字幕**：使用开始时间 + 3 秒作为结束时间

### 时间轴生成

- 每段字幕自动分配序号（从 1 开始）
- 时间格式：`HH:MM:SS,mmm --> HH:MM:SS,mmm`
- 字幕文本自动合并多行为一行（用空格连接）

## 技术细节

### 插件接口

```python
class TranscriptConverterPlugin(TextProcessorPlugin):
    def get_input_type(self) -> type:
        return str  # 接收文件路径字符串
    
    def get_output_type(self) -> type:
        return list  # 返回文件路径列表
    
    def process(self, input_data: str) -> list:
        # 返回生成的文件路径列表
        return ["path/to/output.srt", "path/to/output.txt"]
```

### 输出目录

- 输出目录由平台层通过 `config["_output_dir"]` 注入
- 如果未指定输出目录，使用输入文件所在目录

### 时间戳处理

- 插件返回基础文件名（不含时间戳）
- 时间戳前缀由平台层统一处理（如果启用了"Add timestamp"选项）

## 注意事项

1. **文件编码**：插件使用 UTF-8 编码读写文件
2. **时间戳格式**：仅支持 `m:ss` 格式，秒数必须是两位数
3. **空行处理**：输入文件中的空行会被自动忽略
4. **文件覆盖**：输出文件如果已存在会被覆盖
5. **多文件输出**：插件返回文件路径列表，支持一次生成多个文件

## 错误处理

- **无效时间戳**：无法解析的时间戳会导致该段字幕被跳过
- **文件不存在**：如果输入文件不存在，插件会返回空列表
- **权限错误**：如果无法写入输出目录，会抛出异常

## 版本信息

- **版本**：1.0.0
- **作者**：SubtitleFormatter Team
- **分类**：format_conversion
- **标签**：transcript, srt, txt

## 相关文档

- [SubtitleFormatter 插件开发指南](../../../docs/plugins/README.md)
- [插件架构说明](../../../docs/architecture/plugins.md)

