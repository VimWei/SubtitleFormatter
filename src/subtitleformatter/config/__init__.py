"""Configuration package for SubtitleFormatter.

Exposes `load_config` to consumers.
"""

from .loader import load_config, create_config_from_args

__all__ = ["load_config", "create_config_from_args"]


