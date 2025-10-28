"""
Plugin configuration utilities for SubtitleFormatter.

This module provides utility functions for working with plugin configurations,
including loading default values from plugin.json files.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.unified_logger import logger


def get_plugin_default_config_from_json(plugin_name: str, plugin_registry=None) -> Dict[str, Any]:
    """
    从插件的 plugin.json 文件读取默认配置
    
    这是一个通用的工具函数，可以被 GUI 组件和插件实例使用。
    它统一了默认配置的读取逻辑。
    
    Args:
        plugin_name: 插件名称（如 "builtin/punctuation_adder"）
        plugin_registry: 可选的插件注册表，用于获取元数据
        
    Returns:
        包含默认配置的字典
    """
    try:
        # 方法1: 如果有插件注册表，从元数据中获取
        if plugin_registry:
            metadata = plugin_registry.get_plugin_metadata(plugin_name)
            if metadata:
                config_schema = metadata.get("config_schema", {})
                properties = config_schema.get("properties", {})
                
                default_config = {}
                for prop_name, prop_config in properties.items():
                    if "default" in prop_config:
                        default_config[prop_name] = prop_config["default"]
                
                logger.debug(f"Loaded default config from registry metadata for {plugin_name}: {default_config}")
                return default_config
        
        # 方法2: 直接从 plugin.json 文件读取
        plugin_dir = Path("plugins") / plugin_name.replace("builtin/", "builtin/")
        plugin_json_path = plugin_dir / "plugin.json"
        
        if not plugin_json_path.exists():
            logger.warning(f"plugin.json not found at {plugin_json_path}")
            return {}
        
        with plugin_json_path.open("r", encoding="utf-8") as f:
            plugin_data = json.load(f)
        
        config_schema = plugin_data.get("config_schema", {})
        properties = config_schema.get("properties", {})
        
        default_config = {}
        for prop_name, prop_config in properties.items():
            if "default" in prop_config:
                default_config[prop_name] = prop_config["default"]
        
        logger.debug(f"Loaded default config from plugin.json for {plugin_name}: {default_config}")
        return default_config
        
    except Exception as e:
        logger.error(f"Failed to load default config for {plugin_name}: {e}")
        return {}


def get_plugin_default_config_from_instance(plugin_instance) -> Dict[str, Any]:
    """
    从插件实例获取默认配置
    
    这是基类 get_default_config_from_plugin_json() 方法的包装器，
    用于统一接口。
    
    Args:
        plugin_instance: 插件实例
        
    Returns:
        包含默认配置的字典
    """
    try:
        return plugin_instance.get_default_config_from_plugin_json()
    except Exception as e:
        logger.error(f"Failed to get default config from plugin instance: {e}")
        return {}
