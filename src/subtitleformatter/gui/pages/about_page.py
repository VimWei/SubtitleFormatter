from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget, QFormLayout, QPushButton, QHBoxLayout, QSizePolicy
from subtitleformatter.services.version_check_service import VersionCheckService
from PySide6.QtCore import QThread, Signal


class AboutPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        url = "https://github.com/VimWei/SubtitleFormatter"
        self.label_homepage = QLabel(f'<a href="{url}">{url}</a>')
        self.label_homepage.setOpenExternalLinks(True)
        layout.addRow("Homepage:", self.label_homepage)

        updates_row = QHBoxLayout()
        # Use a compact label like MdxScraper instead of a large text box
        self.label_updates = QLabel("Click 'Check for Updates' to check", self)
        # Enable clickable links similar to MdxScraper
        self.label_updates.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label_updates.setOpenExternalLinks(True)
        self.label_updates.setWordWrap(True)
        self.label_updates.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        updates_row.addWidget(self.label_updates)
        self.btn_check = QPushButton("Check for Updates", self)
        self.btn_check.clicked.connect(self.check_for_updates)
        updates_row.addWidget(self.btn_check)
        layout.addRow("Updates:", updates_row)

        # init thread holder
        self._version_thread = None

    def check_for_updates(self) -> None:
        if self._version_thread and self._version_thread.isRunning():
            return
        self.label_updates.setText("Checking for updates...")
        self.btn_check.setEnabled(False)
        self.btn_check.setText("Checking...")

        self._version_thread = _VersionCheckThread()
        self._version_thread.update_available.connect(self._on_update_check_complete)
        self._version_thread.finished.connect(self._on_update_check_finished)
        self._version_thread.start()

    def _on_update_check_complete(self, is_latest: bool, message: str, latest_version: str) -> None:
        self.label_updates.setText(message)
        self.btn_check.setText("Check Again")

    def _on_update_check_finished(self) -> None:
        self.btn_check.setEnabled(True)
        self.btn_check.setText("Check Again")
        if self._version_thread:
            self._version_thread.deleteLater()
            self._version_thread = None


class _VersionCheckThread(QThread):
    update_available = Signal(bool, str, str)

    def __init__(self):
        super().__init__()
        self._service = VersionCheckService()

    def run(self) -> None:
        is_latest, message, latest_version = self._service.check_for_updates()
        self.update_available.emit(is_latest, message, latest_version or "")


