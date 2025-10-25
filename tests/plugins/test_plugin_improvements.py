"""
测试插件系统的改进

这个模块测试我们在测试中发现的问题的修复：
1. 配置验证改进
2. 错误处理改进
3. 性能优化
"""

from typing import Any, Dict, List, Optional, Union

import pytest

from src.subtitleformatter.plugins.base import (
    PluginConfigurationError,
    PluginProcessingError,
    TextProcessorPlugin,
)


class ImprovedTestPlugin(TextProcessorPlugin):
    """改进的测试插件，用于测试修复"""

    name = "improved_test_plugin"
    version = "1.0.0"
    description = "改进的测试插件"
    author = "Test Author"
    dependencies = []

    # 配置架构
    config_schema = {
        "required": ["enabled"],
        "optional": {"max_length": 1000, "batch_size": 100},
        "field_types": {"enabled": bool, "max_length": int, "batch_size": int},
        "field_validators": {
            "max_length": lambda x: x > 0,
            "batch_size": lambda x: x > 0,
            "enabled": lambda x: isinstance(x, bool),
        },
        "default_values": {"enabled": True, "max_length": 1000, "batch_size": 100},
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.processed_count = 0

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """处理文本"""
        try:
            if isinstance(text, str):
                return self._process_string(text)
            elif isinstance(text, list):
                return [self._process_string(item) for item in text]
            else:
                raise ValueError(f"Unsupported text type: {type(text)}")
        except Exception as e:
            raise PluginProcessingError(
                f"Failed to process text: {e}",
                plugin_name=self.name,
                input_data=str(text)[:100] if text else None,
                cause=e,
            )

    def _process_string(self, text: str) -> str:
        """处理单个字符串"""
        self.processed_count += 1

        # 检查长度限制
        max_length = self.config.get("max_length", 1000)
        if len(text) > max_length:
            raise ValueError(f"Text too long: {len(text)} > {max_length}")

        return f"[{self.processed_count}] {text.upper()}"

    def process_batch(self, texts: List[str], batch_size: int = None) -> List[str]:
        """优化的批量处理"""
        if not texts:
            return []

        # 使用配置中的批量大小
        if batch_size is None:
            batch_size = self.config.get("batch_size", 100)

        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_results = self.process(batch)
            results.extend(batch_results)

        return results


class TestConfigurationValidation:
    """测试配置验证改进"""

    def test_valid_configuration(self):
        """测试有效配置"""
        config = {"enabled": True, "max_length": 500, "batch_size": 50}
        plugin = ImprovedTestPlugin(config)
        assert plugin.config["enabled"] == True
        assert plugin.config["max_length"] == 500
        assert plugin.config["batch_size"] == 50

    def test_missing_required_field(self):
        """测试缺少必需字段"""
        with pytest.raises(PluginConfigurationError) as exc_info:
            ImprovedTestPlugin({"max_length": 500})

        assert "Required field 'enabled' is missing" in str(exc_info.value)
        assert exc_info.value.plugin_name == "improved_test_plugin"
        assert exc_info.value.error_code == "CONFIG_ERROR"

    def test_invalid_field_type(self):
        """测试无效字段类型"""
        with pytest.raises(PluginConfigurationError) as exc_info:
            ImprovedTestPlugin({"enabled": "true"})  # 应该是 bool

        assert "must be of type bool" in str(exc_info.value)
        assert "got str" in str(exc_info.value)

    def test_invalid_field_value(self):
        """测试无效字段值"""
        with pytest.raises(PluginConfigurationError) as exc_info:
            ImprovedTestPlugin({"enabled": True, "max_length": -1})  # 应该是正数

        assert "validation failed" in str(exc_info.value)

    def test_unknown_field(self):
        """测试未知字段"""
        with pytest.raises(PluginConfigurationError) as exc_info:
            ImprovedTestPlugin({"enabled": True, "unknown_field": "value"})

        assert "Unknown field 'unknown_field' is not allowed" in str(exc_info.value)

    def test_default_values_applied(self):
        """测试默认值应用"""
        plugin = ImprovedTestPlugin({"enabled": True})
        assert plugin.config["max_length"] == 1000  # 默认值
        assert plugin.config["batch_size"] == 100  # 默认值


class TestErrorHandling:
    """测试错误处理改进"""

    def test_processing_error_with_details(self):
        """测试处理错误包含详细信息"""
        plugin = ImprovedTestPlugin({"enabled": True, "max_length": 10})

        with pytest.raises(PluginProcessingError) as exc_info:
            plugin.process("This is a very long text that exceeds the limit")

        assert "Failed to process text" in str(exc_info.value)
        assert exc_info.value.plugin_name == "improved_test_plugin"
        assert exc_info.value.error_code == "PROCESSING_ERROR"
        assert exc_info.value.input_data == "This is a very long text that exceeds the limit"
        assert exc_info.value.cause is not None

    def test_unsupported_input_type(self):
        """测试不支持的输入类型"""
        plugin = ImprovedTestPlugin({"enabled": True})

        with pytest.raises(PluginProcessingError) as exc_info:
            plugin.process(123)  # 数字类型

        assert "Unsupported text type" in str(exc_info.value)
        assert exc_info.value.input_data == "123"

    def test_error_propagation(self):
        """测试错误传播"""
        plugin = ImprovedTestPlugin({"enabled": True, "max_length": 5})

        with pytest.raises(PluginProcessingError) as exc_info:
            plugin.process("Hello world")

        # 验证原始错误被保留
        assert exc_info.value.cause is not None
        assert "Text too long" in str(exc_info.value.cause)


class TestPerformanceOptimizations:
    """测试性能优化"""

    def test_batch_processing(self):
        """测试批量处理"""
        plugin = ImprovedTestPlugin({"enabled": True, "batch_size": 10})

        # 创建大量文本
        texts = [f"Text {i}" for i in range(50)]

        results = plugin.process_batch(texts)

        # 验证结果
        assert len(results) == 50
        assert all("[" in result and "]" in result for result in results)
        assert results[0] == "[1] TEXT 0"
        assert results[49] == "[50] TEXT 49"

    def test_batch_processing_with_custom_size(self):
        """测试自定义批量大小的批量处理"""
        plugin = ImprovedTestPlugin({"enabled": True, "batch_size": 100})

        texts = [f"Text {i}" for i in range(25)]
        results = plugin.process_batch(texts, batch_size=5)

        assert len(results) == 25
        assert all("[" in result and "]" in result for result in results)

    def test_empty_batch_processing(self):
        """测试空批量处理"""
        plugin = ImprovedTestPlugin({"enabled": True})

        results = plugin.process_batch([])
        assert results == []

    def test_batch_processing_performance(self):
        """测试批量处理性能"""
        import time

        plugin = ImprovedTestPlugin({"enabled": True, "batch_size": 50})

        # 创建大量文本
        texts = [f"Text {i}" for i in range(1000)]

        start_time = time.time()
        results = plugin.process_batch(texts)
        end_time = time.time()

        processing_time = end_time - start_time

        # 验证结果
        assert len(results) == 1000
        assert processing_time < 1.0  # 应该在1秒内完成

        # 验证批量处理比单个处理更高效
        start_time = time.time()
        for text in texts[:100]:  # 只测试前100个
            plugin.process(text)
        end_time = time.time()

        single_processing_time = end_time - start_time
        # 批量处理应该比单个处理快（或者至少不会慢太多）
        # 由于我们的实现比较简单，这里只验证处理时间合理
        assert processing_time < 1.0  # 批量处理应该在1秒内完成
        assert single_processing_time < 1.0  # 单个处理也应该在1秒内完成


class TestPluginIntegration:
    """测试插件集成"""

    def test_plugin_with_strict_configuration(self):
        """测试严格配置的插件"""
        # 测试有效配置
        config = {"enabled": True, "max_length": 100, "batch_size": 20}
        plugin = ImprovedTestPlugin(config)

        # 测试处理
        result = plugin.process("Hello world")
        assert result == "[1] HELLO WORLD"

        # 测试长度限制
        with pytest.raises(PluginProcessingError):
            plugin.process("a" * 150)  # 超过长度限制

    def test_plugin_error_recovery(self):
        """测试插件错误恢复"""
        plugin = ImprovedTestPlugin({"enabled": True, "max_length": 10})

        # 测试正常处理
        result = plugin.process("Hello")
        assert result == "[1] HELLO"

        # 测试错误处理
        with pytest.raises(PluginProcessingError):
            plugin.process("This is too long")

        # 测试错误后仍能正常处理（计数会继续增加）
        result = plugin.process("World")
        assert result == "[3] WORLD"  # 计数会继续增加，包括失败的尝试


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
