from utils.fileIO import FILEIO


def test_read_exact_match(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text(
        "laser_power=10\n"
        "laser_power_max=100\n"
    )

    result = FILEIO.read_value(str(cfg), "laser_power")

    assert result == "10"


def test_read_ignores_prefix_match(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text("laser_power_max=100\n")

    result = FILEIO.read_value(str(cfg), "laser_power")

    assert result is None


def test_read_skips_malformed_lines(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text(
        "brokenline\n"
        "foo=bar\n"
    )

    result = FILEIO.read_value(str(cfg), "foo")

    assert result == "bar"


def test_write_existing_key(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text("foo=1\n")

    FILEIO.write_value(str(cfg), "foo", "99")

    assert "foo = 99" in cfg.read_text()


def test_write_new_key(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text("foo=1\n")

    FILEIO.write_value(str(cfg), "bar", "22")

    content = cfg.read_text()
    assert "bar = 22" in content