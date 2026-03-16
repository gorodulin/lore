import json

from lore.claude.save_display_rate_state import save_display_rate_state


def test_creates_file_and_dirs(tmp_path):
    path = str(tmp_path / "sub" / "state.json")
    save_display_rate_state({"a": 1}, path)

    assert json.loads(open(path).read()) == {"a": 1}


def test_overwrites_existing(tmp_path):
    path = str(tmp_path / "state.json")
    save_display_rate_state({"a": 1}, path)
    save_display_rate_state({"a": 2, "b": 1}, path)

    assert json.loads(open(path).read()) == {"a": 2, "b": 1}


def test_ignores_write_errors():
    # Non-writable path - should not raise
    save_display_rate_state({"a": 1}, "/dev/null/impossible/state.json")
