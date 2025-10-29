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

    chain_cfg: Dict = {}
    if plugin_management_panel is not None and hasattr(plugin_management_panel, "get_plugin_chain_config"):
        chain_cfg = plugin_management_panel.get_plugin_chain_config() or {}

    return {**base, **chain_cfg}


