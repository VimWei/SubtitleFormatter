# SRT重分段工具

## 功能描述
基于JSON时间戳重新分段SRT文件，实现断句的完全自由，提升文本匹配的兼容性。

## 使用方法

### 通过脚本管理器（推荐）
```bash
uv run python scripts_manager.py srt-resegment <json_file> <srt_file>
```

### 直接运行
```bash
uv run python scripts/srt_resegment/main.py <json_file> <srt_file>
```

## 参数说明
- `json_file`: Whisper输出的JSON时间戳文件
- `srt_file`: 要重新分段的SRT文件

## 输出
- 重新分段后的SRT文件

## 特性
- 无视标点符号
- 适应简单的文本增删改情形
- 实现断句的完全自由
- 提升文本匹配的兼容性

## 示例
```bash
# 基于JSON时间戳重新分段SRT
uv run python scripts_manager.py srt-resegment timestamps.json input.srt
```
