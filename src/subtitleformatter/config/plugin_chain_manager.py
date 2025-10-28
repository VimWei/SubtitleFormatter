"""
Plugin Chain Manager for SubtitleFormatter.

Manages plugin chain configurations including:
- Loading and saving plugin chain configurations
- Handling plugin chain references
- Supporting on-demand loading of plugin configurations
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomli_w  # type: ignore
import tomllib  # type: ignore

from ..utils import normalize_path
from ..utils.unified_logger import logger
from .config_state import ConfigState


class PluginChainManager:
    """Manages plugin chain configurations."""

    def __init__(self, project_root: Path, configs_dir: Path):
        """
        Initialize plugin chain manager.

        Args:
            project_root: Project root directory
            configs_dir: Configurations directory (data/configs)
        """
        self.project_root = project_root
        self.configs_dir = configs_dir
        self.plugin_chains_dir = configs_dir / "plugin_chains"
        self.plugins_dir = configs_dir / "plugins"
        self.default_chain_path = project_root / "src" / "subtitleformatter" / "config" / "default_plugin_chain.toml"

        # Ensure directories exist
        self.plugin_chains_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # 不再在启动时复制默认链到用户目录；仅在引用缺失时按需复制到目标路径

        self.current_chain_file: Optional[Path] = None
        self.current_chain_config: Dict[str, Any] = {}
        
        # Configuration state management
        self.config_state = ConfigState()
    
    def _ensure_default_chain_exists(self):
        """Ensure default plugin chain file exists in user directory."""
        default_user_path = self.plugin_chains_dir / "default_plugin_chain.toml"
        if not default_user_path.exists() and self.default_chain_path.exists():
            try:
                import shutil
                shutil.copy2(self.default_chain_path, default_user_path)
                logger.info(f"Initialized default plugin chain at {default_user_path}")
            except Exception as e:
                logger.error(f"Failed to initialize default chain: {e}")

    def load_chain(self, chain_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load plugin chain configuration.

        Args:
            chain_path: Path to chain file relative to plugin_chains_dir, or None for default

        Returns:
            Plugin chain configuration dictionary
        """
        if chain_path is None:
            # Load default chain
            return self._load_default_chain()

        # Try to load from plugin_chains_dir
        chain_file = self.plugin_chains_dir / chain_path
        
        # If file doesn't exist, try to copy from default
        if not chain_file.exists():
            logger.info(f"Plugin chain file not found: {chain_file}, attempting to copy default chain")
            # Try to copy default chain
            if self._copy_default_chain_to_user_dir(chain_path):
                chain_file = self.plugin_chains_dir / chain_path
                if chain_file.exists():
                    logger.debug(f"Successfully copied and found default chain at {chain_file}")
                else:
                    logger.warning(f"Failed to create chain file, falling back to default")
                    return self._load_default_chain()
            else:
                logger.warning(f"Failed to copy default chain, falling back to default")
                return self._load_default_chain()

        # Verify file exists before loading
        if not chain_file.exists():
            logger.warning(f"Chain file does not exist: {chain_file}, falling back to default")
            return self._load_default_chain()

        self.current_chain_file = chain_file
        config = self._load_chain_from_file(chain_file)
        
        # Update configuration state
        chain_path_str = str(chain_file.relative_to(self.plugin_chains_dir))
        self.config_state.load_from_saved(config, chain_path_str)
        
        return config

    def _load_default_chain(self) -> Dict[str, Any]:
        """Load default plugin chain."""
        # Try to load from user directory first
        default_user_path = self.plugin_chains_dir / "default_plugin_chain.toml"
        if default_user_path.exists():
            try:
                config = self._load_chain_from_file(default_user_path)
                logger.info(f"Loaded default plugin chain from {default_user_path}")
                return config
            except Exception as e:
                logger.error(f"Failed to load default chain from user directory: {e}")
        
        # Fallback to built-in default
        if self.default_chain_path.exists():
            try:
                config = self._load_chain_from_file(self.default_chain_path)
                logger.info(f"Loaded default plugin chain from built-in {self.default_chain_path}")
                return config
            except Exception as e:
                logger.error(f"Failed to load built-in default chain: {e}")

        # Return minimal default chain
        logger.warning("Using minimal default chain as fallback")
        return self._create_default_chain()

    def _load_chain_from_file(self, chain_file: Path) -> Dict[str, Any]:
        """Load chain configuration from file."""
        try:
            with chain_file.open("rb") as f:
                config = tomllib.load(f)

            # Ensure proper structure
            if "plugins" not in config:
                config["plugins"] = {}
            if "order" not in config["plugins"]:
                config["plugins"]["order"] = []

            self.current_chain_config = config
            logger.debug(f"Loaded plugin chain from {chain_file}")
            return config

        except Exception as e:
            logger.error(f"Failed to load chain file {chain_file}: {e}")
            return self._create_default_chain()

    def _create_default_chain(self) -> Dict[str, Any]:
        """Create minimal default chain configuration."""
        return {
            "plugins": {
                "order": []
            },
            "plugin_configs": {}
        }

    def _copy_default_chain_to_user_dir(self, target_path: str) -> bool:
        """Copy default chain to user directory."""
        try:
            if self.default_chain_path.exists():
                import shutil
                target_file = self.plugin_chains_dir / target_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.default_chain_path, target_file)
                
                # Verify copy succeeded
                if target_file.exists():
                    logger.debug(f"Successfully copied default chain to {target_file}")
                    return True
                else:
                    logger.error(f"Copy appeared to succeed but file not found: {target_file}")
                    return False
            else:
                logger.error(f"Default chain file not found: {self.default_chain_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to copy default chain: {e}")
            return False

    def save_chain(self, order: List[str], plugin_configs: Dict[str, Dict[str, Any]], chain_path: Optional[str] = None) -> Path:
        """
        Save plugin chain configuration.

        Args:
            order: List of plugin names in execution order
            plugin_configs: Dictionary of plugin configurations
            chain_path: Optional path to save chain file (None for latest)

        Returns:
            Path to saved chain file
        """
        if chain_path is None:
            # Use latest chain file
            chain_path = "chain_latest.toml"

        chain_file = self.plugin_chains_dir / chain_path

        config = {
            "plugins": {
                "order": order
            },
            "plugin_configs": plugin_configs
        }

        try:
            chain_file.parent.mkdir(parents=True, exist_ok=True)
            with chain_file.open("wb") as f:
                tomli_w.dump(config, f)

            self.current_chain_file = chain_file
            self.current_chain_config = config
            logger.info(f"Saved plugin chain to {chain_file}")
            return chain_file

        except Exception as e:
            logger.error(f"Failed to save chain file {chain_file}: {e}")
            raise

    def export_chain(self, output_path: Path, order: List[str], plugin_configs: Dict[str, Dict[str, Any]]):
        """Export chain configuration to file."""
        config = {
            "plugins": {
                "order": order
            },
            "plugin_configs": plugin_configs
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("wb") as f:
                tomli_w.dump(config, f)

            logger.info(f"Exported plugin chain to {normalize_path(output_path)}")
            logger.debug(f"[TRACE] export_chain: Set current_chain_file to {output_path}")

            # Set exported file as current chain file and update state
            self.current_chain_file = output_path
            self.current_chain_config = config
            try:
                if output_path.is_relative_to(self.plugin_chains_dir):
                    chain_path_str = str(output_path.relative_to(self.plugin_chains_dir))
                else:
                    chain_path_str = str(output_path.relative_to(self.configs_dir))
            except Exception:
                chain_path_str = str(output_path)
            self.config_state.load_from_saved(config, chain_path_str)

        except Exception as e:
            logger.error(f"Failed to export chain to {output_path}: {e}")
            raise

    def import_chain(self, chain_file: Path) -> Dict[str, Any]:
        """Import chain configuration from file."""
        if not chain_file.exists():
            raise FileNotFoundError(f"Chain file not found: {chain_file}")

        # Set as current chain file
        self.current_chain_file = chain_file
        logger.debug(f"[TRACE] import_chain: Set current_chain_file to {chain_file}")

        # Load configuration
        config = self._load_chain_from_file(chain_file)

        # Update configuration state as saved baseline
        try:
            if chain_file.is_relative_to(self.plugin_chains_dir):
                chain_path_str = str(chain_file.relative_to(self.plugin_chains_dir))
            else:
                chain_path_str = str(chain_file.relative_to(self.configs_dir))
        except Exception:
            chain_path_str = str(chain_file)
        self.config_state.load_from_saved(config, chain_path_str)

        return config

    def get_chain_path(self) -> Optional[str]:
        """Get current chain file path relative to plugin_chains_dir."""
        if self.current_chain_file is None:
            return None

        try:
            relative_path = self.current_chain_file.relative_to(self.plugin_chains_dir)
            return str(relative_path)
        except ValueError:
            # File is outside plugin_chains_dir, return absolute path
            return str(self.current_chain_file.relative_to(self.configs_dir))

    def update_plugin_config_in_working(self, plugin_name: str, config: Dict[str, Any]):
        """
        Update plugin configuration in working configuration.
        
        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration to update
        """
        working_config = self.config_state.get_working_config()
        
        # Ensure plugin_configs section exists
        if "plugin_configs" not in working_config:
            working_config["plugin_configs"] = {}
        
        # Update plugin configuration
        working_config["plugin_configs"][plugin_name] = config.copy()
        
        # Update working configuration
        self.config_state.update_working_config(working_config)
        
        logger.debug(f"Updated plugin {plugin_name} config in working configuration")
    
    def get_working_config(self) -> Dict[str, Any]:
        """Get current working configuration."""
        return self.config_state.get_working_config()
    
    def save_working_config(self, save_to: Optional[str] = None) -> Path:
        """
        Save working configuration to file.
        
        Args:
            save_to: Optional file name to save chain (None for current file)
        
        Returns:
            Path to saved chain file
        """
        working_config = self.config_state.get_working_config()
        
        if save_to is None:
            # Save to current file
            if self.current_chain_file:
                chain_file = self.current_chain_file
                logger.debug(f"[TRACE] save_working_config: Will write to current_chain_file {chain_file}")
            else:
                # Save to latest chain file
                chain_file = self.plugin_chains_dir / "chain_latest.toml"
                logger.debug(f"[TRACE] save_working_config: current_chain_file is None, fallback to {chain_file}")
        else:
            chain_file = self.plugin_chains_dir / save_to
            logger.debug(f"[TRACE] save_working_config: Save to explicit file {chain_file}")
        
        try:
            chain_file.parent.mkdir(parents=True, exist_ok=True)
            with chain_file.open("wb") as f:
                tomli_w.dump(working_config, f)
            
            # Update configuration state
            chain_path_str = str(chain_file.relative_to(self.plugin_chains_dir))
            self.config_state.save_working_config(chain_path_str)
            
            self.current_chain_file = chain_file
            self.current_chain_config = working_config
            logger.debug(f"[TRACE] save_working_config: Updated current_chain_file to {chain_file}")
            
            logger.info(f"Saved working configuration to {chain_file}")
            return chain_file
            
        except Exception as e:
            logger.error(f"Failed to save working configuration to {chain_file}: {e}")
            raise
    
    def create_snapshot(self):
        """Create a snapshot of current saved configuration for restore functionality."""
        self.config_state.create_snapshot()
        logger.debug("Created configuration snapshot")
    
    def restore_from_snapshot(self) -> Dict[str, Any]:
        """Restore configuration from snapshot."""
        self.config_state.restore_from_snapshot()
        
        # Update current chain config
        self.current_chain_config = self.config_state.get_saved_config()
        
        # If snapshot captured a path, switch current_chain_file to it
        snapshot_path = getattr(self.config_state, "snapshot_path", None)
        if snapshot_path:
            # Determine absolute path for snapshot path
            candidate = self.plugin_chains_dir / snapshot_path
            try:
                # If snapshot_path was absolute or relative to configs_dir, normalize
                if not candidate.exists():
                    candidate = (self.configs_dir / snapshot_path) if not Path(snapshot_path).is_absolute() else Path(snapshot_path)
            except Exception:
                candidate = Path(snapshot_path)
            self.current_chain_file = candidate
            logger.debug(f"[TRACE] restore_from_snapshot: Switched current_chain_file to {self.current_chain_file}")
        
        logger.info("Restored configuration from snapshot")
        return self.current_chain_config
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.config_state.has_unsaved_changes()
    
    def get_plugin_config_from_working(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get plugin configuration from working configuration.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin configuration from working config, or empty dict if not found
        """
        working_config = self.config_state.get_working_config()
        plugin_configs = working_config.get("plugin_configs", {})
        return plugin_configs.get(plugin_name, {})

