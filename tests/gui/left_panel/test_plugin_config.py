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


def test_save_to_plugins_dir_when_source_is_available(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.gui.components.plugin_config_panel import PluginConfigPanel
    from PySide6.QtWidgets import QSpinBox

    coordinator = ConfigCoordinator(temp_project)

    panel = PluginConfigPanel()
    panel.set_config_coordinator(coordinator)

    panel.current_plugin = "builtin/sentence_splitter"
    panel.is_from_chain = False

    spin = QSpinBox()
    spin.setMinimum(0)
    spin.setMaximum(10000)
    spin.setValue(80)
    panel.parameter_widgets = {"min_recursive_length": spin}

    panel._on_parameter_changed()

    cfg_file = temp_project / "data" / "configs" / "plugins" / "builtin" / "sentence_splitter.toml"
    assert cfg_file.exists()
    data = read_toml(cfg_file)
    assert data["min_recursive_length"] == 80


def test_save_to_chain_when_source_is_plugin_chain(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.gui.components.plugin_config_panel import PluginConfigPanel
    from PySide6.QtWidgets import QSpinBox

    coordinator = ConfigCoordinator(temp_project)

    panel = PluginConfigPanel()
    panel.set_config_coordinator(coordinator)

    panel.current_plugin = "builtin/sentence_splitter"
    panel.is_from_chain = True

    spin = QSpinBox()
    spin.setMinimum(0)
    spin.setMaximum(10000)
    spin.setValue(90)
    panel.parameter_widgets = {"min_recursive_length": spin}

    panel._on_parameter_changed()

    chain_file = temp_project / "data" / "configs" / "plugin_chains" / "chain_latest.toml"
    assert chain_file.exists()
    data = read_toml(chain_file)
    assert data["plugin_configs"]["builtin/sentence_splitter"]["min_recursive_length"] == 90


def test_reset_defaults_sources_from_plugin_json(qapp, temp_project):
    from subtitleformatter.config.config_coordinator import ConfigCoordinator
    from subtitleformatter.gui.components.plugin_config_panel import PluginConfigPanel
    from subtitleformatter.plugins import PluginRegistry
    from subtitleformatter.utils.plugin_config_utils import get_plugin_default_config_from_json

    coordinator = ConfigCoordinator(temp_project)

    registry = PluginRegistry()
    registry.add_plugin_dir(Path.cwd() / "plugins")
    registry.scan_plugins()

    plugin_name = "builtin/sentence_splitter"
    defaults = get_plugin_default_config_from_json(plugin_name, registry)

    # Available Plugins 源
    panel = PluginConfigPanel()
    panel.set_config_coordinator(coordinator)
    panel.set_plugin_registry(registry)
    panel.current_plugin = plugin_name
    panel.is_from_chain = False
    panel.reset_to_defaults()
    cfg_file = temp_project / "data" / "configs" / "plugins" / "builtin" / "sentence_splitter.toml"
    assert cfg_file.exists()
    data = read_toml(cfg_file)
    for k, v in defaults.items():
        assert data.get(k) == v

    # Plugin Chain 源
    panel2 = PluginConfigPanel()
    panel2.set_config_coordinator(coordinator)
    panel2.set_plugin_registry(registry)
    panel2.current_plugin = plugin_name
    panel2.is_from_chain = True
    panel2.reset_to_defaults()
    chain_file = temp_project / "data" / "configs" / "plugin_chains" / "chain_latest.toml"
    chain = read_toml(chain_file)
    for k, v in defaults.items():
        assert chain["plugin_configs"][plugin_name].get(k) == v


