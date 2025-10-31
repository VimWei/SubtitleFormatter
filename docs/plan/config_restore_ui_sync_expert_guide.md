# SubtitleFormatter 配置恢复 UI 联动机制详解（专家方案）

---

## 一、配置类恢复动作差异（restore last / restore default / import config）

| 恢复动作             | 数据来源及操作                          | 需刷新的UI                                      |
|----------------------|-----------------------------------------|-------------------------------------------------|
| Restore Default      | default_config.toml + default_plugin_chain.toml  | 全面刷新（plugin chain，plugin config，全tabs，processing flow, logpanel）|
| Import config        | 选中文件 + 所依赖链文件                 | 同上（与 default 机制无本质区别）               |
| Restore Last         | **从快照（内存）恢复**，强制写回链文件并切链路径 | 同上（但数据来源区别见下文）                    |

### Restore Default / Import Config

- 直接读取指定 toml 文件（default 或 import），构造 unified_config、chain_config
- 恢复后必须完全调用 UI 刷新链，对所有依赖配置的界面生效

### Restore Last 机制区别
- 并非“重新加载磁盘 config_latest.toml + 链文件”
- 按 [working_config_separation_mechanism.md](working_config_separation_mechanism.md) 执行：
    - 恢复为快照时刻的“工作配置（unified_config + chain_config）”
    - 快照恢复后**强制写回链文件（以快照的实际值覆盖当前链文件）**
    - 切换当前链路径（配置引用链文件路径）为快照时刻链路径
    - 再统一刷新 UI

## 二、各配置项归属与UI面板联动列表

| 配置项           | 归属面板/控件         | 刷新接口/方法                        |
|------------------|----------------------|--------------------------------------|
| logging level    | LogPanel             | set_logging_level                    |
| debug mode等     | Tab Advanced         | load_config_from_coordinator         |
| input/output路径 | Tab Basic            | load_config_from_coordinator         |
| plugin chain     | PluginChainVisualizer/PluginManagementPanel | update_plugin_chain                  |
| 每个插件参数     | PluginConfigPanel        | reload_all_configs                   |
| processing flow  | ProcessingFlowPanel      | update_processing_flow               |
| 其它tabs         | 各自tab/控件         | 各自的 load/refresh 接口             |

---

## 三、推荐的恢复—刷新链走向（核心准则）

### 触发入口（示例伪码）

```python
# restore last
unified_config = self.config_coordinator.restore_last_config()
chain_config = self.config_coordinator.restore_chain_from_snapshot()  # 快照
self.parent().on_configuration_restored(unified_config, chain_config)

# restore default
unified_config = ... # 读 default_config.toml
chain_config = ...   # 读 default_plugin_chain.toml
self.parent().on_configuration_restored(unified_config, chain_config)

# import config
unified_config = ... # 读导入文件
generate chain_config as above
self.parent().on_configuration_restored(unified_config, chain_config)
```

### 统一刷新口实现（推荐 on_configuration_restored 核心链）

```python
def on_configuration_restored(self, unified_config, chain_config):
    plugin_order = chain_config.get("plugins", {}).get("order", [])
    self.plugin_chain_visualizer.update_plugin_chain(plugin_order)
    self.plugin_management.update_plugin_chain(plugin_order)
    self.plugin_config_panel.reload_all_configs(chain_config)
    self.processing_flow_panel.update_processing_flow(plugin_order)
    self.tabs_panel.tab_basic.load_config_from_coordinator()
    self.tabs_panel.tab_advanced.load_config_from_coordinator()
    level = unified_config.get('logging', {}).get('level', 'INFO')
    self.log_panel.set_logging_level(level)
    # 其它控件如有配置联动，仿照同方式补齐
```

---

## 四、快照机制的特殊策略

- **快照作为恢复源，保证 Restore Last 还原时 UI 所见即所得，不被磁盘编辑等干扰**
- 恢复后链文件被快照值覆盖，当前链路径被快照路径取代，彻底同步状态
- 工作-已保存-快照分层，所有 UI 联动以 in-memory config 为准


## 五、总结

1. 任一配置恢复（Restore last/default/import），都应走唯一的 UI 刷新总口，按上表彻底刷全 UI
2. 恢复 last 不等价于最新磁盘链文件加载，必须以快照管理工作状态为准
3. 各 UI 控件逻辑严格区分 logging level（LogPanel）、debug mode（Advanced）、路径（Basic）
4. 机制规则与 UI 联动全盘打通，配置对象转动时界面始终一致可靠。

---

**文档生成：2025-10。依据 working_config_separation_mechanism.md 及 SubtitleFormatter 当前 UI 构架与配置机制设计的专家级解读总结。**

---

## 附录：与配置架构设计文档一致的增补说明

### 1. 配置文件丢失/失效自动回退
- 若恢复过程中遇到 unified config 或 chain config 文件丢失、损坏，系统应自动回退到 src/subtitleformatter/config/default_config.toml、default_plugin_chain.toml 等内置默认配置，并在 UI 明显提示用户。

### 2. 配置兼容性校验与升级
- 每次恢复动作调度 on_configuration_restored 之前，都需确保 configs 已经过有效性校验、字段升级、丢失字段补填，字段冗余移除等处理（详见配置设计文档 7.5节）。

### 3. 插件链参数全量传递
- 统一传递到 UI 的 chain_config 必须包含链中所有实际用到插件的完整参数（包括默认），确保 UI 编辑、展示、保存的一致性。

### 4. 配置优先级严格应用
- 所有 UI 组件、控件、tab 刷新时读取参数配置，必须按优先级依次尝试：
  - 插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件 plugin.json 默认值
- 禁止遗漏、混用，实现“所见即所得”同步体验。

### 5. 自动保存与退出保存策略
- 参照配置管理设计文档，参数编辑时即时保存到目标位置；退出或切链、导入等场合若有未保存变更，需自动写盘生成 latest 文件，保证状态不丢失。

### 6. 插件参数默认值唯一来源
- 插件参数默认值仅来自 plugins 目录下 plugin.json 的 config_schema.properties.default，不从 default_plugin_chain.toml 继承，避免混淆。
- Reset Defaults、首次加载等场景均以此为准，保证插件默认参数与开发者代码一致。

---

**本补充附录确保 config_restore_ui_sync_expert_guide.md 与 configuration_management_design.md 全面一致，避免遗漏/偏差，提升整体文档的工程可执行性和项目规范性。**
