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


def test_add_plugin_persists_order(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.gui.components.plugin_management_panel import PluginManagementPanel

    coordinator = ConfigCoordinator(temp_project)

    panel = PluginManagementPanel()
    panel.set_config_coordinator(coordinator)

    panel.update_available_plugins({
        "builtin/text_cleaning": {"name": "builtin/text_cleaning", "description": "Text cleanup"},
    })

    panel.available_list.setCurrentRow(0)
    panel.add_plugin_to_chain()

    chain_file = temp_project / "data" / "configs" / "plugin_chains" / "chain_latest.toml"
    assert chain_file.exists()
    data = read_toml(chain_file)
    assert data.get("plugins", {}).get("order") == ["builtin/text_cleaning"]


def test_reorder_plugins_persists_order(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.gui.components.plugin_management_panel import PluginManagementPanel

    coordinator = ConfigCoordinator(temp_project)

    panel = PluginManagementPanel()
    panel.set_config_coordinator(coordinator)

    panel.update_available_plugins({
        "builtin/text_cleaning": {"name": "builtin/text_cleaning"},
        "builtin/punctuation_adder": {"name": "builtin/punctuation_adder"},
    })

    panel.available_list.setCurrentRow(0)
    panel.add_plugin_to_chain()
    panel.available_list.setCurrentRow(1)
    panel.add_plugin_to_chain()

    panel.chain_list.setCurrentRow(1)
    panel.move_plugin_up()

    chain_file = temp_project / "data" / "configs" / "plugin_chains" / "chain_latest.toml"
    data = read_toml(chain_file)
    assert data.get("plugins", {}).get("order") == [
        "builtin/punctuation_adder",
        "builtin/text_cleaning",
    ]


