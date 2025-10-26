"""
插件配置面板组件

提供插件参数的动态配置界面
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.plugins import PluginRegistry
from subtitleformatter.utils.unified_logger import logger


class PluginConfigPanel(QWidget):
    """
    插件配置面板

    功能:
    - 动态生成插件参数配置界面
    - 支持多种参数类型（字符串、数字、布尔值、选择等）
    - 实时配置验证和保存
    """

    configChanged = Signal(str, dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_plugin: Optional[str] = None
        self.plugin_registry: Optional[PluginRegistry] = None
        self.parameter_widgets: Dict[str, QWidget] = {}
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 标题
        title = QLabel("Plugin Configuration")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2196F3;")
        layout.addWidget(title)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 配置内容区域
        self.config_content = QWidget()
        self.config_layout = QVBoxLayout(self.config_content)
        self.config_layout.setContentsMargins(8, 8, 8, 8)
        self.config_layout.setSpacing(12)
        # 设置布局策略，不拉伸子控件
        self.config_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.config_content)
        layout.addWidget(scroll_area)

        # 操作按钮
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply Configuration")
        self.apply_btn.clicked.connect(self.apply_configuration)
        self.apply_btn.setEnabled(False)

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setEnabled(False)

        self.export_btn = QPushButton("Export Config")
        self.export_btn.clicked.connect(self.export_configuration)
        self.export_btn.setEnabled(False)

        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

        # 设置布局
        self.setLayout(layout)

    def set_plugin_registry(self, registry: PluginRegistry):
        """设置插件注册表"""
        self.plugin_registry = registry

    def load_plugin_config(self, plugin_name: str):
        """加载插件配置"""
        self.current_plugin = plugin_name
        self.clear_config_ui()

        if not self.plugin_registry:
            self.show_no_registry_message()
            return

        try:
            # 获取插件元数据
            metadata = self.plugin_registry.get_plugin_metadata(plugin_name)
            if not metadata:
                self.show_plugin_not_found_message(plugin_name)
                return

            # 获取配置模式
            config_schema = metadata.get("config_schema")
            if not config_schema:
                self.show_no_config_schema_message(plugin_name)
                return

            # 生成配置界面
            self.generate_config_ui(config_schema, metadata)

            # 启用按钮
            self.apply_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.export_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"❌ Failed to load plugin config for {plugin_name}: {e}")
            self.show_error_message(f"Failed to load configuration: {e}")

    def clear_config_ui(self):
        """清空配置界面"""
        # 清空参数控件
        self.parameter_widgets.clear()

        # 清空布局
        while self.config_layout.count():
            child = self.config_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 禁用按钮
        self.apply_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

    def generate_config_ui(self, config_schema: Dict[str, Any], metadata: Dict[str, Any]):
        """生成配置界面"""
        properties = config_schema.get("properties", {})

        if not properties:
            self.show_no_properties_message()
            return

        # 添加插件信息
        self.add_plugin_info(metadata)

        # 为每个属性创建配置控件
        for prop_name, prop_config in properties.items():
            self.create_parameter_widget(prop_name, prop_config)

    def add_plugin_info(self, metadata: Dict[str, Any]):
        """添加插件信息"""
        info_group = QGroupBox()
        info_layout = QFormLayout(info_group)

        info_layout.addRow("Name:", QLabel(metadata.get("name", "Unknown")))
        info_layout.addRow("Version:", QLabel(metadata.get("version", "Unknown")))
        info_layout.addRow("Author:", QLabel(metadata.get("author", "Unknown")))

        description = metadata.get("description", "No description available")
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addRow("Description:", desc_label)

        self.config_layout.addWidget(info_group)

    def create_parameter_widget(self, param_name: str, param_config: Dict[str, Any]):
        """创建参数控件"""
        param_type = param_config.get("type", "string")
        default_value = param_config.get("default", "")
        description = param_config.get("description", "")

        # 创建控件
        widget = self.create_control_by_type(param_type, param_config, default_value, param_name)
        if widget:
            # 为每个配置项创建容器，添加适当的间隔
            item_container = QWidget()
            item_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            item_layout = QVBoxLayout(item_container)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)
            item_layout.setAlignment(Qt.AlignTop)

            if param_type == "boolean":
                # 复选框直接添加
                item_layout.addWidget(widget)
            else:
                # 其他类型创建标签+控件的水平布局
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)

                label = QLabel(f"{param_name}:")
                label.setMinimumWidth(120)
                row_layout.addWidget(label)
                row_layout.addWidget(widget)

                item_layout.addWidget(row_widget)

            # 添加描述
            if description:
                desc_label = QLabel(description)
                desc_label.setStyleSheet("color: #666; font-size: 11px;")
                desc_label.setWordWrap(True)
                item_layout.addWidget(desc_label)

            # 将整个配置项容器添加到主布局
            self.config_layout.addWidget(item_container)

            # 添加配置项之间的间隔
            spacer = QWidget()
            spacer.setFixedHeight(8)
            spacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.config_layout.addWidget(spacer)

            self.parameter_widgets[param_name] = widget

    def create_control_by_type(
        self, param_type: str, param_config: Dict[str, Any], default_value: Any, param_name: str
    ) -> Optional[QWidget]:
        """根据类型创建控件"""
        if param_type == "boolean":
            control = QCheckBox()
            control.setChecked(bool(default_value))
            # 为复选框设置文本标签
            control.setText(param_name.replace("_", " ").title())
            return control

        elif param_type == "integer":
            control = QSpinBox()
            control.setRange(
                param_config.get("minimum", -999999), param_config.get("maximum", 999999)
            )
            control.setValue(int(default_value) if default_value != "" else 0)
            return control

        elif param_type == "number":
            control = QDoubleSpinBox()
            control.setRange(
                param_config.get("minimum", -999999.0), param_config.get("maximum", 999999.0)
            )
            control.setDecimals(param_config.get("decimals", 2))
            control.setValue(float(default_value) if default_value != "" else 0.0)
            return control

        elif param_type == "string":
            if "enum" in param_config:
                # 枚举类型使用下拉框
                control = QComboBox()
                control.addItems(param_config["enum"])
                if default_value in param_config["enum"]:
                    control.setCurrentText(default_value)
                return control
            else:
                # 普通字符串使用文本框
                control = QLineEdit()
                control.setText(str(default_value))
                return control

        elif param_type == "array":
            # 数组类型使用文本框（JSON格式）
            control = QTextEdit()
            control.setMaximumHeight(100)
            if isinstance(default_value, list):
                control.setText(json.dumps(default_value, indent=2))
            else:
                control.setText(str(default_value))
            return control

        elif param_type == "object":
            # 对象类型使用文本框（JSON格式）
            control = QTextEdit()
            control.setMaximumHeight(150)
            if isinstance(default_value, dict):
                control.setText(json.dumps(default_value, indent=2))
            else:
                control.setText(str(default_value))
            return control

        else:
            # 未知类型使用文本框
            control = QLineEdit()
            control.setText(str(default_value))
            return control

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        config = {}

        for param_name, widget in self.parameter_widgets.items():
            try:
                if isinstance(widget, QCheckBox):
                    config[param_name] = widget.isChecked()
                elif isinstance(widget, QSpinBox):
                    config[param_name] = widget.value()
                elif isinstance(widget, QDoubleSpinBox):
                    config[param_name] = widget.value()
                elif isinstance(widget, QComboBox):
                    config[param_name] = widget.currentText()
                elif isinstance(widget, QLineEdit):
                    config[param_name] = widget.text()
                elif isinstance(widget, QTextEdit):
                    text = widget.toPlainText()
                    try:
                        # 尝试解析JSON
                        config[param_name] = json.loads(text)
                    except json.JSONDecodeError:
                        # 如果解析失败，使用原始文本
                        config[param_name] = text
            except Exception as e:
                logger.warning(f"⚠️ Failed to get value for parameter {param_name}: {e}")
                config[param_name] = None

        return config

    def apply_configuration(self):
        """应用配置"""
        if not self.current_plugin:
            return

        try:
            config = self.get_current_config()
            self.configChanged.emit(self.current_plugin, config)
            logger.info(f"Applied configuration for plugin '{self.current_plugin}'")
        except Exception as e:
            logger.error(f"Failed to apply configuration: {e}")

    def reset_to_defaults(self):
        """重置为默认值"""
        if not self.current_plugin or not self.plugin_registry:
            return

        try:
            # 重新加载插件配置
            self.load_plugin_config(self.current_plugin)
            logger.info(f"Reset configuration for plugin '{self.current_plugin}' to defaults")
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")

    def export_configuration(self):
        """导出配置"""
        if not self.current_plugin:
            return

        try:
            config = self.get_current_config()
            config_json = json.dumps(config, indent=2)

            # 这里可以添加文件保存对话框
            logger.info(
                f"Exported configuration for plugin '{self.current_plugin}':\n{config_json}"
            )
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")

    def show_no_registry_message(self):
        """显示无注册表消息"""
        label = QLabel("Plugin registry not available")
        label.setStyleSheet("color: #f44336; font-style: italic;")
        self.config_layout.addWidget(label)

    def show_plugin_not_found_message(self, plugin_name: str):
        """显示插件未找到消息"""
        label = QLabel(f"Plugin '{plugin_name}' not found")
        label.setStyleSheet("color: #f44336; font-style: italic;")
        self.config_layout.addWidget(label)

    def show_no_config_schema_message(self, plugin_name: str):
        """显示无配置模式消息"""
        label = QLabel(f"Plugin '{plugin_name}' has no configuration schema")
        label.setStyleSheet("color: #FF9800; font-style: italic;")
        self.config_layout.addWidget(label)

    def show_no_properties_message(self):
        """显示无属性消息"""
        label = QLabel("No configurable properties available")
        label.setStyleSheet("color: #FF9800; font-style: italic;")
        self.config_layout.addWidget(label)

    def show_error_message(self, message: str):
        """显示错误消息"""
        label = QLabel(message)
        label.setStyleSheet("color: #f44336; font-style: italic;")
        self.config_layout.addWidget(label)
