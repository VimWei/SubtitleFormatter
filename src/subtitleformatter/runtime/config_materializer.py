from __future__ import annotations

from pathlib import Path
from typing import Dict
from datetime import datetime
import os


def materialize_runtime_config(
    project_root: Path,
    config_coordinator,
    plugin_management_panel,
) -> Dict:
    """Assemble full runtime config for processing."""
    unified_cfg = config_coordinator.unified_manager.get_config()

    paths_cfg = unified_cfg.get("paths", {}) or {}
    debug_cfg = unified_cfg.get("debug", {}) or {}
    output_cfg = unified_cfg.get("output", {}) or {}

    input_file = (paths_cfg.get("input_file") or "").strip()
    output_file = (paths_cfg.get("output_file") or "").strip()

    if input_file:
        p = Path(input_file)
        if not p.is_absolute():
            input_file = str(project_root / input_file)
    if output_file:
        p = Path(output_file)
        if not p.is_absolute():
            output_file = str(project_root / output_file)

    # Resolve default/suggested output when not provided
    add_timestamp = bool(output_cfg.get("add_timestamp", True))
    if not output_file and input_file:
        try:
            in_base = Path(input_file).stem
            out_dir = (project_root / "data" / "output").resolve()
            os.makedirs(out_dir, exist_ok=True)
            filename = f"{in_base}.txt"
            if add_timestamp:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{filename}"
            output_file = str(out_dir / filename)
        except Exception:
            # Fallback: leave empty if any issue arises
            pass

    # If output provided and timestamp is enabled, prefix at runtime
    if output_file and add_timestamp:
        try:
            p = Path(output_file)
            ts_prefix = datetime.now().strftime("%Y%m%d%H%M%S")
            prefixed = p.with_name(f"{ts_prefix}-{p.name}")
            # Avoid double-prefixing if already has the same prefix
            if not p.name.startswith(ts_prefix + "-"):
                output_file = str(prefixed)
        except Exception:
            pass

    # Ensure output directory exists
    if output_file:
        try:
            out_dir = os.path.dirname(output_file)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
        except Exception:
            pass

    base: Dict = {
        "paths": {
            "input_file": input_file,
            "output_file": output_file,
        },
        "output": {
            "add_timestamp": add_timestamp,
        },
        "debug": {
            "enabled": bool(debug_cfg.get("enabled", False)),
            "debug_dir": debug_cfg.get("debug_dir", "data/debug"),
        },
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
        # As a last resort, leave order empty; right panel should be authoritative
        plugins_section["order"] = plugins_section.get("order", [])

    return {**base, "plugins": plugins_section}
