from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.utils.unified_logger import logger
from subtitleformatter.version import get_app_title

from .components.command_panel import CommandPanel
from .components.log_panel import LogPanel
from .pages.about_page import AboutPage
from .pages.advanced_page import AdvancedPage
from .pages.basic_page import BasicPage
from .styles.theme_loader import ThemeLoader


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle(get_app_title())

        icon_path = project_root / "src" / "subtitleformatter" / "gui" / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Splitter: top tabs, middle command panel, bottom log
        self.splitter = QSplitter(Qt.Vertical, self)

        # Top tabs
        self.tabs = QTabWidget(self)
        self.tab_basic = BasicPage(self)
        self.tab_advanced = AdvancedPage(self)
        self.tab_about = AboutPage(self)
        self.tabs.addTab(self.tab_basic, "Basic")
        self.tabs.addTab(self.tab_advanced, "Advanced")
        self.tabs.addTab(self.tab_about, "About")
        self.splitter.addWidget(self.tabs)

        # Middle command panel
        self.command_panel = CommandPanel(self)
        self.command_panel.btn_format.setObjectName("scrape-button")
        self.splitter.addWidget(self.command_panel)

        # Bottom log panel
        self.log_panel = LogPanel(self)
        self.splitter.addWidget(self.log_panel)

        # Splitter behavior: fix middle height, allow resizing top and bottom only
        self.splitter.setSizes([300, 120, 200])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setChildrenCollapsible(False)

        # Enforce middle fixed height when splitter moved
        self.splitter.splitterMoved.connect(self._on_splitter_moved)

        layout.addWidget(self.splitter)
        self.setCentralWidget(central)
        self.setMinimumSize(800, 520)

        # Apply theme styling
        self.apply_modern_styling()

        # Wire advanced signals: open user data dir and restore default config
        self.tab_advanced.btn_open_user_data.clicked.connect(self._open_user_data_dir)
        self.tab_advanced.btn_restore_default.clicked.connect(self._restore_default_config)
        # Initialize user data path display with relative hint only
        # Actual resolution occurs when user clicks Open

        # Wire command panel config actions
        self.command_panel.restoreRequested.connect(self._on_restore_last_config)
        self.command_panel.importRequested.connect(self._on_import_config)
        self.command_panel.exportRequested.connect(self._on_export_config)
        self.command_panel.formatRequested.connect(self._on_format_clicked)

        # 设置统一日志系统的GUI回调
        logger.set_gui_callback(self.log_panel.append_log)

        # Wire basic page browse buttons and edits
        self.tab_basic.btn_input.clicked.connect(self._choose_input)
        self.tab_basic.btn_output.clicked.connect(self._choose_output)
        self.tab_basic.edit_input.editingFinished.connect(
            lambda: self._set_input_file(self.tab_basic.edit_input.text().strip())
        )
        self.tab_basic.edit_output.editingFinished.connect(
            lambda: self._set_output_file(self.tab_basic.edit_output.text().strip())
        )
        self.tab_basic.check_timestamp.stateChanged.connect(self._on_timestamp_toggled)

        # Connect new configuration controls
        self.tab_basic.spin_max_width.valueChanged.connect(self._on_max_width_changed)
        self.tab_basic.combo_language.currentTextChanged.connect(self._on_language_changed)
        self.tab_basic.combo_model_size.currentTextChanged.connect(self._on_model_size_changed)
        self.tab_basic.check_debug.stateChanged.connect(self._on_debug_toggled)

        # ---- In-memory configuration state ----
        self._config = self._load_user_config()
        self._apply_cfg_to_ui(self._config)

    def apply_modern_styling(self) -> None:
        app = QApplication.instance()
        theme_loader = ThemeLoader(self.project_root)
        theme_name = "default"
        theme_loader.apply_base_style(app, theme_name)
        self.setStyleSheet(theme_loader.load_theme(theme_name))

    # ---- Path normalization helper (consistent display) ----
    def _normalize_path_for_display(self, path_text: str) -> str:
        try:
            import os

            if not path_text:
                return ""
            return os.path.normpath(path_text)
        except Exception:
            return path_text

    # ---- Relative path helpers (portable like MdxScraper) ----
    def _to_relative(self, p: str | Path) -> str:
        try:
            import os

            abs_path = Path(p).resolve()
            root = self.project_root.resolve()
            rel = abs_path.relative_to(root)
            return os.path.normpath(str(rel))
        except Exception:
            # If on different drive or outside root, keep absolute normalized
            return self._normalize_path_for_display(str(p))

    def _resolve_path(self, maybe_path: str | Path) -> Path:
        try:
            p = Path(maybe_path)
            if not p.is_absolute():
                return (self.project_root / p).resolve()
            return p.resolve()
        except Exception:
            return Path(str(maybe_path))

    def _path_for_log(self, p: str | Path) -> str:
        try:
            return self._normalize_path_for_display(self._to_relative(p))
        except Exception:
            return str(p)

    # ---- Format execution (background) ----
    class _FormatThread(QThread):
        progress = Signal(int, str)
        log = Signal(str)
        done = Signal(bool, str)

        def __init__(self, runtime_cfg: dict):
            super().__init__()
            self.runtime_cfg = runtime_cfg

        def run(self) -> None:
            try:
                from subtitleformatter.processors.text_processor import TextProcessor

                # 设置统一日志系统，让日志同时输出到终端和GUI
                def gui_log_callback(message: str):
                    # 在后台线程中安全地发送信号到GUI线程
                    self.log.emit(message)

                logger.set_gui_callback(gui_log_callback)
                logger.enable_gui(True)
                logger.enable_terminal(True)

                self.log.emit("Starting format...")
                processor = TextProcessor(self.runtime_cfg)
                processor.process()
                self.done.emit(True, "Format completed.")
            except Exception as e:
                self.done.emit(False, f"Format failed: {e}")

    def _materialize_runtime_cfg(self) -> dict:
        import copy
        import os
        from datetime import datetime

        cfg = copy.deepcopy(self._config)
        paths = cfg.setdefault("paths", {})
        output = cfg.setdefault("output", {})
        add_ts = bool(output.get("add_timestamp", True))

        in_text = paths.get("input_file", "").strip()
        out_text = paths.get("output_file", "").strip()

        # Resolve input absolute
        abs_input = str(self._resolve_path(in_text)) if in_text else ""

        # Determine output suggestion if empty
        if not out_text and abs_input:
            base = Path(abs_input).stem
            out_dir = (self.project_root / "data" / "output").resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{base}.txt"
            if add_ts:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{filename}"
            abs_output = str(out_dir / filename)
        else:
            abs_output = str(self._resolve_path(out_text)) if out_text else ""

        # If output exists and add_timestamp is enabled, add timestamp prefix at run-time
        if abs_output and add_ts:
            p = Path(abs_output)
            ts_prefix = datetime.now().strftime("%Y%m%d%H%M%S")
            abs_output = (
                str(p.with_name(f"{ts_prefix}-{p.name}"))
                if not p.name.startswith(ts_prefix + "-")
                else str(p)
            )

        # Write back absolute paths for runtime
        paths["input_file"] = abs_input
        paths["output_file"] = abs_output

        # Ensure directories exist (similar to _materialize_paths in loader.py)
        if abs_output:
            output_dir = os.path.dirname(abs_output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

        # Flatten for compatibility with TextProcessor
        cfg["input_file"] = abs_input
        cfg["output_file"] = abs_output

        return cfg

    def _on_format_clicked(self) -> None:
        cfg = self._materialize_runtime_cfg()
        inp = cfg.get("paths", {}).get("input_file", "").strip()
        outp = cfg.get("paths", {}).get("output_file", "").strip()
        if not inp:
            QMessageBox.warning(self, "Format", "Please select an input file first.")
            return
        if not outp:
            QMessageBox.warning(
                self, "Format", "Please select an output file or set input to auto-suggest."
            )
            return

        # UI state
        self.command_panel.btn_format.setEnabled(False)
        self.command_panel.set_progress(0)
        if hasattr(self, "log_panel"):
            self.log_panel.append_log(f"Input: {self._path_for_log(inp)}")
            self.log_panel.append_log(f"Output: {self._path_for_log(outp)}")

        # Run in background
        self._format_thread = self._FormatThread(cfg)
        self._format_thread.log.connect(lambda msg: self.log_panel.append_log(msg))
        self._format_thread.progress.connect(
            lambda v, m: (self.command_panel.set_progress(v), self.log_panel.append_log(m))
        )
        self._format_thread.done.connect(self._on_format_done)
        self._format_thread.start()

    def _on_format_done(self, ok: bool, message: str) -> None:
        self.command_panel.set_progress(100 if ok else 0)
        self.command_panel.btn_format.setEnabled(True)
        if hasattr(self, "log_panel"):
            self.log_panel.append_log(("✅ " if ok else "❌ ") + message)

    def _on_splitter_moved(self, pos: int, index: int) -> None:
        sizes = self.splitter.sizes()
        # force middle pane to its fixed height (120)
        middle = 120
        total = sum(sizes)
        # redistribute difference to top/bottom keeping their ratio
        top, _, bottom = sizes
        remaining = max(100, total - middle)
        # keep at least 150 for bottom log
        min_bottom = 150
        if bottom < min_bottom:
            bottom = min_bottom
            top = remaining - bottom
        else:
            # keep current ratio
            ratio = top / max(1, (top + bottom))
            top = int(remaining * ratio)
            bottom = remaining - top
        self.splitter.blockSignals(True)
        self.splitter.setSizes([top, middle, bottom])
        self.splitter.blockSignals(False)

    # ---- User data path helpers (replicate MdxScraper behavior) ----
    def _user_data_dir(self) -> Path:
        # Relative to project root
        return (self.project_root / "data").resolve()

    def _update_user_data_path(self) -> None:
        # Show relative hint; defer actual absolute resolution to _open_user_data_dir
        self.tab_advanced.edit_user_data.setText("data/ (relative to project root)")

    def _open_user_data_dir(self) -> None:
        try:
            path = self._user_data_dir()
            path.mkdir(parents=True, exist_ok=True)
            # Use OS to open folder
            import os

            os.startfile(str(path))
            # After opening, update UI with absolute path
            self.tab_advanced.edit_user_data.setText(str(path))
        except Exception:
            pass

    def _restore_default_config(self) -> None:
        try:
            # Load bundled default into memory only; do not write to disk now
            import tomllib

            from subtitleformatter.config.loader import DEFAULT_CONFIG_PATH

            with open(DEFAULT_CONFIG_PATH, "rb") as f:
                defaults = tomllib.load(f)
            defaults.setdefault("paths", {})
            defaults.setdefault("output", {})
            if "add_timestamp" not in defaults["output"]:
                defaults["output"]["add_timestamp"] = True

            # Update session config and reflect in UI
            self._config = defaults
            self._apply_cfg_to_ui(self._config)
            if hasattr(self, "log_panel"):
                self.log_panel.append_log("✅ Restored default config.")
            self._update_user_data_path()
        except Exception:
            pass

    # ---- Basic page: input/output browse and persistence ----
    def _configs_dir(self) -> Path:
        return (self.project_root / "data" / "configs").resolve()

    def _load_user_config(self) -> dict:
        from subtitleformatter.config.loader import load_config

        return load_config()

    def _save_user_config(self, cfg: dict) -> None:
        import tomli_w  # type: ignore

        from subtitleformatter.config.loader import USER_CONFIG_PATH

        USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Normalize and convert to relative before saving to disk
        to_save = self._normalized_config_for_save(cfg)
        with open(USER_CONFIG_PATH, "wb") as f:
            f.write(tomli_w.dumps(to_save).encode("utf-8"))

    def _normalized_config_for_save(self, cfg: dict) -> dict:
        try:
            import copy
            import os

            normalized = copy.deepcopy(cfg)
            paths = normalized.setdefault("paths", {})
            if isinstance(paths.get("input_file"), str):
                paths["input_file"] = (
                    self._to_relative(paths["input_file"]) if paths["input_file"] else ""
                )
            if isinstance(paths.get("output_file"), str):
                paths["output_file"] = (
                    self._to_relative(paths["output_file"]) if paths["output_file"] else ""
                )
            return normalized
        except Exception:
            return cfg

    def _relativize_paths_in_config(self, cfg: dict) -> dict:
        try:
            import copy

            new_cfg = copy.deepcopy(cfg)
            paths = new_cfg.setdefault("paths", {})
            if isinstance(paths.get("input_file"), str) and paths.get("input_file"):
                paths["input_file"] = self._to_relative(paths["input_file"])
            if isinstance(paths.get("output_file"), str) and paths.get("output_file"):
                paths["output_file"] = self._to_relative(paths["output_file"])
            return new_cfg
        except Exception:
            return cfg

    def _set_input_file(self, path_text: str) -> None:
        try:
            cfg = self._config
            cfg.setdefault("paths", {})
            cfg["paths"]["input_file"] = path_text
            # If output empty, suggest under data/output with same basename
            out = cfg["paths"].get("output_file", "").strip()
            if not out and path_text:
                in_path = Path(path_text)
                base = in_path.stem
                suffix = ".txt"
                filename = f"{base}{suffix}"
                suggested = str(self.project_root / "data" / "output" / filename)
                cfg["paths"]["output_file"] = suggested
                self.tab_basic.edit_output.setText(self._normalize_path_for_display(suggested))
        except Exception:
            pass

    def _set_output_file(self, path_text: str) -> None:
        try:
            cfg = self._config
            cfg.setdefault("paths", {})
            cfg["paths"]["output_file"] = path_text
        except Exception:
            pass

    def _choose_input(self) -> None:
        start_dir = str((self.project_root / "data" / "input").resolve())
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            start_dir,
            "Text/Markdown files (*.txt *.md);;All files (*.*)",
        )
        if not file:
            return
        # Display relative for portability like MdxScraper
        self.tab_basic.edit_input.setText(self._normalize_path_for_display(self._to_relative(file)))
        self._set_input_file(file)
        # Update or suggest output according to linkage rules
        try:
            cfg = self._config
            out_text = cfg.get("paths", {}).get("output_file", "").strip()
            in_base = Path(file).stem
            if out_text:
                out_path = Path(out_text)
                new_out = str(out_path.with_name(in_base + out_path.suffix))
            else:
                out_dir = (self.project_root / "data" / "output").resolve()
                out_dir.mkdir(parents=True, exist_ok=True)
                new_out = str(out_dir / f"{in_base}.txt")
            self.tab_basic.edit_output.setText(
                self._normalize_path_for_display(self._to_relative(new_out))
            )
            self._set_output_file(new_out)
        except Exception:
            pass

    def _choose_output(self) -> None:
        # Prefer data/output as start dir
        out_dir = (self.project_root / "data" / "output").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        # Suggest a name based on input if present
        suggested = ""
        in_text = self.tab_basic.edit_input.text().strip()
        if in_text:
            try:
                in_base = Path(in_text).stem
                # honor timestamp toggle when suggesting
                suggested = str(out_dir / f"{in_base}.txt")
            except Exception:
                pass
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Select output file",
            suggested or str(out_dir),
            "Text files (*.txt);;All files (*.*)",
        )
        if not file:
            return
        self.tab_basic.edit_output.setText(
            self._normalize_path_for_display(self._to_relative(file))
        )
        self._set_output_file(file)

    def _on_timestamp_toggled(self) -> None:
        try:
            cfg = self._config
            cfg.setdefault("output", {})
            cfg["output"]["add_timestamp"] = bool(self.tab_basic.check_timestamp.isChecked())
            # Do not open dialogs or alter current output immediately; only affects future formatting
        except Exception:
            pass

    def _on_max_width_changed(self, value: int) -> None:
        try:
            self._config["max_width"] = value
        except Exception:
            pass

    def _on_language_changed(self, language: str) -> None:
        try:
            self._config["language"] = language
        except Exception:
            pass

    def _on_model_size_changed(self, display_text: str) -> None:
        try:
            # Map display text back to internal value
            from .pages.basic_page import DISPLAY_TO_MODEL_SIZE

            actual_value = DISPLAY_TO_MODEL_SIZE.get(display_text, "md")
            self._config["model_size"] = actual_value
        except Exception:
            pass

    def _on_debug_toggled(self) -> None:
        try:
            cfg = self._config
            cfg.setdefault("debug", {})
            cfg["debug"]["enabled"] = bool(self.tab_basic.check_debug.isChecked())
        except Exception:
            pass

    def closeEvent(self, event):
        # Persist in-memory configuration on close
        try:
            self._save_user_config(self._config)
        except Exception:
            pass
        event.accept()

    # ---- Config management for CommandPanel ----
    def _ensure_user_config_exists(self) -> Path:
        import shutil

        from subtitleformatter.config.loader import (
            DEFAULT_CONFIG_PATH,
            USER_CONFIG_PATH,
        )

        if not USER_CONFIG_PATH.exists():
            USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)
        return USER_CONFIG_PATH

    def _load_user_config(self) -> dict:
        import tomllib

        path = self._ensure_user_config_exists()
        with open(path, "rb") as f:
            return tomllib.load(f)

    def _apply_cfg_to_ui(self, cfg: dict) -> None:
        paths = cfg.get("paths", {})
        input_file = paths.get("input_file", "")
        output_file = paths.get("output_file", "")
        # If input is empty, ensure output shown as empty (GUI suggests later)
        if not input_file:
            output_file = ""
            cfg.setdefault("paths", {})
            cfg["paths"]["output_file"] = ""

        # Get configuration values with defaults
        max_width = cfg.get("max_width", 78)
        language = cfg.get("language", "en")
        model_size = cfg.get("model_size", "md")
        add_timestamp = cfg.get("output", {}).get("add_timestamp", True)
        debug_enabled = cfg.get("debug", {}).get("enabled", False)

        self.tab_basic.set_config(
            self._normalize_path_for_display(input_file),
            self._normalize_path_for_display(output_file),
            max_width,
            language,
            model_size,
            add_timestamp,
            debug_enabled,
        )

    def _on_restore_last_config(self) -> None:
        try:
            cfg = self._load_user_config()
            self._apply_cfg_to_ui(cfg)
            if hasattr(self, "log_panel"):
                self.log_panel.append_log("✅ Restored last config.")
        except Exception as e:
            QMessageBox.warning(self, "Restore config", f"Failed to restore config: {e}")

    def _on_import_config(self) -> None:
        import tomllib

        start_dir = str((self.project_root / "data" / "configs").resolve())
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Import config (TOML)",
            start_dir,
            "TOML files (*.toml)",
        )
        if not file:
            return
        try:
            with open(file, "rb") as f:
                imported = tomllib.load(f)
            # Ensure required sections and defaults
            imported.setdefault("paths", {})
            imported.setdefault("output", {})
            if "add_timestamp" not in imported["output"]:
                imported["output"]["add_timestamp"] = True
            # Convert imported absolute paths to project-relative when applicable
            imported = self._relativize_paths_in_config(imported)
            # Update in-memory config only
            self._config = imported
            # Reflect in UI
            self._apply_cfg_to_ui(self._config)
            if hasattr(self, "log_panel"):
                self.log_panel.append_log(f"✅ Imported config from: {self._path_for_log(file)}")
        except Exception as e:
            QMessageBox.warning(self, "Import config", f"Failed to import config: {e}")

    def _on_export_config(self) -> None:
        start_dir = str((self.project_root / "data" / "configs").resolve())
        Path(start_dir).mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Export config as (TOML)",
            str(Path(start_dir)),
            "TOML files (*.toml)",
        )
        if not file:
            return
        try:
            import tomli_w  # type: ignore

            to_save = self._normalized_config_for_save(self._config)
            with open(file, "wb") as f:
                f.write(tomli_w.dumps(to_save).encode("utf-8"))
            if hasattr(self, "log_panel"):
                self.log_panel.append_log(f"✅ Exported config to: {self._path_for_log(file)}")
        except Exception as e:
            QMessageBox.warning(self, "Export config", f"Failed to export config: {e}")


def run_gui() -> None:
    import sys

    app = QApplication(sys.argv)

    root = Path(__file__).resolve().parents[3]
    icon_path = root / "src" / "subtitleformatter" / "gui" / "assets" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    w = MainWindow(root)
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec())
