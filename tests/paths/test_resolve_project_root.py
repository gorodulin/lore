import os

from lore.paths.resolve_project_root import resolve_project_root


def test_explicit_path_takes_priority(tmp_path, monkeypatch):
    """Explicit path is used even if env var is set."""
    target = tmp_path / "from_arg"
    target.mkdir()
    monkeypatch.setenv("LORE_PROJECT_ROOT", str(tmp_path / "from_env"))

    assert resolve_project_root(str(target)) == os.path.realpath(str(target))


def test_env_var_used_when_no_explicit_path(tmp_path, monkeypatch):
    """LORE_PROJECT_ROOT env var is used when no explicit path given."""
    target = tmp_path / "from_env"
    target.mkdir()
    monkeypatch.setenv("LORE_PROJECT_ROOT", str(target))

    assert resolve_project_root() == os.path.realpath(str(target))


def test_cwd_fallback(tmp_path, monkeypatch):
    """Falls back to cwd when neither explicit path nor env var is set."""
    monkeypatch.delenv("LORE_PROJECT_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)

    assert resolve_project_root() == str(tmp_path)


def test_resolves_symlinks(tmp_path):
    """Symlinked paths are resolved to their real location."""
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    link_dir = tmp_path / "link"
    link_dir.symlink_to(real_dir)

    assert resolve_project_root(str(link_dir)) == str(real_dir)
