# Changelog

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