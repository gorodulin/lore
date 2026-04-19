from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet


class TestBuildFactFromDict:
    def test_minimal_fact(self):
        raw = {"fact": "Use snake_case", "incl": ["p:**/*.py"]}
        result = build_fact_from_dict("f1", raw)
        assert isinstance(result, Fact)
        assert result.fact_id == "f1"
        assert result.text == "Use snake_case"
        assert len(result.incl.path_globs) == 1
        assert result.skip == MatcherSet()
        assert result.tags == ()

    def test_with_skip(self):
        raw = {
            "fact": "No tests here",
            "incl": ["p:src/**"],
            "skip": ["p:src/vendor/**"],
        }
        result = build_fact_from_dict("f2", raw)
        assert len(result.skip.path_globs) == 1
        assert result.skip.path_globs[0]["raw"] == "src/vendor/**"

    def test_with_tags(self):
        raw = {
            "fact": "Tagged fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:read", "action:block"],
        }
        result = build_fact_from_dict("f3", raw)
        assert result.tags == ("hook:read", "action:block")

    def test_with_regex_matchers(self):
        raw = {
            "fact": "Check imports",
            "incl": ["p:**/*.py", "c:import os"],
        }
        result = build_fact_from_dict("f4", raw)
        assert len(result.incl.path_globs) == 1
        assert len(result.incl.content_regexes) == 1
        assert result.incl.content_regexes[0].pattern == "import os"

    def test_empty_skip_produces_default_matcher_set(self):
        raw = {"fact": "Test", "incl": ["p:**"], "skip": []}
        result = build_fact_from_dict("f5", raw)
        assert result.skip == MatcherSet()

    def test_with_tool_matchers(self):
        raw = {
            "fact": "Git push is risky",
            "incl": ["t:git push", "t:kubectl apply"],
        }
        result = build_fact_from_dict("f6", raw)
        assert result.incl.path_globs == ()
        assert len(result.incl.tool_regexes) == 2
        assert result.incl.tool_regexes[0].pattern == "git push"
        assert result.incl.tool_regexes[1].pattern == "kubectl apply"

    def test_with_endpoint_matchers(self):
        raw = {
            "fact": "Prod endpoints",
            "incl": ["e:\\.prod\\.", "e:api\\.internal"],
        }
        result = build_fact_from_dict("f7", raw)
        assert len(result.incl.endpoint_regexes) == 2
        assert result.incl.endpoint_regexes[0].pattern == "\\.prod\\."
        assert result.incl.endpoint_regexes[1].pattern == "api\\.internal"
