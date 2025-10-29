from pathlib import Path

import pytest


def _ensure_qapp():
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        pytest.skip("PySide6 not available")
        return None
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="module")
def qapp():
    return _ensure_qapp()


@pytest.fixture()
def temp_project(tmp_path: Path):
    (tmp_path / "data" / "configs" / "plugins").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "configs" / "plugin_chains").mkdir(parents=True, exist_ok=True)
    return tmp_path


def read_toml(path: Path):
    import tomllib
    with path.open("rb") as f:
        return tomllib.load(f)


def write_toml(path: Path, data: dict):
    from tomli_w import dump as toml_dump  # type: ignore
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        toml_dump(data, f)


def test_export_and_import_plugin_chain(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator

    coordinator = ConfigCoordinator(temp_project)
    order = ["builtin/text_cleaning", "builtin/punctuation_adder"]
    plugin_cfgs = {
        "builtin/text_cleaning": {},
        "builtin/punctuation_adder": {"capitalize_sentences": True},
    }

    out_path = temp_project / "data" / "configs" / "plugin_chains" / "exported.toml"
    coordinator.export_plugin_chain(order, plugin_cfgs, out_path)
    assert out_path.exists()

    exported = read_toml(out_path)
    assert exported["plugins"]["order"] == order
    assert exported["plugin_configs"]["builtin/punctuation_adder"]["capitalize_sentences"] is True

    imported = coordinator.import_plugin_chain(out_path)
    assert imported["plugins"]["order"] == order
    assert imported["plugin_configs"]["builtin/punctuation_adder"]["capitalize_sentences"] is True


def test_export_and_import_unified_config(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.config.unified_config_manager import UnifiedConfigManager
    from tomli_w import dump as toml_dump  # type: ignore

    coordinator = ConfigCoordinator(temp_project)

    chain_file = temp_project / "data" / "configs" / "plugin_chains" / "my_chain.toml"
    chain_file.parent.mkdir(parents=True, exist_ok=True)
    with chain_file.open("wb") as f:
        toml_dump({"plugins": {"order": ["builtin/text_cleaning"]}, "plugin_configs": {}}, f)

    ucm: UnifiedConfigManager = coordinator.unified_manager
    ucm.load()
    ucm._config.setdefault("file_processing", {})
    ucm._config.setdefault("plugins", {})
    rel = str(chain_file.relative_to(temp_project / "data" / "configs" / "plugin_chains"))
    ucm._config["plugins"]["current_plugin_chain"] = rel

    out = temp_project / "data" / "configs" / "exported_config.toml"
    coordinator.export_unified_config(out)
    assert out.exists()
    uni = read_toml(out)
    assert uni["plugins"]["current_plugin_chain"] == rel

    imported = coordinator.import_unified_config(out)
    assert imported["plugins"]["current_plugin_chain"] == rel


def test_load_missing_chain_falls_back(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator

    coordinator = ConfigCoordinator(temp_project)
    cfg = coordinator.chain_manager.load_chain("nonexistent_chain.toml")
    assert "plugins" in cfg and "order" in cfg["plugins"]


import pytest


def test_restore_last_writes_back_chain(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator

    coordinator = ConfigCoordinator(temp_project)
    chain_dir = temp_project / "data" / "configs" / "plugin_chains"

    # Prepare initial chain A and load it
    chain_a = chain_dir / "a.toml"
    chain_a_cfg = {"plugins": {"order": ["builtin/text_cleaning"]}, "plugin_configs": {}}
    write_toml(chain_a, chain_a_cfg)
    coordinator.chain_manager.load_chain("a.toml")
    coordinator.chain_manager.create_snapshot()

    # Modify working config and persist to file
    working = coordinator.chain_manager.get_working_config()
    working["plugins"]["order"] = ["builtin/punctuation_adder"]
    coordinator.chain_manager.config_state.update_working_config(working)
    coordinator.chain_manager.save_working_config()
    # Verify file now reflects modified order
    assert read_toml(chain_a)["plugins"]["order"] == ["builtin/punctuation_adder"]

    # Restore from snapshot and ensure write-back to chain file
    coordinator.chain_manager.restore_from_snapshot()
    assert read_toml(chain_a)["plugins"]["order"] == ["builtin/text_cleaning"]


def test_restore_default_writes_back_chain(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator

    coordinator = ConfigCoordinator(temp_project)
    chain_dir = temp_project / "data" / "configs" / "plugin_chains"

    # Create a user default chain file
    default_user_chain = chain_dir / "default_plugin_chain.toml"
    default_cfg = {"plugins": {"order": ["builtin/text_cleaning"]}, "plugin_configs": {}}
    write_toml(default_user_chain, default_cfg)

    # Load a different chain B and persist
    chain_b = chain_dir / "b.toml"
    write_toml(chain_b, {"plugins": {"order": ["builtin/punctuation_adder"]}, "plugin_configs": {}})
    coordinator.chain_manager.load_chain("b.toml")
    coordinator.chain_manager.save_working_config()
    assert read_toml(chain_b)["plugins"]["order"] == ["builtin/punctuation_adder"]

    # Restore default by loading default chain, then persist
    coordinator.chain_manager.load_chain(None)
    coordinator.chain_manager.save_working_config()

    # Assert that current chain file is the user default and content matches default
    assert read_toml(default_user_chain)["plugins"]["order"] == ["builtin/text_cleaning"]


