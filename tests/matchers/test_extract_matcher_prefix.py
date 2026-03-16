from lore.matchers.extract_matcher_prefix import extract_matcher_prefix


def test_glob_with_fixed_prefix():
    assert extract_matcher_prefix("g:src/api/**/*.ts") == ["src", "api"]


def test_glob_starting_with_globstar():
    assert extract_matcher_prefix("g:**/*.py") == []


def test_simple_glob():
    assert extract_matcher_prefix("g:src/*.py") == ["src"]


def test_regex_returns_none():
    assert extract_matcher_prefix("r:import os") is None


def test_invalid_matcher_returns_none():
    assert extract_matcher_prefix("bad_matcher") is None
