"""
Unified Config Manager for SubtitleFormatter.

Manages the unified configuration including:
- Global settings
- File processing settings
- Plugin chain reference
- Import/Export functionality
"""

from __future__ import annotations

import tomllib  # type: ignore
from pathlib import Path
from typing import Any, Dict, Optional

import tomli_w  # type: ignore

from ..utils.path_utils import normalize_path
from ..utils.unified_logger import logger


class UnifiedConfigManager:
    """Manages the unified configuration."""

    def __init__(self, project_root: Path, configs_dir: Path):
        """
        Initialize unified config manager.

        Args:
            project_root: Project root directory
            configs_dir: Configurations directory (data/configs)
        """
        self.project_root = project_root
        self.configs_dir = configs_dir
        self.latest_config_path = configs_dir / "config_latest.toml"
        self.default_config_path = (
            project_root / "src" / "subtitleformatter" / "config" / "default_config.toml"
        )

        self._config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load unified configuration (latest or default)."""
        try:
            if self.latest_config_path.exists():
                with self.latest_config_path.open("rb") as f:
                    self._config = tomllib.load(f)
                logger.info(f"Loaded configuration from {normalize_path(self.latest_config_path)}")
            elif self.default_config_path.exists():
                with self.default_config_path.open("rb") as f:
                    self._config = tomllib.load(f)
                logger.info(
                    f"Loaded default configuration from {normalize_path(self.default_config_path)}"
                )
                # Create latest config from default
                self.save()
            else:
                # No config files exist
                self._config = {"file_processing": {}, "plugins": {}}
                logger.warning("No configuration files found, using empty config")

            return self._config.copy()

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config = {"file_processing": {}, "plugins": {}}
            return self._config.copy()

    def save(self):
        """Save current configuration to latest config."""
        try:
            self.configs_dir.mkdir(parents=True, exist_ok=True)
            with self.latest_config_path.open("wb") as f:
                tomli_w.dump(self._config, f)
            logger.info(f"Saved configuration to {normalize_path(self.latest_config_path)}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def export_config(self, output_path: Path):
        """
        Export current configuration to file.

        Args:
            output_path: Path to export configuration
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a portable configuration (relativize paths)
            export_config = self._relativize_paths(self._config.copy())

            with output_path.open("wb") as f:
                tomli_w.dump(export_config, f)

            logger.info(f"Exported configuration to {normalize_path(output_path)}")

        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise

    def import_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Import configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Imported configuration dictionary
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with config_path.open("rb") as f:
                imported_config = tomllib.load(f)

            # Update current config
            self._config = imported_config
            logger.info(f"Imported configuration from {normalize_path(config_path)}")

            return imported_config

        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            raise

    def restore_last(self) -> Dict[str, Any]:
        """Restore to last saved configuration."""
        return self.load()

    def restore_default(self) -> Dict[str, Any]:
        """Restore to default configuration."""
        try:
            if self.default_config_path.exists():
                with self.default_config_path.open("rb") as f:
                    self._config = tomllib.load(f)
                logger.info("Restored default configuration")
            else:
                self._config = {"paths": {}, "output": {}, "debug": {}, "plugins": {}}
                logger.warning("Default configuration not found, using empty config")

            return self._config.copy()

        except Exception as e:
            logger.error(f"Failed to restore default configuration: {e}")
            self._config = {"paths": {}, "output": {}, "debug": {}, "plugins": {}}
            return self._config.copy()

    def set_config(self, config: Dict[str, Any]):
        """Set current configuration."""
        self._config = config
        logger.debug("Updated configuration")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()

    def set_file_processing_config(self, config: Dict[str, Any]):
        """Set file processing configuration (mapped to unified schema)."""
        self._config.setdefault("paths", {})
        self._config.setdefault("output", {})
        self._config.setdefault("debug", {})

        if isinstance(config, dict):
            if "input_file" in config:
                self._config["paths"]["input_file"] = config.get("input_file") or ""
            if "output_file" in config:
                self._config["paths"]["output_file"] = config.get("output_file") or ""
            if "add_timestamp" in config:
                self._config["output"]["add_timestamp"] = bool(config.get("add_timestamp"))
            if "debug_enabled" in config:
                self._config["debug"]["enabled"] = bool(config.get("debug_enabled"))
            elif isinstance(config.get("debug"), dict) and "enabled" in config.get("debug", {}):
                self._config["debug"]["enabled"] = bool(config["debug"]["enabled"])

    def set_plugin_chain_reference(self, chain_path: Optional[str]):
        """
        Set plugin chain reference.

        Args:
            chain_path: Path to plugin chain file relative to plugin_chains_dir
        """
        if "plugins" not in self._config:
            self._config["plugins"] = {}

        if chain_path is None:
            self._config["plugins"].pop("current_plugin_chain", None)
        else:
            self._config["plugins"]["current_plugin_chain"] = chain_path

    def get_plugin_chain_reference(self) -> Optional[str]:
        """Get current plugin chain reference."""
        return self._config.get("plugins", {}).get("current_plugin_chain")

    def _relativize_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Relativize absolute paths in configuration (unified schema)."""
        try:
            if "paths" in config:
                for key in ["input_file", "output_file"]:
                    if key in config["paths"] and isinstance(config["paths"][key], str):
                        path = Path(config["paths"][key])
                        if path.is_absolute():
                            config["paths"][key] = str(path.relative_to(self.project_root))
        except Exception:
            pass
        return config
