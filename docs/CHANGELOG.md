# Changelog

## [1.4.1] - 2025-10-30

- refactor(gui): modularize panels and migrate debug settings to Advanced
- refactor(logging): update configuration loading log message for clarity
- refactor(logging): switch from info to debug logging in plugin visualizer and management panel
- refactor(logging): replace print statements with unified logging across the codebase
- Refactor: unify config schema, modernize DebugOutput, and remove legacy paths

## [1.4.0] - 2025-10-30

- refactor(sentence_splitter): ensure consistency by trimming trailing whitespace from split sentences
- fix(punctuation_adder): enhance dash replacement logic for numeric values
- refactor(punctuation_adder): enhance punctuation processing and sentence capitalization
- refactor(config): enhance runtime configuration materialization for plugin management
- refactor(gui): delegate plugin system initialization and configuration assembly to runtime layer
- refactor(gui): enhance MainWindowV2 with plugin system integration and processing improvements
- refactor(gui): streamline MainWindowV2 layout and enhance configuration handling
- fix(punctuation_adder): suppress deprecation warnings for grouped_entities in transformers

## [1.3.12] - 2025-10-30

- feat(tests): add comprehensive tests for plugin management and configuration handling
- refactor(config): improve configuration handling with deepcopy for state management
- doc(gui): implement right panel refactor with four-way vertical splitter
- refactor(gui): update layout and comments in MainWindowV2 for clarity
- refactor(punctuation_adder): remove model_name configuration and simplify logging
- feat(logging): implement dynamic logging level adjustment in GUI
- refactor(logging): normalize file paths in log messages for configuration management
- feat(gui): add dynamic title update for plugin chain management
- chore(gui, logging): show startup logs in Log panel and reduce verbosity
- refactor: Improve synchronization logic for unified plugin chain reference
- refactor: Remove redundant plugin configuration synchronization logic
- feat: Enhance snapshot management and configuration persistence
- feat: Enhance configuration management with immediate persistence and improved saving mechanisms
- feat: Introduce legacy GUI support and update main entry point
- docs: Enhance plugin development guide with DebugOutput system details
- docs: Update design documents to resolve conflicts and improve organization
- fix: Adopt plugin.json as single source of truth for plugin defaults
- feat: Implement working configuration management with snapshot protection
- fix: Correct plugin chain initialization and configuration storage
- feat: complete plugin configurations in default chain
- refactor: Update punctuation adder plugin configuration and logic
- refactor: Update button styles and font sizes in ConfigurationManagementPanel
- feat: Add keyboard navigation support for plugin selection in PluginManagementPanel
- refactor: Simplify PluginManagementPanel layout and enhance styling
- refactor: Adjust layout margins and button padding for improved UI consistency
- refactor: Standardize layout margins across GUI components
- refactor: Remove StatusBar integration from MainWindowV2
- refactor: Remove dialog boxes and add configurable log levels
- refactor: Removed unused `backup_current_config` method
- refactor: Update core module documentation and deprecate old functionality
- refactor: Simplify layout in FileProcessingPanel
- feat: Enhance PluginChainCanvas with bent arrow drawing
- fix: Align panels and optimize right panel layout
- feat: Enable auto-scaling for Configuration Management panel
- feat: Integrate Configuration Management Panel into Main Window
- feat: Enhance GUI components and configuration management
- feat: Enhance configuration management design document
- feat: Implement configuration management system

## [1.3.11] - 2025-10-27

- refactor: Rename button in PluginManagementPanel for clarity
- feat: Add configuration management design document
- fix: Correct cursor movement in LogPanel copy function
- chore: .vbs use test_gui_v2.py
- refactor: Remove unused configuration options from FileProcessingPanel
- fix: Update PluginConfigPanel to remove hardcoded group title

## [1.3.10] - 2025-10-26

- refactor: Enhance plugin registration with full namespacing
- feat: Add draft plugin-based GUI interface
- Refactor plugin scanning and fix examples/simple_uppercase

## [1.3.9] - 2025-10-26

- Update .gitignore to remove .coverage file from tests

## [1.3.8] - 2025-10-26

- feat: Complete Phase 3 pluginization of core components

## [1.3.7] - 2025-10-25

- feat: implement plugin interface and base class system
- feat(tests): add comprehensive performance, requirements clarification, and user scenarios tests for plugin system

## [1.3.6] - 2025-10-25

- feat: implement plugin infrastructure foundation

## [1.3.5] - 2025-10-25

- feat(docs): adopt platform-first refactor strategy with comprehensive planning
- feat(docs): add plugin GUI design document

## [1.3.4] - 2025-10-25

- feat(docs): introduce plugin architecture design document

## [1.3.3] - 2025-10-25

- feat(docs): add comprehensive refactor plan for src/ main program
- chore(docs): archive old plan

## [1.3.2] - 2025-10-25

- feat(sentence_splitter): unify punctuation handling in sentence splitting

## [1.3.1] - 2025-10-24

- feat(sentence_splitter): enhance conjunction handling and priority settings
- refactor(sentence_splitter): optimize splitting algorithm parameters
- feat(sentence_splitter): enhance sentence splitting logic and improve documentation
- feat(sentence_splitter): implement fallback strategy and colon handling
- chore: remove unused dependencies from uv.lock
- refactor: update dependencies and enhance README documentation

## [1.3.0] - 2025-10-23

- fix(text-to-sentences): correct punctuation in examples for clarity
- feat(punctuation_adder): refactor to follow SubtitleFormatter scripts standards and enhance post-processing
- feat(punctuation_adder)：add new script to add punctuation
- refactor: rename diff dependency to text-diff for clarity

## [1.2.1] - 2025-10-23

- fix(sentence_splitter): clean up output formatting by removing trailing spaces
- refactor: update output file naming conventions

## [1.2.0] - 2025-10-23

- refactor: rename scripts for clearer functionality distinction
- fix(smart_sentence_splitter): prioritize clause-introducing conjunctions
- fix(smart_sentence_splitter): increase max recursion depth from 5 to 8
- fix(smart_sentence_splitter): improve number context detection and enumeration logic
- fix(smart_sentence_splitter): improve compound clause detection and enumeration logic
- fix: exclude sentence boundaries from split point selection
- refactor(smart_sentence_splitter): improve split point selection and enumeration detection
- feat(smart_sentence_splitter): length/depth stop, remove lowercase check, drop special cases
- fix(smart_sentence_splitter): preserve punctuation/whitespace when splitting lines
- feat(scripts): add smart sentence splitter tool

## [1.1.3] - 2025-10-22

- refactor(scripts): optimize documentation and directory structure

## [1.1.2] - 2025-10-21

- feat(scripts): introduce scripts manager and enhance text processing tools
- feat(docs): add unified development roadmap for SubtitleFormatter
- docs(plan): add draft scripts_orchestration_plan.md
- add scripts clean_vtt.py and srt-resegment-by-json.py

## [1.1.1] - 2025-10-15

- feat(config): remove legacy shim and import loader directly
- feat(config): implement centralized configuration management
- feat(windows): add SubtitleFormatter launcher VBScript using uv

## [1.1.0] - 2025-10-15

- docs(README): update installation and usage instructions
- feat(models): enhance model loading and management
- feat: refactor startup modes and configuration handling
- feat(gui): add application icons and screenshot assets
- fix(gui): adjust main window size for improved layout
- feat(gui): adjust button size on About page for better UI

## [1.0.0] - 2025-10-15

- docs(logging): enhance unified logging guide with debug mode details
- feat(logging): enhance logging functionality with debug support
- feat(logging): implement unified logging system for terminal and GUI
- feat(gui): add PySide6-based GUI for Subtitle Formatter

## [0.2.4] - 2025-10-14

- docs: streamline README, remove deprecated guides, clarify config comments
- refactor(config): update TOML handling and dependencies

## [0.2.3] - 2025-10-14

- refactor(config): migrate to TOML-based configuration system

## [0.2.2] - 2025-10-14

- fix(release,ci): handle both changelog casings

## [0.2.1] - 2025-10-14

- Automated release: Patch release

## [0.2.0] - 2025-10-14

- feat(tests): add initial test structure with smoke test and package setup
- feat(release): add ci workflows and version tooling
- chore(config): set up pytest/coverage/isort/black and update dev deps
- refactor: restructure project to src architecture

## [0.1.0] - 2025-10-14

- 改用 uv 管理环境
- 清理代码

## [0.0.1] - 2024-12-27

### Added
- 初始项目结构设置
  - 模块化设计
  - 文件处理模块
  - 文本预处理模块
  - 句子处理模块
  - 行格式化模块
- 基础文本处理功能
  - 删除停顿词
  - 保持原文单词不变

### Changed
- 从单文件结构重构为模块化结构
- 优化了文件组织方式

### Deprecated
- 原 smart_text_formatter.py 移至 legacy 目录 