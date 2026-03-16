from lore.globs.relativize_glob_to_root import relativize_glob_to_root


def test_relativize_globstar():
    assert relativize_glob_to_root("lore/globs/**/*.py", "lore/globs") == "**/*.py"


def test_relativize_literal():
    assert relativize_glob_to_root("lore/globs/file.py", "lore/globs") == "file.py"


def test_relativize_partial_prefix():
    assert relativize_glob_to_root("lore/globs/file.py", "lore") == "globs/file.py"


def test_relativize_unsafe_globstar():
    # Globstar at start means no fixed prefix - unsafe to relocate
    assert relativize_glob_to_root("**/*.py", "lore") is None


def test_relativize_unsafe_wildcard():
    assert relativize_glob_to_root("*/*.py", "lore") is None


def test_relativize_prefix_mismatch():
    assert relativize_glob_to_root("src/test.py", "other") is None


def test_relativize_empty_root():
    assert relativize_glob_to_root("src/file.py", "") == "src/file.py"


def test_relativize_dot_root():
    assert relativize_glob_to_root("src/file.py", ".") == "src/file.py"


def test_relativize_insufficient_prefix():
    # Pattern has only 1 literal prefix segment, but root needs 2
    assert relativize_glob_to_root("src/**/*.py", "src/utils") is None


def test_relativize_invalid_pattern():
    assert relativize_glob_to_root("", "src") is None
