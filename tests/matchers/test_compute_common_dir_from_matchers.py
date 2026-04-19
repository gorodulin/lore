from lore.matchers.compute_common_dir_from_matchers import compute_common_dir_from_matchers


def test_single_glob_pattern():
    result = compute_common_dir_from_matchers(["p:lore/globs/**/*.py"])
    assert result == "lore/globs"


def test_multiple_patterns_common_prefix():
    result = compute_common_dir_from_matchers([
        "p:lore/globs/**/*.py",
        "p:lore/globs/compile_glob_pattern.py",
    ])
    assert result == "lore/globs"


def test_multiple_patterns_partial_common():
    result = compute_common_dir_from_matchers([
        "p:lore/globs/**/*.py",
        "p:lore/rules/**/*.py",
    ])
    assert result == "lore"


def test_no_common_prefix():
    result = compute_common_dir_from_matchers([
        "p:src/**/*.py",
        "p:lib/**/*.py",
    ])
    assert result == "."


def test_globstar_only():
    result = compute_common_dir_from_matchers(["p:**/*.py"])
    assert result == "."


def test_empty_patterns():
    result = compute_common_dir_from_matchers([])
    assert result == "."


def test_non_glob_matchers_ignored():
    result = compute_common_dir_from_matchers([
        "s:exact match",
        "p:lore/globs/**/*.py",
    ])
    assert result == "lore/globs"


def test_literal_file_pattern():
    # A fully literal pattern like "src/utils/file.py" - the file name
    # is excluded, so directory is "src/utils"
    result = compute_common_dir_from_matchers(["p:src/utils/file.py"])
    assert result == "src/utils"


def test_directory_pattern():
    result = compute_common_dir_from_matchers(["p:src/utils/"])
    assert result == "src/utils"


def test_mixed_depth_patterns():
    result = compute_common_dir_from_matchers([
        "p:lore/globs/**/*.py",
        "p:lore/**/*.py",
    ])
    assert result == "lore"
