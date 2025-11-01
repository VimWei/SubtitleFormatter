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
    - Windows: backslashes (\\)
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


def to_relative_path(path: str | Path, project_root: Path) -> str:
    """
    Convert absolute path to relative path from project root, using platform-native separators.

    This function converts an absolute path to a relative path from the project root,
    using platform-native path separators (backslashes on Windows, forward slashes on Unix).

    Args:
        path: Absolute or relative path as string or Path object
        project_root: Project root directory as Path object

    Returns:
        Relative path string using platform-native separators, or absolute path if outside project root

    Examples:
        >>> project_root = Path("C:/Apps/SubtitleFormatter")
        >>> to_relative_path("C:/Apps/SubtitleFormatter/data/input/file.txt", project_root)
        'data\\input\\file.txt'  # On Windows
        'data/input/file.txt'  # On Unix

        >>> to_relative_path("data/input/file.txt", project_root)
        'data\\input\\file.txt'  # On Windows
        'data/input/file.txt'  # On Unix

        >>> to_relative_path("C:/Other/file.txt", project_root)
        'C:\\Other\\file.txt'  # On Windows (outside project root, return absolute)
    """
    if not path:
        return ""
    
    try:
        abs_path = Path(path).resolve()
        root = Path(project_root).resolve()
        
        # Try to get relative path
        try:
            rel_path = abs_path.relative_to(root)
            # Normalize to platform-native separators
            return normalize_path(rel_path)
        except ValueError:
            # Path is outside project root, keep absolute but normalize
            return normalize_path(abs_path)
    except Exception:
        # If conversion fails, return as-is but normalize
        return normalize_path(path)


def normalize_relative_path(path: str) -> str:
    """
    Normalize a relative path string to use platform-native separators.
    
    This is useful for normalizing relative paths that may come from
    configuration files or user input (which often use forward slashes
    for portability) to platform-native format.
    
    Args:
        path: Relative path string (e.g., "data/input/" or "data/output/")
    
    Returns:
        Normalized relative path using platform-native separators
    
    Examples:
        >>> normalize_relative_path("data/input/")
        'data\\input\\'  # On Windows
        'data/input/'  # On Unix
        
        >>> normalize_relative_path("data/output")
        'data\\output'  # On Windows
        'data/output'  # On Unix
    """
    if not path:
        return ""
    return normalize_path(path)


def to_absolute_path(path: str | Path, project_root: Path) -> Path:
    """
    Convert relative or absolute path to absolute Path object.

    This function resolves a path (relative or absolute) to an absolute Path.
    Relative paths are resolved relative to the project root.

    Args:
        path: Relative or absolute path as string or Path object
        project_root: Project root directory as Path object

    Returns:
        Absolute Path object

    Examples:
        >>> project_root = Path("C:/Apps/SubtitleFormatter")
        >>> to_absolute_path("data/input/file.txt", project_root)
        Path('C:/Apps/SubtitleFormatter/data/input/file.txt')

        >>> to_absolute_path("C:/Apps/SubtitleFormatter/data/input/file.txt", project_root)
        Path('C:/Apps/SubtitleFormatter/data/input/file.txt')
    """
    if not path:
        return Path()
    
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.resolve()
    
    # Relative path - resolve relative to project root
    return (Path(project_root) / path).resolve()