## Right Panel Refactor Plan: Four-way Vertical Splitter with Processing Flow

### Goal
Extract valuable components from the legacy MainWindow and integrate them into MainWindowV2's right side, creating a unified application. The right panel will have a vertical 4-pane splitter:
1) Tabs (Basic, Advanced, About) - from legacy
2) Processing Flow (visualize plugin chain execution) - **retained from current V2**
3) Command Panel (Format + Progress only; remove Restore/Import/Export here) - from legacy
4) Log Panel (already in V2) - **retained from current V2**

**Key principle**: Legacy MainWindow will be completely replaced. Only maintain V2 going forward. Extract valuable components from the old GUI (Tabs, Command Panel, Log Panel, etc.) and integrate them into V2's right panel, not via wrappers. **Clear out current V2 right panel except Processing Flow and Log Panel.**

### Context: Why This Refactor?
- **Old GUI problem**: Core processing (text_cleaning, sentence_splitting, filler_handling, line_breaking) was hardcoded and inflexible.
- **New GUI solution**: Plugin-based architecture replaces the old core processing.
- **What to preserve**: Legacy GUI's right panel (tabs, command controls, logs) and its configuration handling works well and should be kept.
- **What's new**: The left side of V2 GUI (plugin management, configuration management) replaces the old core.

### Scope
- **In-scope**:
  - Extract components (Tabs, Command Panel, etc.) from legacy MainWindow and migrate them to MainWindowV2's right panel.
  - Use a single, unified configuration system (ConfigCoordinator) for the entire application.
  - Integrate plugin-chain visualization as a dedicated pane in the right panel.
  - Wire configuration reading/writing through ConfigCoordinator for all components.
- **Out-of-scope**:
  - No adapter layers or dual configuration systems.
  - Legacy MainWindow will be deprecated and removed after migration completes.
  - Do not change plugin execution semantics.

### Desired Layout (Right Side)
- QSplitter(Qt.Vertical)
  - Pane 1: Tabs (Basic, Advanced, About)
  - Pane 2: Processing Flow (PluginChainVisualizer + possible controls)
  - Pane 3: Command Panel (Format button + Progress bar only)
  - Pane 4: Log Panel

### Components and Ownership
- Tabs: reuse `pages/basic_page.py`, `pages/advanced_page.py`, `pages/about_page.py` within MainWindowV2. Style via existing ThemeLoader.
  - Advanced: remove "Restore Default" (handled centrally by Configuration Management to avoid duplication).
  - Basic: remove legacy spaCy-related settings (language, model size, max width).
- Processing Flow: extract from current new-GUI design:
  - Prefer using `PluginChainVisualizer` as the core visualization widget.
  - If FileProcessingPanel contains auxiliary logic (signals, helpers), move those to a neutral controller or keep in MainWindowV2 as orchestration.
- Command Panel:
  - Based on `components/command_panel.py`, delete Restore/Import/Export controls (not hidden).
  - Keep only the Format button, Progress bar, and progress text.
- Log Panel: already present in new GUI; keep as Pane 4.

### Configuration Integration Strategy
- **Single unified backend**: Use `ConfigCoordinator` exclusively as the backend configuration management system.
- **Distributed frontend configuration interfaces**:
  - **Configuration Management Panel**: Handles config file import/export/restore (Restore Last, Restore Default, Import, Export)
  - **Tabs (Basic/Advanced)**: Handles basic processing parameter settings (e.g., input/output files)
  - **Command Panel**: Handles processing execution (Format button + Progress)
  - **Plugin Management Panel**: Handles plugin chain construction and management
  - **Plugin Config Panel**: Handles individual plugin parameter tuning
- **Migration approach**: 
  - Evaluate legacy `ConfigManager` (used in old MainWindow) functionality and integrate useful parts into ConfigCoordinator where needed.
  - All components that need to read/write settings will use ConfigCoordinator APIs directly, not through adapters.
  - When Format is clicked, materialize runtime config by:
    - Getting file processing settings from ConfigCoordinator
    - Getting plugin-chain configuration from PluginManagementPanel
    - Merging into single runtime config for processing thread

### Event Flow (Runtime)
1) User edits config via Configuration Management and Plugin Management.
2) Plugin chain changes → `on_plugin_chain_changed` → update Processing Flow visualizer.
3) User clicks Format in the Command Panel.
4) MainWindowV2 builds `full_config`:
   - `file_processing = self.file_processing.get_processing_config()` is replaced by coordinator-backed getters or equivalent.
   - `plugin_config = self.plugin_management.get_plugin_chain_config()` remains.
   - Merge into `full_config`.
5) Spawn processing thread, connect progress/log signals to Command Panel and Log Panel.
   - Note: Format uses an in-memory snapshot from `ConfigCoordinator` as the runtime config; this step does not write to disk.

### Progress and Status Model (Plugin-chain aware)
- Progress source: processing thread emits plugin-aware signals (to be implemented):
  - `pluginStarted(name: str, index: int, total: int)`
  - `pluginProgress(name: str, percent: int, message: str)` (optional granular updates per plugin)
  - `pluginFinished(name: str, success: bool)`
- Command Panel aggregation:
  - Overall percent = floor((index − 1) / total * 100) before a plugin starts; during a plugin, interpolate using its `percent` with weight 1/total.
  - Progress text shows: `[{index}/{total}] <display_name> — <message>`.
- Edge cases:
  - If a plugin is skipped, treat as instant 1/total increment.
  - On failure, stop at current percent, show error, and allow retry.
  - If total is dynamic (plugins added/removed at runtime), recompute weights on the fly and update UI safely.
- Logging integration: all plugin lifecycle messages are mirrored to Log Panel for traceability.

### API Contracts and Adapter Work
- Tabs
  - Keep their APIs; if they require save/restore, map to `ConfigCoordinator`.
- Processing Flow
  - Provide `update_plugin_chain(plugin_order, plugin_metadata)` API (already in visualizer).
- Command Panel
  - Expose `formatRequested` signal.
  - Expose `set_progress(int)` and possibly `set_busy(bool)`.
  - Delete Restore/Import/Export controls (not hidden, no feature flags).

### Migration Steps
1) Create right-side vertical splitter with 4 panes in `MainWindowV2.create_right_panel`.
2) Pane 1: embed Tabs (reuse pages). Wire minimal signals as needed.
3) Pane 2: embed Processing Flow
   - Instantiate `PluginChainVisualizer` (or extracted widget) with `self` as parent.
   - Remove `file_processing.set_plugin_chain_visualizer(...)` dependency.
   - Ensure `on_plugin_chain_changed` targets the new visualizer widget.
4) Pane 3: Command Panel
   - Wire `formatRequested` → `on_format_requested` (existing V2 handler adapted to no FileProcessingPanel).
   - Wire progress updates from processing thread to this panel.
5) Pane 4: keep Log Panel unchanged.
6) Remove/retire `FileProcessingPanel` usage from V2 (keep file but unused, or deprecate with TODO note in docs; do not delete yet).
7) Update configuration reads in V2 to use `ConfigCoordinator` exclusively where possible; avoid legacy `ConfigManager`.
8) Verify processing thread construction still uses plugin-based processor first, with legacy fallback unchanged.

### Risks and Mitigations
- Risk: Mixed config sources (legacy vs new) cause inconsistencies.
  - Mitigation: Single point of config materialization in V2 via `ConfigCoordinator` and `PluginManagementPanel` outputs.
- Risk: Coupling between visualizer and panel lifecycles.
  - Mitigation: Keep creation and injection in MainWindowV2; expose only setters/signals.
- Risk: Breakage of old GUI.
  - Mitigation: Acceptable per decision; old GUI is preserved in git.
 - Note: No concurrent edit risk by design.
   - Rationale: Each config domain has a single UI owner (single ownership); all writes go through `ConfigCoordinator`, so no conflict resolution or heavy change-broadcasting is required—only targeted UI refresh.

### Testing Plan
- Manual
  - Resize behavior of each pane in 4-way splitter.
  - Drag plugin order and observe Processing Flow updates.
  - Start processing; verify progress and logs flow correctly.
  - Change logging level; ensure log panel and runtime logger sync.
  - Verify that Format does not write to disk: it reads an in-memory snapshot; persistence occurs on window close or explicit save, serialized by `ConfigCoordinator`.
- Automated (smoke)
  - Unit test `on_plugin_chain_changed` updates visualizer without errors.
  - Unit test config materialization path for processing thread input.

### Acceptance Criteria
- Right panel shows 4 panes in order: Tabs, Processing Flow, Command Panel, Log Panel.
- Processing Flow visualizer reflects plugin chain changes.
- Command Panel shows Format button and Progress bar only; other config actions are removed from it.
- Clicking Format runs processing using the new unified config path; logs and progress update correctly.
- No reliance on `FileProcessingPanel` in V2 runtime.

### Rollback Strategy
- Revert to prior commit where V2 used two-pane right splitter with FileProcessingPanel.
- Keep `FileProcessingPanel` code intact until refactor stabilizes.

### Decisions
- Tabs in V2 will write directly via `ConfigCoordinator` (not read-only).
- No separate controller for Processing Flow for now; MainWindowV2 is sufficient.

### Next Steps (after plan approval)
1) Implement the 4-way splitter and embed placeholders for panes.
2) Extract and wire Processing Flow visualizer.
3) Introduce trimmed Command Panel (flag or subclass) and wire signals.
4) Replace config reads with coordinator-based materialization.
5) Smoke-test and adjust sizes/stretch factors.


