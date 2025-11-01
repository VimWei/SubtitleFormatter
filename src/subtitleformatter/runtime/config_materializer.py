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
    """Assemble full runtime config for processing.
    
    Supports both legacy mode (input_file/output_file) and new IO modes
    (file/files/directory input, file/directory output).
    """
    unified_cfg = config_coordinator.unified_manager.get_config()

    paths_cfg = unified_cfg.get("paths", {}) or {}
    debug_cfg = unified_cfg.get("debug", {}) or {}
    output_cfg = unified_cfg.get("output", {}) or {}

    # Read IO mode (new) or default to "file" (legacy)
    input_mode = paths_cfg.get("input_mode") or "file"
    output_mode = paths_cfg.get("output_mode") or "file"

    # Resolve input file(s) based on mode
    input_file = ""
    if input_mode == "file":
        input_file = (paths_cfg.get("input_file") or "").strip()
        # Fallback to input_paths[0] if input_file is empty
        if not input_file:
            input_paths = paths_cfg.get("input_paths", [])
            if input_paths:
                input_file = str(input_paths[0]).strip()
    elif input_mode == "files":
        input_paths = paths_cfg.get("input_paths", [])
        if input_paths:
            input_file = str(input_paths[0]).strip()  # Use first file for now
    elif input_mode == "directory":
        input_dir = paths_cfg.get("input_dir", "").strip()
        input_glob = paths_cfg.get("input_glob", "*.*").strip()
        if input_dir:
            # Resolve first matching file (simplified for now)
            try:
                from glob import glob
                search_path = str(Path(input_dir) / input_glob)
                matches = glob(search_path, recursive="**" in input_glob)
                if matches:
                    input_file = matches[0]
            except Exception:
                pass

    # Make input_file absolute
    if input_file:
        p = Path(input_file)
        if not p.is_absolute():
            input_file = str(project_root / input_file)

    # Resolve output based on mode
    output_file = ""
    output_dir = ""
    add_timestamp = bool(output_cfg.get("add_timestamp", True))

    if output_mode == "file":
        # Legacy single file output
        output_file = (paths_cfg.get("output_file") or "").strip()
        if output_file:
            p = Path(output_file)
            if not p.is_absolute():
                output_file = str(project_root / output_file)

        # Resolve default/suggested output when not provided
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
                pass

        # If output provided and timestamp is enabled, prefix at runtime
        if output_file and add_timestamp:
            try:
                p = Path(output_file)
                ts_prefix = datetime.now().strftime("%Y%m%d%H%M%S")
                prefixed = p.with_name(f"{ts_prefix}-{p.name}")
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
    else:
        # New directory output mode
        output_dir = (paths_cfg.get("output_path") or "").strip()
        if not output_dir:
            # Fallback to input file's directory
            if input_file:
                output_dir = str(Path(input_file).parent)
            else:
                output_dir = str((project_root / "data" / "output").resolve())
        
        # Make output_dir absolute
        p = Path(output_dir)
        if not p.is_absolute():
            output_dir = str(project_root / output_dir)
        
        # Ensure output directory exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception:
            pass

    # Generate timestamp value if needed
    timestamp_value = None
    if add_timestamp:
        timestamp_value = datetime.now().strftime("%Y%m%d%H%M%S")

    # Build runtime config
    base: Dict = {
        "paths": {
            "input_file": input_file,
            "output_file": output_file,
            "output_mode": output_mode,
        },
        "output": {
            "add_timestamp": add_timestamp,
        },
        "debug": {
            "enabled": bool(debug_cfg.get("enabled", False)),
            "debug_dir": debug_cfg.get("debug_dir", "data/debug"),
        },
    }

    # Add directory output fields if in directory mode
    if output_mode == "directory":
        base["paths"]["output_dir"] = output_dir
        if timestamp_value:
            base["output"]["timestamp_value"] = timestamp_value

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
