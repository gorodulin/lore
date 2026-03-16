
from lore.paths.resolve_relative_path import resolve_relative_path


def test_relative_path_passthrough():
    result = resolve_relative_path("/project", "src/app.py")
    assert result == "src/app.py"


def test_absolute_path_inside_project():
    result = resolve_relative_path("/project", "/project/src/app.py")
    assert result == "src/app.py"


def test_absolute_path_outside_project():
    result = resolve_relative_path("/project", "/other/app.py")
    assert result is None


def test_normalizes_separators():
    result = resolve_relative_path("/project", "src//app.py")
    assert result == "src/app.py"
