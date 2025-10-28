## Right Panel Refactor Plan: Four-way Vertical Splitter with Processing Flow

### Goal
Refactor the new GUI (MainWindowV2) right side into a vertical 4-pane splitter:
1) Tabs (Basic, Advanced, About)
2) Processing Flow (existing visual flow preserved)
3) Command Panel (Format + Progress only; remove Restore/Import/Export here)
4) Log Panel

Replace the current FileProcessingPanel usage by extracting its “Processing Flow” and integrating with the new configuration system. Preserve existing visual flow and plugin-chain visualization behavior.

### Scope
- In-scope:
  - Layout changes in MainWindowV2 right panel to a 4-way vertical splitter.
  - Introduce tabs reused from legacy MainWindow where feasible.
  - Extract and embed Processing Flow component (and/or PluginChainVisualizer) as dedicated pane.
  - Trim Command Panel features to only Format button and Progress bar.
  - Wire new configuration system into processing start.
- Out-of-scope:
  - Functional changes to plugin execution semantics.
  - Rewriting the legacy configuration manager; use adapters where needed.
  - The old GUI (MainWindow) can be left as-is; breakage is acceptable per decision.

### Desired Layout (Right Side)
- QSplitter(Qt.Vertical)
  - Pane 1: Tabs (Basic, Advanced, About)
  - Pane 2: Processing Flow (PluginChainVisualizer + possible controls)
  - Pane 3: Command Panel (Format button + Progress bar only)
  - Pane 4: Log Panel

### Components and Ownership
- Tabs: reuse `pages/basic_page.py`, `pages/advanced_page.py`, `pages/about_page.py` within MainWindowV2. Style via existing ThemeLoader.
- Processing Flow: extract from current new-GUI design:
  - Prefer using `PluginChainVisualizer` as the core visualization widget.
  - If FileProcessingPanel contains auxiliary logic (signals, helpers), move those to a neutral controller or keep in MainWindowV2 as orchestration.
- Command Panel (trimmed):
  - Reuse `components/command_panel.py` but hide/remove Restore/Import/Export controls.
  - Keep Format button, Progress bar, progress text.
  - Option A: create `MinimalCommandPanel` subclass.
  - Option B: parametrize `CommandPanel` with feature flags and disable unneeded controls.
- Log Panel: already present in new GUI; keep as Pane 4.

### Configuration Integration Strategy
- New GUI uses `ConfigCoordinator` and unified config managers.
- Legacy MainWindow used `ConfigManager` (user config). We will:
  - Continue using new unified configuration for runtime.
  - On Format click, materialize a single runtime config by merging:
    - Unified file processing settings from new system.
    - Plugin-chain configuration from new system.
  - Do not call legacy `ConfigManager` from V2. If tabs require reading/writing settings, route through `ConfigCoordinator` where reasonable, or use read-only bindings and persist via V2 managers.

### Event Flow (Runtime)
1) User edits config via Configuration Management and Plugin Management.
2) Plugin chain changes → `on_plugin_chain_changed` → update Processing Flow visualizer.
3) User clicks Format in trimmed Command Panel.
4) MainWindowV2 builds `full_config`:
   - `file_processing = self.file_processing.get_processing_config()` is replaced by coordinator-backed getters or equivalent.
   - `plugin_config = self.plugin_management.get_plugin_chain_config()` remains.
   - Merge into `full_config`.
5) Spawn processing thread, connect progress/log signals to Command Panel and Log Panel.

### API Contracts and Adapter Work
- Tabs
  - Keep their APIs; if they require save/restore, map to `ConfigCoordinator`.
- Processing Flow
  - Provide `update_plugin_chain(plugin_order, plugin_metadata)` API (already in visualizer).
  - If the visualizer needs config, inject via setter rather than creating inside the panel.
- Command Panel (trimmed)
  - Expose `formatRequested` signal.
  - Expose `set_progress(int)` and possibly `set_busy(bool)`.
  - Hide/disable Restore/Import/Export controls, or omit creation entirely behind a flag.

### Migration Steps
1) Create right-side vertical splitter with 4 panes in `MainWindowV2.create_right_panel`.
2) Pane 1: embed Tabs (reuse pages). Wire minimal signals as needed.
3) Pane 2: embed Processing Flow
   - Instantiate `PluginChainVisualizer` (or extracted widget) with `self` as parent.
   - Remove `file_processing.set_plugin_chain_visualizer(...)` dependency.
   - Ensure `on_plugin_chain_changed` targets the new visualizer widget.
4) Pane 3: trimmed Command Panel
   - Option A: Feature-flag `CommandPanel` to hide extra buttons; or
   - Option B: Introduce `MinimalCommandPanel` in `components/` reusing internal pieces.
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

### Testing Plan
- Manual
  - Resize behavior of each pane in 4-way splitter.
  - Drag plugin order and observe Processing Flow updates.
  - Start processing; verify progress and logs flow correctly.
  - Change logging level; ensure log panel and runtime logger sync.
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

### Open Questions
- Should Tabs in V2 write directly via `ConfigCoordinator`, or act as read-only helpers?
- Do we need a dedicated controller class for Processing Flow to prepare metadata or is MainWindowV2 sufficient?

### Next Steps (after plan approval)
1) Implement the 4-way splitter and embed placeholders for panes.
2) Extract and wire Processing Flow visualizer.
3) Introduce trimmed Command Panel (flag or subclass) and wire signals.
4) Replace config reads with coordinator-based materialization.
5) Smoke-test and adjust sizes/stretch factors.


