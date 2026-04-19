import re
import pytest

from lore.store.build_matcher_set_from_strings import build_matcher_set_from_strings
from lore.facts.matcher_set import MatcherSet


class TestBuildMatcherSetFromStrings:
    def test_empty_list(self):
        result = build_matcher_set_from_strings([])
        assert result == MatcherSet()

    def test_glob_only(self):
        result = build_matcher_set_from_strings(["p:**/*.py"])
        assert len(result.path_globs) == 1
        assert result.path_globs[0]["raw"] == "**/*.py"
        assert result.content_regexes == ()

    def test_regex_only(self):
        result = build_matcher_set_from_strings(["c:import os"])
        assert result.path_globs == ()
        assert len(result.content_regexes) == 1
        assert result.content_regexes[0].pattern == "import os"

    def test_mixed_glob_and_regex(self):
        result = build_matcher_set_from_strings(["p:src/**/*.js", "c:require\\(", "p:lib/**"])
        assert len(result.path_globs) == 2
        assert result.path_globs[0]["raw"] == "src/**/*.js"
        assert result.path_globs[1]["raw"] == "lib/**"
        assert len(result.content_regexes) == 1
        assert result.content_regexes[0].pattern == "require\\("

    def test_multiple_globs(self):
        result = build_matcher_set_from_strings(["p:**/*.py", "p:src/**/*.ts"])
        assert len(result.path_globs) == 2
        assert result.content_regexes == ()

    def test_multiple_regexes(self):
        result = build_matcher_set_from_strings(["c:import", "c:from .* import"])
        assert result.path_globs == ()
        assert len(result.content_regexes) == 2

    def test_invalid_prefix_raises(self):
        with pytest.raises(ValueError):
            build_matcher_set_from_strings(["z:bad"])

    def test_regex_is_compiled_multiline(self):
        result = build_matcher_set_from_strings(["c:^import"])
        assert result.content_regexes[0].flags & re.MULTILINE

    def test_description_only(self):
        result = build_matcher_set_from_strings(["d:(?i)deploy"])
        assert result.path_globs == ()
        assert result.content_regexes == ()
        assert len(result.description_regexes) == 1
        assert result.description_regexes[0].pattern == "(?i)deploy"

    def test_description_mixed_with_path(self):
        result = build_matcher_set_from_strings(["p:**/*.py", "d:(?i)deploy"])
        assert len(result.path_globs) == 1
        assert len(result.description_regexes) == 1

    def test_description_regex_compiled_multiline(self):
        result = build_matcher_set_from_strings(["d:^deploy"])
        assert result.description_regexes[0].flags & re.MULTILINE
