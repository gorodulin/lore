from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.globs.extract_glob_fixed_prefix import extract_glob_fixed_prefix


def test_extract_full_literal():
    compiled = compile_glob_pattern("src/utils/file.ts")
    assert extract_glob_fixed_prefix(compiled) == ["src", "utils", "file.ts"]


def test_extract_with_globstar():
    compiled = compile_glob_pattern("src/**/test.ts")
    assert extract_glob_fixed_prefix(compiled) == ["src"]


def test_extract_globstar_at_start():
    compiled = compile_glob_pattern("**/api.js")
    assert extract_glob_fixed_prefix(compiled) == []


def test_extract_with_wildcard():
    compiled = compile_glob_pattern("src/*/index.ts")
    assert extract_glob_fixed_prefix(compiled) == ["src"]


def test_extract_empty_for_invalid():
    compiled = compile_glob_pattern("")
    assert extract_glob_fixed_prefix(compiled) == []
