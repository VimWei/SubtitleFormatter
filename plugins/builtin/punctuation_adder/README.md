# PunctuationAdderPlugin - 自动标点恢复插件

## 功能描述

PunctuationAdderPlugin 是 SubtitleFormatter 的自动标点恢复插件，使用机器学习模型为英文文本自动添加标点符号。该插件基于 `deepmultilingualpunctuation` 模型，提供高精度的标点恢复功能。

## 核心功能

### 1. 智能标点恢复
- 使用 `deepmultilingualpunctuation` 模型自动添加标点符号
- 支持英文、德文、法文等多种语言（不支持中文）
- 基于 RNN 的轻量级模型，处理速度快

### 2. 句子分割
- 自动在句号、问号、感叹号后分割文本
- 将连续文本转换为每行一个句子的格式
- 支持复杂句子的智能识别

### 3. 首字母大写
- 自动将每个句子的首字母大写
- 保留其余字母的原始大小写
- 智能识别句子边界

### 4. 后处理优化
- 将破折号替换为逗号（更适合后续处理）
- 清理多余空格和换行符
- 标准化输出格式

## 配置选项

```json
{
    "enabled": true,
    "model_name": "oliverguhr/fullstop-punctuation-multilang-large",
    "capitalize_sentences": true,
    "split_sentences": true,
    "replace_dashes": true
}
```

### 配置说明

- `enabled`: 是否启用标点恢复功能
- `model_name`: 使用的标点恢复模型名称
- `capitalize_sentences`: 是否将句子首字母大写
- `split_sentences`: 是否将文本分割为句子
- `replace_dashes`: 是否将破折号替换为逗号

## 使用示例

### 输入输出示例

**输入**:
```
hello world this is a test without punctuation
```

**输出**:
```
Hello world, this is a test without punctuation.
```

**输入**:
```
this is a long sentence that needs punctuation and capitalization
```

**输出**:
```
This is a long sentence that needs punctuation and capitalization.
```

### 处理流程

1. **标点恢复**: 使用机器学习模型添加标点符号
2. **句子分割**: 在句号、问号、感叹号后分割
3. **首字母大写**: 每个句子首字母大写
4. **后处理**: 破折号转逗号，格式标准化

## 技术实现

### 模型选择
- **模型**: `deepmultilingualpunctuation`
- **类型**: RNN-based 轻量级模型
- **优势**: 处理速度快，资源需求低，适合批量操作
- **训练数据**: 基于政治演讲数据训练

### 模型管理
- **当前状态**: 使用直接模型加载，依赖Hugging Face默认缓存
- **未来计划**: 将通过ModelManager统一管理，支持本地模型存储和离线使用
- **相关文档**: 详见 `docs/plan/model_manager_migration.md`

### 处理算法
1. **模型调用**: 使用 `restore_punctuation()` 方法
2. **句子分割**: 正则表达式 `(?<=[.?!])\s+`
3. **首字母大写**: 查找第一个字母并大写
4. **后处理**: 字符串替换规则

### 性能特点
- **延迟加载**: 模型在首次使用时加载
- **内存管理**: 支持模型资源清理
- **错误处理**: 降级到原始文本
- **批量处理**: 支持列表输入

## 依赖要求

### 必需依赖
```bash
uv sync --group punctuation-adder
```

### 依赖包
- `deepmultilingualpunctuation`: 标点恢复模型

## 注意事项

### 模型限制
1. **语言支持**: 主要支持英文，对技术文本准确性可能较低
2. **训练数据**: 基于政治演讲数据，可能不适合所有文本类型
3. **大小写**: 主要专注于标点恢复，大小写纠正能力有限

### 使用建议
1. **预处理**: 建议先用 TextCleaningPlugin 清理文本
2. **后处理**: 建议人工检查重要文档
3. **批量处理**: 适合处理大量文本文件
4. **性能优化**: 对于大文件，考虑分批处理

## 集成方式

该插件作为 SubtitleFormatter 插件系统的一部分，通过以下方式集成：

1. **插件注册**: 自动在 `builtin` 命名空间下注册
2. **配置管理**: 通过统一的配置系统管理模型参数
3. **依赖注入**: 自动注入日志和配置服务
4. **生命周期**: 支持插件的加载、初始化和清理

## 扩展性

该插件设计为可扩展的，支持：

- 自定义模型配置
- 添加新的后处理规则
- 扩展语言支持
- 集成其他标点恢复模型

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查网络连接
   - 确认依赖包已安装
   - 检查模型存储目录权限

2. **处理速度慢**
   - 检查输入文本质量
   - 检查系统资源使用情况
   - 考虑分批处理大文件

3. **输出质量不佳**
   - 检查输入文本质量
   - 考虑调整后处理规则
   - 人工检查重要文档
