# 左侧面板测试用例（插件管理 / 插件配置 / 配置管理）

## 0. 概述
- 目标：验证左侧面板三块的功能逻辑、数据持久化与配置优先级，确保与《configuration_management_design.md》一致。
- 覆盖范围：
  - 插件管理（Available Plugins / Plugin Chain / Chain Actions）
  - 插件配置（参数编辑 / Reset Defaults / 保存策略）
  - 配置管理（Import/Export/Restore Last/Restore Default 与 latest 文件保存）
- 数据位置（相对项目根）：
  - 统一配置：`data/configs/config_latest.toml`
  - 插件链目录：`data/configs/plugin_chains/`（含 `chain_latest.toml` 和用户链）
  - 插件配置目录：`data/configs/plugins/<namespace>/<plugin>.toml`
  - 内置默认：`src/subtitleformatter/config/default_config.toml`、`default_plugin_chain.toml`

前置条件：
- 保证应用能正常启动，GUI 左侧面板三块可见。
- 建议在一个干净的工作副本中执行测试；必要时备份 `data/configs` 目录。

---

## 1. 通用验证要点（适用于三块）
- 配置优先级必须符合：插件链工作配置 > 插件链保存配置 > 插件自定义配置 > 插件默认配置（plugin.json）。
- 智能保存策略：
  - 从 Available Plugins 进入的插件 → 保存到 `data/configs/plugins/...`（立即写盘）。
  - 从 Plugin Chain 进入的插件 → 写入“当前链文件”的 `plugin_configs`（即时写盘）。
- 快照/Restore Last：启动时创建快照；Restore Last 应恢复至快照记录的链文件与内容，并写回该链文件。
- latest 文件保存策略：编辑即时保存（链/插件）；`config_latest.toml` 与 `chain_latest.toml` 在退出时保存或在显式保存时写入。

---

## 2. 插件管理（Plugin Management）
### 2.1 列表与加载
步骤：
1) 启动应用，展开左侧“Plugin Management”。
2) 观察 Available Plugins 列表应包含内置插件（如 `builtin/punctuation_adder`、`builtin/sentence_splitter`、`builtin/text_cleaning`、`builtin/text_to_sentences`）。
期望：
- 列表加载成功，无报错；名称包含命名空间。

### 2.2 插件链展示与排序
步骤：
1) 在 Plugin Chain 中确认已加载链（由 `config_latest.toml` 的 `plugins.current_plugin_chain` 指向）。
2) 拖拽调整插件顺序（例如交换两个相邻插件）。
3) 打开对应链文件（如 `data/configs/plugin_chains/chain_workflow.toml`）。
期望：
- 链文件 `plugins.order` 顺序即时更新，写盘成功。
- 应无与未使用插件相关的额外配置写入。

### 2.3 Chain Actions: Import/Export Chain
步骤：
1) 点击 Export Chain，选择保存为 `data/configs/plugin_chains/custom_chain.toml`。
2) 手动打开该文件，确认包含：
   - `plugins.order`
   - `plugin_configs."<namespace>/<plugin>"` 的完整配置（含默认值与覆盖值）
3) 修改 `plugins.order` 后点击 Import Chain 导入这个文件。
期望：
- 导出为“全量保存”格式；仅包含当前链使用的插件配置。
- 导入后 GUI 的链顺序与配置与文件匹配，且即时写盘为当前链文件。

### 2.4 链文件缺失回退
步骤：
1) 关闭应用，暂时重命名当前链文件（`current_plugin_chain` 指向的文件）。
2) 重新启动应用。
期望：
- 应用回退到内置默认链（`default_plugin_chain.toml`），并提示用户（告警 UI）。
- 选择其他链后可恢复正常；`config_latest.toml` 的引用可更新。

---

## 3. 插件配置（Plugin Configuration）
### 3.1 从 Available Plugins 进入的保存行为
步骤：
1) 在 Available Plugins 中选中 `builtin/punctuation_adder`。
2) 修改配置项（例如 `capitalize_sentences = false`）。
3) 检查 `data/configs/plugins/builtin/punctuation_adder.toml`。
期望：
- 文件即时写盘，内容键名使用完整插件名节（示例中为 `[builtin/punctuation_adder]`）。
- 修改值准确落盘。

### 3.2 从 Plugin Chain 进入的保存行为
步骤：
1) 在 Plugin Chain 列表中选中 `builtin/sentence_splitter`。
2) 修改配置项（例如 `min_recursive_length = 80`）。
3) 打开“当前链文件”（`current_plugin_chain` 指向的文件）。
期望：
- 修改立即写入链文件的 `plugin_configs."builtin/sentence_splitter"` 节。
- 不会在 `data/configs/plugins/...` 中生成或更新该插件条目（若仅从链进入）。

### 3.3 Reset Defaults（默认值来源）
步骤：
1) 任意插件打开配置面板，点击 Reset Defaults。
2) 打开该插件对应的保存位置：
   - 若从 Available Plugins 进入 → 查看 `data/configs/plugins/...`
   - 若从 Plugin Chain 进入 → 查看当前链文件的 `plugin_configs."..."`
3) 对照插件 `plugin.json` 中 `config_schema.properties` 的 `default` 值。
期望：
- 默认值来自 `plugin.json`，不是 `default_plugin_chain.toml`。
- 保存位置遵循“进入来源”，并即时写盘。

### 3.4 配置验证与类型校验
步骤：
1) 输入非法类型值（例如把应为布尔改成字符串）。
2) 观察 UI 校验提示/阻止保存机制。
期望：
- UI 阻止非法值保存或回退到合法值；不产生坏文件。

---

## 4. 配置管理（Import/Export/Restore）
### 4.1 Import Config / Export Config（统一配置）
步骤：
1) 在文件处理面板或配置管理入口执行 Export Config，保存为 `data/configs/my_config.toml`。
2) 打开文件，确认存在：
   - `[file_processing]` 段
   - `[plugins]` 中的 `current_plugin_chain` 引用
3) 修改该文件的 `current_plugin_chain` 指向一个已存在链，然后 Import Config。
期望：
- 统一配置只保存链引用，不保存具体插件配置。
- 导入后，GUI 切换到新链并正确加载链内配置。

### 4.2 Restore Last（快照恢复）
步骤：
1) 启动后随意在链内调整两个插件参数与顺序（确保已经即时写回链文件）。
2) 点击 Restore Last。
3) 打开快照记录的链文件，并观察 GUI。
期望：
- 恢复至启动快照时的链路径与内容；恢复后内容写回该链文件。
- 启动快照不受运行期工作配置编辑影响。

### 4.3 Restore Default（恢复默认）
步骤：
1) 执行 Restore Default。
2) 确认 GUI 切到内置默认配置与默认链（默认配置文件与默认链文件定义）。
期望：
- 对应默认文件中的值生效；可继续 Import/Export。

### 4.4 程序退出保存（latest 文件）
步骤：
1) 正常编辑：
   - 在链内修改某插件参数（应已即时写盘到链文件）。
   - 在 Available Plugins 修改某插件参数（应已即时写盘到 `data/configs/plugins/...`）。
2) 退出应用。
3) 打开 `data/configs/config_latest.toml` 与 `data/configs/plugin_chains/chain_latest.toml`。
期望：
- 两个 latest 文件已更新，记录最后一次运行会话的统一配置与当前链。

---

## 5. 优先级与合并逻辑验证
步骤：
1) 设定同一插件在三个位置分别有值：
   - plugin.json 默认：A
   - `data/configs/plugins/...` 自定义：B
   - 当前链文件 `plugin_configs."..."`：C
2) 在 GUI 执行处理或刷新。
期望：
- 生效值应为 C；若删除链内该字段，则回退至 B；若再无 B，则回退至 A。

---

## 6. 快速人工检查清单（Smoke Checklist）
- 插件列表加载正确；命名空间显示正确。
- 拖拽链顺序后，链文件 `plugins.order` 即时更新。
- 从 Available Plugins 修改 → 写入 `data/configs/plugins/...`。
- 从 Plugin Chain 修改 → 写入当前链文件的 `plugin_configs`。
- Reset Defaults 使用 plugin.json 的默认值。
- Export Chain 为“全量保存”，仅包含使用到的插件配置。
- Import Chain 正确替换链和配置并写盘。
- Import/Export Config 仅包含链引用，不嵌入具体插件配置。
- Restore Last 恢复至启动快照对应的链和内容，并写回链文件。
- 退出后存在/更新 `config_latest.toml` 与 `chain_latest.toml`。

---

## 7. 可选：自动化测试思路
- 使用 pytest 标记 GUI/E2E 测试，配合一个临时 `data/configs` 测试夹具（创建临时目录并在测试前后切换工作目录）。
- 核心断言：
  - 文件是否创建/更新；内容键名是否为完整插件名节。
  - `plugins.order` 与链文件的 `plugin_configs` 是否匹配 UI 操作。
  - 配置优先级是否按预期生效。
  - Restore Last 是否恢复并写回链文件。

示例断言片段（TOML 结构，伪代码）：
```python
# 读取 TOML 后断言
assert toml_data["plugins"]["order"] == [
    "builtin/punctuation_adder",
    "builtin/sentence_splitter",
]
assert "plugin_configs" in toml_data
assert "builtin/sentence_splitter" in toml_data["plugin_configs"]
assert toml_data["plugin_configs"]["builtin/sentence_splitter"]["min_recursive_length"] == 80
```

---

参考：
- `docs/plan/configuration_management_design.md`
- 插件 `plugin.json` 的 `config_schema.properties.default`
- 内置默认：`src/subtitleformatter/config/default_config.toml`、`default_plugin_chain.toml`
