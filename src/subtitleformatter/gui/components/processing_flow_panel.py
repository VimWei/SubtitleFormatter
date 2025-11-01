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

    def update_processing_flow(self, plugin_order: list):
        """根据 plugin_order 更新流程展示（占位实现）"""
        # TODO: 实现流程面板的节点重构与流程渲染
        from subtitleformatter.utils.unified_logger import logger

        logger.info(f"[ProcessingFlowPanel] Updated processing flow: {plugin_order}")
