# SentenceSplitterPlugin - 句子拆分插件

## 功能描述

SentenceSplitterPlugin 是 SubtitleFormatter 的句子拆分插件，将长句和复合句拆分为更短的句子。该插件基于规则和启发式方法，无需LLM即可实现智能拆分，通过分析句子结构、连接词和标点符号来做出拆分决策。

## 核心功能

### 1. 智能句子拆分
- 基于连接词和标点符号的优先级进行拆分
- 支持多种连接词类型（并列、从属、转折等）
- 智能识别最佳拆分点

### 2. 上下文感知
- 排除数字格式和简单并列的误拆分
- 识别固定短语，避免误拆分
- 处理从句结构，保持语义完整性

### 3. 多轮弱化策略
- 5轮逐步弱化策略，确保复杂长句能够被合理拆分
- 从严格规则到宽松规则，逐步放宽限制
- 兜底机制，确保长句最终能被拆分

### 4. 递归处理
- 支持对复合句进行多次拆分
- 可配置的递归深度和最小长度阈值
- 防止过度递归的保护机制

### 5. 格式保持
- 逗号和冒号及其空格保留在上一行
- 保持标点符号的完整性
- 智能处理从句引导词的位置

## 配置选项

```json
{
    "enabled": true,
    "min_recursive_length": 70,
    "max_depth": 8,
    "max_degradation_round": 5
}
```

### 配置说明

- `enabled`: 是否启用句子拆分功能
- `min_recursive_length`: 最小递归长度阈值，低于此长度不再递归拆分
- `max_depth`: 最大递归深度，防止过度递归
- `max_degradation_round`: 最大退化轮次
  - `1`: 严格模式，只执行第1轮
  - `3`: 中等模式，执行前3轮
  - `5`: 宽松模式，执行全部5轮（默认）

## 使用示例

### 输入输出示例

**输入**:
```
This is a very long sentence that contains multiple clauses and should be split into shorter, more manageable parts.
```

**输出**:
```
This is a very long sentence that contains multiple clauses,
and should be split into shorter, more manageable parts.
```

**输入**:
```
The project was successful, however, we need to improve the quality, and we should also consider the cost.
```

**输出**:
```
The project was successful,
however, we need to improve the quality,
and we should also consider the cost.
```

### 处理效果

1. **连接词拆分**: 在 "and", "however" 等连接词处拆分
2. **标点符号拆分**: 在逗号、分号等标点符号处拆分
3. **上下文保护**: 避免在数字格式中误拆分
4. **递归处理**: 对拆分后的部分继续拆分

## 技术实现

### 核心算法

#### 1. 拆分点识别
- **标点符号优先级**: 分号(5) > 冒号(4) > 逗号(3)
- **连接词优先级**: 高优先级(2) > 中优先级(1) > 低优先级(0)
- **复合优先级**: 逗号+连接词组合获得额外加分

#### 2. 多轮弱化策略
- **第1轮**: 正常策略，包含所有限制
- **第2轮**: 移除从句检测
- **第3轮**: 移除简单并列检测
- **第4轮**: 降低长度要求
- **第5轮**: 移除所有限制

#### 3. 上下文保护
- **数字格式**: 识别千位分隔符、货币格式
- **固定短语**: 保护 "so that", "as well as" 等短语
- **从句结构**: 识别从句引导词，保持语义完整

### 处理流程
1. **预处理**: 分析句子结构和长度
2. **拆分点查找**: 识别所有可能的拆分点
3. **有效性检查**: 验证拆分点的合理性
4. **最佳选择**: 选择优先级最高的拆分点
5. **递归处理**: 对拆分后的部分继续处理

### 性能特点
- 基于规则和启发式方法，无需外部模型
- 处理速度快，适合批量操作
- 内存占用低，支持大文件处理

## 连接词处理

### 支持的连接词类型
1. **并列连接词**: and, or, but, yet, so, for, nor
2. **从属连接词**: because, since, as, if, when, while, although, though
3. **转折连接词**: however, therefore, moreover, furthermore, nevertheless
4. **从句引导词**: which, that, who, whom, whose, where, when, why, how
5. **短语连接词**: such as, as well as, in order to, so that

### 优先级系统
- **高优先级**: however, therefore, moreover, furthermore, but, yet
- **中优先级**: because, since, although, though, that, which, who
- **低优先级**: and, or, so, for, nor, such as, as well as

## 集成方式

该插件作为 SubtitleFormatter 插件系统的一部分，通过以下方式集成：

1. **插件注册**: 自动在 `builtin` 命名空间下注册
2. **配置管理**: 通过统一的配置系统管理参数
3. **依赖注入**: 自动注入日志和配置服务
4. **生命周期**: 支持插件的加载、初始化和清理

## 扩展性

该插件设计为可扩展的，支持：

- 自定义连接词列表和优先级
- 添加新的标点符号处理规则
- 扩展上下文保护机制
- 集成其他句子拆分算法

## 使用场景

### 适用场景
1. **字幕处理**: 将长句拆分为适合字幕显示的短句
2. **文本预处理**: 为后续处理准备标准化的句子格式
3. **批量处理**: 处理大量文本文件的句子拆分
4. **格式转换**: 将复合句转换为简单句

### 处理顺序
建议在以下插件之后使用：
- TextCleaningPlugin: 基础文本清理
- PunctuationAdderPlugin: 标点符号恢复
- TextToSentencesPlugin: 文本转句子

## 注意事项

### 使用建议
1. **预处理**: 确保输入文本包含适当的标点符号
2. **配置调整**: 根据文本类型调整递归参数
3. **质量检查**: 对重要文档进行人工检查
4. **性能优化**: 对于大文件，考虑分批处理

### 限制说明
1. **语言支持**: 主要针对英文文本优化
2. **复杂句子**: 对于极复杂的长句，可能需要人工干预
3. **语义理解**: 基于规则，无法理解深层语义

## 故障排除

### 常见问题

1. **句子拆分不准确**
   - 检查连接词列表是否完整
   - 调整优先级设置
   - 检查上下文保护规则

2. **过度拆分**
   - 增加最小长度阈值
   - 减少递归深度
   - 启用更多上下文保护

3. **无法拆分长句**
   - 检查多轮弱化策略
   - 降低长度要求
   - 检查兜底机制

4. **性能问题**
   - 调整递归参数
   - 检查输入文本质量
   - 考虑分批处理
