import types
import pytest


class DummyState:
    def __init__(self):
        self.kcube_position = 0


class DummyConfig:
    def __init__(self, values=None, bools=None):
        self.values = values or {}
        self.bools = bools or {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def get_bool(self, key):
        return self.bools.get(key, False)


class DummyDevice:
    def __init__(self):
        self.position = None
        self.homed = False
        self.closed = False

    def set_position(self, pos):
        self.position = pos

    def home(self):
        self.homed = True

    def close(self):
        self.closed = True


@pytest.fixture
def dummy_state():
    return DummyState()


@pytest.fixture
def dummy_device():
    return DummyDevice()


@pytest.fixture
def dummy_config():
    return DummyConfig(
        values={"kcube_serial_number": "12345678"},
        bools={"using_kcube": True},
    )
