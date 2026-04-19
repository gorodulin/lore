import pytest
from lore.matchers.parse_matcher_string import parse_matcher_string


class TestParseMatcher:
    def test_path_matcher(self):
        assert parse_matcher_string("p:**/*.js") == ("path", "**/*.js")

    def test_path_simple_pattern(self):
        assert parse_matcher_string("p:*.txt") == ("path", "*.txt")

    def test_path_directory_pattern(self):
        assert parse_matcher_string("p:src/") == ("path", "src/")

    def test_path_literal(self):
        assert parse_matcher_string("p:src/api/users.ts") == ("path", "src/api/users.ts")

    def test_content_matcher(self):
        assert parse_matcher_string("c:.*\\.js$") == ("content", ".*\\.js$")

    def test_description_matcher(self):
        assert parse_matcher_string("d:(?i)deploy") == ("description", "(?i)deploy")

    def test_command_matcher(self):
        assert parse_matcher_string("x:rm -rf") == ("command", "rm -rf")

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
            parse_matcher_string("z:**/*.js")

    def test_no_colon_raises(self):
        with pytest.raises(ValueError, match="must have prefix"):
            parse_matcher_string("glob**/*.js")

    def test_preserves_special_characters(self):
        assert parse_matcher_string("p:**/[test]/*.js") == ("path", "**/[test]/*.js")

    def test_preserves_spaces(self):
        assert parse_matcher_string("p:path with spaces/file.txt") == ("path", "path with spaces/file.txt")
