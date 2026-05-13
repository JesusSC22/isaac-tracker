from tracker.exceptions import SaveNotFoundError, SaveParseError


def test_save_not_found_is_exception():
    assert issubclass(SaveNotFoundError, Exception)


def test_save_parse_error_is_exception():
    assert issubclass(SaveParseError, Exception)


def test_save_parse_error_carries_path():
    err = SaveParseError("bad header", path="C:\\foo\\bar.dat")
    assert "bad header" in str(err)
    assert err.path == "C:\\foo\\bar.dat"
