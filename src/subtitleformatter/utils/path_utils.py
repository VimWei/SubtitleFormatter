"""
Path utilities for SubtitleFormatter.

Provides path normalization functions that adapt to the local platform
(Windows uses backslashes, Linux/Mac use forward slashes).
"""

import os
from pathlib import Path


def normalize_path(path: str | Path) -> str:
    """
    Normalize a path to use platform-native separators.
    
    This function ensures paths use the correct separator for the current platform:
    - Windows: backslashes (\)
    - Unix/Linux/Mac: forward slashes (/)
    
    Args:
        path: Path as string or Path object
        
    Returns:
        Normalized path string using platform-native separators
        
    Examples:
        >>> normalize_path("data/configs/plugin_chains/file.toml")
        'data\\configs\\plugin_chains\\file.toml'  # On Windows
        'data/configs/plugin_chains/file.toml'  # On Unix
        
        >>> normalize_path(Path("data/configs/plugin_chains/file.toml"))
        'data\\configs\\plugin_chains\\file.toml'  # On Windows
    """
    return os.path.normpath(str(path))

