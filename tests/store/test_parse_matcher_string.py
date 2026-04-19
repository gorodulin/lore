import pytest
from lore.store.parse_matcher_string import parse_matcher_string


class TestParseMatcher:
    def test_glob_matcher(self):
        assert parse_matcher_string("p:**/*.js") == ("glob", "**/*.js")

    def test_glob_simple_pattern(self):
        assert parse_matcher_string("p:*.txt") == ("glob", "*.txt")

    def test_glob_directory_pattern(self):
        assert parse_matcher_string("p:src/") == ("glob", "src/")

    def test_glob_literal_path(self):
        assert parse_matcher_string("p:src/api/users.ts") == ("glob", "src/api/users.ts")

    def test_regex_matcher(self):
        assert parse_matcher_string("c:.*\\.js$") == ("regex", ".*\\.js$")

    def test_string_matcher(self):
        assert parse_matcher_string("s:exact/path.txt") == ("string", "exact/path.txt")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid matcher format"):
            parse_matcher_string("")

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="Invalid matcher format"):
            parse_matcher_string("p:")

    def test_missing_prefix_raises(self):
        with pytest.raises(ValueError, match="must have prefix"):
            parse_matcher_string("**/*.js")

    def test_invalid_prefix_raises(self):
        with pytest.raises(ValueError, match="Invalid matcher prefix"):
            parse_matcher_string("x:**/*.js")

    def test_no_colon_raises(self):
        with pytest.raises(ValueError, match="must have prefix"):
            parse_matcher_string("glob**/*.js")

    def test_preserves_special_characters(self):
        assert parse_matcher_string("p:**/[test]/*.js") == ("glob", "**/[test]/*.js")

    def test_preserves_spaces(self):
        assert parse_matcher_string("p:path with spaces/file.txt") == ("glob", "path with spaces/file.txt")
