from lore.globs.compile_glob_pattern import compile_glob_pattern


def test_compile_valid_pattern():
    result = compile_glob_pattern("src/**/test.ts")
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["globstar_index"] == 1
    assert result["fixed_prefix"] == ["src"]


def test_compile_invalid_pattern():
    result = compile_glob_pattern("src/**/**/test.ts")
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert result["segments"] == []


def test_compile_no_globstar():
    result = compile_glob_pattern("src/utils/file.ts")
    assert result["globstar_index"] == -1
    assert result["fixed_prefix"] == ["src", "utils", "file.ts"]


def test_compile_globstar_at_start():
    result = compile_glob_pattern("**/api.js")
    assert result["globstar_index"] == 0
    assert result["fixed_prefix"] == []


def test_compile_wildcard_breaks_prefix():
    result = compile_glob_pattern("src/*/test.ts")
    assert result["fixed_prefix"] == ["src"]


def test_compile_directory_pattern():
    result = compile_glob_pattern("src/utils/")
    assert result["is_dir"] is True
    assert result["fixed_prefix"] == ["src", "utils"]
