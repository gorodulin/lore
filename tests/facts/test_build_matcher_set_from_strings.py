import re
import pytest

from lore.facts.build_matcher_set_from_strings import build_matcher_set_from_strings
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

    def test_command_only(self):
        result = build_matcher_set_from_strings(["x:rm -rf"])
        assert result.path_globs == ()
        assert result.content_regexes == ()
        assert result.description_regexes == ()
        assert len(result.command_regexes) == 1
        assert result.command_regexes[0].pattern == "rm -rf"

    def test_command_regex_compiled_multiline(self):
        result = build_matcher_set_from_strings(["x:^rm"])
        assert result.command_regexes[0].flags & re.MULTILINE

    def test_tool_only(self):
        result = build_matcher_set_from_strings(["t:git push"])
        assert result.path_globs == ()
        assert result.content_regexes == ()
        assert result.description_regexes == ()
        assert result.command_regexes == ()
        assert len(result.tool_regexes) == 1
        assert result.tool_regexes[0].pattern == "git push"

    def test_tool_multiple(self):
        result = build_matcher_set_from_strings(["t:kubectl apply", "t:helm install"])
        assert len(result.tool_regexes) == 2
        assert result.tool_regexes[0].pattern == "kubectl apply"
        assert result.tool_regexes[1].pattern == "helm install"

    def test_tool_regex_compiled_multiline(self):
        result = build_matcher_set_from_strings(["t:^git"])
        assert result.tool_regexes[0].flags & re.MULTILINE

    def test_tool_mixed_with_other_prefixes(self):
        result = build_matcher_set_from_strings(["p:**/*.py", "t:git push", "d:(?i)deploy"])
        assert len(result.path_globs) == 1
        assert len(result.tool_regexes) == 1
        assert len(result.description_regexes) == 1

    def test_endpoint_only(self):
        result = build_matcher_set_from_strings(["e:api.prod.com"])
        assert result.path_globs == ()
        assert result.tool_regexes == ()
        assert len(result.endpoint_regexes) == 1
        assert result.endpoint_regexes[0].pattern == "api.prod.com"

    def test_endpoint_multiple(self):
        result = build_matcher_set_from_strings(["e:prod", "e:staging"])
        assert len(result.endpoint_regexes) == 2
        assert result.endpoint_regexes[0].pattern == "prod"
        assert result.endpoint_regexes[1].pattern == "staging"

    def test_endpoint_regex_compiled_multiline(self):
        result = build_matcher_set_from_strings(["e:^api"])
        assert result.endpoint_regexes[0].flags & re.MULTILINE

    def test_endpoint_mixed_with_tool(self):
        result = build_matcher_set_from_strings(["t:kubectl", "e:\\.prod\\."])
        assert len(result.tool_regexes) == 1
        assert len(result.endpoint_regexes) == 1

    def test_flag_only(self):
        result = build_matcher_set_from_strings(["f:mutates"])
        assert result.path_globs == ()
        assert result.tool_regexes == ()
        assert result.endpoint_regexes == ()
        assert result.flag_literals == ("mutates",)

    def test_flag_multiple(self):
        result = build_matcher_set_from_strings(["f:mutates", "f:network"])
        assert result.flag_literals == ("mutates", "network")

    def test_flag_stored_as_raw_string_not_regex(self):
        """Flag literals are exact-match strings, not re.Pattern objects."""
        result = build_matcher_set_from_strings(["f:agent_initiated"])
        assert result.flag_literals[0] == "agent_initiated"
        assert isinstance(result.flag_literals[0], str)
