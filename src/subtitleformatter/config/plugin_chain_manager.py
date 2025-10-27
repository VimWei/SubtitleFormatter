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

from ..utils.unified_logger import logger


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

        self.current_chain_file: Optional[Path] = None
        self.current_chain_config: Dict[str, Any] = {}

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
        if not chain_file.exists():
            # If not found, try relative to configs_dir
            chain_file = self.configs_dir / chain_path
            if not chain_file.exists():
                logger.warning(f"Plugin chain file not found: {chain_path}, falling back to default")
                return self._load_default_chain()

        self.current_chain_file = chain_file
        return self._load_chain_from_file(chain_file)

    def _load_default_chain(self) -> Dict[str, Any]:
        """Load default plugin chain."""
        if self.default_chain_path.exists():
            try:
                config = self._load_chain_from_file(self.default_chain_path)
                logger.info(f"Loaded default plugin chain from {self.default_chain_path}")
                return config
            except Exception as e:
                logger.error(f"Failed to load default chain: {e}")

        # Return minimal default chain
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

            logger.info(f"Exported plugin chain to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export chain to {output_path}: {e}")
            raise

    def import_chain(self, chain_file: Path) -> Dict[str, Any]:
        """Import chain configuration from file."""
        if not chain_file.exists():
            raise FileNotFoundError(f"Chain file not found: {chain_file}")

        return self._load_chain_from_file(chain_file)

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

