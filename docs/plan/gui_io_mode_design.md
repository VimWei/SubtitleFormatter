# GUI 输入/输出模式重构设计与实施

## 📋 概述

本文档描述将现有"单输入文件 → 单输出文件"的固定模型，升级为"多模式输入 + 目录/文件输出 + 插件自定义产物"的方案，兼容以下场景：
- 输入一个，输出多个（如 `.srt`、`.txt`，插件自行决定文件名）
- 输入多个，输出一个（合并方式由插件实现决定）
- 输入多个，输出多个（输出为目录，插件自行决定每个文件的名称和格式）

**目标**：在不破坏现有体验的前提下，提供可扩展、清晰、可验证的配置与 GUI 交互。

**核心理解**：
- **GUI IO MODE 只是 I/O 配置层的扩展**：不改变插件接口和执行语义
- **插件仍然是标准文本处理插件**：所有插件遵循 `TextProcessorPlugin` 接口
- **执行层需要适配新 I/O 模式**：根据 `output_mode` 调整文件读写逻辑

---

## 🎯 实施状态

### 已完成 ✅
1. ✅ BasicPage UI 改造（模式切换、文件对话框、多文件列表）
2. ✅ 插件 transcript_converter 实现（符合标准插件接口）
3. ✅ BasicPage 配置读写（支持新字段，向后兼容）
4. ✅ ConfigCoordinator 支持新 I/O 字段（读取和保存）
5. ✅ config_materializer 适配新 I/O 配置（支持 input_mode、output_mode）
6. ✅ PluginTextProcessor 支持输出目录模式（统一时间戳处理）
7. ✅ 移除 filename_pattern 字段（简化 UI）
8. ✅ 统一时间戳处理（由平台层统一处理，插件只返回基础文件名）
9. ✅ GUI 输入模式扩展（Files/Directory+Glob UI已实现）

### 待完成 🔲
1. 🔲 输入模式运行时支持：多文件输入和目录+Glob 的批量处理逻辑

**说明**：合并策略、并行处理等高级功能应由插件自行实现，不属于平台层职责。

---

## 1. 数据模型（向后兼容）

### 保留旧字段
- `input_file: str`
- `output_file: str`
- `add_timestamp: bool`

### 新增字段（缺省时从旧字段推导，保证向后兼容）
- `input_mode: "file" | "files" | "directory"`
- `input_paths: list[str]`（`file`/`files` 模式使用）
- `input_dir: str`（`directory` 模式使用）
- `input_glob: str | null`（`directory` 模式使用，如 `*.srt` 或 `**/*.srt`）
- `output_mode: "file" | "directory"`
- `output_path: str`（文件或目录路径）

### 时间戳格式（统一使用前缀）
- File 模式：`{timestamp}-{filename}.ext`（如 `20240101120000-sample.txt`）
- Directory 模式：同样使用前缀格式 `{timestamp}-{filename}.ext`
- **重要**：时间戳由平台层统一处理，插件只返回基础文件名（不含时间戳）

### 默认推导规则
- 若仅存在旧字段：视为 `input_mode = file`、`output_mode = file`，其余字段用默认值
- 一旦用户使用新 UI，保存为新字段；运行时优先读取新字段

---

## 2. GUI/交互改造

**页面**：`src/subtitleformatter/gui/pages/basic_page.py`

### 新增与调整
- **输入模式下拉**：`File / Files / Directory+Glob`
  - File：保留现有 `QLineEdit + Browse...`
  - Files：`QListWidget` 展示选中文件列表 + 按钮"Add files…/Remove"
  - Directory+Glob：目录选择器 + `QLineEdit` 输入 `glob`（默认 `*.srt`）
- **输出模式下拉**：`File / Directory`
  - File：保留现有"输出文件"选择
  - Directory：目录选择器（插件在目录内自行决定输出文件名和格式）
- **条件控件**：
  - "添加时间戳"在两种模式下均可用；统一使用前缀格式 `{timestamp}-{filename}.ext`
  - 插件选项面板：已存在，支持插件暴露自定义配置项

### 展现方式
- 使用 `QComboBox` + `QStackedWidget` 进行子表单切换，切换时仅展示相关控件
- 禁用/启用与校验：根据当前模式控制输入可用性与必填校验

---

## 3. 插件契约

### 标准插件接口
所有插件遵循 `TextProcessorPlugin` 标准接口：
- **输入**：可以是文本（`str`/`list`）或文件路径（`str`）
- **输出**：可以是文本（`str`/`list`）或文件路径列表（`list`）

### transcript_converter 插件示例
```python
class TranscriptConverterPlugin(TextProcessorPlugin):
    def get_input_type(self) -> type:
        return str  # 接收文件路径字符串
    
    def get_output_type(self) -> type:
        return list  # 返回文件路径列表
    
    def process(self, input_data: str) -> list:
        """
        处理 .transcript 文件，生成 .srt 和 .txt 文件。
        
        Args:
            input_data: 输入文件路径（字符串）
            
        Returns:
            生成的文件路径列表（基础文件名，不含时间戳）
        """
        # 插件只返回基础文件名（如 sample.srt, sample.txt）
        # 时间戳由平台层统一处理
        ...
```

### 要点
- GUI/配置层提供 `input_file` 与 `output_dir`（通过 `plugin.config["_output_dir"]` 注入）
- 插件在 `output_dir` 内产出多个文件，命名与数量由插件定义
- **插件只返回基础文件名（不含时间戳）**，时间戳由平台层统一处理（与 file mode 一致）
- 文件写入默认覆盖已存在的文件

---

## 4. 运行时决策流

```python
# 解析输入源
sources = resolve_sources(input_mode, input_paths, input_glob)

if output_mode == "file":
    # 多入 -> 单文件
    # 合并方式完全由插件实现决定（平台层不强制任何策略）
    result = plugin.process(sources, output_path)
else:
    # 输出到目录
    if plugin.get_output_type() == list:
        # 交由插件在目录内写出多个产物
        results = plugin.process(input_file, output_dir)
        # 平台层统一处理时间戳（重命名文件）
        if add_timestamp:
            results = add_timestamp_prefix(results, timestamp_value)
    else:
        # 一对一/多对多：传统文本处理流程
        for idx, src in enumerate(sources, 1):
            process_one_to_one(src, output_dir)
```

---

## 5. 关键技术实现

### 5.1 插件如何获取输出目录？
**方案**：通过执行层注入到 `plugin.config`
```python
# 在 PluginTextProcessor.process() 中
for plugin in self.loaded_plugins:
    if plugin.get_output_type() == list:  # 可能生成多文件的插件
        plugin.config["_output_dir"] = output_dir
        # 不注入时间戳，由平台层统一处理
```

### 5.2 平台层时间戳处理
**位置**：`src/subtitleformatter/processors/plugin_text_processor.py`

```python
# 插件返回文件路径列表后，平台层统一处理时间戳
if add_timestamp and timestamp_value and artifacts:
    from pathlib import Path
    timestamped_artifacts = []
    for artifact_path in artifacts:
        artifact = Path(artifact_path)
        # 添加时间戳前缀（如果未存在）
        if not artifact.name.startswith(timestamp_value + "-"):
            timestamped_name = f"{timestamp_value}-{artifact.name}"
            timestamped_path = artifact.parent / timestamped_name
            # 重命名文件
            artifact.rename(timestamped_path)
            timestamped_artifacts.append(str(timestamped_path))
        else:
            timestamped_artifacts.append(artifact_path)
    artifacts = timestamped_artifacts
```

### 5.3 如何保持向后兼容？
**方案**：
- 配置读取：优先读取新字段，无则读取旧字段
- 执行流程：检测 `output_mode`，传统模式走旧流程，目录模式走新流程
- 插件配置：传统插件不受影响，新插件自动获取输出目录信息

---

## 6. 校验与错误处理

- **模式校验**：
  - `File` 必须选择单一文件
  - `Files` 至少包含一个文件
  - `Directory+Glob` 必须选择目录，`glob` 合法
  - `output_mode = file` 时必须选择文件路径；`directory` 时必须选择目录
- **路径与权限校验**：输入存在、输出目录可写
- **文件写入**：默认覆盖已存在的文件
- **运行失败**：标准化异常消息并在 GUI 提示，附带日志落盘

---

## 7. 向后兼容策略

- **加载配置时**：若无新字段，按旧模型填充 UI（`file` → `file`）
- **保存配置时**：当用户未触达新控件，仅保存旧字段；当用户使用新模式，保存新增字段（保留旧字段以兼容老版本）
- **运行时**：优先读取新字段；旧字段仅作为默认回退

---

## 8. 实施计划

### 阶段 A（已完成 ✅）- 最小可用版本
- ✅ 数据模型扩展（读/写配置，含默认推导）
- ✅ GUI 增加 `Output=Directory`，支持单入多出（插件产物）
- ✅ 将 `transcript_converter` 以插件形式接入（单入 → 目录内多文件）
- ✅ 统一时间戳格式：File 和 Directory 模式均使用前缀格式 `{timestamp}-{filename}.ext`
- ✅ 平台层统一处理时间戳（插件只返回基础文件名）

### 阶段 B（已完成 ✅）
- ✅ GUI 增加 `Input=Files/Directory+Glob`（UI已实现，支持三种输入模式）


---

## 9. 验收标准

1. **BasicPage UI 功能正常**：
   - ✅ 模式切换正常
   - ✅ 文件/目录选择正常
   - ✅ 多文件列表添加/删除正常
   - ✅ 配置保存/加载正常

2. **配置系统支持新字段**：
   - ✅ ConfigCoordinator 正确读写新字段
   - ✅ 向后兼容：旧配置仍可正常使用
   - ✅ 配置持久化到 TOML 文件

3. **执行层支持目录输出**：
   - ✅ `output_mode == "directory"` 时，插件能在目录中生成文件
   - ✅ `transcript_converter` 插件能正常生成 .srt/.txt
   - ✅ 文件路径正确返回并在日志中显示
   - ✅ 时间戳由平台层统一处理，文件名格式正确

4. **向后兼容性**：
   - ✅ 旧配置（只有 input_file/output_file）仍能正常工作
   - ✅ 新旧配置混合使用不冲突

---

## 10. 风险与缓解

- **模式切换后的状态一致性**：通过 `QStackedWidget` 与集中 `load/save` 逻辑保证
- **旧配置与新配置混用**：采用"新优先、旧回退"的读取策略，并在 UI 上提示当前实际生效的模式
- **文件名生成**：由插件决定输出文件名和格式，时间戳由执行层统一注入（前缀格式）
- **插件职责清晰**：插件只处理业务逻辑，平台层统一处理文件命名策略（时间戳等）

---

## 11. 成功判据

- ✅ 三类场景均可通过 GUI 配置与一次执行完成（部分场景已实现）
- ✅ 老项目无需修改即可运行；新项目可启用新模式
- ✅ `transcript_converter` 插件在选择目录输出后，稳定产出 `.srt/.txt` 并被 UI 正确显示
- ✅ 时间戳格式统一，与 file mode 保持一致

---

## 📅 实施顺序（已完成部分）

1. ✅ **阶段 1**：配置层扩展（ConfigCoordinator + UnifiedConfigManager）
2. ✅ **阶段 2**：config_materializer 适配
3. ✅ **阶段 3**：PluginTextProcessor 输出目录模式支持
4. ✅ **阶段 4**：输入模式UI扩展（多文件、目录+glob的UI已实现）
5. 🔲 **阶段 5**：输入模式运行时支持（批量处理逻辑）

**架构原则**：合并策略、并行处理等高级功能应由插件自行实现，平台层只负责I/O配置和路径解析，不强制任何处理策略。

---

## 🚨 注意事项

1. **不修改插件接口**：所有插件保持 `TextProcessorPlugin` 标准接口
2. **执行层适配**：只在执行层检测 `output_mode` 并调整处理逻辑
3. **向后兼容**：始终支持旧配置格式
4. **配置优先级**：新字段优先，旧字段作为回退
5. **时间戳处理**：统一由平台层处理，插件只返回基础文件名

