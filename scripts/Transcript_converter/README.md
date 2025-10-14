# 字幕格式转换器

这个Python程序可以将非标准格式的字幕文件转换为标准的SRT格式和纯文本格式。

## 功能特点

- 自动识别时间戳格式（如 `0:02`, `1:30`）
- 智能计算字幕的结束时间
- 生成标准SRT格式文件
- 生成纯文本文件（去除时间轴信息）
- 支持中文和英文内容

## 使用方法

### 基本用法
```bash
python Transcript_converter.py "输入文件.transcript"
```

### 示例
```bash
python Transcript_converter.py "input.transcript"
```

## 输入格式

程序支持以下格式的输入文件：
```
0:02
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw
0:05
as an important and rapidly growing trend in how people were building on-base applications,
0:10
what I did not realize was that a bunch of marketers would get hold of this term
...
```

## 输出格式

程序会生成两种格式的文件：

### SRT格式文件
```
1
00:00:02,000 --> 00:00:05,000
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw

2
00:00:05,000 --> 00:00:10,000
as an important and rapidly growing trend in how people were building on-base applications,
...
```

### 纯文本格式文件
```
Welcome to this course on Agentic AI. When I coined the term agentic to describe what I saw
as an important and rapidly growing trend in how people were building on-base applications,
...
```

## 输出文件

程序会根据输入文件类型自动确定输出文件名：
- 输入：`input.transcript` → 输出：`input.srt` 和 `input.txt`
- 输入：`input`（无扩展名）→ 输出：`input.srt` 和 `input.txt`

### 输出文件说明
- **SRT文件**：包含完整的时间轴信息和字幕文本，适用于视频播放器
- **TXT文件**：仅包含纯文本内容，去除时间轴信息，自动删除空行

## 系统要求

- Python 3.6+
- 无需额外依赖包

## 注意事项

- 程序会自动计算每个字幕的结束时间
- 如果无法确定下一个时间戳，会假设字幕持续3秒
- 支持的时间戳格式：`m:ss` 或 `mm:ss`
