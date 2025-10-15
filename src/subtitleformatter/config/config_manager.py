from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional

import tomli_w  # type: ignore


class ConfigManager:
    """Centralized configuration manager for SubtitleFormatter.

    Responsibilities:
    - Load default and user configs
    - Normalize (reconcile) user config strictly against defaults
      • remove unknown keys
      • add missing keys
      • fix type mismatches by using defaults
    - Save/export configs (atomic write)
    - Simple get/set helpers (dot-path)
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.data_dir = self.project_root / "data"
        self.configs_dir = self.data_dir / "configs"
        self.default_config_path = Path(__file__).with_name("default_config.toml")
        self.latest_config_path = self.configs_dir / "config_latest.toml"

        self._config: Dict[str, Any] = {}

    # ---- Public API ----
    def load(self) -> Dict[str, Any]:
        if self.latest_config_path.is_file():
            self._config = self._read_toml(self.latest_config_path)
        else:
            self._config = self._read_toml(self.default_config_path)
            self.configs_dir.mkdir(parents=True, exist_ok=True)
            self._atomic_write(self.latest_config_path, self._config)
        # Normalize to latest schema
        self._config = self._normalize_against_defaults(self._config)
        return self._config

    def save(self) -> None:
        # Ensure normalized before persisting
        self._config = self._normalize_against_defaults(self._config)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        self._atomic_write(self.latest_config_path, self._config)

    def export(self, file_path: str | Path) -> None:
        # Export normalized and relativized for portability
        to_save = self.normalized_for_save(self._config)
        self._atomic_write(Path(file_path), to_save)

    def get(self, dotted_path: str, default: Any = None) -> Any:
        node: Any = self._config
        for key in dotted_path.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, dotted_path: str, value: Any) -> None:
        node = self._config
        keys = dotted_path.split(".")
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value

    def set_config(self, cfg: Dict[str, Any]) -> None:
        # Replace in-memory config (normalize on save)
        self._config = cfg if isinstance(cfg, dict) else {}

    # ---- Helpers ----
    def ensure_user_config_exists(self) -> Path:
        import shutil

        if not self.latest_config_path.exists():
            self.configs_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.default_config_path, self.latest_config_path)
        return self.latest_config_path

    def normalized_for_save(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        # Strictly reconcile against defaults, then relativize paths
        import copy

        normalized = self._normalize_against_defaults(copy.deepcopy(cfg))

        # Relativize paths for portability
        paths = normalized.setdefault("paths", {})
        if isinstance(paths.get("input_file"), str):
            paths["input_file"] = (
                self._to_relative(paths["input_file"]) if paths["input_file"] else ""
            )
        if isinstance(paths.get("output_file"), str):
            paths["output_file"] = (
                self._to_relative(paths["output_file"]) if paths["output_file"] else ""
            )
        return normalized

    # ---- Internal IO ----
    def _read_toml(self, path: Path) -> Dict[str, Any]:
        with open(path, "rb") as f:
            return tomllib.load(f)

    def _atomic_write(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        content = tomli_w.dumps(data)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)

    def _to_relative(self, any_path: str | Path) -> str:
        try:
            p = Path(any_path)
            resolved = p.resolve()
            rel = resolved.relative_to(self.project_root)
            return os.path.normpath(rel.as_posix())
        except Exception:
            return os.path.normpath(str(any_path))

    # ---- Normalization ----
    def _normalize_against_defaults(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        try:
            defaults: Dict[str, Any] = self._read_toml(self.default_config_path)
        except Exception:
            defaults = {}

        def reconcile(current: Any, default: Any) -> Any:
            # If default is not a dict, enforce type or use default when None
            if not isinstance(default, dict):
                if (default is None) or isinstance(current, type(default)):
                    return current if current is not None else default
                return default

            # default is a dict: current must be a dict, otherwise replace subtree
            if not isinstance(current, dict):
                return reconcile({}, default)

            # remove unknown keys
            for k in list(current.keys()):
                if k not in default:
                    current.pop(k, None)

            # add missing keys and recurse existing keys
            for k, dv in default.items():
                if k in current:
                    current[k] = reconcile(current[k], dv)
                else:
                    current[k] = dv
            return current

        if not isinstance(cfg, dict):
            cfg = {}
        return reconcile(cfg, defaults)
