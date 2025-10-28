## 右侧面板重构计划：包含处理流程的纵向四段分割布局

### 目标
将新 GUI（MainWindowV2）右侧改造为纵向四段分割器（QSplitter）：
1) 选项卡（Basic、Advanced、About）
2) Processing Flow（保留现有可视化流程）
3) 命令面板（仅保留 Format 按钮和进度条；移除 Restore/Import/Export）
4) 日志面板

用“提取 FileProcessingPanel 中的处理流程组件”的方式替换当前用法，并与新配置系统对接。保持现有可视化与插件链可视化行为不变。

### 范围
- 范围内：
  - 在 MainWindowV2 的右侧改造为四段纵向分割布局。
  - 在可行处复用旧版 MainWindow 的 Tabs。
  - 提取并嵌入 Processing Flow 组件（以及/或 PluginChainVisualizer）为独立面板。
  - 命令面板精简为仅 Format 按钮与进度条。
  - 将新配置系统接入处理启动流程。
- 范围外：
  - 不改变插件执行语义层面的功能。
  - 不重写旧版配置管理器；如需兼容，通过适配器处理。
  - 旧版 GUI（MainWindow）可保持不变；即使暂时受影响也可接受（仓库中留有历史）。

### 期望布局（右侧）
- QSplitter(Qt.Vertical)
  - 面板1：Tabs（Basic、Advanced、About）
  - 面板2：Processing Flow（PluginChainVisualizer + 可能的控制）
  - 面板3：Command Panel（仅 Format 按钮 + 进度条）
  - 面板4：Log Panel

### 组件与归属
- Tabs：在 MainWindowV2 中复用 `pages/basic_page.py`、`pages/advanced_page.py`、`pages/about_page.py`，样式沿用 ThemeLoader。
- Processing Flow：从当前新 GUI 设计中提取：
  - 优先使用 `PluginChainVisualizer` 作为核心可视化组件。
  - 若 FileProcessingPanel 中含有辅助逻辑（信号、工具方法），迁移到中立的控制器，或保留在 MainWindowV2 中由其编排。
- 命令面板（精简版）：
-  复用 `components/command_panel.py`，隐藏/移除 Restore/Import/Export 控件。
  - 保留 Format 按钮、进度条、进度文本。
  - 方案A：创建 `MinimalCommandPanel` 子类。
  - 方案B：为 `CommandPanel` 增加特性开关参数，禁用不需要的控件。
- 日志面板：新 GUI 已存在，作为第四段保持不变。

### 配置整合策略
- 新 GUI 使用 `ConfigCoordinator` 与统一配置管理器。
- 旧版 MainWindow 使用 `ConfigManager`（用户配置）。本次处理：
  - 运行时继续使用新统一配置。
  - 点击 Format 时，合成单一的运行时配置，合并：
    - 新系统中的文件处理相关设置；
    - 新系统中的插件链配置。
  - 在 V2 中不直接调用旧版 `ConfigManager`。若 Tabs 需要读写配置，尽量通过 `ConfigCoordinator` 转发；或在必要时仅做只读绑定，由 V2 管理器负责持久化。

### 事件流（运行时）
1) 用户通过 Configuration Management 与 Plugin Management 修改配置。
2) 插件链变更 → `on_plugin_chain_changed` → 更新 Processing Flow 可视化。
3) 用户在精简命令面板中点击 Format。
4) MainWindowV2 构建 `full_config`：
   - `file_processing = self.file_processing.get_processing_config()` 改为通过协调器（或等价 getter）获取；
   - `plugin_config = self.plugin_management.get_plugin_chain_config()` 保持不变；
   - 将二者合并为 `full_config`。
5) 启动处理线程，连接进度/日志信号到命令面板与日志面板。

### API 契约与适配工作
- Tabs
  - 保持其现有 API；如需保存/恢复，映射到 `ConfigCoordinator`。
- Processing Flow
  - 提供 `update_plugin_chain(plugin_order, plugin_metadata)`（可视化组件已具备）。
  - 如需要配置，采用注入式（setter）而非在面板内部创建依赖。
- 命令面板（精简）
  - 暴露 `formatRequested` 信号。
  - 暴露 `set_progress(int)` 与可选 `set_busy(bool)`。
  - 隐藏/禁用 Restore/Import/Export 控件，或通过特性开关根本不创建。

### 迁移步骤
1) 在 `MainWindowV2.create_right_panel` 中创建四段纵向分割器。
2) 面板1：嵌入 Tabs（复用 pages），按需连线最小必要信号。
3) 面板2：嵌入 Processing Flow
   - 以 `self` 为父创建 `PluginChainVisualizer`（或抽取后的组件）。
   - 移除 `file_processing.set_plugin_chain_visualizer(...)` 依赖。
   - 确保 `on_plugin_chain_changed` 指向新的可视化组件。
4) 面板3：精简命令面板
   - 方案A：为 `CommandPanel` 增加特性开关隐藏多余按钮；或
   - 方案B：新增 `MinimalCommandPanel`，复用现有内部组件。
   - 连接 `formatRequested` → `on_format_requested`（适配无 FileProcessingPanel 的 V2 版本）。
   - 将处理线程的进度更新连接到此面板。
5) 面板4：日志面板保持不变。
6) 在 V2 中移除/停用 `FileProcessingPanel` 的使用（代码暂保留或在文档中标记弃用，先不删除）。
7) 在 V2 中尽量只通过 `ConfigCoordinator` 读取配置；避免直接使用旧 `ConfigManager`。
8) 确认处理线程优先使用插件化处理器，旧版回退路径保持可用。

### 风险与缓解
- 风险：新旧配置来源混用导致不一致。
  - 缓解：在 V2 中统一由 `ConfigCoordinator` + `PluginManagementPanel` 输出构建运行时配置。
- 风险：可视化组件与面板生命周期耦合。
  - 缓解：在 MainWindowV2 创建并注入，仅暴露 setter/信号。
- 风险：旧 GUI 受影响。
  - 缓解：可接受；旧 GUI 在 git 中留存，可随时回滚。

### 测试计划
- 手动
  - 检查四段分割器中各面板的缩放行为。
  - 调整插件顺序，观察 Processing Flow 实时更新。
  - 运行处理，验证进度与日志的联动。
  - 切换日志级别，确认日志面板与运行时 logger 同步。
- 自动（冒烟）
  - 单测 `on_plugin_chain_changed` 能在无异常下更新可视化。
  - 单测运行时配置的构建路径（传入处理线程的配置）。

### 验收标准
- 右侧显示四段，顺序为：Tabs、Processing Flow、Command Panel、Log Panel。
- Processing Flow 可视化能反映插件链变更。
- 命令面板仅显示 Format 按钮与进度条；其他配置操作不再出现在此面板。
- 点击 Format 使用新统一配置路径执行处理；日志与进度正常更新。
- V2 运行时不再依赖 `FileProcessingPanel`。

### 回滚策略
- 回退到 V2 使用两段右侧分割（含 FileProcessingPanel）的前一版本提交。
- 在重构稳定前保留 `FileProcessingPanel` 代码。

### 未决问题
- V2 中的 Tabs 是否直接通过 `ConfigCoordinator` 写入，还是以只读辅助为主？
- Processing Flow 是否需要独立控制器来准备元数据，或由 MainWindowV2 即可满足？

### 下一步（获得计划批准后）
1) 实现四段分割器并嵌入占位组件。
2) 提取并接线 Processing Flow 可视化组件。
3) 引入精简命令面板（特性开关或子类）并连线信号。
4) 用协调器路径替换配置读取与合成。
5) 进行冒烟测试并微调尺寸/拉伸因子。


