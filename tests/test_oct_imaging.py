import time
import pytest
from driver.oct_imaging import OctImaging


def test_start_twice_raises():
    octi = OctImaging()

    octi.start_recording("tmp", 1, 1, 10)

    with pytest.raises(RuntimeError):
        octi.start_recording("tmp", 1, 1, 10)

    octi.stop_recording()


def test_stop_clears_worker():
    octi = OctImaging()

    octi.start_recording("tmp", 10, 1, 10)
    octi.stop_recording()

    assert octi.worker is None


def test_worker_completes(tmp_path):
    from driver.oct_imaging import OctImaging
    import time

    octi = OctImaging()

    octi.start_recording(str(tmp_path), 1, 0, 1)

    time.sleep(0.5)

    assert octi.worker is None
    assert octi.last_error is None


def test_worker_exception_sets_last_error(mocker):
    from driver.oct_imaging import OctImaging

    octi = OctImaging()

    mocker.patch(
        "driver.oct_imaging.os.makedirs",
        side_effect=RuntimeError("simulated acquisition failure"),
    )

    octi.start_recording("tmp", 1, 0, 1)

    octi.worker.join(timeout=2)

    assert isinstance(octi.last_error, RuntimeError)
    assert str(octi.last_error) == "simulated acquisition failure"
    assert octi.worker is None
