import re

from lore.facts.matcher_set import MatcherSet
from lore.globs.compile_glob_pattern import compile_glob_pattern


class TestMatcherSet:
    def test_default_empty(self):
        ms = MatcherSet()
        assert ms.path_globs == ()
        assert ms.content_regexes == ()
        assert ms.description_regexes == ()
        assert ms.command_regexes == ()
        assert ms.tool_regexes == ()
        assert ms.endpoint_regexes == ()
        assert ms.flag_literals == ()

    def test_with_path_globs(self):
        glob = compile_glob_pattern("**/*.py")
        ms = MatcherSet(path_globs=(glob,))
        assert len(ms.path_globs) == 1
        assert ms.path_globs[0]["raw"] == "**/*.py"

    def test_with_content_regexes(self):
        pattern = re.compile("import os", re.MULTILINE)
        ms = MatcherSet(content_regexes=(pattern,))
        assert len(ms.content_regexes) == 1
        assert ms.content_regexes[0].pattern == "import os"

    def test_with_tool_regexes(self):
        pattern = re.compile("git push", re.MULTILINE)
        ms = MatcherSet(tool_regexes=(pattern,))
        assert len(ms.tool_regexes) == 1
        assert ms.tool_regexes[0].pattern == "git push"

    def test_with_endpoint_regexes(self):
        pattern = re.compile("\\.prod\\.", re.MULTILINE)
        ms = MatcherSet(endpoint_regexes=(pattern,))
        assert len(ms.endpoint_regexes) == 1
        assert ms.endpoint_regexes[0].pattern == "\\.prod\\."

    def test_with_flag_literals(self):
        ms = MatcherSet(flag_literals=("mutates", "network"))
        assert ms.flag_literals == ("mutates", "network")

    def test_frozen(self):
        ms = MatcherSet()
        try:
            ms.path_globs = ()
            assert False, "Should raise FrozenInstanceError"
        except AttributeError:
            pass

    def test_equality(self):
        pattern = re.compile("test")
        ms1 = MatcherSet(content_regexes=(pattern,))
        ms2 = MatcherSet(content_regexes=(pattern,))
        assert ms1 == ms2
