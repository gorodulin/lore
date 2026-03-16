from lore.globs.strip_glob_prefix import strip_glob_prefix


def test_remove_prefix_globstar():
    assert strip_glob_prefix("lore/globs/**/*.py", "lore/globs") == "**/*.py"


def test_remove_prefix_partial():
    assert strip_glob_prefix("lore/globs/file.py", "lore") == "globs/file.py"


def test_remove_prefix_no_match():
    assert strip_glob_prefix("src/**/*.py", "other") is None


def test_remove_prefix_globstar_at_start():
    assert strip_glob_prefix("**/*.py", "lore") is None


def test_remove_prefix_wildcard_at_start():
    assert strip_glob_prefix("*/*.py", "lore") is None


def test_remove_prefix_empty():
    assert strip_glob_prefix("src/file.py", "") == "src/file.py"


def test_remove_prefix_dot():
    assert strip_glob_prefix("src/file.py", ".") == "src/file.py"


def test_remove_prefix_exact_match():
    # All segments consumed, nothing left
    assert strip_glob_prefix("src/file.py", "src/file.py") is None


def test_remove_prefix_preserves_trailing_slash():
    assert strip_glob_prefix("src/utils/", "src") == "utils/"


def test_remove_prefix_deep():
    assert strip_glob_prefix("a/b/c/d/*.py", "a/b") == "c/d/*.py"
