from utils.pluginmanager import PluginManager


def test_load_plugin_missing_file(tmp_path):
    pm = PluginManager("dummy.cfg")

    status, mod = pm.load_plugin(
        str(tmp_path / "missing.py"),
        "missing",
        ["Foo"],
    )

    assert status == -1
    assert mod is None


def test_load_plugin_missing_symbol(tmp_path):
    plugin = tmp_path / "plug.py"
    plugin.write_text("x = 1\n")

    pm = PluginManager("dummy.cfg")

    status, mod = pm.load_plugin(
        str(plugin),
        "plug",
        ["Foo"],
    )

    assert status == -2
    assert mod is None


def test_load_plugin_success(tmp_path):
    plugin = tmp_path / "plug.py"
    plugin.write_text("class Foo:\n    pass\n")

    pm = PluginManager("dummy.cfg")

    status, mod = pm.load_plugin(
        str(plugin),
        "plug",
        ["Foo"],
    )

    assert status == 0
    assert mod is not None


def test_unload_plugin_calls_close(mocker):
    import utils.pluginmanager as pluginmanager
    from utils.pluginmanager import PluginManager

    pm = PluginManager("dummy.cfg")

    dev = mocker.Mock()

    pluginmanager.KcubeHandle = dev

    pm.unload_plugin("dummy", ["KcubeHandle"])

    dev.close.assert_called_once()
