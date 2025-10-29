"""
测试插件接口和基类功能

这个模块测试插件系统的核心功能，包括：
- 插件基类功能
- 插件接口协议
- 配置管理
- 依赖注入
"""

from typing import Any, Dict, List, Optional, Union

import pytest

from src.subtitleformatter.plugins.base import (
    ConfigurableProtocol,
    DependencyAwareProtocol,
    LifecycleProtocol,
    MetadataProtocol,
    PluginConfigManager,
    PluginConfigSchema,
    PluginConfigurationError,
    PluginDependencyError,
    PluginError,
    PluginTypeValidator,
    TextProcessorPlugin,
    TextProcessorProtocol,
)


class TestPluginImpl(TextProcessorPlugin):
    """测试用的插件类"""

    name = "test_plugin"
    version = "1.0.0"
    description = "测试插件"
    author = "Test Author"
    dependencies = []

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.processed_count = 0

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """处理文本"""
        self.processed_count += 1
        if isinstance(text, str):
            return f"processed: {text}"
        elif isinstance(text, list):
            return [f"processed: {item}" for item in text]
        else:
            raise ValueError(f"Unsupported text type: {type(text)}")


class TestPluginBase:
    """测试插件基类功能"""

    def test_plugin_initialization(self):
        """测试插件初始化"""
        plugin = TestPluginImpl()

        # 检查基本属性
        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "测试插件"
        assert plugin.author == "Test Author"
        assert plugin.dependencies == []

        # 检查初始化状态
        assert not plugin.is_initialized()
        assert plugin.processed_count == 0

    def test_plugin_with_config(self):
        """测试带配置的插件初始化"""
        config = {"enabled": True, "custom_option": "test"}
        plugin = TestPluginImpl(config)

        assert plugin.config["enabled"] == True
        assert plugin.config["custom_option"] == "test"

    def test_text_processing_string(self):
        """测试字符串处理"""
        plugin = TestPluginImpl()

        result = plugin.process("hello")
        assert result == "processed: hello"
        assert plugin.processed_count == 1

    def test_text_processing_list(self):
        """测试列表处理"""
        plugin = TestPluginImpl()

        result = plugin.process(["hello", "world"])
        assert result == ["processed: hello", "processed: world"]
        assert plugin.processed_count == 1

    def test_text_processing_invalid_type(self):
        """测试无效类型处理"""
        plugin = TestPluginImpl()

        with pytest.raises(ValueError):
            plugin.process(123)  # 数字类型

    def test_plugin_lifecycle(self):
        """测试插件生命周期"""
        plugin = TestPluginImpl()

        # 初始化
        assert not plugin.is_initialized()
        plugin.initialize()
        assert plugin.is_initialized()

        # 清理
        plugin.cleanup()
        assert not plugin.is_initialized()

    def test_plugin_info(self):
        """测试插件信息获取"""
        plugin = TestPluginImpl()

        info = plugin.get_info()
        assert info["name"] == "test_plugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "测试插件"
        assert info["author"] == "Test Author"
        assert info["initialized"] == False


class TestPluginInterfaces:
    """测试插件接口协议"""

    def test_text_processor_protocol(self):
        """测试文本处理协议"""
        plugin = TestPluginImpl()

        # 检查是否实现了协议
        assert isinstance(plugin, TextProcessorProtocol)

        # 测试协议方法
        result = plugin.process("test")
        assert result == "processed: test"

    def test_configurable_protocol(self):
        """测试可配置协议"""
        plugin = TestPluginImpl()

        # 检查是否实现了协议
        assert isinstance(plugin, ConfigurableProtocol)

        # 测试配置方法
        config = {"enabled": True}
        plugin.set_config(config)
        assert plugin.get_config()["enabled"] == True

        # 测试配置验证
        assert plugin.validate_config(config) == True

    def test_dependency_aware_protocol(self):
        """测试依赖感知协议"""
        plugin = TestPluginImpl()

        # 检查是否实现了协议
        assert isinstance(plugin, DependencyAwareProtocol)

        # 测试依赖方法
        plugin.set_dependency("test_service", "test_value")
        assert plugin.has_dependency("test_service") == True
        assert plugin.get_dependency("test_service") == "test_value"

        # 测试不存在的依赖
        assert plugin.has_dependency("nonexistent") == False
        with pytest.raises(KeyError):
            plugin.get_dependency("nonexistent")

    def test_lifecycle_protocol(self):
        """测试生命周期协议"""
        plugin = TestPluginImpl()

        # 检查是否实现了协议
        assert isinstance(plugin, LifecycleProtocol)

        # 测试生命周期方法
        assert plugin.is_initialized() == False
        plugin.initialize()
        assert plugin.is_initialized() == True
        plugin.cleanup()
        assert plugin.is_initialized() == False

    def test_metadata_protocol(self):
        """测试元数据协议"""
        plugin = TestPluginImpl()

        # 检查是否实现了协议
        assert isinstance(plugin, MetadataProtocol)

        # 测试元数据属性
        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "测试插件"
        assert plugin.author == "Test Author"

        # 测试信息获取
        info = plugin.get_info()
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "author" in info


class TestPluginTypeValidator:
    """测试插件类型验证器"""

    def test_validate_plugin_class(self):
        """测试插件类验证"""
        # 测试有效插件类
        errors = PluginTypeValidator.validate_plugin_class(TestPluginImpl)
        assert len(errors) == 0

        # 测试无效插件类
        class InvalidPlugin:
            pass

        errors = PluginTypeValidator.validate_plugin_class(InvalidPlugin)
        assert len(errors) > 0
        assert "must inherit from TextProcessorPlugin" in errors[0]

    def test_validate_plugin_instance(self):
        """测试插件实例验证"""
        plugin = TestPluginImpl()

        # 测试有效插件实例
        errors = PluginTypeValidator.validate_plugin_instance(plugin)
        assert len(errors) == 0

        # 测试无效插件实例
        errors = PluginTypeValidator.validate_plugin_instance("not a plugin")
        assert len(errors) > 0

    def test_is_valid_plugin_class(self):
        """测试插件类有效性检查"""
        assert PluginTypeValidator.is_valid_plugin_class(TestPluginImpl) == True

        class InvalidPlugin:
            pass

        assert PluginTypeValidator.is_valid_plugin_class(InvalidPlugin) == False

    def test_is_valid_plugin_instance(self):
        """测试插件实例有效性检查"""
        plugin = TestPluginImpl()
        assert PluginTypeValidator.is_valid_plugin_instance(plugin) == True
        assert PluginTypeValidator.is_valid_plugin_instance("not a plugin") == False


class TestPluginConfigSchema:
    """测试插件配置架构"""

    def test_config_schema_creation(self):
        """测试配置架构创建"""
        schema = PluginConfigSchema(
            required_fields=["enabled"],
            optional_fields={"option1": "default"},
            field_types={"enabled": bool, "option1": str},
            default_values={"enabled": True, "option1": "default"},
        )

        assert schema.required_fields == ["enabled"]
        assert schema.optional_fields == {"option1": "default"}
        assert schema.field_types["enabled"] == bool
        assert schema.default_values["enabled"] == True

    def test_config_validation(self):
        """测试配置验证"""
        schema = PluginConfigSchema(
            required_fields=["enabled"],
            field_types={"enabled": bool},
            field_validators={"enabled": lambda x: isinstance(x, bool)},
        )

        # 测试有效配置
        config = {"enabled": True}
        errors = schema.validate(config)
        assert len(errors) == 0

        # 测试缺少必需字段
        config = {}
        errors = schema.validate(config)
        assert len(errors) == 1
        assert "Required field 'enabled' is missing" in errors[0]

        # 测试类型错误
        config = {"enabled": "true"}
        errors = schema.validate(config)
        assert len(errors) == 1
        assert "must be of type bool" in errors[0]

    def test_apply_defaults(self):
        """测试默认值应用"""
        schema = PluginConfigSchema(default_values={"enabled": True, "option1": "default"})

        config = {"option2": "custom"}
        result = schema.apply_defaults(config)

        assert result["enabled"] == True
        assert result["option1"] == "default"
        assert result["option2"] == "custom"


class TestPluginConfigManager:
    """测试插件配置管理器"""

    def test_config_manager_creation(self):
        """测试配置管理器创建"""
        manager = PluginConfigManager()
        assert isinstance(manager, PluginConfigManager)

    def test_schema_registration(self):
        """测试架构注册"""
        manager = PluginConfigManager()
        schema = PluginConfigSchema(required_fields=["enabled"])

        manager.register_schema("test_plugin", schema)
        assert "test_plugin" in manager._schemas

    def test_config_validation(self):
        """测试配置验证"""
        manager = PluginConfigManager()
        schema = PluginConfigSchema(required_fields=["enabled"])
        manager.register_schema("test_plugin", schema)

        # 测试有效配置
        config = {"enabled": True}
        errors = manager.validate_config("test_plugin", config)
        assert len(errors) == 0

        # 测试无效配置
        config = {}
        errors = manager.validate_config("test_plugin", config)
        assert len(errors) == 1

    def test_config_storage(self):
        """测试配置存储"""
        manager = PluginConfigManager()

        config = {"enabled": True}
        manager.set_config("test_plugin", config)

        stored_config = manager.get_config("test_plugin")
        assert stored_config == config

        # 测试不存在的配置
        assert manager.get_config("nonexistent") is None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
