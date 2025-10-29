from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QThread, Signal

from subtitleformatter.runtime.processing_runner import run_processing


class ProcessingThread(QThread):
    """Thin QThread wrapper around the UI-agnostic processing runner."""

    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, config: Dict):
        super().__init__()
        self.config = config

    def run(self):
        try:
            run_processing(self.config, emit_log=self.log.emit, emit_progress=lambda p, m="": self.progress.emit(p, m))
            self.finished.emit(True, "Processing completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))


