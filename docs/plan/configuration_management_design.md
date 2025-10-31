# SubtitleFormatter 配置管理设计方案

## 概述

本文档描述了 SubtitleFormatter 的配置管理系统设计方案，包括统一配置管理、插件链配置管理、插件参数配置管理等功能。

## 1. 核心创新

- **配置状态管理**：工作配置、保存配置、快照配置三层分离
- **智能保存策略**：根据插件选择来源自动决定保存位置
- **快照保护机制**：确保 Restore Last 功能不受配置修改影响
- **自动保存机制**：插件链/插件配置即时保存；latest 类文件退出时保存

- **Import Config**: 从文件导入完整配置
- **Export Config**: 导出当前配置到文件
- **Restore Last**: 恢复到上次保存的配置
- **Restore Default**: 恢复默认配置

## 2. 设计目标

### 2.1 用户体验目标
- **快速切换**: 用户可以在不同工作场景间快速切换配置
- **配置安全**: 避免配置丢失，支持配置回滚
- **配置分享**: 支持配置的导入导出和团队共享
- **工作流不中断**: 配置管理不干扰主要工作流程

### 2.2 技术目标
- **配置层次化**: 清晰的配置层次结构
- **配置持久化**: 可靠的配置保存和加载机制
- **配置兼容性**: 处理配置版本升级和兼容性
- **配置验证**: 配置的有效性验证和错误处理

## 3. 配置架构设计

### 3.1 配置架构

```
配置结构:
├── 统一配置 (Unified Config)
│   ├── 全局设置
│   ├── 文件处理设置
│   └── 插件链引用
├── 插件链配置 (Plugin Chain Config)
│   ├── 插件顺序
│   └── 插件链特定参数（用于覆盖插件默认配置）
│       ├── 工作配置 (Working Config) - 内存中正在编辑的配置
│       ├── 保存配置 (Saved Config) - 持久化到文件的配置
│       └── 快照配置 (Snapshot Config) - 用于 Restore Last 的备份
└── 插件配置 (Plugin Config)
    ├── 单个插件参数
    ├── 参数验证规则
    └── 参数默认值
```

**说明**: 配置采用三层架构，统一配置引用插件链配置，插件配置独立存储。插件链配置引入工作配置、保存配置、快照配置三层状态管理，确保配置修改的正确保存和 Restore Last 功能的保护。

### 3.2 简化的配置存储结构

```
data/configs/
├── config_latest.toml              # 当前配置（程序启动时加载）
├── *.toml                          # 用户保存的配置文件
│   ├── basic_processing.toml
│   ├── advanced_processing.toml
│   └── my_custom_config.toml
├── plugins/                        # 插件配置目录
│   └── builtin/                    # 命名空间目录
│       ├── text_cleaning.toml
│       ├── sentence_splitter.toml
│       └── punctuation_adder.toml
└── plugin_chains/                  # 插件链配置目录
    ├── default_plugin_chain.toml
    ├── chain_latest.toml
    ├── basic_chain.toml
    ├── advanced_chain.toml
    └── custom_*.toml
```

**说明**:
- 统一配置: 存储全局设置和插件链引用
- 插件链配置: 存储插件顺序和链特定参数（包括工作配置、保存配置、快照配置）
- 插件配置: 独立存储每个插件的参数配置
- 配置优先级: 插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置

### 3.3 配置架构的核心原则

**关键结论**: 统一配置永远只保存插件链引用，不保存任何具体插件的配置。

- **统一配置**: 只包含全局设置和 `current_plugin_chain` 引用
- **插件链配置**: 包含完整的插件配置（用户配置 + 默认配置）
  - **工作配置**: 内存中正在编辑的配置，实时保存
  - **保存配置**: 持久化到文件的配置，Restore Last 的参照标准
  - **快照配置**: 启动时的配置快照，用于 Restore Last 功能
- **插件配置**: 独立存储，根据选择来源智能保存
  - **来自可用插件列表**: 保存到 `data/configs/plugins/`
  - **来自插件链**: 保存到插件链工作配置，并即时写回当前链文件
- **配置层次**: 统一配置 → 插件链配置 → 插件配置
- **配置优先级**: 插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置
- **按需加载**: 只加载当前插件链需要的插件配置，提升性能
- **配置格式**: 使用 TOML 格式
- **智能保存**: 根据插件选择来源（可用插件列表 vs 插件链）自动决定保存位置

## 4. 功能设计

### 4.1 统一配置管理

#### 文件处理面板功能
- **Import Config**: 导入完整配置文件
- **Export Config**: 导出完整配置文件（包括引用的插件链和插件配置）
- **Restore Last**: 恢复到上次保存的配置
  - 从启动时创建的快照恢复，确保不受工作配置修改影响
  - 恢复后重新创建快照，继续支持后续的 Restore Last 操作
- **Restore Default**: 恢复默认配置

#### UI布局设计
- **配置按钮位置**: 配置按钮放在文件处理面板和插件管理面板，更符合用户习惯
- **功能分组**: 全局配置操作放在文件处理面板，插件链配置操作放在插件管理面板

#### 错误处理机制
- **文件丢失处理**: 引用的插件链文件不存在时，自动回退到内置默认插件链并提示用户
- **配置验证**: 配置加载时进行有效性验证

#### 用户体验决策
- **配置切换流程**: 通过 Import Config 和 Export Config 实现
- **配置分享**: 通过 Export Config 实现

#### 配置文件内容
```toml
# config_latest.toml 或任意文件名.toml
[paths]
input_dir = "data/input"
output_dir = "data/output"
add_timestamp = true

[plugins]
current_plugin_chain = "plugin_chains/chain_workflow.toml"
```

**注意**: 统一配置永远只保存插件链引用，不保存任何具体插件的配置

### 4.2 插件链配置管理

#### 功能设计
- **Export Chain**: 导出插件链配置
- **Import Chain**: 导入插件链配置

#### 插件链配置的完整保存策略
**关键结论**: 插件链配置采用全量保存策略 - 保存所有用到的插件的完整配置。

- **全量保存优势**:
  - 用户可以看到完整的配置，避免用户需要翻阅插件程序中的默认配置，方便手动修改
  - 程序简洁高效，无需复杂的对比和合并逻辑
- **保存内容**: 插件链配置文件包含 `order` 和所有插件的完整配置（包括默认值）
- **配置完整性**: 插件链配置中包含所有插件的配置节，对于有配置项的插件返回完整配置，对于没有配置项的插件返回空配置 `{}`，确保配置文件结构的一致性

#### 配置状态管理与保存策略

**工作配置与保存配置分离**:
- **工作配置** (Working Config): 内存中正在编辑的配置，用户修改插件链中插件配置时实时更新
- **保存配置** (Saved Config): 持久化到文件中的配置，Restore Last 功能的参照标准
- **快照配置** (Snapshot Config): 启动时创建的配置快照，确保 Restore Last 功能不受配置修改影响

**存储策略**:
- **插件链工作配置**: 实时保存在内存中，用户修改立即更新
- **插件链配置文件**: 即时保存（来自插件链的编辑时直接写入当前链文件）
- **latest 文件**: `config_latest.toml`/`chain_latest.toml` 在退出时或显式保存时写入
- **智能保存**: 根据插件选择来源决定保存位置
  - 点击 Available Plugins 中的插件 → 保存到插件自定义配置文件（即时写盘）
  - 点击 Plugin Chain 中的插件 → 保存到插件链工作配置并即时写回链文件

#### 插件链配置文件内容
```toml
# 插件链配置文件 (如: data/configs/plugin_chains/chain_workflow.toml)
[plugins]
# 插件名称使用完整命名空间格式: namespace/plugin_name
order = ["builtin/punctuation_adder", "builtin/sentence_splitter"]

# 包含且只包含当前插件链用到的插件的完整配置
# 注意：当插件名称包含斜杠时，键名需要用引号括起来
[plugin_configs."builtin/punctuation_adder"]
enabled = true
model_name = "oliverguhr/fullstop-punctuation-multilang-large"
capitalize_sentences = true
split_sentences = true
replace_dashes = true

[plugin_configs."builtin/sentence_splitter"]
enabled = true
min_recursive_length = 70
max_depth = 8
max_degradation_round = 5
```

**注意**:
- 插件链配置文件包含当前链用到的所有插件的完整配置，不包含未使用的插件配置
- 插件名称使用命名空间格式 `namespace/plugin_name`，例如 `builtin/punctuation_adder`
- TOML 配置节中，如果键名包含特殊字符（如 `/`），需要用引号括起来：`[plugin_configs."builtin/punctuation_adder"]`

### 4.3 插件参数配置管理

#### 功能设计
- **Reset Defaults**: 重置为默认值

#### 插件默认配置的正确理解
**关键结论**: 插件的默认配置是指 `plugin.json` 中 `config_schema.properties` 定义的 `default` 值，而不是 `default_plugin_chain.toml` 中的配置。

- **插件默认配置来源**: `plugin.json` → `config_schema` → `properties` → `default` 值
- **`default_plugin_chain.toml` 的作用**: 仅用于满足配置文件结构要求，不是插件默认配置的继承来源
- **配置加载逻辑**: 当插件配置文件不存在时，从 `plugin.json` 的 `config_schema.properties` 提取默认配置；如果插件没有配置项，则返回空配置 `{}`

#### 插件参数配置内容
```toml
# 插件自定义配置文件 (如: data/configs/plugins/builtin/punctuation_adder.toml)
# 注意：使用插件完整命名空间作为配置节键名
[builtin/punctuation_adder]
add_periods = true
add_commas = false
add_question_marks = true

# 插件自定义配置文件 (如: data/configs/plugins/builtin/sentence_splitter.toml)
[builtin/sentence_splitter]
min_recursive_length = 70
max_depth = 8
max_degradation_round = 5
```

**注意**:
- 每个插件有独立的配置文件，用户修改参数后根据选择来源智能保存
  - 选择来自可用插件列表: 立即保存到 `data/configs/plugins/` 目录
  - 选择来自插件链: 保存到插件链工作配置并即时写回链文件
- 配置文件按命名空间存储为目录结构，例如 `data/configs/plugins/builtin/punctuation_adder.toml`
- 配置文件内容中的键名使用完整插件名称（包括斜杠）：`[builtin/punctuation_adder]`

#### 设计原则
- **独立存储**: 每个插件有独立的配置文件，存储在 `data/configs/plugins/` 目录
- **按需加载**: 只加载当前插件链需要的插件配置，不加载未使用的插件
- **智能保存**: 根据插件选择来源决定保存位置
  - 来自可用插件列表: 保存到插件自定义配置文件（立即保存）
  - 来自插件链: 保存到插件链工作配置并即时写回链文件
- **存储策略**: 插件自定义配置和插件链配置文件即时保存，latest 文件延迟保存
- **配置优先级**: 插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置
- **同一插件多次使用**: 采用简单方案，同一插件在插件链中多次使用时使用相同参数
- **文件丢失处理**: 如果引用的插件链文件不存在，自动回退到内置默认插件链并提示用户
- **配置状态管理**: 插件链配置引入工作配置、保存配置、快照配置三层状态管理

### 4.4 插件默认值管理

插件系统采用统一的默认值管理机制，确保配置的一致性和可维护性。

#### 设计原则
- **单一数据源**: 所有默认配置来自 `plugin.json` 文件的 `config_schema.properties` 中的 `default` 值
- **自动加载**: 基类自动处理配置的加载、合并和验证
- **配置完整性**: 确保配置的完整性和一致性，避免配置丢失

#### 配置优先级
插件配置的加载优先级（参见 3.3 节）：
1. **插件链工作配置** (最高优先级)
2. **插件链保存配置**
3. **插件自定义配置** (存储在 `data/configs/plugins/`)
4. **plugin.json 中的默认配置** (config_schema.properties.default)

#### 系统职责分工

**基类职责**：
- 自动从 plugin.json 加载默认配置
- 将默认配置合并到 `self.config` 中
- 确保配置的完整性和一致性
- 处理配置的验证和规范化

**插件子类职责**：
- 直接使用 `self.config["key"]` 访问配置
- 信任基类已经处理了默认配置
- 专注于业务逻辑实现

**配置管理器职责**：
- 管理插件配置文件的保存和加载
- 处理配置优先级和应用
- 提供配置导入导出功能

#### 与其他系统的交互
- **GUI 系统**: GUI 从 `plugin.json` 读取配置 schema 和默认值，用于构建配置界面
- **Reset to Defaults 功能**: 依赖 `plugin.json` 中的默认值，确保与插件内部使用一致
- **配置验证**: 使用 `config_schema` 进行配置验证

**详细的开发指导**: 请参考 [插件开发指南](plugin_development_guide.md#插件默认值管理) 中的代码示例和最佳实践。

## 5. 配置生命周期

### 5.1 启动时配置加载
1. **优先级顺序**:
   - 用户当前配置 (config_latest.toml)
   - 内置默认配置 (src/subtitleformatter/config/default_config.toml)
   - 内置默认插件链 (src/subtitleformatter/config/default_plugin_chain.toml)

2. **加载流程**:
   ```
   启动 → 检查config_latest.toml → 加载统一配置
        → 读取current_plugin_chain引用 → 检查插件链文件是否存在
        → 存在: 加载插件链配置 → 不存在: 回退到内置默认插件链并提示
        → 按需加载插件配置 → 合并配置优先级 → 创建快照配置
        → 更新界面状态 → 完成初始化
   ```

3. **插件链文件丢失处理**:
   - 如果引用的插件链文件不存在，自动回退到内置默认插件链
   - 在GUI中显示警告信息，告知用户插件链文件丢失
   - 提供"选择其他插件链"的恢复选项

### 5.2 运行时配置管理
1. **配置变更检测**: 实时检测配置变更
2. **智能保存机制**: 根据插件选择来源决定保存位置
   - **来自可用插件列表**: 保存到插件自定义配置文件（立即保存到文件）
   - **来自插件链**: 保存到插件链工作配置，并即时保存到当前链文件
3. **配置状态管理**: 工作配置、保存配置、快照配置三层分离
   - 工作配置实时更新，链文件即时保存
   - 快照配置在启动时创建，用于 Restore Last 功能保护（恢复时会切回快照记录的链文件路径）
4. **配置验证**: 配置变更时进行有效性验证
5. **配置同步**: 确保界面与配置数据同步
6. **配置优先级**: 按插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置的顺序加载

### 5.3 退出时配置保存
1. **统一配置保存**: 保存到 `config_latest.toml`
2. **插件链保存**:
   - 链文件在编辑时已即时保存
   - 如果用户显式另存为插件链，写入 `data/configs/plugin_chains/` 目录指定文件
   - 程序退出时，保存到 `chain_latest.toml`（不生成新文件）
3. **配置引用更新**: 更新统一配置中的 `current_plugin_chain` 引用
4. **插件配置**: 插件自定义配置在运行时即时保存到 `data/configs/plugins/` 目录
5. **配置状态检查**: 检查是否有未保存的最新快照变更
6. **配置备份**: 重要配置变更前创建备份
7. **配置清理**: 清理临时配置和缓存

## 6. 用户界面设计

### 6.1 文件处理面板
```
File Processing Panel
├── 文件选择区域
├── 处理按钮
└── Config Actions
    ├── [Import Config] [Export Config]
    └── [Restore Last] [Restore Default]
```

### 6.2 插件管理面板
```
Plugin Management
├── Available Plugins
│   └── [插件列表]
├── Plugin Chain
│   └── [插件链列表]
└── Chain Actions
    ├── [Import Chain]
    └── [Export Chain]
```

**注意**: 插件链配置文件只包含当前链用到的插件配置，不包含未使用的插件配置

### 6.3 插件配置面板
```
Plugin Configuration
├── [插件参数配置界面]
└── Config Actions
    └── [Reset Defaults]
```

**注意**: 每个插件有独立的配置文件，用户修改参数后根据选择来源智能保存：
- 选择来自可用插件列表: 立即保存到 `data/configs/plugins/` 目录
- 选择来自插件链: 保存到插件链工作配置并即时写回链文件

## 7. 技术实现要点

### 7.1 配置管理器设计
- **UnifiedConfigManager**: 统一配置管理（主要）
- **PluginChainManager**: 插件链配置管理
- **PluginConfigManager**: 插件参数配置管理
- **ConfigCoordinator**: 配置协调器，统一管理所有配置操作

### 7.1.1 关键实现细节
- **配置状态管理**: 实现工作配置、保存配置、快照配置三层分离
  - `ConfigState` 类管理配置状态（working_config, saved_config, snapshot_config）
  - `is_dirty` 标志跟踪未保存的修改
- **智能保存策略**: 根据插件选择来源决定保存位置
  - `update_plugin_config_in_working()` - 更新插件链工作配置
  - `save_plugin_config_to_chain()` - 保存到插件链工作配置并即时写回链文件
  - `get_plugin_config_from_working()` - 获取插件链工作配置
- **快照管理机制**: 保护 Restore Last 功能
  - `create_snapshot()` / `restore_from_snapshot()` - 快照管理（恢复后保存到链文件）
  - `create_chain_snapshot()` / `restore_chain_from_snapshot()` - 插件链快照管理
- **插件默认配置获取**: `PluginConfigManager._get_plugin_default_config()` 从 `plugin.json` 提取默认值
- **插件注册表集成**: `PluginConfigManager` 接收 `PluginRegistry` 实例，避免重复初始化
- **配置缓存机制**: 使用 `_config_cache` 避免重复文件I/O操作
- **错误处理**: 配置加载失败时自动回退到默认配置
- **信号分离**: 区分来自可用插件列表和插件链的选择事件
  - `pluginSelected` - 来自可用插件列表
  - `pluginChainSelected` - 来自插件链

### 7.2 配置文件结构
```
data/configs/
├── config_latest.toml          # 统一配置文件
├── plugins/                     # 插件配置目录
│   └── builtin/                # 命名空间目录
│       ├── punctuation_adder.toml        # 标点插件配置
│       ├── sentence_splitter.toml        # 断句插件配置
│       └── text_cleaning.toml           # 文本清理插件配置
├── plugin_chains/               # 插件链配置目录
│   ├── chain_latest.toml       # 当前插件链配置
│   ├── chain_workflow.toml     # 用户保存的插件链
│   └── chain_another.toml      # 其他插件链
└── *.toml                      # 用户保存/导入的配置文件
```

```
src/subtitleformatter/config/
├── default_config.toml         # 内置默认配置
├── default_plugin_chain.toml   # 内置默认插件链
└── config_manager.py           # 配置管理器
```

### 7.3 配置引用关系
- **统一配置** → 引用插件链配置文件
- **插件链配置** → 只包含当前链用到的插件配置
- **插件配置** → 每个插件有独立的配置文件，存储在 `data/configs/plugins/` 目录
- **按需加载** → 只加载当前插件链需要的插件配置

### 7.4 错误处理机制
- **文件丢失处理**: 引用的插件链文件不存在时，自动回退到内置默认插件链
- **用户提示**: 在GUI中显示警告信息，提供恢复选项
- **配置验证**: 配置加载时进行有效性验证
- **按需加载**: 只加载当前插件链需要的插件配置，避免加载未使用的插件
- **快照保护**: 通过快照机制确保 Restore Last 功能不受配置修改影响
  - 启动时创建快照，Restore Last 时从快照恢复并切回快照记录的链文件路径，再写回该链文件
  - 工作配置的修改不会破坏快照配置的完整性
- **状态一致性**: 确保工作配置、保存配置、快照配置的状态一致性
  - 工作配置与保存配置分离，避免互相干扰
  - 配置优先级正确应用，避免配置冲突

### 7.5 插件升级时的配置处理
**关键结论**: 通过现有的 `normalize` 机制处理插件升级时的配置兼容性问题。

- **配置规范化**: 使用 `_normalize_against_defaults` 方法处理配置版本升级
- **字段变化处理**: 自动移除过时字段，添加新字段的默认值
- **向后兼容**: 确保旧配置在新版本插件中正常工作

## 8. 实施状态与计划

### 8.1 已完成功能 ✅
- ✅ **统一配置管理**: `UnifiedConfigManager` 实现
- ✅ **插件链配置管理**: `PluginChainManager` 实现
- ✅ **插件参数配置管理**: `PluginConfigManager` 实现
- ✅ **配置协调器**: `ConfigCoordinator` 实现
- ✅ **插件默认配置获取**: 从 `plugin.json` 正确提取默认配置
- ✅ **配置导入导出**: Import/Export 功能实现
- ✅ **配置恢复功能**: Restore Last/Default 功能实现
- ✅ **UI集成**: 配置按钮已集成到文件处理面板和插件管理面板
- ✅ **配置持久化**: 插件配置与插件链配置即时保存；latest 文件延迟保存
- ✅ **错误处理**: 插件链文件丢失时自动回退到默认配置
- ✅ **配置状态管理**: `ConfigState` 类实现工作配置、保存配置、快照配置分离
- ✅ **智能保存策略**: 根据插件选择来源决定保存位置
- ✅ **配置优先级修复**: 正确实现插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置
- ✅ **快照保护机制**: Restore Last 功能通过快照机制保护原始配置，并在恢复后写回链文件
- ✅ **自动保存机制**: 编辑即时保存，latest 文件在退出时自动保存

### 8.2 配置状态管理机制 ✅

在实施过程中，我们发现并解决了一个关键的配置管理两难问题：插件链中的插件配置修改既需要正确保存，又不能影响 Restore Last 功能。

**核心解决方案**：引入工作配置、保存配置、快照配置三层分离的设计模式，确保配置修改的正确保存和 Restore Last 功能的保护。

详细内容请参阅：[工作配置与保存配置分离机制](working_config_separation_mechanism.md)

**主要特性**：
- ✅ 配置状态管理：工作配置、保存配置、快照配置三层分离
- ✅ 智能保存策略：根据插件选择来源自动决定保存位置
- ✅ 快照保护机制：确保 Restore Last 功能不受配置修改影响（恢复后写回链文件）
- ✅ 自动保存机制：编辑即时保存，latest 文件在退出时保存

### 8.3 下一步计划
- **配置验证机制**: 配置加载时的有效性验证
- **配置比较和合并**: 配置差异比较功能
- **配置版本控制**: 配置升级时的兼容性处理
- **配置备份机制**: 重要配置变更前的自动备份
- **性能优化**: 优化配置加载和保存性能
- **用户反馈收集**: 收集用户反馈并持续优化
- **文档完善**: 根据实际使用情况完善用户文档
