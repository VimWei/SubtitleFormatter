"""
Simple uppercase plugin example for SubtitleFormatter.

This plugin demonstrates the basic plugin structure and converts
input text to uppercase.
"""

from subtitleformatter.plugins import TextProcessorPlugin


class SimpleUppercasePlugin(TextProcessorPlugin):
    """
    Simple plugin that converts text to uppercase.
    
    This plugin serves as an example of how to create a basic
    text processing plugin for SubtitleFormatter.
    """
    
    # Plugin metadata
    name = "simple_uppercase"
    version = "1.0.0"
    description = "A simple plugin that converts text to uppercase"
    author = "SubtitleFormatter Team"
    dependencies = []
    
    def process(self, text):
        """
        Process text by converting it to uppercase.
        
        Args:
            text: Input text (string or list of strings)
            
        Returns:
            Processed text in uppercase (same type as input)
        """
        if isinstance(text, str):
            return text.upper()
        elif isinstance(text, list):
            return [item.upper() if isinstance(item, str) else item for item in text]
        else:
            return text
