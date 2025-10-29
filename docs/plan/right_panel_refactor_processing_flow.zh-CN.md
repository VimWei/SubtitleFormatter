## 右侧面板重构计划：包含处理流程的纵向四段分割布局

### 目标
从旧版 MainWindow 整体中提取有价值的部分，集成到 MainWindowV2 的右侧，构建统一的应用程序。右侧面板将采用纵向四段分割器（QSplitter）：
1) 选项卡（Basic、Advanced、About）- 来自旧版
2) Processing Flow（可视化插件链执行）- **保留当前 V2 的**
3) 命令面板（仅保留 Format 按钮和进度条；移除 Restore/Import/Export）- 来自旧版
4) 日志面板（V2 已有）- **保留当前 V2 的**

**核心原则**：旧版 MainWindow 将被完全替换。今后只维护 V2 版本。从旧版 GUI 摘取有价值的组件（Tabs、Command Panel、Log Panel 等）保留并整合到新版右侧，而非通过包装器适配。**清空当前 V2 右侧面板，仅保留 Processing Flow 和日志面板。**

### 背景：为什么要重构？
- **旧版 GUI 的问题**：核心处理逻辑（text_cleaning、sentence_splitting、filler_handling、line_breaking）是硬编码的，灵活性不足。
- **新版 GUI 的解决方案**：基于插件的架构取代旧版核心处理逻辑。
- **需要保留的内容**：旧版 GUI 的右侧面板（选项卡、命令控件、日志）及其配置处理机制运行良好，应该保留。
- **新增加的内容**：V2 GUI 的左侧（插件管理、配置管理）取代了旧版的核心部分。

### 范围
- **范围内**：
  - 从旧版 MainWindow 整体中提取组件（Tabs、Command Panel 等）迁移到 MainWindowV2 的右侧。
  - 使用单一、统一的配置系统（ConfigCoordinator）贯穿整个应用。
  - 将插件链可视化集成为右侧面板的独立面板。
  - 所有组件的配置读写都通过 ConfigCoordinator 进行。
- **范围外**：
  - 不使用适配层或双重配置系统。
  - 旧版 MainWindow 将在迁移完成后被弃用并移除。
  - 不改变插件执行语义层面的功能。

### 期望布局（右侧）
- QSplitter(Qt.Vertical)
  - 面板1：Tabs（Basic、Advanced、About）
  - 面板2：Processing Flow（PluginChainVisualizer + 可能的控制）
  - 面板3：Command Panel（仅 Format 按钮 + 进度条）
  - 面板4：Log Panel

### 组件与归属
- Tabs：在 MainWindowV2 中复用 `pages/basic_page.py`、`pages/advanced_page.py`、`pages/about_page.py`，样式沿用 ThemeLoader。
  - Advanced：移除 "Restore Default"，该能力由新版的 Configuration Management 统一提供，避免功能重复。
  - Basic：删除与旧版 spaCy 相关的参数项（如语言、模型大小、最大宽度等）。
- Processing Flow：从当前新 GUI 设计中提取：
  - 优先使用 `PluginChainVisualizer` 作为核心可视化组件。
  - 若 FileProcessingPanel 中含有辅助逻辑（信号、工具方法），迁移到中立的控制器，或保留在 MainWindowV2 中由其编排。
- 命令面板：
  - 基于 `components/command_panel.py`，直接删除 Restore/Import/Export 控件。
  - 仅保留 Format 按钮、进度条、进度文本。
- 日志面板：新 GUI 已存在，作为第四段保持不变。

### 配置整合策略
- **单一统一系统**：在整个应用中只使用 `ConfigCoordinator` 作为后端配置管理。
- **分散的前端配置界面**：
  - **Configuration Management Panel**：负责配置文件的导入/导出/恢复（Restore Last、Restore Default、Import、Export）
  - **Tabs（Basic/Advanced）**：负责基础处理参数设置（例如输入/输出文件等）
  - **Command Panel**：负责执行处理（Format 按钮 + Progress）
  - **Plugin Management Panel**：负责插件链的构建和管理
  - **Plugin Config Panel**：负责单个插件的参数调优
- **迁移方法**：
  - 评估旧版 `ConfigManager`（旧 MainWindow 使用）的功能，将有用部分整合到 ConfigCoordinator 中。
  - 所有需要读写配置的组件都将直接使用 ConfigCoordinator 的 API，不通过适配器。
  - 当点击 Format 时，通过以下方式生成运行时配置：
    - 从 ConfigCoordinator 获取文件处理设置
    - 从 PluginManagementPanel 获取插件链配置
    - 合并为单一运行时配置，传入处理线程

### 事件流（运行时）
1) 用户通过 Configuration Management 与 Plugin Management 修改配置。
2) 插件链变更 → `on_plugin_chain_changed` → 更新 Processing Flow 可视化。
3) 用户在精简命令面板中点击 Format。
4) MainWindowV2 构建 `full_config`：
   - `file_processing = self.file_processing.get_processing_config()` 改为通过协调器（或等价 getter）获取；
   - `plugin_config = self.plugin_management.get_plugin_chain_config()` 保持不变；
   - 将二者合并为 `full_config`。
5) 启动处理线程，连接进度/日志信号到命令面板与日志面板。
   - 说明：Format 使用 `ConfigCoordinator` 的内存快照作为运行时配置传入处理线程，此步骤不执行写盘。

### 进度与状态模型（面向插件链）
- 进度来源：处理线程发出带插件上下文的信号（计划新增）：
  - `pluginStarted(name: str, index: int, total: int)`
  - `pluginProgress(name: str, percent: int, message: str)`（每插件细粒度进度，可选）
  - `pluginFinished(name: str, success: bool)`
- 命令面板聚合策略：
  - 总体百分比：在插件开始前为 floor((index − 1) / total * 100)；插件执行中按该插件的 `percent` 以 1/total 权重线性插值。
  - 进度文本显示：`[{index}/{total}] <display_name> — <message>`。
- 边界情况：
  - 跳过插件：视为瞬时完成 1/total 的增量。
  - 失败：停留在当前百分比，显示错误，并允许重试。
  - total 动态变化（运行时新增/移除插件）：即时重算权重并平滑更新 UI。
- 日志联动：所有插件生命周期消息同步输出到日志面板，便于追踪。

### API 契约与适配工作
- Tabs
  - 保持其现有 API；保存/恢复映射到 `ConfigCoordinator`。
- Processing Flow
  - 提供 `update_plugin_chain(plugin_order, plugin_metadata)`（可视化组件已具备）。
- 命令面板
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
4) 面板3：嵌入 命令面板
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
 - 注：配置并发修改不在本系统中出现。
   - 说明：各配置域采用单一面板负责的单一所有权设计（Single Ownership），彼此不重叠；所有写入均经由 `ConfigCoordinator`，因此无需冲突解决与复杂的变更广播，仅需按需触发 UI 刷新。

### 测试计划
- 手动
  - 检查四段分割器中各面板的缩放行为。
  - 调整插件顺序，观察 Processing Flow 实时更新。
  - 运行处理，验证进度与日志的联动。
  - 切换日志级别，确认日志面板与运行时 logger 同步。
  - 验证 Format 时不写盘：仅读取内存快照；关闭窗口或显式保存时再串行持久化。
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

### 已确定事项
- V2 中的 Tabs 将直接通过 `ConfigCoordinator` 写入（非只读）。
- Processing Flow 暂不引入独立控制器，由 MainWindowV2 负责编排即可。

### 下一步（获得计划批准后）
1) 实现四段分割器并嵌入占位组件。
2) 提取并接线 Processing Flow 可视化组件。
3) 引入精简命令面板（特性开关或子类）并连线信号。
4) 用协调器路径替换配置读取与合成。
5) 进行冒烟测试并微调尺寸/拉伸因子。


