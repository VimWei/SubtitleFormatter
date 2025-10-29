"""
Tests for PluginConfigManager.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from subtitleformatter.plugins import PluginConfigManager


class TestPluginConfigManager:
    """Test cases for PluginConfigManager."""

    def test_config_manager_creation(self):
        """Test config manager creation."""
        config_manager = PluginConfigManager()

        assert config_manager.config_dir == Path("data/configs")
        assert config_manager._configs == {}
        assert config_manager._default_configs == {}
        assert config_manager._config_schema is None

    def test_config_manager_creation_with_dir(self):
        """Test config manager creation with custom directory."""
        custom_dir = Path("custom/config")
        config_manager = PluginConfigManager(custom_dir)

        assert config_manager.config_dir == custom_dir

    def test_load_plugin_config_existing_file(self):
        """Test loading plugin config from existing file."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            # Create config file
            config_file = config_dir / "test_plugin.toml"
            config_data = {"enabled": True, "param1": "value1"}

            with open(config_file, "wb") as f:
                import tomli_w

                tomli_w.dump(config_data, f)

            config = config_manager.load_plugin_config("test_plugin")

            assert config == config_data
            assert "test_plugin" in config_manager._configs

    def test_load_plugin_config_nonexistent_file(self):
        """Test loading plugin config from non-existent file."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            config = config_manager.load_plugin_config("nonexistent_plugin")

            assert config == {}

    def test_load_plugin_config_custom_path(self):
        """Test loading plugin config from custom path."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "custom_config.toml"
            config_data = {"enabled": True, "param1": "value1"}

            with open(config_file, "wb") as f:
                import tomli_w

                tomli_w.dump(config_data, f)

            config = config_manager.load_plugin_config("test_plugin", config_file)

            assert config == config_data

    def test_load_all_plugin_configs(self):
        """Test loading all plugin configs."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            # Create multiple config files
            configs = {
                "plugin1": {"enabled": True, "param1": "value1"},
                "plugin2": {"enabled": False, "param2": "value2"},
                "plugin3": {"enabled": True, "param3": "value3"},
            }

            for plugin_name, config_data in configs.items():
                config_file = config_dir / f"{plugin_name}.toml"
                with open(config_file, "wb") as f:
                    import tomli_w

                    tomli_w.dump(config_data, f)

            loaded_configs = config_manager.load_all_plugin_configs()

            assert len(loaded_configs) == 3
            assert loaded_configs["plugin1"] == configs["plugin1"]
            assert loaded_configs["plugin2"] == configs["plugin2"]
            assert loaded_configs["plugin3"] == configs["plugin3"]

    def test_load_all_plugin_configs_nonexistent_dir(self):
        """Test loading all configs from non-existent directory."""
        config_manager = PluginConfigManager()
        config_manager.config_dir = Path("nonexistent_dir")

        configs = config_manager.load_all_plugin_configs()

        assert configs == {}

    def test_get_plugin_config(self):
        """Test getting plugin config."""
        config_manager = PluginConfigManager()

        config_data = {"enabled": True, "param1": "value1"}
        config_manager._configs["test_plugin"] = config_data

        config = config_manager.get_plugin_config("test_plugin")
        assert config == config_data

        config = config_manager.get_plugin_config("nonexistent")
        assert config == {}

    def test_set_plugin_config(self):
        """Test setting plugin config."""
        config_manager = PluginConfigManager()

        config_data = {"enabled": True, "param1": "value1"}
        config_manager.set_plugin_config("test_plugin", config_data)

        assert config_manager._configs["test_plugin"] == config_data

    def test_save_plugin_config(self):
        """Test saving plugin config to file."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            config_data = {"enabled": True, "param1": "value1"}
            config_manager.set_plugin_config("test_plugin", config_data)

            config_manager.save_plugin_config("test_plugin")

            # Verify file was created
            config_file = config_dir / "test_plugin.toml"
            assert config_file.exists()

            # Verify content
            with open(config_file, "rb") as f:
                import tomllib

                saved_config = tomllib.load(f)

            assert saved_config == config_data

    def test_save_plugin_config_custom_path(self):
        """Test saving plugin config to custom path."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "custom_config.toml"

            config_data = {"enabled": True, "param1": "value1"}
            config_manager.set_plugin_config("test_plugin", config_data)

            config_manager.save_plugin_config("test_plugin", config_file)

            assert config_file.exists()

    def test_save_plugin_config_nonexistent(self):
        """Test saving non-existent plugin config."""
        config_manager = PluginConfigManager()

        # Should not raise error
        config_manager.save_plugin_config("nonexistent_plugin")

    def test_save_all_configs(self):
        """Test saving all plugin configs."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            # Set multiple configs
            configs = {
                "plugin1": {"enabled": True, "param1": "value1"},
                "plugin2": {"enabled": False, "param2": "value2"},
            }

            for plugin_name, config_data in configs.items():
                config_manager.set_plugin_config(plugin_name, config_data)

            config_manager.save_all_configs()

            # Verify files were created
            for plugin_name in configs:
                config_file = config_dir / f"{plugin_name}.toml"
                assert config_file.exists()

    def test_merge_configs(self):
        """Test merging configurations."""
        config_manager = PluginConfigManager()

        base_config = {
            "enabled": True,
            "param1": "value1",
            "nested": {"param2": "value2", "param3": "value3"},
        }

        override_config = {
            "param1": "new_value1",
            "nested": {"param2": "new_value2"},
            "new_param": "new_value",
        }

        merged = config_manager.merge_configs(base_config, override_config)

        expected = {
            "enabled": True,
            "param1": "new_value1",
            "nested": {"param2": "new_value2", "param3": "value3"},
            "new_param": "new_value",
        }

        assert merged == expected

    def test_validate_plugin_config_no_schema(self):
        """Test validating config without schema."""
        config_manager = PluginConfigManager()

        config = {"enabled": True, "param1": "value1"}
        errors = config_manager.validate_plugin_config("test_plugin", config)

        assert errors == []

    def test_validate_plugin_config_with_schema(self):
        """Test validating config with schema."""
        config_manager = PluginConfigManager()

        schema = {
            "type": "object",
            "properties": {"enabled": {"type": "boolean"}, "param1": {"type": "string"}},
            "required": ["enabled"],
        }

        config_manager._config_schema = schema

        # Valid config
        valid_config = {"enabled": True, "param1": "value1"}
        errors = config_manager.validate_plugin_config("test_plugin", valid_config)
        assert errors == []

        # Invalid config - missing required field
        invalid_config = {"param1": "value1"}
        errors = config_manager.validate_plugin_config("test_plugin", invalid_config)
        assert len(errors) == 1
        assert "Required field 'enabled' missing" in errors[0]

        # Invalid config - wrong type
        invalid_config = {"enabled": "true", "param1": "value1"}
        errors = config_manager.validate_plugin_config("test_plugin", invalid_config)
        assert len(errors) == 1
        assert "Field 'enabled' has wrong type" in errors[0]

    def test_set_default_config(self):
        """Test setting default config."""
        config_manager = PluginConfigManager()

        default_config = {"enabled": True, "param1": "default_value"}
        config_manager.set_default_config("test_plugin", default_config)

        assert config_manager._default_configs["test_plugin"] == default_config

    def test_get_default_config(self):
        """Test getting default config."""
        config_manager = PluginConfigManager()

        default_config = {"enabled": True, "param1": "default_value"}
        config_manager._default_configs["test_plugin"] = default_config

        config = config_manager.get_default_config("test_plugin")
        assert config == default_config

        config = config_manager.get_default_config("nonexistent")
        assert config == {}

    def test_normalize_config(self):
        """Test normalizing config with defaults."""
        config_manager = PluginConfigManager()

        default_config = {"enabled": True, "param1": "default_value", "param2": "default_value2"}
        config_manager.set_default_config("test_plugin", default_config)

        user_config = {"param1": "user_value", "param3": "user_value3"}

        normalized = config_manager.normalize_config("test_plugin", user_config)

        expected = {
            "enabled": True,
            "param1": "user_value",
            "param2": "default_value2",
            "param3": "user_value3",
        }

        assert normalized == expected

    def test_load_plugin_order_config(self):
        """Test loading plugin order config."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            # Create main config file
            main_config = {"plugins": {"order": ["plugin1", "plugin2", "plugin3"]}}

            main_config_file = config_dir / "config_latest.toml"
            with open(main_config_file, "wb") as f:
                import tomli_w

                tomli_w.dump(main_config, f)

            order = config_manager.load_plugin_order_config()

            assert order == ["plugin1", "plugin2", "plugin3"]

    def test_load_plugin_order_config_nonexistent(self):
        """Test loading plugin order config from non-existent file."""
        config_manager = PluginConfigManager()
        config_manager.config_dir = Path("nonexistent_dir")

        order = config_manager.load_plugin_order_config()

        assert order == []

    def test_save_plugin_order_config(self):
        """Test saving plugin order config."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            plugin_order = ["plugin1", "plugin2", "plugin3"]
            config_manager.save_plugin_order_config(plugin_order)

            # Verify file was created
            main_config_file = config_dir / "config_latest.toml"
            assert main_config_file.exists()

            # Verify content
            with open(main_config_file, "rb") as f:
                import tomllib

                saved_config = tomllib.load(f)

            assert saved_config["plugins"]["order"] == plugin_order

    def test_save_plugin_order_config_existing(self):
        """Test saving plugin order config to existing file."""
        config_manager = PluginConfigManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_manager.config_dir = config_dir

            # Create existing config file
            existing_config = {"other_section": {"param1": "value1"}}

            main_config_file = config_dir / "config_latest.toml"
            with open(main_config_file, "wb") as f:
                import tomli_w

                tomli_w.dump(existing_config, f)

            plugin_order = ["plugin1", "plugin2"]
            config_manager.save_plugin_order_config(plugin_order)

            # Verify content was merged
            with open(main_config_file, "rb") as f:
                import tomllib

                saved_config = tomllib.load(f)

            assert saved_config["other_section"]["param1"] == "value1"
            assert saved_config["plugins"]["order"] == plugin_order

    def test_get_enabled_plugins(self):
        """Test getting enabled plugins."""
        config_manager = PluginConfigManager()

        configs = {
            "plugin1": {"enabled": True, "param1": "value1"},
            "plugin2": {"enabled": False, "param2": "value2"},
            "plugin3": {"enabled": True, "param3": "value3"},
            "plugin4": {"param4": "value4"},  # No enabled field, should default to True
        }

        for plugin_name, config_data in configs.items():
            config_manager.set_plugin_config(plugin_name, config_data)

        enabled_plugins = config_manager.get_enabled_plugins()

        assert "plugin1" in enabled_plugins
        assert "plugin2" not in enabled_plugins
        assert "plugin3" in enabled_plugins
        assert "plugin4" in enabled_plugins
        assert len(enabled_plugins) == 3

    def test_list_plugin_configs(self):
        """Test listing plugin configs."""
        config_manager = PluginConfigManager()

        configs = {
            "plugin1": {"enabled": True},
            "plugin2": {"enabled": False},
            "plugin3": {"enabled": True},
        }

        for plugin_name, config_data in configs.items():
            config_manager.set_plugin_config(plugin_name, config_data)

        plugin_list = config_manager.list_plugin_configs()

        assert set(plugin_list) == {"plugin1", "plugin2", "plugin3"}

    def test_remove_plugin_config(self):
        """Test removing plugin config."""
        config_manager = PluginConfigManager()

        config_manager.set_plugin_config("test_plugin", {"enabled": True})
        assert "test_plugin" in config_manager._configs

        config_manager.remove_plugin_config("test_plugin")
        assert "test_plugin" not in config_manager._configs

    def test_clear_all_configs(self):
        """Test clearing all configs."""
        config_manager = PluginConfigManager()

        config_manager.set_plugin_config("plugin1", {"enabled": True})
        config_manager.set_plugin_config("plugin2", {"enabled": False})

        assert len(config_manager._configs) == 2

        config_manager.clear_all_configs()

        assert len(config_manager._configs) == 0
