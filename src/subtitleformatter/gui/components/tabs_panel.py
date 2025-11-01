from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from ..pages.about_page import AboutPage
from ..pages.advanced_page import AdvancedPage
from ..pages.basic_page import BasicPage


class TabsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self.tabs = QTabWidget(self)
        self.tab_basic = BasicPage(self)
        self.tab_advanced = AdvancedPage(self)
        self.tab_about = AboutPage(self)
        self.tabs.addTab(self.tab_basic, "Basic")
        self.tabs.addTab(self.tab_advanced, "Advanced")
        self.tabs.addTab(self.tab_about, "About")
        self.tabs.setMinimumHeight(180)
        layout.addWidget(self.tabs)

        # 增加下列内容: 使 set_config_coordinator 可自适应主窗口调用
        def set_config_coordinator(self, coordinator):
            if hasattr(self.tab_basic, "set_config_coordinator"):
                self.tab_basic.set_config_coordinator(coordinator)
            if hasattr(self.tab_advanced, "set_config_coordinator"):
                self.tab_advanced.set_config_coordinator(coordinator)

        self.set_config_coordinator = set_config_coordinator.__get__(self)
