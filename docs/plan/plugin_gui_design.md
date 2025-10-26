# 插件化架构 GUI 设计文档

## 📋 概述

本文档详细描述了 SubtitleFormatter 插件化架构的 GUI 设计方案，旨在充分发挥插件化架构的灵活性和可扩展性优势。

**文档定位**: 本文档专注于**GUI设计**，包括界面布局、交互设计、动态UI更新等。核心架构设计请参考 [插件架构设计文档](plugin_architecture_design.md)，开发指南请参考 [插件开发指南](plugin_development_guide.md)，实施计划请参考 [主重构计划](src_refactor_plan.md)。

## 🎯 设计目标

### 核心目标
- **动态性**: 支持插件的动态加载/卸载，无需重启应用
- **可配置性**: 用户可自由配置插件链和处理流程
- **可视化**: 直观展示处理流程和插件状态
- **扩展性**: 新插件可无缝集成到现有界面

### 参考案例
- **VS Code**: 插件市场、动态菜单、配置面板
- **Eclipse IDE**: 插件管理、工作台定制、视图系统
- **Figma**: 插件沙箱、动态UI、协作功能
- **GIMP**: 插件管理器、滤镜链、参数调整

## 🏗️ GUI 架构设计

### 1. 整体布局设计

```
+----------------------------------------------------------------------------------------+
|  Menu bar                                                                              |
+----------------------------------------------------------------------------------------+
|  Tool bar                                                                              |
+----------------------------------------------------------------------------------------+
+----------------------------------------------------------------------------------------+
|+--------------------+ +-------------------++------------------------------------------+|
||Plugin Manager      | |Plugin Configer    || Processing Panel                         ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   |+------------------------------------------+|
||                    | |                   |+------------------------------------------+|
||                    | |                   ||                                          ||
||                    | |                   ||                                          ||
||                    | |                   || log panel                                ||
|+--------------------+ +-------------------+|                                          ||
|+------------------------------------------+|                                          ||
|| processing flow                          ||                                          ||
||                                          ||                                          ||
||                                          ||                                          ||
||                                          ||                                          ||
||                                          ||                                          ||
||                                          ||                                          ||
|+------------------------------------------++------------------------------------------+|
+----------------------------------------------------------------------------------------+
+----------------------------------------------------------------------------------------+
|  status bar                                                                            |
+----------------------------------------------------------------------------------------+
```

### 2. 核心组件设计

#### 2.1 插件管理面板 (Plugin Management Panel)
```python
class PluginManagementPanel(QWidget):
    """插件管理面板 - 类似 vim 插件的简单管理"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 插件链配置区域
        self.chain_config = PluginChainConfigWidget()
        layout.addWidget(self.chain_config)

        # 插件管理区域
        self.plugin_management = SimplePluginManagerWidget()
        layout.addWidget(self.plugin_management)

        # 插件详情区域
        self.plugin_details = PluginDetailsWidget()
        layout.addWidget(self.plugin_details)

        self.setLayout(layout)

class SimplePluginManagerWidget(QWidget):
    """简单插件管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 插件列表
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.install_btn = QPushButton("安装插件")
        self.uninstall_btn = QPushButton("卸载选中")
        self.update_btn = QPushButton("更新选中")

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.uninstall_btn)
        button_layout.addWidget(self.update_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
```

#### 2.2 插件链配置组件 (Plugin Chain Config)
```python
class PluginChainConfigWidget(QWidget):
    """插件链配置组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 标题
        title = QLabel("处理流程配置")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # 插件链可视化
        self.chain_visualizer = PluginChainVisualizer()
        layout.addWidget(self.chain_visualizer)

        # 拖拽区域
        self.drag_area = QListWidget()
        self.drag_area.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.drag_area)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.add_plugin_btn = QPushButton("添加插件")
        self.remove_plugin_btn = QPushButton("移除插件")
        self.reset_btn = QPushButton("重置")

        button_layout.addWidget(self.add_plugin_btn)
        button_layout.addWidget(self.remove_plugin_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
```

#### 2.3 插件链可视化组件 (Plugin Chain Visualizer)
```python
class PluginChainVisualizer(QWidget):
    """插件链可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = []
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            PluginChainVisualizer {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)

    def paintEvent(self, event):
        """绘制插件链"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制插件节点和连接线
        self.draw_plugin_chain(painter)

    def draw_plugin_chain(self, painter):
        """绘制插件链"""
        if not self.plugins:
            return

        # 计算节点位置
        node_width = 80
        node_height = 40
        spacing = 20

        for i, plugin in enumerate(self.plugins):
            x = 20 + i * (node_width + spacing)
            y = (self.height() - node_height) // 2

            # 绘制插件节点
            self.draw_plugin_node(painter, x, y, node_width, node_height, plugin)

            # 绘制连接箭头
            if i < len(self.plugins) - 1:
                self.draw_arrow(painter, x + node_width, y + node_height // 2,
                              x + node_width + spacing, y + node_height // 2)

    def draw_plugin_node(self, painter, x, y, width, height, plugin):
        """绘制插件节点"""
        # 根据插件状态选择颜色
        color = QColor("#4CAF50" if plugin.enabled else "#f44336")

        # 绘制圆角矩形
        rect = QRect(x, y, width, height)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#333"), 1))
        painter.drawRoundedRect(rect, 5, 5)

        # 绘制插件名称
        painter.setPen(QPen(QColor("#fff"), 1))
        painter.drawText(rect, Qt.AlignCenter, plugin.name)

    def update_chain(self, plugins):
        """更新插件链"""
        self.plugins = plugins
        self.update()
```

#### 2.4 插件参数配置组件 (Plugin Parameters Widget)
```python
class PluginParametersWidget(QWidget):
    """插件参数配置组件"""

    def __init__(self, plugin=None, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        if not self.plugin:
            layout.addWidget(QLabel("请选择一个插件"))
            self.setLayout(layout)
            return

        # 插件标题
        title = QLabel(f"{self.plugin.name} 配置")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # 动态生成参数控件
        self.parameter_widgets = {}
        for param_name, param_config in self.plugin.get_parameters().items():
            widget = self.create_parameter_widget(param_name, param_config)
            if widget:
                layout.addWidget(widget)
                self.parameter_widgets[param_name] = widget

        # 应用按钮
        apply_btn = QPushButton("应用配置")
        apply_btn.clicked.connect(self.apply_parameters)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    def create_parameter_widget(self, name, config):
        """创建参数控件"""
        param_type = config.get("type", "string")
        default_value = config.get("default", "")
        description = config.get("description", "")

        widget = QWidget()
        layout = QHBoxLayout()

        # 参数标签
        label = QLabel(f"{name}:")
        label.setToolTip(description)
        layout.addWidget(label)

        # 根据类型创建控件
        if param_type == "boolean":
            control = QCheckBox()
            control.setChecked(default_value)
        elif param_type == "integer":
            control = QSpinBox()
            control.setRange(config.get("min", 0), config.get("max", 100))
            control.setValue(default_value)
        elif param_type == "float":
            control = QDoubleSpinBox()
            control.setRange(config.get("min", 0.0), config.get("max", 100.0))
            control.setValue(default_value)
        elif param_type == "choice":
            control = QComboBox()
            control.addItems(config.get("choices", []))
            control.setCurrentText(default_value)
        else:  # string
            control = QLineEdit()
            control.setText(str(default_value))

        layout.addWidget(control)
        widget.setLayout(layout)

        return widget

    def apply_parameters(self):
        """应用参数配置"""
        parameters = {}
        for name, widget in self.parameter_widgets.items():
            # 获取控件值并更新参数
            pass
```

## 🎨 界面设计规范

### 1. 视觉设计原则

#### 1.1 色彩方案
```css
/* 主色调 */
--primary-color: #2196F3;      /* 蓝色 - 主要操作 */
--secondary-color: #4CAF50;    /* 绿色 - 成功状态 */
--warning-color: #FF9800;      /* 橙色 - 警告 */
--error-color: #f44336;        /* 红色 - 错误 */
--neutral-color: #9E9E9E;      /* 灰色 - 中性 */

/* 背景色 */
--bg-primary: #FFFFFF;         /* 主背景 */
--bg-secondary: #F5F5F5;       /* 次背景 */
--bg-tertiary: #EEEEEE;        /* 三级背景 */

/* 文字色 */
--text-primary: #212121;       /* 主要文字 */
--text-secondary: #757575;     /* 次要文字 */
--text-disabled: #BDBDBD;      /* 禁用文字 */
```

#### 1.2 组件样式
```css
/* 插件节点样式 */
.plugin-node {
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.plugin-node.enabled {
    background-color: var(--secondary-color);
    color: white;
    box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.plugin-node.disabled {
    background-color: var(--neutral-color);
    color: white;
    opacity: 0.6;
}

.plugin-node:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* 连接线样式 */
.plugin-connection {
    stroke: var(--primary-color);
    stroke-width: 2;
    fill: none;
    marker-end: url(#arrowhead);
}

/* 参数控件样式 */
.parameter-group {
    border: 1px solid var(--bg-tertiary);
    border-radius: 4px;
    padding: 12px;
    margin: 8px 0;
    background-color: var(--bg-primary);
}
```

### 2. 交互设计

#### 2.1 拖拽操作
- **插件添加**: 从插件库拖拽到插件链
- **顺序调整**: 在插件链中拖拽调整顺序
- **参数复制**: 拖拽参数配置到其他插件

#### 2.2 实时反馈
- **处理进度**: 实时显示每个插件的处理进度
- **状态指示**: 插件启用/禁用状态的可视化
- **错误提示**: 插件错误的即时反馈

#### 2.3 快捷操作
- **键盘快捷键**: 常用操作的快捷键支持
- **右键菜单**: 插件的上下文菜单
- **批量操作**: 多选插件的批量配置

## 🔧 技术实现

### 1. 动态UI更新机制

```python
class DynamicUIManager:
    """动态UI管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.plugin_registry = PluginRegistry()
        self.ui_components = {}

    def register_plugin_ui(self, plugin_name, ui_component):
        """注册插件UI组件"""
        self.ui_components[plugin_name] = ui_component

    def update_plugin_chain_ui(self, plugin_chain):
        """更新插件链UI"""
        # 更新插件链可视化
        self.main_window.plugin_chain_visualizer.update_chain(plugin_chain)

        # 更新工具栏
        self.update_toolbar(plugin_chain)

        # 更新菜单
        self.update_menu(plugin_chain)

    def update_toolbar(self, plugin_chain):
        """更新工具栏"""
        toolbar = self.main_window.toolbar
        toolbar.clear()

        for plugin in plugin_chain:
            if plugin.has_toolbar_actions():
                actions = plugin.get_toolbar_actions()
                for action in actions:
                    toolbar.addAction(action)

    def update_menu(self, plugin_chain):
        """更新菜单"""
        menu = self.main_window.menuBar()

        # 清除插件菜单
        for action in menu.actions():
            if hasattr(action, 'is_plugin_menu') and action.is_plugin_menu:
                menu.removeAction(action)

        # 添加插件菜单
        for plugin in plugin_chain:
            if plugin.has_menu_items():
                menu_items = plugin.get_menu_items()
                self.add_menu_items(menu, menu_items)
```

### 2. 插件UI接口

```python
class PluginUIInterface:
    """插件UI接口"""

    def get_toolbar_actions(self) -> List[QAction]:
        """获取工具栏操作"""
        return []

    def get_menu_items(self) -> List[Dict]:
        """获取菜单项"""
        return []

    def get_parameters_widget(self) -> QWidget:
        """获取参数配置控件"""
        return None

    def get_status_widget(self) -> QWidget:
        """获取状态显示控件"""
        return None

    def on_plugin_enabled(self):
        """插件启用时的回调"""
        pass

    def on_plugin_disabled(self):
        """插件禁用时的回调"""
        pass
```

### 3. 事件系统

```python
class PluginEventSystem:
    """插件事件系统"""

    def __init__(self):
        self.listeners = {}

    def register_listener(self, event_type, callback):
        """注册事件监听器"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit_event(self, event_type, data=None):
        """发送事件"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Event callback error: {e}")

    def unregister_listener(self, event_type, callback):
        """取消注册事件监听器"""
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

# 事件类型定义
class PluginEvents:
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"
    PLUGIN_ENABLED = "plugin_enabled"
    PLUGIN_DISABLED = "plugin_disabled"
    PLUGIN_CHAIN_CHANGED = "plugin_chain_changed"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_ERROR = "processing_error"
```

## 📱 响应式设计

### 1. 布局适配

```python
class ResponsiveLayout(QVBoxLayout):
    """响应式布局"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.breakpoints = {
            "mobile": 480,
            "tablet": 768,
            "desktop": 1024,
            "large": 1440
        }
        self.current_breakpoint = "desktop"

    def update_layout(self, width):
        """根据宽度更新布局"""
        if width < self.breakpoints["mobile"]:
            self.set_mobile_layout()
        elif width < self.breakpoints["tablet"]:
            self.set_tablet_layout()
        elif width < self.breakpoints["desktop"]:
            self.set_desktop_layout()
        else:
            self.set_large_layout()

    def set_mobile_layout(self):
        """移动端布局"""
        # 垂直堆叠，隐藏侧边栏
        pass

    def set_tablet_layout(self):
        """平板端布局"""
        # 可折叠侧边栏
        pass

    def set_desktop_layout(self):
        """桌面端布局"""
        # 标准布局
        pass

    def set_large_layout(self):
        """大屏布局"""
        # 扩展布局，显示更多信息
        pass
```

## 📝 相关文档

### 插件开发指南
详细的插件开发规范、实现示例和使用流程请参考：
**[插件开发指南文档](plugin_development_guide.md)**

### 插件架构设计
核心架构设计、接口定义和配置系统请参考：
**[插件架构设计文档](plugin_architecture_design.md)**

## 🚀 高级特性

### 1. 插件性能监控

```python
class PluginPerformanceMonitor(QWidget):
    """插件性能监控组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.performance_data = {}

    def setup_ui(self):
        layout = QVBoxLayout()

        # 性能图表
        self.performance_chart = QChart()
        self.chart_view = QChartView(self.performance_chart)
        layout.addWidget(self.chart_view)

        # 性能指标
        self.metrics_widget = QTableWidget()
        self.metrics_widget.setColumnCount(3)
        self.metrics_widget.setHorizontalHeaderLabels(["插件", "执行时间", "内存使用"])
        layout.addWidget(self.metrics_widget)

        self.setLayout(layout)

    def update_performance_data(self, plugin_name, execution_time, memory_usage):
        """更新性能数据"""
        self.performance_data[plugin_name] = {
            "execution_time": execution_time,
            "memory_usage": memory_usage
        }
        self.refresh_display()
```

## 📋 实施计划

### 阶段1: 基础框架 (2-3天)
- 实现插件管理面板基础结构
- 实现插件链可视化组件
- 建立动态UI更新机制

### 阶段2: 核心功能 (3-4天)
- 实现插件参数配置界面
- 实现拖拽操作支持
- 实现事件系统

### 阶段3: 高级特性 (2-3天)
- 实现插件市场集成
- 实现性能监控
- 实现响应式设计

### 阶段4: 优化完善 (1-2天)
- 界面美化优化
- 用户体验改进
- 性能优化

## 🎯 总结

这个GUI设计方案充分考虑了插件化架构的特点，提供了：

1. **动态性**: 支持插件的动态加载和UI更新
2. **可视化**: 直观的插件链配置和处理流程展示
3. **可配置性**: 丰富的参数配置和界面定制选项
4. **扩展性**: 新插件可无缝集成到现有界面
5. **用户友好**: 直观的操作界面和实时反馈

通过这样的设计，用户可以充分发挥插件化架构的优势，灵活配置处理流程，获得最佳的使用体验。

---

**注意**: 此GUI设计需要与插件化架构设计配合实施，确保架构和界面的完美结合。
