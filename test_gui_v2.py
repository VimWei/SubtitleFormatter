#!/usr/bin/env python3
"""
SubtitleFormatter GUI V2 测试脚本

用于测试新的插件化架构GUI
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from subtitleformatter.gui.main_window_v2 import MainWindowV2


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("SubtitleFormatter V2")
    app.setApplicationVersion("2.0.0")
    
    # 设置应用程序属性（移除已弃用的属性）
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 已弃用
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 已弃用
    
    # 创建主窗口
    window = MainWindowV2(project_root)
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
