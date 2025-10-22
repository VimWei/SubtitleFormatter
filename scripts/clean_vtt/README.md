# VTT文件清理工具

## 功能描述
清理和格式化VTT字幕文件，去除重复内容，优化字幕结构。

## 使用方法

### 通过脚本管理器（推荐）
```bash
uv run python scripts_manager.py clean-vtt <input_file>
```

### 直接运行
```bash
uv run python scripts/clean_vtt/main.py <input_file>
```

## 参数说明
- `input_file`: 输入的VTT文件路径

## 输出
- 清理后的VTT文件保存为 `cleaned_subtitles.vtt`
- 在控制台显示清理后的DataFrame

## 依赖
- pandas >= 1.5.0

## 示例
```bash
# 清理VTT文件
uv run python scripts_manager.py clean-vtt input.vtt
```
