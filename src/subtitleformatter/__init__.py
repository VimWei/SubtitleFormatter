"""
SubtitleFormatter - An intelligent subtitle processing tool

This package provides intelligent text processing capabilities for subtitle files,
including text cleaning, sentence segmentation, filler word removal, and smart line breaking.
"""

__version__ = "0.1.0"
__author__ = "VimWei"
__description__ = "An intelligent subtitle processing tool that uses NLP models to clean, segment, and format text for better readability"

# Re-export common API
from .config import load_config  # noqa: E402

__all__ = ["load_config"]
