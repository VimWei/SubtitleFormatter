from __future__ import annotations

from typing import Callable, Dict

from subtitleformatter.utils.unified_logger import logger as unified_logger


def run_processing(
    config: Dict,
    emit_log: Callable[[str], None],
    emit_progress: Callable[[int, str], None] | None = None,
) -> None:
    """
    Run text processing using the plugin-based processor.

    This function is UI-agnostic and can be called from any threading context.
    """
    import traceback

    emit_log("Starting text processing...")

    if not config:
        raise RuntimeError("No configuration provided")

    # Always use plugin-based processor; legacy processor is removed from runtime path
    try:
        from subtitleformatter.processors.plugin_text_processor import (
            PluginTextProcessor,
        )

        processor = PluginTextProcessor(config)
        emit_log("Using plugin-based processing system")
    except Exception as e:
        if getattr(unified_logger, "log_level", "INFO") == "DEBUG":
            raise RuntimeError(f"Failed to initialize processor: {e}\n{traceback.format_exc()}")
        raise RuntimeError(f"Failed to initialize processor: {e}")

    # Optionally connect processor-specific progress into emit_progress here in future

    # Run
    try:
        processor.process()
    except Exception as e:
        if getattr(unified_logger, "log_level", "INFO") == "DEBUG":
            raise RuntimeError(f"Processing failed: {e}\n{traceback.format_exc()}")
        raise RuntimeError(f"Processing failed: {e}")


