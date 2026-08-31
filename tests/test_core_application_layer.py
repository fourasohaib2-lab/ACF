"""
Atmospheric Complexity Framework (ACF)

Core Application Layer Test Suite
(ConfigManager, ServiceManager, PluginManager, ACFError hierarchy)

acf.core.* previously had 0% coverage - no test file imported any of
these modules at all. This is a separate application-bootstrap layer
from the newer gui/esoc/ ESOC subsystem (which is tested elsewhere).
Application/Bootstrap/logger are not covered here since they have
process-wide side effects (stdout printing, log file/directory
creation) that are riskier to exercise in a shared test run; the
side-effect-free units below are.
"""

import pytest

from acf.core.config import ConfigManager
from acf.core.exceptions import ACFError, ConfigurationError, PluginError, WorkspaceError
from acf.core.plugin_manager import PluginManager
from acf.core.service_manager import ServiceManager


def test_service_manager_register_and_get():
    services = ServiceManager()
    sentinel = object()
    services.register("thing", sentinel)
    assert services.exists("thing") is True
    assert services.get("thing") is sentinel
    assert services.list_services() == ["thing"]


def test_service_manager_missing_service_raises():
    services = ServiceManager()
    assert services.exists("missing") is False
    with pytest.raises(KeyError):
        services.get("missing")


def test_plugin_manager_discovers_subdirectories(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / "plugin_a").mkdir()
    (plugin_dir / "plugin_b").mkdir()
    (plugin_dir / "not_a_plugin.txt").write_text("x")

    pm = PluginManager(plugin_dir=str(plugin_dir))
    pm.discover()

    assert sorted(pm.list_plugins()) == ["plugin_a", "plugin_b"]


def test_plugin_manager_missing_directory_is_handled(tmp_path):
    pm = PluginManager(plugin_dir=str(tmp_path / "does_not_exist"))
    pm.discover()  # must not raise
    assert pm.list_plugins() == []


def test_config_manager_loads_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("general:\n  mode: production\n  retries: 3\n")

    cfg = ConfigManager(filename=str(config_file))
    cfg.load()

    assert cfg.get("general", "mode") == "production"
    assert cfg.get("general", "retries") == 3
    assert cfg.get("general", "missing_key", "fallback") == "fallback"
    assert cfg.get("missing_section", "x", "fallback") == "fallback"


def test_config_manager_missing_file_raises(tmp_path):
    cfg = ConfigManager(filename=str(tmp_path / "does_not_exist.yaml"))
    with pytest.raises(FileNotFoundError):
        cfg.load()


def test_acf_exception_hierarchy():
    for exc_cls in (ConfigurationError, PluginError, WorkspaceError):
        assert issubclass(exc_cls, ACFError)
        with pytest.raises(ACFError):
            raise exc_cls("boom")
