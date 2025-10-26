"""
示例插件：简单的大写转换器

这个插件演示了如何创建一个基本的文本处理插件。
"""

from typing import Any, Dict, List, Optional, Union

from subtitleformatter.plugins.base import TextProcessorPlugin


class SimpleUppercasePlugin(TextProcessorPlugin):
    """
    简单的大写转换插件

    这个插件将输入的文本转换为大写字母。
    主要用于演示插件开发的基本流程。
    """

    # 插件元数据
    name = "simple_uppercase"
    version = "1.0.0"
    description = "将文本转换为大写字母的简单插件"
    author = "SubtitleFormatter Team"
    dependencies = []

    # 配置架构
    config_schema = {
        "required": ["enabled"],
        "optional": {"preserve_spaces": True, "max_length": 10000},
        "field_types": {"enabled": bool, "preserve_spaces": bool, "max_length": int},
        "field_validators": {
            "max_length": lambda x: x > 0,
            "enabled": lambda x: isinstance(x, bool),
        },
        "default_values": {"enabled": True, "preserve_spaces": True, "max_length": 10000},
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化插件"""
        super().__init__(config)

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        处理输入文本，将其转换为大写

        Args:
            text: 输入文本（字符串或字符串列表）

        Returns:
            转换为大写的文本（与输入类型相同）

        Raises:
            PluginProcessingError: 当处理失败时
        """
        try:
            if isinstance(text, str):
                return self._process_string(text)
            elif isinstance(text, list):
                return [self._process_string(item) for item in text]
            else:
                raise ValueError(f"Unsupported text type: {type(text)}")
        except Exception as e:
            from .plugin_base import PluginProcessingError

            raise PluginProcessingError(
                f"Failed to process text: {e}",
                plugin_name=self.name,
                input_data=str(text)[:100] if text else None,
                cause=e,
            )

    def _process_string(self, text: str) -> str:
        """处理单个字符串"""
        # 检查插件是否启用
        if not self.config.get("enabled", True):
            return text

        # 检查长度限制
        max_length = self.config.get("max_length", 10000)
        if len(text) > max_length:
            raise ValueError(f"Text too long: {len(text)} > {max_length}")

        # 转换为大写
        result = text.upper()

        # 如果不需要保留空格，可以进一步处理
        if not self.config.get("preserve_spaces", True):
            result = result.replace(" ", "")

        return result

    def initialize(self) -> None:
        """初始化插件"""
        super().initialize()
        print(f"插件 {self.name} 已初始化")

    def cleanup(self) -> None:
        """清理插件资源"""
        super().cleanup()
        print(f"插件 {self.name} 已清理")
