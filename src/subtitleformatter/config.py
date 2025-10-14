"""
Compatibility shim: delegate to new TOML-based loader in
`subtitleformatter.config.loader` while preserving import path.
"""

from typing import Any, Dict

from .config.loader import load_config, create_config_from_args  # type: ignore F401

__all__ = ["load_config", "create_config_from_args"]
