import pytest

from controllers.kcube_controller import KcubeController


def test_init_valid_serial(mocker, dummy_config, dummy_state, dummy_device):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        return_value=dummy_device,
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    assert ctrl.serial_number == "12345678"
    assert ctrl.dev is dummy_device


def test_init_invalid_serial(mocker, dummy_state):
    class Cfg:
        def get(self, section, key):
            return "abc"

        def get_bool(self, key):
            return True

    patched = mocker.patch("controllers.kcube_controller.KcubeHandle")

    ctrl = KcubeController(Cfg(), dummy_state)

    assert ctrl.serial_number is None
    assert ctrl.dev is None
    patched.assert_not_called()


def test_init_hw_failure(mocker, dummy_config, dummy_state):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        side_effect=RuntimeError("USB fail"),
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    assert ctrl.dev is None


def test_move_absolute_valid(mocker, dummy_config, dummy_state, dummy_device):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        return_value=dummy_device,
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    ctrl.move_absolute(25)

    assert dummy_state.kcube_position == 25
    assert dummy_device.position == 25


def test_move_absolute_invalid_string(mocker, dummy_config, dummy_state, dummy_device):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        return_value=dummy_device,
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    with pytest.raises(ValueError):
        ctrl.move_absolute("abc")


def test_move_absolute_clamps(mocker, dummy_config, dummy_state, dummy_device):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        return_value=dummy_device,
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    ctrl.move_absolute(150)

    assert dummy_state.kcube_position == 100
    assert dummy_device.position == 100


def test_home(mocker, dummy_config, dummy_state, dummy_device):
    mocker.patch(
        "controllers.kcube_controller.KcubeHandle",
        return_value=dummy_device,
    )

    ctrl = KcubeController(dummy_config, dummy_state)

    ctrl.home()

    assert dummy_state.kcube_position == 0
    assert dummy_device.homed is True