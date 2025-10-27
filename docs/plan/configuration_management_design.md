# SubtitleFormatter 配置管理设计方案

## 1. 背景与问题分析

### 1.1 当前配置管理现状

#### 旧版GUI的优秀设计
- **Import Config**: 从文件导入完整配置
- **Export Config**: 导出当前配置到文件
- **Restore Last**: 恢复到上次保存的配置
- **Restore Default**: 恢复默认配置

#### 新版GUI的配置管理问题
1. **功能缺失**: 旧版的优秀配置管理功能在新版中消失
2. **功能不明确**: Plugin Configuration 底部的3个按钮作用不清晰
   - Apply Configuration: 作用不明
   - Export Config: 只输出到日志，无文件保存
   - Reset to Defaults: 功能正常
3. **插件链配置缺失**: Plugin Chain 缺乏导入导出机制
4. **配置流程不明确**: Start Processing 和程序退出时的配置处理机制未定义

### 1.2 核心问题
- 用户无法快速切换不同配置
- 配置备份与恢复机制缺失
- 插件链配置每次都要重新设置
- 配置的持久化和加载策略不明确

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
└── 插件配置 (Plugin Config)
    ├── 单个插件参数
    ├── 参数验证规则
    └── 参数默认值
```

**说明**: 配置采用三层架构，统一配置引用插件链配置，插件配置独立存储

### 3.2 简化的配置存储结构

```
data/configs/
├── config_latest.toml              # 当前配置（程序启动时加载）
├── plugins/                        # 插件配置目录
│   └── builtin/                    # 命名空间目录
│       ├── text_cleaning.toml
│       ├── sentence_splitter.toml
│       └── punctuation_adder.toml
├── plugin_chains/                  # 插件链配置目录
│   ├── default_plugin_chain.toml
│   ├── chain_latest.toml
│   ├── basic_chain.toml
│   ├── advanced_chain.toml
│   └── custom_*.toml
└── *.toml                          # 用户保存的配置文件
    ├── basic_processing.toml
    ├── advanced_processing.toml
    └── my_custom_config.toml
```

**说明**: 
- 统一配置: 存储全局设置和插件链引用
- 插件链配置: 存储插件顺序和链特定参数
- 插件配置: 独立存储每个插件的参数配置
- 配置优先级: 插件链特定配置 > 插件自定义配置 > 内置默认配置

### 3.3 配置架构的核心原则

**关键结论**: 统一配置永远只保存插件链引用，不保存任何具体插件的配置。

- **统一配置**: 只包含全局设置和 `current_plugin_chain` 引用
- **插件链配置**: 包含完整的插件配置（用户配置 + 默认配置）
- **插件配置**: 独立存储，立即保存到 `data/configs/plugins/`
- **配置层次**: 统一配置 → 插件链配置 → 插件配置
- **配置优先级**: 插件链特定配置 > 插件自定义配置 > 内置默认配置
- **按需加载**: 只加载当前插件链需要的插件配置，提升性能
- **配置格式**: 使用 TOML 格式

## 4. 功能设计

### 4.1 统一配置管理

#### 处理面板功能
- **Import Config**: 导入完整配置文件
- **Export Config**: 导出完整配置文件（包括引用的插件链和插件配置）
- **Restore Last**: 恢复到上次保存的配置
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
[file_processing]
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
- **存储策略**: 插件链配置延迟保存，只在退出时或用户显式保存时保存

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
- 每个插件有独立的配置文件，用户修改参数后立即保存到 `data/configs/plugins/` 目录
- 配置文件按命名空间存储为目录结构，例如 `data/configs/plugins/builtin/punctuation_adder.toml`
- 配置文件内容中的键名使用完整插件名称（包括斜杠）：`[builtin/punctuation_adder]`

#### 设计原则
- **独立存储**: 每个插件有独立的配置文件，存储在 `data/configs/plugins/` 目录
- **按需加载**: 只加载当前插件链需要的插件配置，不加载未使用的插件
- **存储策略**: 插件配置立即保存，插件链配置延迟保存
- **配置优先级**: 插件链特定配置 > 插件自定义配置 > 内置默认配置
- **同一插件多次使用**: 采用简单方案，同一插件在插件链中多次使用时使用相同参数
- **文件丢失处理**: 如果引用的插件链文件不存在，自动回退到内置默认插件链并提示用户

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
        → 按需加载插件配置 → 合并配置优先级 → 更新界面状态
        → 完成初始化
   ```

3. **插件链文件丢失处理**:
   - 如果引用的插件链文件不存在，自动回退到内置默认插件链
   - 在GUI中显示警告信息，告知用户插件链文件丢失
   - 提供"选择其他插件链"的恢复选项

### 5.2 运行时配置管理
1. **配置变更检测**: 实时检测配置变更
2. **插件配置立即保存**: 用户修改插件参数后立即保存到 `data/configs/plugins/` 目录下的对应插件配置文件
3. **插件链配置延迟保存**: 插件链配置不立即保存，只在退出时或用户显式保存时保存
4. **配置验证**: 配置变更时进行有效性验证
5. **配置同步**: 确保界面与配置数据同步

### 5.3 退出时配置保存
1. **统一配置保存**: 保存到 `config_latest.toml`
2. **插件链保存**: 
   - 如果用户显式保存了插件链，保存到 `data/configs/plugin_chains/` 目录
   - 程序退出时，保存到 `chain_latest.toml`（不生成新文件）
3. **配置引用更新**: 更新统一配置中的 `current_plugin_chain` 引用
4. **插件配置**: 插件配置已在运行时立即保存到 `data/configs/plugins/` 目录，无需额外处理
5. **配置备份**: 重要配置变更前创建备份
6. **配置清理**: 清理临时配置和缓存

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

**注意**: 每个插件有独立的配置文件，用户修改参数后立即保存到 `data/configs/plugins/` 目录

## 7. 技术实现要点

### 7.1 配置管理器设计
- **UnifiedConfigManager**: 统一配置管理（主要）
- **PluginChainManager**: 插件链配置管理
- **PluginConfigManager**: 插件参数配置管理
- **ConfigCoordinator**: 配置协调器，统一管理所有配置操作

### 7.1.1 关键实现细节
- **插件默认配置获取**: `PluginConfigManager._get_plugin_default_config()` 从 `plugin.json` 提取默认值
- **插件注册表集成**: `PluginConfigManager` 接收 `PluginRegistry` 实例，避免重复初始化
- **配置缓存机制**: 使用 `_config_cache` 避免重复文件I/O操作
- **错误处理**: 配置加载失败时自动回退到默认配置

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
- ✅ **配置持久化**: 插件配置立即保存，插件链配置延迟保存
- ✅ **错误处理**: 插件链文件丢失时自动回退到默认配置

### 8.2 下一步计划
- **配置验证机制**: 配置加载时的有效性验证
- **配置比较和合并**: 配置差异比较功能
- **配置版本控制**: 配置升级时的兼容性处理
- **配置备份机制**: 重要配置变更前的自动备份
- **性能优化**: 优化配置加载和保存性能
- **用户反馈收集**: 收集用户反馈并持续优化
- **文档完善**: 根据实际使用情况完善用户文档
