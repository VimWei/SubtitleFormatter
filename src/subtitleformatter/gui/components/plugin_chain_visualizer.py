"""
插件链可视化组件

提供直观的插件链配置和处理流程展示
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class PluginChainVisualizer(QWidget):
    """
    插件链可视化组件

    功能:
    - 可视化显示插件链
    - 显示插件状态（启用/禁用）
    - 显示处理流程方向
    - 支持插件状态指示
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.plugin_chain: List[str] = []
        self.plugin_status: Dict[str, bool] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 可视化区域
        self.visualization_area = QScrollArea()
        self.visualization_area.setWidgetResizable(True)
        self.visualization_area.setMinimumHeight(150)
        self.visualization_area.setMaximumHeight(300)
        self.visualization_area.setStyleSheet("QScrollArea { background: transparent; }")

        # 创建可视化画布
        self.canvas = PluginChainCanvas()
        self.visualization_area.setWidget(self.canvas)

        layout.addWidget(self.visualization_area)

        self.setLayout(layout)

    def update_plugin_chain(
        self, plugin_chain: List[str], plugin_metadata: Optional[Dict[str, Dict]] = None
    ):
        """更新插件链显示"""
        print(f"PluginChainVisualizer: Updating with {len(plugin_chain)} plugins: {plugin_chain}")
        self.plugin_chain = plugin_chain
        if plugin_metadata:
            self.plugin_metadata = plugin_metadata

        # 更新画布
        self.canvas.update_plugin_chain(self.plugin_chain, self.plugin_metadata)

    def update_plugin_status(self, plugin_name: str, enabled: bool):
        """更新插件状态"""
        self.plugin_status[plugin_name] = enabled
        self.canvas.update_plugin_status(plugin_name, enabled)

    def set_processing_status(self, plugin_name: str, status: str):
        """设置插件处理状态"""
        self.canvas.set_plugin_processing_status(plugin_name, status)


class PluginChainCanvas(QWidget):
    """插件链画布"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.plugin_chain: List[str] = []
        self.plugin_metadata: Dict[str, Dict] = {}
        self.plugin_status: Dict[str, bool] = {}
        self.plugin_processing_status: Dict[str, str] = {}

        # 设置最小尺寸
        self.setMinimumHeight(120)
        self.setMinimumWidth(400)

    def update_plugin_chain(self, plugin_chain: List[str], plugin_metadata: Dict[str, Dict]):
        """更新插件链"""
        print(f"PluginChainCanvas: Updating with {len(plugin_chain)} plugins: {plugin_chain}")
        self.plugin_chain = plugin_chain
        self.plugin_metadata = plugin_metadata

        # 初始化状态
        for plugin_name in plugin_chain:
            if plugin_name not in self.plugin_status:
                self.plugin_status[plugin_name] = True
            if plugin_name not in self.plugin_processing_status:
                self.plugin_processing_status[plugin_name] = "idle"

        print(f"PluginChainCanvas: Calling update() to redraw")
        self.update()

    def update_plugin_status(self, plugin_name: str, enabled: bool):
        """更新插件状态"""
        self.plugin_status[plugin_name] = enabled
        self.update()

    def set_plugin_processing_status(self, plugin_name: str, status: str):
        """设置插件处理状态"""
        self.plugin_processing_status[plugin_name] = status
        self.update()

    def _remove_namespace(self, name: str) -> str:
        """移除名称中的 namespace 部分"""
        # 如果名称包含斜杠，取最后一部分
        if "/" in name:
            return name.split("/")[-1]
        # 如果名称包含点号，取最后一部分
        elif "." in name:
            return name.split(".")[-1]
        return name

    def _calculate_nodes_per_row(
        self, node_widths: List[int], available_width: int, spacing: int, arrow_width: int
    ) -> int:
        """计算每行能容纳的节点数"""
        if not node_widths:
            return 1

        # 尝试不同的每行节点数
        for nodes_per_row in range(1, len(node_widths) + 1):
            total_width = 0
            for i in range(min(nodes_per_row, len(node_widths))):
                total_width += node_widths[i]
                if i < min(nodes_per_row, len(node_widths)) - 1:
                    total_width += spacing + arrow_width

            if total_width > available_width:
                return max(1, nodes_per_row - 1)

        return len(node_widths)

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 清除背景
        painter.fillRect(self.rect(), Qt.transparent)

        if not self.plugin_chain:
            self.draw_empty_state(painter)
            return

        self.draw_plugin_chain(painter)

    def draw_empty_state(self, painter: QPainter):
        """绘制空状态"""
        painter.setPen(QPen(QColor("#666")))
        painter.setFont(QFont("Arial", 12))

        # 直接在中心绘制文字，不绘制框
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawText(rect, Qt.AlignCenter, "No plugins in processing chain")

    def draw_plugin_chain(self, painter: QPainter):
        """绘制插件链"""
        if not self.plugin_chain:
            return

        # 计算节点尺寸和间距
        node_height = 40
        spacing = 30  # 适当增加行间距，让拐弯箭头有足够的空间
        arrow_width = 30
        margin = 10

        # 计算每个节点的宽度（基于文字长度）
        node_widths = []
        font_metrics = QFontMetrics(QFont("Arial", 10, QFont.Bold))

        for plugin_name in self.plugin_chain:
            # 获取显示名称
            display_name = plugin_name
            if plugin_name in self.plugin_metadata:
                metadata = self.plugin_metadata[plugin_name]
                display_name = metadata.get("name", plugin_name)
            display_name = self._remove_namespace(display_name)

            # 计算文字宽度，添加边距
            text_width = font_metrics.horizontalAdvance(display_name)
            node_width = max(80, text_width + 20)  # 最小宽度80，文字宽度+边距
            node_widths.append(node_width)

        # 计算每行能容纳的节点数
        available_width = self.width() - 2 * margin
        nodes_per_row = self._calculate_nodes_per_row(
            node_widths, available_width, spacing, arrow_width
        )

        # 计算行数
        num_rows = (len(self.plugin_chain) + nodes_per_row - 1) // nodes_per_row

        # 计算每行的起始Y位置
        total_height = num_rows * node_height + (num_rows - 1) * spacing
        start_y = (self.height() - total_height) // 2

        # 第一遍：绘制所有节点
        for i, plugin_name in enumerate(self.plugin_chain):
            row = i // nodes_per_row
            col = i % nodes_per_row

            # 计算当前行的起始X位置
            row_start_idx = row * nodes_per_row
            row_end_idx = min(row_start_idx + nodes_per_row, len(self.plugin_chain))
            row_widths = node_widths[row_start_idx:row_end_idx]

            row_total_width = sum(row_widths)
            if len(row_widths) > 1:
                row_total_width += (len(row_widths) - 1) * (spacing + arrow_width)

            start_x = (self.width() - row_total_width) // 2

            # 计算当前节点的位置
            x = start_x
            for j in range(col):
                x += node_widths[row_start_idx + j] + spacing + arrow_width

            y = start_y + row * (node_height + spacing)

            # 绘制插件节点
            self.draw_plugin_node(painter, x, y, node_widths[i], node_height, plugin_name)

        # 第二遍：绘制所有箭头（在节点之上）
        for i, plugin_name in enumerate(self.plugin_chain):
            row = i // nodes_per_row
            col = i % nodes_per_row

            # 计算当前行的起始X位置
            row_start_idx = row * nodes_per_row
            row_end_idx = min(row_start_idx + nodes_per_row, len(self.plugin_chain))
            row_widths = node_widths[row_start_idx:row_end_idx]

            row_total_width = sum(row_widths)
            if len(row_widths) > 1:
                row_total_width += (len(row_widths) - 1) * (spacing + arrow_width)

            start_x = (self.width() - row_total_width) // 2

            # 计算当前节点的位置
            x = start_x
            for j in range(col):
                x += node_widths[row_start_idx + j] + spacing + arrow_width

            y = start_y + row * (node_height + spacing)

            # 绘制箭头（水平方向，除了每行最后一个节点）
            if col < len(row_widths) - 1:
                arrow_x = x + node_widths[i] + spacing // 2
                self.draw_arrow(
                    painter,
                    arrow_x,
                    y + node_height // 2,
                    arrow_x + arrow_width,
                    y + node_height // 2,
                )

            # 绘制拐弯箭头（除了最后一行，且是每行最后一个节点）
            if row < num_rows - 1 and col == len(row_widths) - 1:
                # 计算下一行的第一个节点位置
                next_row = row + 1
                next_row_start_idx = next_row * nodes_per_row
                next_row_end_idx = min(next_row_start_idx + nodes_per_row, len(self.plugin_chain))
                next_row_widths = node_widths[next_row_start_idx:next_row_end_idx]
                
                next_row_total_width = sum(next_row_widths)
                if len(next_row_widths) > 1:
                    next_row_total_width += (len(next_row_widths) - 1) * (spacing + arrow_width)
                
                next_start_x = (self.width() - next_row_total_width) // 2
                next_y = start_y + next_row * (node_height + spacing)
                
                # 绘制拐弯箭头
                self.draw_bent_arrow(
                    painter,
                    x + node_widths[i] // 2,  # 当前节点中心X
                    y + node_height,  # 当前节点底部
                    next_start_x + next_row_widths[0] // 2,  # 下一行第一个节点中心X
                    next_y,  # 下一行第一个节点顶部
                )

    def draw_plugin_node(
        self, painter: QPainter, x: int, y: int, width: int, height: int, plugin_name: str
    ):
        """绘制插件节点"""
        rect = QRect(x, y, width, height)

        # 获取插件状态
        enabled = self.plugin_status.get(plugin_name, True)
        processing_status = self.plugin_processing_status.get(plugin_name, "idle")

        # 根据状态选择颜色
        if processing_status == "processing":
            bg_color = QColor("#FF9800")  # 橙色 - 处理中
            border_color = QColor("#F57C00")
        elif processing_status == "completed":
            bg_color = QColor("#4CAF50")  # 绿色 - 完成
            border_color = QColor("#388E3C")
        elif processing_status == "error":
            bg_color = QColor("#f44336")  # 红色 - 错误
            border_color = QColor("#D32F2F")
        elif enabled:
            bg_color = QColor("#2196F3")  # 蓝色 - 启用
            border_color = QColor("#1976D2")
        else:
            bg_color = QColor("#9E9E9E")  # 灰色 - 禁用
            border_color = QColor("#757575")

        # 绘制节点背景
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(rect, 8, 8)

        # 绘制插件名称
        painter.setPen(QPen(QColor("#fff"), 1))
        painter.setFont(QFont("Arial", 10, QFont.Bold))

        # 获取插件显示名称
        display_name = plugin_name
        if plugin_name in self.plugin_metadata:
            metadata = self.plugin_metadata[plugin_name]
            display_name = metadata.get("name", plugin_name)

        # 移除 namespace 部分（如果有的话）
        display_name = self._remove_namespace(display_name)

        # 如果名称太长，截断
        font_metrics = QFontMetrics(painter.font())
        if font_metrics.horizontalAdvance(display_name) > width - 10:
            display_name = font_metrics.elidedText(display_name, Qt.ElideMiddle, width - 10)

        painter.drawText(rect, Qt.AlignCenter, display_name)

        # 绘制状态指示器
        if processing_status != "idle":
            self.draw_status_indicator(painter, x + width - 15, y + 5, processing_status)

    def draw_status_indicator(self, painter: QPainter, x: int, y: int, status: str):
        """绘制状态指示器"""
        indicator_size = 8

        if status == "processing":
            # 绘制旋转的圆点表示处理中
            painter.setBrush(QBrush(QColor("#fff")))
            painter.setPen(QPen(QColor("#fff"), 1))
            painter.drawEllipse(x, y, indicator_size, indicator_size)
        elif status == "completed":
            # 绘制勾号
            painter.setPen(QPen(QColor("#fff"), 2))
            painter.drawLine(x + 2, y + 4, x + 4, y + 6)
            painter.drawLine(x + 4, y + 6, x + 6, y + 2)
        elif status == "error":
            # 绘制X号
            painter.setPen(QPen(QColor("#fff"), 2))
            painter.drawLine(x + 2, y + 2, x + 6, y + 6)
            painter.drawLine(x + 6, y + 2, x + 2, y + 6)

    def draw_arrow(
        self,
        painter: QPainter,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        vertical: bool = False,
    ):
        """绘制箭头"""
        painter.setPen(QPen(QColor("#666"), 2))

        # 绘制主线
        painter.drawLine(start_x, start_y, end_x, end_y)

        # 绘制箭头头部
        arrow_size = 8

        if vertical:
            # 垂直箭头：箭头向下
            x1 = end_x - arrow_size // 2
            y1 = end_y - arrow_size
            x2 = end_x + arrow_size // 2
            y2 = end_y - arrow_size
        else:
            # 水平箭头：箭头向右
            angle = math.atan2(end_y - start_y, end_x - start_x)

            # 箭头点1
            x1 = end_x - arrow_size * math.cos(angle - math.pi / 6)
            y1 = end_y - arrow_size * math.sin(angle - math.pi / 6)

            # 箭头点2
            x2 = end_x - arrow_size * math.cos(angle + math.pi / 6)
            y2 = end_y - arrow_size * math.sin(angle + math.pi / 6)

        # 绘制箭头
        painter.drawLine(end_x, end_y, x1, y1)
        painter.drawLine(end_x, end_y, x2, y2)

    def draw_bent_arrow(
        self,
        painter: QPainter,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ):
        """绘制拐弯箭头（从一行的最后一个节点到下一行的第一个节点）
        
        箭头路径根据节点位置自适应：向下 -> 水平 -> 向上
        """
        painter.setPen(QPen(QColor("#666"), 2))

        # 计算总垂直距离
        if end_y < start_y:
            # 目标在上方：向下 -> 水平 -> 向上
            total_height = start_y - end_y
            
            # 第一段向下
            down_dist = total_height // 3
            mid_y = start_y + down_dist
            
            # 绘制路径
            painter.drawLine(start_x, start_y, start_x, mid_y)  # 向下
            painter.drawLine(start_x, mid_y, end_x, mid_y)      # 水平移动
            painter.drawLine(end_x, mid_y, end_x, end_y)         # 向上连接到终点
            
            # 箭头向上 - 使用线段风格，与其他箭头一致
            arrow_size = 8
            x1 = end_x - arrow_size // 2
            y1 = end_y - arrow_size
            x2 = end_x + arrow_size // 2
            y2 = end_y - arrow_size
            painter.drawLine(end_x, end_y, x1, y1)
            painter.drawLine(end_x, end_y, x2, y2)
        elif end_y > start_y:
            # 目标在下方：继续向下 -> 水平 -> 继续向下
            total_height = end_y - start_y
            
            # 第一段向下
            down_dist = total_height // 2
            mid_y = start_y + down_dist
            
            # 绘制路径
            painter.drawLine(start_x, start_y, start_x, mid_y)  # 继续向下
            painter.drawLine(start_x, mid_y, end_x, mid_y)      # 水平移动
            painter.drawLine(end_x, mid_y, end_x, end_y)         # 继续向下连接到终点
            
            # 箭头向下 - 使用线段风格，与其他箭头一致
            arrow_size = 8
            x1 = end_x - arrow_size // 2
            y1 = end_y - arrow_size
            x2 = end_x + arrow_size // 2
            y2 = end_y - arrow_size
            painter.drawLine(end_x, end_y, x1, y1)
            painter.drawLine(end_x, end_y, x2, y2)
        else:
            # 同一水平线，只画水平箭头
            painter.drawLine(start_x, start_y, end_x - 8, start_y)
            arrow_size = 8
            x1 = end_x - arrow_size
            y1 = start_y - arrow_size // 2
            x2 = end_x - arrow_size
            y2 = start_y + arrow_size // 2
            painter.drawLine(end_x, start_y, x1, y1)
            painter.drawLine(end_x, start_y, x2, y2)
