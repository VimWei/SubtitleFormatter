from PySide6.QtWidgets import QVBoxLayout, QWidget

from .plugin_chain_visualizer import PluginChainVisualizer


class ProcessingFlowPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self.visualizer = PluginChainVisualizer(self)
        self.visualizer.setMinimumHeight(120)
        layout.addWidget(self.visualizer)
