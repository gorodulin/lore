import os

from lore.claude.load_display_rate_state import load_display_rate_state


def test_returns_empty_dict_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    state, path = load_display_rate_state("sess1", str(tmp_path))
    assert state == {}
    assert "display_rate_sess1.json" in path


def test_loads_existing_state(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    (tmp_path / "display_rate_sess1.json").write_text('{"abc":3}')

    state, _ = load_display_rate_state("sess1", str(tmp_path))
    assert state == {"abc": 3}


def test_recovers_from_corrupt_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    (tmp_path / "display_rate_sess1.json").write_text("NOT JSON")

    state, _ = load_display_rate_state("sess1", str(tmp_path))
    assert state == {}


def test_env_var_overrides_path(tmp_path, monkeypatch):
    custom_dir = tmp_path / "custom_cache"
    custom_dir.mkdir()
    (custom_dir / "display_rate_sess1.json").write_text('{"k":7}')
    monkeypatch.setenv("LORE_CACHE_DIR", str(custom_dir))

    state, path = load_display_rate_state("sess1", str(tmp_path))
    assert state == {"k": 7}
    assert str(custom_dir) in path


def test_default_path_uses_resolve_cache_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("LORE_CACHE_DIR", raising=False)
    monkeypatch.setattr(
        "lore.claude.load_display_rate_state.resolve_cache_dir",
        lambda: str(tmp_path / "mocked_cache"),
    )
    _, path = load_display_rate_state("sess1", str(tmp_path))
    expected = os.path.join(str(tmp_path / "mocked_cache"), "display_rate_sess1.json")
    assert path == expected
