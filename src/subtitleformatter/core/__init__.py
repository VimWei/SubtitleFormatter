"""
Core text processing modules.

This package contains the core text processing functionality:
- TextCleaner: Basic text cleaning and normalization (kept for backward compatibility)
- SentenceHandler: Intelligent sentence segmentation (deprecated - use plugins instead)
- FillerRemover: Filler word and repetition removal (deprecated - use plugins instead)
- LineBreaker: Smart line breaking based on grammar (deprecated - use plugins instead)

Note: Most functionality has been migrated to the plugin system.
Only TextCleaner is kept for backward compatibility.
"""

from .text_cleaner import TextCleaner

# Deprecated imports - kept for backward compatibility
try:
    from .filler_remover import FillerRemover
    from .line_breaker import LineBreaker
    from .sentence_handler import SentenceHandler

    __all__ = ["TextCleaner", "SentenceHandler", "FillerRemover", "LineBreaker"]
except ImportError:
    # These modules have been removed in the plugin migration
    __all__ = ["TextCleaner"]
