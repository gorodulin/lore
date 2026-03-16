import pytest

from lore.facts.build_matcher_string import build_matcher_string


class TestBuildMatcherString:
    def test_glob_type(self):
        assert build_matcher_string("glob", "**/*.py") == "g:**/*.py"

    def test_regex_type(self):
        assert build_matcher_string("regex", "import os") == "r:import os"

    def test_string_type(self):
        assert build_matcher_string("string", "exact/path.txt") == "s:exact/path.txt"

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown matcher type"):
            build_matcher_string("unknown", "value")

    def test_preserves_special_characters(self):
        assert build_matcher_string("glob", "**/[test]/*.js") == "g:**/[test]/*.js"

    def test_preserves_spaces(self):
        assert build_matcher_string("glob", "path with spaces/file.txt") == "g:path with spaces/file.txt"

    def test_roundtrip_with_parse(self):
        from lore.facts.parse_matcher_string import parse_matcher_string

        original = "g:src/**/*.ts"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original

    def test_roundtrip_regex(self):
        from lore.facts.parse_matcher_string import parse_matcher_string

        original = "r:.*\\.js$"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original
