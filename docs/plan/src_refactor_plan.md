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

### 插件化架构优势

#### 1. 灵活性
- **自由组合**: 可以任意组合和排序插件
- **动态配置**: 通过配置文件控制插件启用/禁用
- **运行时调整**: 支持动态添加/移除插件

#### 2. 可扩展性
- **新功能添加**: 只需实现新的插件类
- **向后兼容**: 现有插件不受新插件影响
- **独立开发**: 每个插件可以独立开发和测试

#### 3. 可维护性
- **职责分离**: 每个插件只负责特定功能
- **接口统一**: 所有插件遵循相同的接口规范
- **类型安全**: 自动检查数据类型兼容性

### 新的处理流程

```
原始文本 → [插件链] → 最终输出

插件链示例:
text_cleaning → punctuation_adder → text_to_sentences → sentence_splitter

未来可扩展为:
text_cleaning → punctuation_adder → text_to_sentences → sentence_splitter → grammar_checker → style_optimizer
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

### 🎯 重构策略：插件管理平台优先

基于基础设施架构分析，本重构采用"**插件管理平台优先**"的策略：

1. **阶段一**: 构建插件管理平台基础设施
2. **阶段二**: 定义插件接口和基类
3. **阶段三**: 将现有组件插件化
4. **阶段四**: 开发GUI管理界面

### 阶段一：插件管理平台构建 (3-4天)

#### 1.1 核心基础设施组件
**目标**: 构建插件生态系统的核心基础设施

**详细架构**: [基础设施架构文档](infrastructure_architecture.md)

**核心组件**:
- 🔧 **PluginRegistry**: 插件发现和注册机制
- 🔄 **PluginLifecycleManager**: 插件加载/卸载/初始化
- ⚙️ **PluginConfigManager**: 插件配置管理
- 📡 **PluginEventSystem**: 插件间通信系统

**实施优先级**: 🔴 **P0 - 最高优先级**

#### 1.2 插件接口和基类
**目标**: 定义统一的插件开发接口

**详细设计**: [插件化架构设计文档](plugin_architecture_design.md)

**核心内容**:
- 📋 **TextProcessorPlugin**: 插件基类定义
- 🔌 **插件接口规范**: 统一的输入/输出接口
- 💉 **依赖注入机制**: 基础设施注入到插件
- 📝 **插件配置标准**: 标准化的配置格式

**实施优先级**: 🔴 **P0 - 最高优先级**

#### 1.3 现有基础设施集成
**目标**: 确保现有优秀组件与新平台完美集成

**详细计划**:
- 📋 **UnifiedLogger 集成**: [UnifiedLogger 集成计划](unified_logger_integration.md)
- 🐛 **DebugOutput 集成**: [DebugOutput 集成计划](debug_output_integration.md)
- ⚙️ **ConfigManager 扩展**: 支持插件配置管理
- 🔧 **ModelManager 适配**: 为插件提供模型访问接口

**实施优先级**: 🟡 **P1 - 高优先级**

#### 1.4 插件目录结构设计
**目标**: 建立清晰的插件组织架构

**灵活的命名空间目录结构**:
```
SubtitleFormatter/
├── src/subtitleformatter/plugins/    # 插件基础设施
│   ├── __init__.py
│   ├── base/                         # 插件基类和接口
│   │   ├── __init__.py
│   │   ├── plugin_base.py            # TextProcessorPlugin 基类
│   │   └── plugin_registry.py        # 插件注册机制
│   └── manager/                      # 插件管理组件
│       ├── __init__.py
│       ├── plugin_lifecycle.py       # 生命周期管理
│       ├── plugin_config.py          # 配置管理
│       └── plugin_sandbox.py         # 安全沙箱
├── plugins/                          # 统一插件目录
│   ├── README.md                    # 插件开发指南
│   ├── builtin/                      # 内置插件 (分类方式)
│   │   ├── text_cleaning/           # 插件目录 (下划线)
│   │   │   ├── plugin.json
│   │   │   ├── plugin.py
│   │   │   └── README.md
│   │   ├── punctuation_adder/       # 插件目录 (下划线)
│   │   ├── text_to_sentences/       # 插件目录 (下划线)
│   │   └── sentence_splitter/      # 插件目录 (下划线)
│   ├── examples/                     # 示例插件 (分类方式)
│   │   ├── simple_uppercase/        # 插件目录 (下划线)
│   │   └── word_counter/            # 插件目录 (下划线)
│   ├── community/                    # 社区插件 (分类方式)
│   │   ├── grammar_checker/         # 插件目录 (下划线)
│   │   └── style_optimizer/         # 插件目录 (下划线)
│   ├── username/                     # 个人插件 (来源方式)
│   │   ├── my_plugin1/              # 插件目录 (下划线)
│   │   └── my_plugin2/              # 插件目录 (下划线)
│   ├── experimental/                 # 实验性插件 (分类方式)
│   │   ├── ai_enhancer/             # 插件目录 (下划线)
│   │   └── voice_synthesis/         # 插件目录 (下划线)
│   └── deprecated/                   # 废弃插件 (分类方式)
│       ├── old_processor/           # 插件目录 (下划线)
│       └── legacy_converter/        # 插件目录 (下划线)
└── scripts/                          # 独立脚本 (保持现状)
    ├── punctuation_adder/            # 现有脚本 (下划线目录)
    ├── text_to_sentences/           # 现有脚本 (下划线目录)
    └── sentence_splitter/           # 现有脚本 (下划线目录)
```

**目录优势**:
- 🏠 **命名空间隔离**: 避免插件名称冲突
- 🔌 **灵活组织**: 支持多种组织方式 (分类、来源、功能、状态)
- 📜 **分层命名**: 与现有 scripts 系统保持一致
- 🎯 **技术自由**: 命名空间可以是任意合法的目录名称

**实施优先级**: 🟡 **P1 - 高优先级**

#### 1.5 命名规范设计
**目标**: 建立统一的命名规范，与现有 scripts 系统保持一致

**分层命名策略**:
- **文件系统层**: 使用下划线 (`text_cleaning`, `punctuation_adder`)
- **命令行层**: 使用连字符 (`text-to-sentences`, `sentence-splitter`)
- **配置引用**: 使用完整命名空间 (`builtin/text_cleaning`)

**命名空间规则**:
- **技术限制**: 使用合法的目录名称，避免特殊字符和空格
- **推荐约定**: 
  - `builtin/` - 内置插件
  - `examples/` - 示例插件
  - `community/` - 社区插件
  - `username/` - 个人插件
  - `experimental/` - 实验性插件
- **自定义命名空间**: 可以使用任意合法的目录名称

**与现有系统的一致性**:
- ✅ **Scripts 目录**: 保持现有的下划线目录名
- ✅ **CLI 命令**: 保持现有的连字符命令名
- ✅ **映射机制**: CLI 名称自动映射到文件路径

**实施优先级**: 🟡 **P1 - 高优先级**

### 阶段二：插件接口和基类 (1-2天)

#### 2.1 TextProcessorPlugin 基类
**目标**: 定义统一的插件开发接口

**详细设计**: [插件化架构设计文档](plugin_architecture_design.md)

**核心内容**:
- 📋 **插件基类**: 统一的插件接口定义
- 🔌 **类型安全**: 输入/输出类型检查
- 💉 **依赖注入**: 基础设施自动注入
- 📝 **配置管理**: 标准化的配置处理

**实施优先级**: 🔴 **P0 - 最高优先级**

#### 2.2 插件开发指南
**目标**: 为开发者提供完整的开发规范

**详细指南**: [插件开发指南文档](plugin_development_guide.md)

**核心内容**:
- 📁 **目录结构**: 标准的插件目录结构
- ⚙️ **配置文件**: plugin.json 格式说明
- 💻 **实现示例**: 完整的插件开发示例
- 📦 **安装使用**: 插件安装和使用流程

**实施优先级**: 🟡 **P1 - 高优先级**

### 阶段三：现有组件插件化 (2-3天)

#### 3.1 内置插件实现
**目标**: 将现有组件和脚本转换为插件

**插件列表**:
- 🧹 **TextCleaner 插件化**: 现有 `TextCleaner` 组件改造
- 🔤 **PunctuationAdder 插件化**: 基于 `scripts/punctuation_adder`
- 📝 **TextToSentences 插件化**: 基于 `scripts/text_to_sentences`
- ✂️ **SentenceSplitter 插件化**: 基于 `scripts/sentence_splitter`

**实施优先级**: 🟢 **P2 - 中优先级**

#### 3.2 插件配置系统
**目标**: 建立灵活的插件配置管理

**配置结构**:
```toml
# 新的插件化配置结构 - 使用完整的命名空间引用
[plugins]
# 插件执行顺序
order = [
    "builtin/text_cleaning",
    "builtin/punctuation_adder", 
    "builtin/text_to_sentences",
    "builtin/sentence_splitter"
]

# 文本清理插件
[plugins."builtin/text_cleaning"]
enabled = true
# 保留现有配置

# 标点恢复插件
[plugins."builtin/punctuation_adder"]
enabled = true
model_name = "oliverguhr/fullstop-punctuation-multilang-large"
local_models_dir = "models/"

# 句子分割插件
[plugins."builtin/text_to_sentences"]
enabled = true
# 无额外配置

# 句子拆分插件
[plugins."builtin/sentence_splitter"]
enabled = true
min_recursive_length = 70
max_depth = 8
```

**实施优先级**: 🟢 **P2 - 中优先级**

#### 3.3 删除旧组件
**目标**: 清理不再需要的旧组件

**删除清单**:
- 🗑️ **删除** `src/subtitleformatter/core/sentence_handler.py`
- 🗑️ **删除** `src/subtitleformatter/core/filler_remover.py`
- 🗑️ **删除** `src/subtitleformatter/core/line_breaker.py`
- 🗑️ **删除** 相关的 spaCy 模型配置和依赖

**实施优先级**: 🟢 **P2 - 中优先级**

### 阶段四：GUI插件管理界面 (2-3天)

#### 4.1 插件管理面板
**目标**: 提供直观的插件管理界面

**详细设计**: [插件化GUI设计文档](plugin_gui_design.md)

**核心特性**:
- 🎨 **动态界面**: 根据插件配置动态更新界面
- 🔧 **可视化配置**: 直观的插件链配置和处理流程展示
- 📊 **实时监控**: 插件状态和性能的实时监控
- 🛠️ **简单管理**: 类似vim插件的本地管理方式

**实施优先级**: 🔵 **P3 - 低优先级**

#### 4.2 插件链配置界面
**目标**: 提供可视化的插件链配置

**功能特性**:
- 🔄 **拖拽排序**: 通过拖拽调整插件执行顺序
- ⚙️ **参数配置**: 可视化配置每个插件的参数
- 👁️ **预览效果**: 实时预览配置变更的效果
- 💾 **配置保存**: 自动保存配置变更

**实施优先级**: 🔵 **P3 - 低优先级**

### 阶段五：测试和验证 (2-3天)

#### 5.1 单元测试
**目标**: 确保每个组件功能正确

**测试内容**:
- 🧪 **插件基类测试**: 测试插件接口和基类功能
- 🔌 **插件实现测试**: 测试每个内置插件的功能
- ⚙️ **配置管理测试**: 测试插件配置的加载和保存
- 🔄 **生命周期测试**: 测试插件的加载、初始化和清理

**实施优先级**: 🟡 **P1 - 高优先级**

#### 5.2 集成测试
**目标**: 确保整个系统协同工作

**测试内容**:
- 🔗 **端到端测试**: 完整的文本处理流程测试
- 📊 **性能对比测试**: 新旧系统的性能对比
- 🎯 **输出质量测试**: 确保输出质量不降低
- 🔄 **插件链测试**: 测试不同插件组合的效果

**实施优先级**: 🟡 **P1 - 高优先级**

#### 5.3 回归测试
**目标**: 确保现有功能不受影响

**测试内容**:
- ✅ **功能兼容性**: 确保现有功能正常工作
- ⚙️ **配置兼容性**: 确保现有配置文件仍然有效
- 🖥️ **界面兼容性**: 确保GUI和CLI模式都正常
- 📁 **文件兼容性**: 确保输入输出文件格式兼容

**实施优先级**: 🟡 **P1 - 高优先级**

### 阶段六：文档和部署 (1天)

#### 6.1 更新文档
**目标**: 提供完整的用户和开发者文档

**文档更新**:
- 📖 **README.md**: 更新项目介绍和使用说明
- ⚙️ **配置文档**: 更新插件配置说明
- 👨‍💻 **开发者指南**: 更新插件开发指南
- 🚀 **迁移指南**: 提供从旧版本到新版本的迁移说明

**实施优先级**: 🟢 **P2 - 中优先级**

#### 6.2 版本管理
**目标**: 准备新版本发布

**版本管理**:
- 🔢 **版本号更新**: 更新到新的主版本号
- 📝 **发布说明**: 准备详细的发布说明
- 🏷️ **标签管理**: 创建版本标签
- 📦 **打包发布**: 准备发布包

**实施优先级**: 🟢 **P2 - 中优先级**

## 📊 任务优先级和依赖关系

### 🔴 P0 - 最高优先级 (必须首先完成)

#### 执行顺序和里程碑
```
里程碑 M1: 插件基础设施就绪 (2天)
├── 1.1 TextProcessorPlugin 基类 (0.5天)
│   └── 文件: src/subtitleformatter/plugins/base/plugin_base.py
├── 1.2 PluginRegistry 注册机制 (0.5天)
│   └── 文件: src/subtitleformatter/plugins/base/plugin_registry.py
├── 1.3 PluginLifecycleManager 生命周期 (0.5天)
│   └── 文件: src/subtitleformatter/plugins/manager/plugin_lifecycle.py
└── 1.4 依赖注入机制 (0.5天)
    └── 文件: src/subtitleformatter/plugins/manager/dependency_injection.py

检查点 CP1: 基础插件可以加载和初始化
```

#### 具体任务
1. **TextProcessorPlugin 基类** - 统一插件接口
   - 文件: `src/subtitleformatter/plugins/base/plugin_base.py`
   - 依赖: 无
   - 验收: 基类可以实例化，接口方法可调用

2. **PluginRegistry 注册机制** - 插件发现和注册
   - 文件: `src/subtitleformatter/plugins/base/plugin_registry.py`
   - 依赖: TextProcessorPlugin 基类
   - 验收: 可以扫描和注册插件

3. **PluginLifecycleManager 生命周期** - 插件加载/卸载/初始化
   - 文件: `src/subtitleformatter/plugins/manager/plugin_lifecycle.py`
   - 依赖: PluginRegistry
   - 验收: 插件可以加载、初始化和卸载

4. **依赖注入机制** - 基础设施注入到插件
   - 文件: `src/subtitleformatter/plugins/manager/dependency_injection.py`
   - 依赖: PluginLifecycleManager
   - 验收: 基础设施可以注入到插件实例

### 🟡 P1 - 高优先级 (平台核心功能)
1. **PluginConfigManager** - 插件配置管理
2. **PluginEventSystem** - 插件间通信
3. **UnifiedLogger 集成** - 日志系统集成
4. **DebugOutput 集成** - 调试输出集成
5. **插件目录结构** - 建立插件组织架构
6. **插件开发指南** - 开发规范和文档
7. **测试和验证** - 单元测试、集成测试、回归测试

### 🟢 P2 - 中优先级 (具体插件实现)
1. **TextCleaner 插件化** - 现有组件改造
2. **PunctuationAdder 插件化** - scripts 包装
3. **TextToSentences 插件化** - scripts 包装
4. **SentenceSplitter 插件化** - scripts 包装
5. **插件配置系统** - 配置管理实现
6. **删除旧组件** - 清理不再需要的组件
7. **文档和部署** - 更新文档和版本管理

### 🔵 P3 - 低优先级 (增强功能)
1. **PluginSandbox** - 安全沙箱
2. **PluginPerformanceMonitor** - 性能监控
3. **GUI 插件管理界面** - 用户界面
4. **ModelManager 迁移** - 模型管理升级

### 🔗 任务依赖关系
```
P0 基础设施 → P1 平台功能 → P2 插件实现 → P3 增强功能
     ↓              ↓              ↓
   插件基类      配置管理        具体插件      GUI界面
     ↓              ↓              ↓
   注册机制      事件系统        脚本包装     性能监控
     ↓              ↓              ↓
   生命周期      日志集成        配置系统     安全沙箱
```

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

## ⚠️ 风险控制和回滚策略

### 关键风险点
1. **插件系统复杂性**: 插件架构可能增加系统复杂性
2. **性能影响**: 插件链处理可能影响性能
3. **兼容性问题**: 新系统可能与现有功能不兼容
4. **依赖管理**: 新依赖可能引入版本冲突

### 风险缓解措施
1. **渐进式实施**: 分阶段实施，每个阶段都有检查点
2. **充分测试**: 每个阶段都进行单元测试和集成测试
3. **保持兼容**: 确保现有功能在重构过程中正常工作
4. **回滚准备**: 每个阶段都准备回滚方案

### 回滚策略
```
阶段回滚:
P0 → 保持现有架构，删除新增的插件文件
P1 → 回滚到P0完成状态
P2 → 回滚到P1完成状态
P3 → 回滚到P2完成状态

数据回滚:
- 配置文件备份: config_backup_YYYYMMDD.toml
- 代码回滚: git reset --hard <commit_hash>
- 依赖回滚: pip install -r requirements_backup.txt
```

### 检查点定义
- **CP1**: 基础插件可以加载和初始化
- **CP2**: 插件配置系统正常工作
- **CP3**: 现有组件成功插件化
- **CP4**: 端到端测试通过
- **CP5**: 性能测试通过

## 🚀 未来扩展计划

详细的插件扩展计划、开发指南和架构演进路径请参考: [插件化架构设计文档](plugin_architecture_design.md#扩展性设计)

## ✅ 实施准备检查清单

### 技术准备
- [ ] 确认现有代码结构分析完整
- [ ] 确认scripts功能分析准确
- [ ] 确认插件架构设计合理
- [ ] 确认基础设施集成方案可行

### 资源准备
- [ ] 确认开发时间安排合理
- [ ] 确认测试环境准备就绪
- [ ] 确认备份策略完善
- [ ] 确认回滚方案可行

### 风险准备
- [ ] 确认风险识别完整
- [ ] 确认缓解措施有效
- [ ] 确认检查点设置合理
- [ ] 确认回滚策略可行

---

**注意**: 本计划需要完全确认后才能开始实施。请仔细审查所有细节，确保符合项目需求。
