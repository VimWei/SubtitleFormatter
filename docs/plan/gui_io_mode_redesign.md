## GUI 输入/输出模式重构计划（Draft）

本文档梳理将现有“单输入文件 → 单输出文件”的固定模型，升级为“多模式输入 + 目录/文件输出 + 插件自定义产物”的方案，兼容以下场景：
- 输入一个，输出多个（如 `.srt`、`.txt`、未来 `.json`）
- 输入多个，输出一个（合并方式由插件选项决定）
- 输入多个，输出多个（输出为目录 + 文件名模板）

目标：在不破坏现有体验的前提下，提供可扩展、清晰、可验证的配置与 GUI 交互。

---

### 1. 数据模型（向后兼容）

保留旧字段：
- `input_file: str`
- `output_file: str`
- `add_timestamp: bool`

新增字段（缺省时从旧字段推导，保证向后兼容）：
- `input_mode: "file" | "files" | "directory"`
- `input_paths: list[str]`（`file`/`files` 模式使用）
- `input_glob: str | null`（`directory` 模式使用，如 `*.srt` 或 `**/*.srt`）
- `output_mode: "file" | "directory"`
- `output_path: str`（文件或目录路径）
- `filename_pattern: str | null`（当 `output_mode = directory` 时使用）
- `overwrite: bool`（覆盖策略）

模板变量（供 `filename_pattern` 使用）：
- `{input_dir}`, `{input_name}`, `{stem}`, `{ext}`, `{index}`, `{timestamp}`

默认推导规则：
- 若仅存在旧字段：视为 `input_mode = file`、`output_mode = file`，其余字段用默认值。
- 一旦用户使用新 UI，保存为新字段；运行时优先读取新字段。

---

### 2. GUI/交互改造（最小入侵升级）

页面：`src/subtitleformatter/gui/pages/basic_page.py`

新增与调整：
- 输入模式下拉：`File / Files / Directory+Glob`
  - File：保留现有 `QLineEdit + Browse...`
  - Files：`QListWidget` 展示选中文件列表 + 按钮“Add files…/Remove”
  - Directory+Glob：目录选择器 + `QLineEdit` 输入 `glob`（默认 `*.srt`）
- 输出模式下拉：`File / Directory`
  - File：保留现有“输出文件”选择
  - Directory：目录选择器 + “文件名模板”输入框（占位符提示变量集）
- 条件控件：
  - “添加时间戳”在两种模式下均可用；当 `Directory+模板` 时作为 `{timestamp}` 变量是否启用的开关
  - 插件自定义选项：当插件声明需要额外配置时，在此区域挂载其专属表单

展现方式：
- 使用 `QComboBox` + `QStackedWidget` 进行子表单切换，切换时仅展示相关控件
- 禁用/启用与校验：根据当前模式控制输入可用性与必填校验

---

### 3. 插件契约（以 `transcript_converter` 为例）

背景：`scripts/transcript_converter/transcript_converter.py` 将迁移为插件。该插件单输入，输出多文件（`.srt`、`.txt`、后续 `.json`）。

建议最小契约：
```python
class SubtitlePlugin:
    def run(self, input_file: Path, output_dir: Path, options: dict) -> list[str]:
        """执行转换，并返回写入的文件路径列表。"""
        ...
```

要点：
- GUI/配置层提供 `input_file` 与 `output_dir`，插件在 `output_dir` 内产出多个文件，命名与数量由插件定义
- 若 UI 提供 `filename_pattern`，插件可选择遵循（建议在文档中声明支持的变量集合）
- 提供可选 `dry_run/preview()` 以便 GUI 显示“预期输出概览”（非首版必需）
- 覆盖策略：支持 `overwrite` 或自动重命名（如追加 `(1)`）

---

### 4. 运行时决策流（伪代码）

```python
sources = resolve_sources(input_mode, input_paths, input_glob)
if output_mode == "file":
    # 多入 -> 单文件
    # 合并方式由插件实现及其选项决定（非核心模型职责）
    result = plugin.run_many_to_one(sources, output_path, options)
else:
    # 输出到目录
    if plugin_declares_multi_artifacts:
        # 交由插件在目录内写出多个产物
        results = plugin.run(single_or_first_source, output_dir, options)
    else:
        # 一对一/多对多：按模板生成目标文件路径
        for idx, src in enumerate(sources, 1):
            dst = render_pattern(output_path, filename_pattern, src, idx, timestamp=add_timestamp)
            process_one_to_one(src, dst)
```

---

### 5. 校验与错误处理

- 模式校验：
  - `File` 必须选择单一文件
  - `Files` 至少包含一个文件
  - `Directory+Glob` 必须选择目录，`glob` 合法
  - `output_mode = file` 时必须选择文件路径；`directory` 时必须选择目录
  - `directory` + `filename_pattern` 必须校验变量占位符合法
- 路径与权限校验：输入存在、输出目录可写
- 覆盖策略：按 `overwrite` 决策；否则提示冲突或采用重命名策略
- 运行失败：标准化异常消息并在 GUI 提示，附带日志落盘

---

### 6. 向后兼容策略

- 加载配置时：若无新字段，按旧模型填充 UI（`file` → `file`）
- 保存配置时：当用户未触达新控件，仅保存旧字段；当用户使用新模式，保存新增字段（保留旧字段以兼容老版本）
- 运行时优先读取新字段；旧字段仅作为默认回退

---

### 7. 渐进式实施计划

阶段 A（最小可用）：
- 数据模型扩展（读/写配置，含默认推导）
- GUI 增加 `Output=Directory` + `filename_pattern`，支持单入多出（插件产物）
- 将 `transcript_converter` 以插件形式接入（单入 → 目录内多文件）

阶段 B：
- GUI 增加 `Input=Files/Directory+Glob`
- 插件选项面板：支持插件暴露多入单出策略等自定义配置

阶段 C：
- Dry-run 预览与冲突处理（覆盖/重命名）
- 模板变量校验与高亮/提示
- 更丰富的合并策略与插件 API 能力（如并行处理）

---

### 8. 简要 UI 线框

- 输入模式（Combo）：`File | Files | Directory+Glob`
  - File：`[ QLineEdit ][ Browse ]`
  - Files：`[ QListWidget ] [ Add files… ] [ Remove ]`
  - Directory+Glob：`[ QLineEdit(dir) ][ Browse ]  Glob: [ *.srt ]`
- 输出模式（Combo）：`File | Directory`
  - File：`[ QLineEdit(file) ][ Browse ]`
  - Directory：`[ QLineEdit(dir) ][ Browse ]  Pattern: [ {stem}_{timestamp}{ext} ]`
- 其他：`[x] Add timestamp`、（条件出现）插件自定义选项占位区域

---

### 9. 风险与缓解

- 模式切换后的状态一致性：通过 `QStackedWidget` 与集中 `load/save` 逻辑保证
- 旧配置与新配置混用：采用“新优先、旧回退”的读取策略，并在 UI 上提示当前实际生效的模式
- 插件自由命名与用户模板冲突：在插件文档中明确约定遵循优先级（建议：若提供模板则优先模板）

---

### 10. 成功判据

- 三类场景均可通过 GUI 配置与一次执行完成
- 老项目无需修改即可运行；新项目可启用新模式
- `transcript_converter` 插件在选择目录输出后，稳定产出 `.srt/.txt`（后续 `.json`）并被 UI 正确显示


