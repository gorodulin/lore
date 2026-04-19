import pytest

from lore.store.build_matcher_string import build_matcher_string


class TestBuildMatcherString:
    def test_path_type(self):
        assert build_matcher_string("path", "**/*.py") == "p:**/*.py"

    def test_content_type(self):
        assert build_matcher_string("content", "import os") == "c:import os"

    def test_description_type(self):
        assert build_matcher_string("description", "(?i)deploy") == "d:(?i)deploy"

    def test_command_type(self):
        assert build_matcher_string("command", "rm -rf") == "x:rm -rf"

    def test_string_type(self):
        assert build_matcher_string("string", "exact/path.txt") == "s:exact/path.txt"

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown matcher type"):
            build_matcher_string("unknown", "value")

    def test_preserves_special_characters(self):
        assert build_matcher_string("path", "**/[test]/*.js") == "p:**/[test]/*.js"

    def test_preserves_spaces(self):
        assert build_matcher_string("path", "path with spaces/file.txt") == "p:path with spaces/file.txt"

    def test_roundtrip_path(self):
        from lore.store.parse_matcher_string import parse_matcher_string

        original = "p:src/**/*.ts"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original

    def test_roundtrip_content(self):
        from lore.store.parse_matcher_string import parse_matcher_string

        original = "c:.*\\.js$"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original

    def test_roundtrip_description(self):
        from lore.store.parse_matcher_string import parse_matcher_string

        original = "d:(?i)install|remove"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original

    def test_roundtrip_command(self):
        from lore.store.parse_matcher_string import parse_matcher_string

        original = "x:\\|\\s*sh"
        matcher_type, value = parse_matcher_string(original)
        rebuilt = build_matcher_string(matcher_type, value)
        assert rebuilt == original
