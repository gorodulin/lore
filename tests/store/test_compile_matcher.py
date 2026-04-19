import re
import pytest

from lore.store.compile_matcher import compile_matcher


class TestCompileMatcher:
    def test_compile_path(self):
        result = compile_matcher("path", "**/*.py")
        assert isinstance(result, dict)
        assert result["raw"] == "**/*.py"
        assert result["valid"] is True

    def test_compile_content(self):
        result = compile_matcher("content", "import os")
        assert isinstance(result, re.Pattern)
        assert result.pattern == "import os"

    def test_compile_content_with_flags(self):
        result = compile_matcher("content", "(?i)test")
        assert result.search("TEST") is not None

    def test_compile_description(self):
        result = compile_matcher("description", "(?i)deploy")
        assert isinstance(result, re.Pattern)
        assert result.search("Deploy the app") is not None

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown matcher type"):
            compile_matcher("unknown", "value")
