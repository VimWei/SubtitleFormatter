# DebugOutput 集成计划

## 📋 概述

确保现有的优秀调试输出系统 `DebugOutput` 能够完美适配新的内核流程，保持详细的处理步骤记录和中间结果文件保存功能。

## 🔍 现状分析

### DebugOutput 优势
- ✅ 处理步骤的中间结果文件保存
- ✅ 生成详细的处理日志文件
- ✅ 自动步骤序号管理
- ✅ 统计信息收集和展示
- ✅ 时间戳和文件命名管理

### 当前支持的步骤
- 读入文件
- 文本清理
- 智能断句
- 停顿词处理
- 智能断行

## 🎯 集成目标

### 适配新流程
- 🔄 支持新的处理步骤：标点恢复、句子分割、句子拆分
- 📁 保持中间结果文件保存功能
- 🎯 保持统计信息收集和展示
- 📊 保持处理日志生成功能

### 保持现有功能
- ✅ 自动步骤序号管理
- ✅ 时间戳和文件命名
- ✅ 统计信息格式化
- ✅ 调试模式控制

## 📝 详细实施计划

### 阶段一：步骤映射更新 (1天)

#### 1.1 新步骤名称映射
```python
# 更新步骤名称映射
new_step_mappings = {
    "标点恢复": "punctuation_adder",
    "句子分割": "text_to_sentences", 
    "句子拆分": "sentence_splitter"
}
```

#### 1.2 统计信息适配
- 适配 `punctuation_adder` 的统计信息
- 适配 `text_to_sentences` 的统计信息
- 适配 `sentence_splitter` 的统计信息

### 阶段二：功能实现 (1天)

#### 2.1 新步骤处理逻辑
```python
def show_step(self, step_name, content, stats=None):
    # 添加新步骤的处理逻辑
    if step_name == "标点恢复":
        # 处理标点恢复的统计信息
        pass
    elif step_name == "句子分割":
        # 处理句子分割的统计信息
        pass
    elif step_name == "句子拆分":
        # 处理句子拆分的统计信息
        pass
```

#### 2.2 文件保存逻辑
- 保持现有的文件保存机制
- 适配新步骤的输出格式
- 保持文件命名规则

## 🔧 技术实现要点

### 1. 新步骤统计信息
```python
# 标点恢复统计
elif step_name == "标点恢复":
    if stats:
        log_lines.append("\n标点恢复统计:")
        log_lines.append("-" * 40)
        log_lines.append(f"处理文本长度: {stats.get('text_length', 0)} 字符")
        log_lines.append(f"恢复标点数量: {stats.get('punctuation_count', 0)} 个")
        log_lines.append(f"处理时间: {stats.get('processing_time', 0):.2f} 秒")
        log_lines.append("-" * 40)

# 句子分割统计
elif step_name == "句子分割":
    if isinstance(content, list):
        log_lines.append(f"\n句子分割统计:")
        log_lines.append("-" * 40)
        log_lines.append(f"共分割出 {len(content)} 个句子")
        log_lines.append(f"最长句子: {len(max(content, key=len))} 字符")
        log_lines.append(f"最短句子: {len(min(content, key=len))} 字符")
        log_lines.append(f"平均句长: {sum(len(s) for s in content) / len(content):.1f} 字符")
        log_lines.append("-" * 40)

# 句子拆分统计
elif step_name == "句子拆分":
    if stats:
        log_lines.append("\n句子拆分统计:")
        log_lines.append("-" * 40)
        log_lines.append(f"原始句子数: {stats.get('original_sentences', 0)}")
        log_lines.append(f"拆分后句子数: {stats.get('split_sentences', 0)}")
        log_lines.append(f"拆分比例: {stats.get('split_ratio', 0):.1f}%")
        log_lines.append(f"最长拆分深度: {stats.get('max_depth', 0)}")
        log_lines.append("-" * 40)
```

### 2. 文件保存适配
- 保持现有的文件命名规则
- 适配新步骤的输出格式
- 保持文件编码和格式

### 3. 统计信息收集
- 从新组件收集统计信息
- 保持统计信息的完整性
- 确保统计信息的准确性

## 📚 参考文档

- `src/subtitleformatter/utils/debug_output.py` - 调试输出系统
- `src/subtitleformatter/utils/unified_logger.py` - 统一日志系统

## ⚠️ 注意事项

### 兼容性
- 确保现有调试功能不受影响
- 保持文件格式的一致性
- 确保统计信息的准确性

### 性能
- 避免文件I/O影响处理性能
- 合理控制调试信息的详细程度
- 优化文件保存操作

## 🚀 实施时间表

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 1 | 步骤映射更新 | 1天 | 高 |
| 2 | 功能实现 | 1天 | 高 |
| **总计** | | **2天** | **高** |

## 📋 验收标准

### 功能验收
- [ ] 新步骤的统计信息正确显示
- [ ] 中间结果文件正确保存
- [ ] 处理日志正确生成
- [ ] 文件命名规则正确

### 兼容性验收
- [ ] 现有调试功能正常工作
- [ ] 文件格式保持一致
- [ ] 统计信息准确完整

---

**注意**: 此计划为高优先级事项，需要在主要重构过程中同步进行。
