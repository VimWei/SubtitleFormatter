# Simple Uppercase Plugin

This is a simple example plugin that demonstrates the basic plugin structure for SubtitleFormatter.

## Features

- Converts input text to uppercase
- Handles both string and list inputs
- Minimal configuration requirements

## Usage

This plugin can be used in a plugin chain to convert text to uppercase. It's primarily intended as an example for plugin development.

## Configuration

No special configuration is required. The plugin accepts a simple `enabled` boolean flag.

## Example

```python
from subtitleformatter.plugins import PluginRegistry, PluginLifecycleManager

# Load the plugin
registry = PluginRegistry()
registry.add_plugin_dir(Path("plugins/examples"))
registry.scan_plugins()

lifecycle = PluginLifecycleManager(registry)
plugin = lifecycle.load_plugin("simple_uppercase")

# Process text
result = plugin.process("hello world")
print(result)  # "HELLO WORLD"
```
