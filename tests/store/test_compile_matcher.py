import re
import pytest

from lore.store.compile_matcher import compile_matcher


class TestCompileMatcher:
    def test_compile_glob(self):
        result = compile_matcher("glob", "**/*.py")
        assert isinstance(result, dict)
        assert result["raw"] == "**/*.py"
        assert result["valid"] is True

    def test_compile_regex(self):
        result = compile_matcher("regex", "import os")
        assert isinstance(result, re.Pattern)
        assert result.pattern == "import os"

    def test_compile_regex_with_flags(self):
        result = compile_matcher("regex", "(?i)test")
        assert result.search("TEST") is not None

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown matcher type"):
            compile_matcher("unknown", "value")
