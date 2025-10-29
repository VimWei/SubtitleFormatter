from __future__ import annotations

from pathlib import Path
from typing import Dict


def materialize_runtime_config(
    project_root: Path,
    config_coordinator,
    plugin_management_panel,
) -> Dict:
    """Assemble full runtime config for processing."""
    unified_cfg = config_coordinator.unified_manager.get_config()
    file_cfg = unified_cfg.get("file_processing", {})

    input_file = (file_cfg.get("input_file") or "").strip()
    output_file = (file_cfg.get("output_file") or "").strip()

    if input_file:
        p = Path(input_file)
        if not p.is_absolute():
            input_file = str(project_root / input_file)
    if output_file:
        p = Path(output_file)
        if not p.is_absolute():
            output_file = str(project_root / output_file)

    base: Dict = {
        "paths": {
            "input_file": input_file,
            "output_file": output_file,
        },
        "output": {
            "add_timestamp": file_cfg.get("add_timestamp", True),
        },
        "debug": file_cfg.get("debug", {"enabled": False}),
    }

    # Build plugins section from the authoritative chain configuration in coordinator
    plugins_section: Dict = {"order": []}

    try:
        chain_cfg: Dict = config_coordinator.get_plugin_chain_config() or {}

        # Extract order
        plugins_section["order"] = chain_cfg.get("plugins", {}).get("order", [])

        # Map plugin_configs (chain format) into processor-expected layout under "plugins"
        plugin_configs: Dict = chain_cfg.get("plugin_configs", {})
        for plugin_name, plugin_conf in plugin_configs.items():
            plugins_section[plugin_name] = plugin_conf or {}
    except Exception:
        # Fallback to panel (older panel only returns order)
        if plugin_management_panel is not None and hasattr(plugin_management_panel, "get_plugin_chain_config"):
            panel_cfg = plugin_management_panel.get_plugin_chain_config() or {}
            plugins_section["order"] = panel_cfg.get("plugins", {}).get("order", [])

    return {**base, "plugins": plugins_section}


