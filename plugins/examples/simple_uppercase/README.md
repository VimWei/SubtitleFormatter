# Simple Uppercase Plugin

## 描述

这是一个示例插件，演示了如何创建 SubtitleFormatter 插件。该插件将输入的文本转换为大写字母。

## 功能

- 将文本转换为大写字母
- 支持启用/禁用功能
- 支持保留空格选项

## 配置

```json
{
    "enabled": true,
    "preserve_spaces": true
}
```

### 配置选项

- `enabled` (bool): 是否启用插件，默认为 `true`
- `preserve_spaces` (bool): 是否保留空格，默认为 `true`

## 使用方法

1. 将插件放置在 `plugins/examples/simple_uppercase/` 目录
2. 在主程序配置中启用插件
3. 运行文本处理流程

## 示例

### 输入
```
hello world
```

### 输出
```
HELLO WORLD
```

## 开发

### 依赖

- Python 3.8+
- SubtitleFormatter

### 测试

```bash
python -m pytest tests/
```

## 许可证

MIT License