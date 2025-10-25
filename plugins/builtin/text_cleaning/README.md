# TextCleaningPlugin - 基础文本清理插件

## 功能描述

TextCleaningPlugin 是 SubtitleFormatter 的基础文本清理插件，用于统一空白字符、换行符、标点符号并清理多余空行。这是文本处理流程的第一步，为后续的智能处理提供标准化的输入。

## 核心功能

### 1. 空白字符规范化
- 统一各种空白字符为普通空格
- 处理不间断空格、全角空格、Tab等特殊字符
- 合并多个连续空格为单个空格

### 2. 标点符号规范化
- 全角标点符号转半角（：→:，；→;，。→.等）
- 中文引号转英文引号（""→""，''→''）
- 书名号转尖括号（《》→<>）
- 处理重复标点符号

### 3. 数字规范化
- 全角数字转半角（０→0，１→1等）

### 4. 换行符处理
- 统一换行符为 `\n`
- 清理多余空行
- 确保句子边界清晰

### 5. 中英文空格处理
- 在中英文之间自动添加空格
- 在标点符号后添加适当空格

## 配置选项

```json
{
    "enabled": true,
    "normalize_punctuation": true,
    "normalize_numbers": true,
    "normalize_whitespace": true,
    "clean_empty_lines": true,
    "add_spaces_around_punctuation": true,
    "remove_bom": true
}
```

### 配置说明

- `enabled`: 是否启用文本清理功能
- `normalize_punctuation`: 是否规范化标点符号（全角转半角）
- `normalize_numbers`: 是否规范化数字（全角转半角）
- `normalize_whitespace`: 是否规范化空白字符
- `clean_empty_lines`: 是否清理多余空行
- `add_spaces_around_punctuation`: 是否在标点符号后添加空格
- `remove_bom`: 是否移除UTF-8 BOM标记

## 使用示例

### 输入输出示例

**输入**:
```
Hello　world，this　is　a　test。
This is a test\n\n\n\nAnother paragraph
```

**输出**:
```
Hello world, this is a test.
This is a test

Another paragraph
```

### 处理效果

1. **标点规范化**: `，` → `,`，`。` → `.`
2. **空格规范化**: 全角空格 `　` → 普通空格 ` `
3. **空行清理**: 多个连续空行合并为单个空行
4. **句子分割**: 在句号后自动换行

## 技术实现

### 核心算法
- 使用正则表达式进行模式匹配和替换
- 分步骤处理不同类型的字符
- 保持处理顺序的逻辑性

### 性能特点
- 轻量级实现，无外部依赖
- 处理速度快，适合批量操作
- 内存占用低

## 集成方式

该插件作为 SubtitleFormatter 插件系统的一部分，通过以下方式集成：

1. **插件注册**: 自动在 `builtin` 命名空间下注册
2. **配置管理**: 通过统一的配置系统管理参数
3. **依赖注入**: 自动注入日志和配置服务
4. **生命周期**: 支持插件的加载、初始化和清理

## 扩展性

该插件设计为可扩展的，支持：

- 自定义标点符号映射
- 添加新的字符规范化规则
- 扩展空白字符处理逻辑
- 集成其他文本清理功能

## 注意事项

1. **处理顺序**: 该插件通常作为处理流程的第一步
2. **编码支持**: 支持 UTF-8 编码，处理 BOM 标记
3. **性能考虑**: 对于大文件，建议分批处理
4. **兼容性**: 与现有 TextCleaner 类完全兼容
