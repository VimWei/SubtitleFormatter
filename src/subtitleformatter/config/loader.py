"""
TOML-based configuration loader for SubtitleFormatter.

Search order:
1) User config: data/configs/config_latest.toml (optional)
2) Built-in default: src/subtitleformatter/config/default_config.toml (required)

User config overrides default via deep merge.
"""

from __future__ import annotations

import os
import tomllib
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import tomli_w  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Single source of truth for user config path (use data/configs only)
USER_CONFIG_PATH = PROJECT_ROOT / "data" / "configs" / "config_latest.toml"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("default_config.toml")
BASE_INPUT_DIR = PROJECT_ROOT / "data" / "input"


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_toml(path: Path) -> Dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def _dump_toml(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(tomli_w.dumps(data).encode("utf-8"))


def _validate(cfg: Dict[str, Any]) -> None:
    language = cfg.get("language", "en")
    if language not in {"auto", "en", "zh"}:
        raise ValueError("language must be one of: auto, en, zh")

    model_size = cfg.get("model_size", "md")
    if model_size not in {"sm", "md", "lg"}:
        raise ValueError("model_size must be one of: sm, md, lg")

    max_width = cfg.get("max_width", 78)
    if not isinstance(max_width, int) or max_width <= 0:
        raise ValueError("max_width must be a positive integer")

    if "paths" not in cfg or not isinstance(cfg["paths"], dict):
        raise ValueError("[paths] section is required in configuration")


def _materialize_paths(cfg: Dict[str, Any]) -> None:
    # Output file is suggested by GUI; no placeholder expansion here

    # Ensure directories exist
    output_file = cfg["paths"]["output_file"]
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    debug_cfg = cfg.get("debug", {})
    if debug_cfg.get("enabled", False):
        temp_dir = debug_cfg.get("temp_dir", "data/debug")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration with user overrides.

    Args:
        config_path: Optional path to custom config file. If None, uses default config_latest.toml
    """
    print("正在加载配置 (TOML)...")
    default_cfg = _load_toml(DEFAULT_CONFIG_PATH)

    user_cfg: Dict[str, Any] = {}
    if config_path:
        # Load custom config file
        custom_path = Path(config_path)

        # If relative path, try to resolve relative to data/configs/ first
        if not custom_path.is_absolute():
            # Try relative to data/configs/ directory
            configs_dir = PROJECT_ROOT / "data" / "configs"
            configs_path = configs_dir / custom_path
            if configs_path.exists():
                custom_path = configs_path
            elif not custom_path.exists():
                # If still not found, try relative to current working directory
                if not custom_path.exists():
                    raise FileNotFoundError(
                        f"Config file not found: {config_path}\n"
                        f"Tried locations:\n"
                        f"  - {configs_dir / custom_path}\n"
                        f"  - {custom_path.resolve()}"
                    )

        if not custom_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        user_cfg = _load_toml(custom_path)
    elif USER_CONFIG_PATH.exists():
        # Load default user config
        user_cfg = _load_toml(USER_CONFIG_PATH)
    else:
        # Create user config from default for easy editing
        USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with USER_CONFIG_PATH.open("wb") as f:
            with DEFAULT_CONFIG_PATH.open("rb") as df:
                f.write(df.read())

    cfg = _deep_merge(default_cfg, user_cfg)
    _validate(cfg)

    # Only prompt for input file in CLI mode when no custom config is provided
    if not config_path:
        # If input_file is empty, interactively prompt and persist
        input_file = cfg.get("paths", {}).get("input_file", "")
        if not input_file:
            # Prompt user for input file path (relative to data/input/ by default)
            print(
                "未检测到输入文件路径。\n"
                "请输入输入文件名（相对于 data/input/ 目录），例如：Bee hunting.txt\n"
                "如需自定义路径，也可输入绝对路径。"
            )
            user_input = input().strip().strip('"').strip("'")
            # If user provided a relative path/filename, resolve it under data/input/
            user_path = Path(user_input)
            if not user_path.is_absolute():
                resolved_path = (BASE_INPUT_DIR / user_path).as_posix()
            else:
                resolved_path = str(user_path)
            cfg["paths"]["input_file"] = resolved_path
            # Persist to user config
            # Merge into existing on-disk user cfg or create fresh
            persisted = _deep_merge(default_cfg, user_cfg)
            persisted["paths"]["input_file"] = resolved_path
            _dump_toml(persisted, USER_CONFIG_PATH)

    _materialize_paths(cfg)

    return cfg


def create_config_from_args(args) -> Dict[str, Any]:
    """Create config dict from CLI args, compatible with TOML schema."""
    cfg: Dict[str, Any] = {
        "max_width": args.max_width,
        "language": args.language,
        "model_size": args.model_size,
        "paths": {
            "input_file": args.input_file,
            "output_file": args.output or f"output_{args.input_file}",
        },
        "debug": {"enabled": args.debug, "temp_dir": "data/debug"},
    }

    _validate(cfg)
    _materialize_paths(cfg)
    # Flatten for compatibility
    cfg.setdefault("input_file", cfg["paths"].get("input_file"))
    cfg.setdefault("output_file", cfg["paths"].get("output_file"))
    return cfg
