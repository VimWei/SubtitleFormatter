"""
Config Coordinator for SubtitleFormatter.

Coordinates between different configuration managers:
- UnifiedConfigManager: Global and file processing settings
- PluginChainManager: Plugin chain configurations
- PluginConfigManager: Individual plugin configurations
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.unified_logger import logger
from .plugin_chain_manager import PluginChainManager
from .plugin_config_manager import PluginConfigManager
from .unified_config_manager import UnifiedConfigManager


class ConfigCoordinator:
    """Coordinates all configuration management."""

    def __init__(self, project_root: Path):
        """
        Initialize config coordinator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.configs_dir = project_root / "data" / "configs"

        # Initialize managers
        self.unified_manager = UnifiedConfigManager(project_root, self.configs_dir)
        self.chain_manager = PluginChainManager(project_root, self.configs_dir)
        self.plugin_manager = PluginConfigManager(project_root, self.configs_dir)

    def load_all_config(self) -> Dict[str, Any]:
        """
        Load all configuration on startup.

        Returns:
            Complete configuration dictionary
        """
        # 1. Load unified configuration
        unified_config = self.unified_manager.load()

        # 2. Get plugin chain reference
        chain_ref = self.unified_manager.get_plugin_chain_reference()

        # 3. Load plugin chain configuration
        try:
            chain_config = self.chain_manager.load_chain(chain_ref)
        except Exception as e:
            logger.warning(f"Failed to load plugin chain, using default: {e}")
            chain_config = self.chain_manager._create_default_chain()

        # 4. Build complete configuration
        complete_config = {"unified": unified_config, "plugin_chain": chain_config}

        logger.info("Configuration files read to memory (unified + plugin chain config)")
        return complete_config

    def save_all_config(self):
        """Save all configuration on exit."""
        try:
            self.unified_manager.save()
            logger.info("Saved unified configuration")

            # Note:
            # - Plugin configs are saved immediately when changed
            # - Plugin chain configs are saved on exit automatically

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def import_unified_config(self, config_path: Path) -> Dict[str, Any]:
        """Import unified configuration from file."""
        imported_config = self.unified_manager.import_config(config_path)

        # Extract and update plugin chain reference if present
        chain_ref = self.unified_manager.get_plugin_chain_reference()
        if chain_ref:
            try:
                chain_config = self.chain_manager.load_chain(chain_ref)
                logger.info(f"Loaded plugin chain: {chain_ref}")
            except Exception as e:
                logger.warning(f"Failed to load plugin chain {chain_ref}: {e}")

        return imported_config

    def export_unified_config(self, output_path: Path):
        """Export unified configuration to file."""
        self.unified_manager.export_config(output_path)

    def restore_last_config(self) -> Dict[str, Any]:
        """Restore to last saved configuration."""
        return self.unified_manager.restore_last()

    def restore_default_config(self) -> Dict[str, Any]:
        """Restore to default configuration."""
        return self.unified_manager.restore_default()

    def save_plugin_chain(
        self,
        order: List[str],
        plugin_configs: Dict[str, Dict[str, Any]],
        save_to: Optional[str] = None,
    ) -> Path:
        """
        Save plugin chain configuration.

        Args:
            order: List of plugin names in execution order
            plugin_configs: Dictionary of plugin configurations
            save_to: Optional file name to save chain (None for latest)

        Returns:
            Path to saved chain file
        """
        chain_file = self.chain_manager.save_chain(order, plugin_configs, save_to)

        # Update unified config with new chain reference
        chain_ref = str(chain_file.relative_to(self.chain_manager.plugin_chains_dir))
        self.unified_manager.set_plugin_chain_reference(chain_ref)
        self.unified_manager.save()

        logger.info(f"Saved plugin chain and updated unified config")
        return chain_file

    def export_plugin_chain(
        self, order: List[str], plugin_configs: Dict[str, Dict[str, Any]], output_path: Path
    ):
        """Export plugin chain to file."""
        self.chain_manager.export_chain(output_path, order, plugin_configs)
        # Update unified config reference to the new current chain file
        chain_ref = self.chain_manager.get_chain_path()
        if chain_ref:
            self.unified_manager.set_plugin_chain_reference(chain_ref)
            self.unified_manager.save()

    def import_plugin_chain(self, chain_file: Path) -> Dict[str, Any]:
        """Import plugin chain from file."""
        config = self.chain_manager.import_chain(chain_file)
        # Update unified config reference to the imported chain file
        chain_ref = self.chain_manager.get_chain_path()
        if chain_ref:
            self.unified_manager.set_plugin_chain_reference(chain_ref)
            self.unified_manager.save()
        return config

    def load_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Load configuration for a specific plugin."""
        return self.plugin_manager.load_plugin_config(plugin_name)

    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> Path:
        """Save plugin configuration immediately."""
        return self.plugin_manager.save_plugin_config(plugin_name, config)

    def save_plugin_config_to_chain(self, plugin_name: str, config: Dict[str, Any]):
        """
        Save plugin configuration to plugin chain working configuration.
        Also persist immediately to the current chain file.

        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration to save
        """
        self.chain_manager.update_plugin_config_in_working(plugin_name, config)
        logger.debug(f"Updated plugin {plugin_name} config in chain working configuration")
        # Immediate persistence to chain file
        try:
            self.chain_manager.save_working_config()
            logger.debug("Persisted working chain configuration to file after plugin change")
            # Keep unified reference in sync ONLY if it changed
            chain_ref = self.chain_manager.get_chain_path()
            current_ref = self.unified_manager.get_plugin_chain_reference()
            if chain_ref and chain_ref != current_ref:
                self.unified_manager.set_plugin_chain_reference(chain_ref)
                self.unified_manager.save()
        except Exception as e:
            logger.error(f"Failed to persist chain configuration after plugin change: {e}")

    def save_working_chain_config(self, save_to: Optional[str] = None) -> Path:
        """
        Save working plugin chain configuration.

        Args:
            save_to: Optional file name to save chain (None for current file)

        Returns:
            Path to saved chain file
        """
        chain_file = self.chain_manager.save_working_config(save_to)

        # Update unified config to point at the active chain file
        chain_ref = self.chain_manager.get_chain_path()
        current_ref = self.unified_manager.get_plugin_chain_reference()
        if chain_ref and chain_ref != current_ref:
            self.unified_manager.set_plugin_chain_reference(chain_ref)
            self.unified_manager.save()

        logger.info(f"Saved working plugin chain configuration")
        return chain_file

    def create_chain_snapshot(self):
        """Create a snapshot of current plugin chain configuration for restore functionality."""
        self.chain_manager.create_snapshot()

    def restore_chain_from_snapshot(self) -> Dict[str, Any]:
        """Restore plugin chain configuration from snapshot."""
        restored = self.chain_manager.restore_from_snapshot()
        # Persist restored snapshot to current chain file
        try:
            self.chain_manager.save_working_config()
            logger.info("Persisted chain configuration to file after restoring from snapshot")
            # Keep unified reference in sync
            chain_ref = self.chain_manager.get_chain_path()
            current_ref = self.unified_manager.get_plugin_chain_reference()
            if chain_ref and chain_ref != current_ref:
                self.unified_manager.set_plugin_chain_reference(chain_ref)
                self.unified_manager.save()
        except Exception as e:
            logger.error(f"Failed to persist chain configuration after snapshot restore: {e}")
        return restored

    def has_unsaved_chain_changes(self) -> bool:
        """Check if there are unsaved changes in plugin chain configuration."""
        return self.chain_manager.has_unsaved_changes()

    def get_all_plugin_configs(self, plugin_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get configurations for multiple plugins."""
        return self.plugin_manager.get_all_plugin_configs(plugin_names)

    def get_file_processing_config(self) -> Dict[str, Any]:
        """Get file processing configuration from unified schema.

        Maps unified sections to the legacy panel structure expected by UI tabs.
        Supports both legacy fields (input_file, output_file) and new IO mode fields.
        """
        # Ensure config is loaded if empty
        if not self.unified_manager._config:
            self.unified_manager.load()

        cfg = self.unified_manager.get_config() or {}
        paths = cfg.get("paths", {}) or {}
        output = cfg.get("output", {}) or {}
        debug = cfg.get("debug", {}) or {}

        # Build base config with legacy fields (for backward compatibility)
        result = {
            "input_file": paths.get("input_file", ""),
            "output_file": paths.get("output_file", ""),
            "add_timestamp": bool(output.get("add_timestamp", True)),
            "debug": {
                "enabled": bool(debug.get("enabled", False)),
                "debug_dir": debug.get("debug_dir", "data/debug"),
            },
        }

        # Add new IO mode fields with defaults
        result["input_mode"] = paths.get("input_mode", "file")
        result["input_paths"] = paths.get("input_paths", [])
        result["input_dir"] = paths.get("input_dir", "data/input/")
        result["input_glob"] = paths.get("input_glob", "*.*")
        result["output_mode"] = paths.get("output_mode", "file")
        result["output_path"] = paths.get("output_path", "data/output/")

        return result

    def set_file_processing_config(self, config: Dict[str, Any]):
        """Set file processing configuration into unified schema.

        Accepts the panel structure and writes back to [paths]/[output]/[debug].
        Supports both legacy fields and new IO mode fields.
        """
        current = self.unified_manager.get_config() or {}
        current.setdefault("paths", {})
        current.setdefault("output", {})
        current.setdefault("debug", {})

        if isinstance(config, dict):
            # Legacy fields (for backward compatibility)
            if "input_file" in config:
                current["paths"]["input_file"] = config.get("input_file") or ""
            if "output_file" in config:
                current["paths"]["output_file"] = config.get("output_file") or ""
            if "add_timestamp" in config:
                current["output"]["add_timestamp"] = bool(config.get("add_timestamp"))
            # Support both flat debug_enabled and nested debug.enabled
            if "debug_enabled" in config:
                current["debug"]["enabled"] = bool(config.get("debug_enabled"))
            elif isinstance(config.get("debug"), dict):
                if "enabled" in config["debug"]:
                    current["debug"]["enabled"] = bool(config["debug"]["enabled"])
                if "debug_dir" in config["debug"]:
                    current["debug"]["debug_dir"] = config["debug"]["debug_dir"]

            # New IO mode fields
            if "input_mode" in config:
                current["paths"]["input_mode"] = config.get("input_mode")
            if "input_paths" in config:
                current["paths"]["input_paths"] = config.get("input_paths", [])
            if "input_dir" in config:
                current["paths"]["input_dir"] = config.get("input_dir", "")
            if "input_glob" in config:
                current["paths"]["input_glob"] = config.get("input_glob", "")
            if "output_mode" in config:
                current["paths"]["output_mode"] = config.get("output_mode")
            if "output_path" in config:
                current["paths"]["output_path"] = config.get("output_path", "")

        # Persist through unified manager
        self.unified_manager.set_config(current)
        try:
            self.unified_manager.save()
        except Exception:
            pass

    def get_plugin_chain_config(self) -> Dict[str, Any]:
        """Get current plugin chain configuration without reloading from disk if possible."""
        # Prefer in-memory working configuration tied to current_chain_file
        try:
            if self.chain_manager.current_chain_file is not None:
                return self.chain_manager.get_working_config()
        except Exception:
            pass

        # Fallback to unified reference if no current chain file is set
        chain_ref = self.unified_manager.get_plugin_chain_reference()
        return self.chain_manager.load_chain(chain_ref)
