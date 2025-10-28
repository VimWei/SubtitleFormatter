"""
Main entry point for SubtitleFormatter.

Default behavior: Launch GUI V2
CLI mode: Use --cli flag with optional config file specification

Usage:
  - uv run subtitleformatter              # Launch GUI V2 (default)
  - uv run subtitleformatter --legacy     # Launch GUI V1 (legacy)
  - uv run subtitleformatter --cli        # CLI mode with default config
  - uv run subtitleformatter --cli --config path/to/config.toml  # CLI mode with custom config
"""

import argparse
import sys
from pathlib import Path

from .config.loader import load_config
from .processors.plugin_text_processor import PluginTextProcessor
from .processors.text_processor import TextProcessor


def main():
    """Main entry point - defaults to GUI, CLI mode available with --cli flag"""
    parser = argparse.ArgumentParser(
        description="SubtitleFormatter - Intelligent text processing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run subtitleformatter                    # Launch GUI V2 (default)
  uv run subtitleformatter --legacy           # Launch GUI V1 (legacy)
  uv run subtitleformatter --cli              # CLI mode with default config
  uv run subtitleformatter --cli --config my_config.toml  # CLI mode with config from data/configs/
  uv run subtitleformatter --cli --config /path/to/config.toml  # CLI mode with absolute path
        """,
    )

    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of GUI")

    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy GUI V1 (legacy mode) instead of the default V2 GUI",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (TOML format). Relative paths are searched in data/configs/ first, then current directory",
    )

    args = parser.parse_args()

    if args.cli:
        # CLI mode
        run_cli(args.config)
    else:
        # GUI mode (default V2, or legacy V1 if --legacy is specified)
        run_gui(use_legacy=args.legacy)


def run_cli(config_path: str = None):
    """Run SubtitleFormatter in CLI mode"""
    try:
        if config_path:
            # Load custom config file
            config = load_config(config_path)
        else:
            # Load default config
            config = load_config()

        # Check if plugin system is enabled
        if config.get("plugins") and config.get("plugins", {}).get("order"):
            # Use new plugin-based processor
            processor = PluginTextProcessor(config)
            print("🔌 Using plugin-based processing system")
        else:
            # Use legacy processor for backward compatibility
            processor = TextProcessor(config)
            print("📜 Using legacy processing system")

        processor.process()
        print("✅ Processing completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def run_gui(use_legacy: bool = False):
    """
    Run SubtitleFormatter in GUI mode.
    
    Args:
        use_legacy: If True, launch legacy V1 GUI. If False, launch V2 GUI (default).
    """
    try:
        if use_legacy:
            # Legacy GUI V1
            from subtitleformatter.gui.main_window import run_gui as run_gui_legacy

            run_gui_legacy()
        else:
            # Modern GUI V2 - New Plugin-Based Architecture (default)
            from subtitleformatter.gui.main_window_v2 import run_gui_v2

            run_gui_v2()
    except ImportError as e:
        print(f"❌ GUI dependencies not available: {e}")
        print("Please install GUI dependencies: pip install PySide6")
        sys.exit(1)
    except Exception as e:
        print(f"❌ GUI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
