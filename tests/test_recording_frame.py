import pytest


def test_numeric_conversion():
    total = int("42")
    delay = float("0.5")
    scans = int("10")

    assert isinstance(total, int)
    assert isinstance(delay, float)
    assert isinstance(scans, int)


def test_invalid_numeric_conversion():
    with pytest.raises(ValueError):
        int("abc")

    with pytest.raises(ValueError):
        float("foo")