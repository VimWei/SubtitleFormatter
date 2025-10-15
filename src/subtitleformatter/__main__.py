"""
Main entry point for SubtitleFormatter using TOML configuration.

Allows running with:
  - uv run subtitleformatter
  - python -m subtitleformatter
"""

from .config import load_config
from .processors.text_processor import TextProcessor


def main():
    config = load_config()
    processor = TextProcessor(config)
    processor.process()


if __name__ == "__main__":
    main()


def main_gui() -> None:
    # Lazy import to avoid importing PySide6 for CLI usage
    from subtitleformatter.gui.main_window import run_gui

    run_gui()
