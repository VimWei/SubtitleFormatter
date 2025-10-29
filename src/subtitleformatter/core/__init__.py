"""
Core text processing modules.

⚠️ DEPRECATION NOTICE:
All core functionality has been migrated to the plugin system.
These modules are kept ONLY for backward compatibility with the old TextProcessor.

Migration Guide:
- TextCleaner → Use plugins/builtin/text_cleaning
- SentenceHandler → Use plugins/builtin/sentence_splitting
- FillerRemover → Use plugins/builtin/filler_removal
- LineBreaker → Use plugins/builtin/line_breaking

For new code, use PluginTextProcessor with the appropriate plugins.

OLD MODULES (KEPT FOR COMPATIBILITY):
- TextCleaner: Basic text cleaning (deprecated - use text_cleaning plugin)
- SentenceHandler: Sentence segmentation (deprecated - use plugins)
- FillerRemover: Filler removal (deprecated - use plugins)
- LineBreaker: Line breaking (deprecated - use plugins)
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
