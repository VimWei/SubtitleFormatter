"""Configuration package for SubtitleFormatter.

Exposes `load_config` to consumers.
"""

from .loader import create_config_from_args, load_config

__all__ = ["load_config", "create_config_from_args"]
