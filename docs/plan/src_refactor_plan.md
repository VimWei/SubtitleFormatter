# SubtitleFormatter 主程序重构计划

## 📋 概述

基于对现有代码的分析，我们发现 `scripts/` 目录下的三个关键脚本（`punctuation_adder`、`text_to_sentences`、`sentence_splitter`）在功能上已经完全超越了当前 `src/` 主程序的相关组件。本计划旨在用这些成熟的脚本完全替换主程序的关键处理步骤。

## 🔍 现状分析

### 当前 src/ 主程序架构

当前主程序包含四个核心处理步骤：

1. **text_cleaning** (`TextCleaner`)
   - 统一空白字符、换行符、标点符号
   - 清理多余空行
   - 规范化中英文标点符号
   - **状态**: 功能完善，保留

2. **sentence_splitting** (`SentenceHandler`)
   - 基于 spaCy 的智能断句
   - 处理缩写词和标点符号
   - 修复基本标点和空格问题
   - **状态**: 将被替换

3. **filler_handling** (`FillerRemover`)
   - 移除停顿词和重复词
   - 基于上下文的停顿词识别
   - **状态**: 将被删除

4. **line_breaking** (`LineBreaker`)
   - 基于语法结构的智能断行
   - 支持最大行宽限制
   - **状态**: 将被替换

### Scripts 功能分析

#### 1. punctuation_adder
- **功能**: 使用 `deepmultilingualpunctuation` 模型自动添加标点符号
- **优势**: 
  - 基于机器学习，准确性高
  - 支持句子分割和首字母大写
  - 处理速度快，适合批量操作
  - 轻量级 RNN 模型，资源需求低
- **输出**: 每行一个句子的格式

#### 2. text_to_sentences
- **功能**: 将连续文本按句分割，每句一行
- **优势**:
  - 简单高效的正则表达式分割
  - 处理缩写词识别
  - 无外部依赖
- **输出**: 每行一个句子的格式

#### 3. sentence_splitter
- **功能**: 将长句和复合句拆分为更短的句子
- **优势**:
  - 基于规则和启发式方法，无需 LLM
  - 智能识别连接词和语法断点
  - 支持递归处理复杂长句
  - 上下文感知，避免误拆分
- **输出**: 每行一个拆分后的句子

## 🎯 重构目标

### 新的处理流程

```
原始文本 → text_cleaning → punctuation_adder → text_to_sentences → sentence_splitter → 最终输出
```

### 组件替换映射

| 当前组件 | 新组件 | 操作类型 | 原因 |
|---------|--------|----------|------|
| `TextCleaner` | `TextCleaner` | **保留** | 功能完善，无需修改 |
| `SentenceHandler` | `punctuation_adder` | **删除+新增** | 机器学习模型更准确 |
| - | `text_to_sentences` | **新增** | 标准化句子格式 |
| `FillerRemover` | - | **删除** | 功能被其他组件覆盖 |
| `LineBreaker` | `sentence_splitter` | **删除+新增** | 更智能的句子拆分 |

## 🗑️ 删除清单

### 需要删除的文件
- `src/subtitleformatter/core/sentence_handler.py` (509行)
- `src/subtitleformatter/core/filler_remover.py` (120行)
- `src/subtitleformatter/core/line_breaker.py` (119行)

### 需要删除的配置项
- `stages.sentence_splitting`
- `stages.filler_handling` 
- `stages.line_breaking`
- 相关的 spaCy 模型配置

### 需要删除的依赖
- `spacy` 及其相关包
- `ModelManager` 中的 spaCy 模型加载逻辑

### 需要重构的组件
- `ModelManager` - 从 spaCy 模型管理改为 `deepmultilingualpunctuation` 模型管理

### 需要更新的导入语句
- 移除 `TextProcessor` 中对旧组件的导入
- 更新相关的类型注解和文档

## 📝 详细改造计划

### 阶段一：架构设计 (1-2天)

#### 1.1 新 TextProcessor 设计
```python
class TextProcessor:
    def __init__(self, config):
        self.config = config
        self.text_cleaner = TextCleaner()
        self.punctuation_adder = PunctuationAdder()
        self.text_to_sentences = TextToSentences()
        self.sentence_splitter = SentenceSplitter()
    
    def process(self):
        # 1. 文本清理
        cleaned_text = self.text_cleaner.process(text)
        
        # 2. 标点恢复
        punctuated_text = self.punctuation_adder.process(cleaned_text)
        
        # 3. 句子分割
        sentences = self.text_to_sentences.process(punctuated_text)
        
        # 4. 句子拆分
        final_sentences = self.sentence_splitter.process(sentences)
        
        return final_sentences
```

#### 1.2 配置系统更新
- **删除** `filler_handling` 相关配置
- **删除** `sentence_splitting` 相关配置  
- **删除** `line_breaking` 相关配置
- **新增** `punctuation_adder` 配置选项
- **新增** `text_to_sentences` 配置选项
- **新增** `sentence_splitter` 配置选项

### 阶段二：组件集成 (2-3天)

#### 2.1 删除旧组件
- **删除** `src/subtitleformatter/core/sentence_handler.py`
- **删除** `src/subtitleformatter/core/filler_remover.py`
- **删除** `src/subtitleformatter/core/line_breaker.py`

#### 2.2 创建脚本包装器
- **新增** `src/subtitleformatter/core/punctuation_adder_wrapper.py`
- **新增** `src/subtitleformatter/core/text_to_sentences_wrapper.py`
- **新增** `src/subtitleformatter/core/sentence_splitter_wrapper.py`

#### 2.3 统一接口设计
```python
class ScriptWrapper:
    def __init__(self, config):
        self.config = config
    
    def process(self, input_data):
        # 统一的处理接口
        pass
    
    def process_file(self, input_file, output_file=None):
        # 统一的文件处理接口
        pass
```

### 阶段三：依赖管理 (1天)

#### 3.1 更新 pyproject.toml
```toml
[dependency-groups]
punctuation-adder = [
    "deepmultilingualpunctuation>=1.0.0",
]
text-to-sentences = []  # 无外部依赖
sentence-splitter = []  # 无外部依赖
```

#### 3.2 删除不需要的依赖
- **删除** `spacy` 相关依赖（不再需要）
- **新增** `deepmultilingualpunctuation` 依赖

#### 3.3 重构 ModelManager (优先级靠后)
- **重构** `ModelManager` 以支持 `deepmultilingualpunctuation` 模型
- **继承** 现有的 `/models/` 目录管理方式
- **支持** 本地模型下载和离线使用
- **参考** 已有的模型存储探索文档

### 阶段四：测试和验证 (2-3天)

#### 4.1 单元测试
- 为每个新组件编写单元测试
- 测试组件间的数据传递
- 测试错误处理机制

#### 4.2 集成测试
- 端到端处理流程测试
- 性能对比测试
- 输出质量对比测试

#### 4.3 回归测试
- 确保现有功能不受影响
- 验证配置兼容性
- 测试 GUI 和 CLI 模式

### 阶段五：文档和部署 (1天)

#### 5.1 更新文档
- 更新 README.md
- 更新配置文档
- 更新用户指南

#### 5.2 版本管理
- 更新版本号
- 创建迁移指南
- 准备发布说明


## 🔄 后续事项

### 高优先级事项

#### 1. UnifiedLogger 集成
- **目标**: 确保现有的优秀日志系统能够完美兼容新的内核流程
- **内容**: 保持统一的终端和GUI日志输出，支持调试模式控制
- **计划**: [UnifiedLogger 集成计划](unified_logger_integration.md)
- **优先级**: 高 - 需要在主要重构过程中同步进行

#### 2. DebugOutput 集成  
- **目标**: 确保现有的调试输出系统能够适配新的处理步骤
- **内容**: 保持中间结果文件保存和处理日志生成功能
- **计划**: [DebugOutput 集成计划](debug_output_integration.md)
- **优先级**: 高 - 需要在主要重构过程中同步进行

### 中优先级事项

#### 3. ModelManager 迁移
- **目标**: 将模型管理从 spaCy 迁移到 `deepmultilingualpunctuation`
- **内容**: 继承现有的优秀模型管理方式，支持离线使用
- **计划**: [ModelManager 迁移计划](model_manager_migration.md)
- **优先级**: 中 - 在主要重构完成后进行

### 实施策略

#### 同步进行 (高优先级)
- UnifiedLogger 集成
- DebugOutput 集成

#### 后续进行 (中优先级)  
- ModelManager 迁移

#### 实施原则
1. **保持现有优势**: 继承所有优秀的设计和功能
2. **最小化影响**: 确保现有功能不受影响
3. **渐进式迁移**: 分阶段实施，降低风险
4. **充分测试**: 每个阶段都要进行充分测试

---

**注意**: 本计划需要完全确认后才能开始实施。请仔细审查所有细节，确保符合项目需求。
