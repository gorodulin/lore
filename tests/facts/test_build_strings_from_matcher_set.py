from lore.facts.build_strings_from_matcher_set import build_strings_from_matcher_set
from lore.facts.build_matcher_set_from_strings import build_matcher_set_from_strings
from lore.facts.matcher_set import MatcherSet


class TestBuildStringsFromMatcherSet:
    def test_empty_matcher_set(self):
        result = build_strings_from_matcher_set(MatcherSet())
        assert result == []

    def test_glob_only(self):
        ms = build_matcher_set_from_strings(["p:**/*.py"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["p:**/*.py"]

    def test_regex_only(self):
        ms = build_matcher_set_from_strings(["c:import os"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["c:import os"]

    def test_mixed_canonical_order(self):
        """Globs come before regexes regardless of input order."""
        ms = build_matcher_set_from_strings(["c:import os", "p:**/*.py"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["p:**/*.py", "c:import os"]

    def test_multiple_globs_preserve_order(self):
        ms = build_matcher_set_from_strings(["p:src/**", "p:lib/**"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["p:src/**", "p:lib/**"]

    def test_roundtrip_single_glob(self):
        original = ["p:**/*.py"]
        ms = build_matcher_set_from_strings(original)
        assert build_strings_from_matcher_set(ms) == original

    def test_roundtrip_single_regex(self):
        original = ["c:.*\\.js$"]
        ms = build_matcher_set_from_strings(original)
        assert build_strings_from_matcher_set(ms) == original

    def test_roundtrip_mixed(self):
        """Round-trip with canonical ordering — globs first, regexes second."""
        original = ["p:src/**/*.py", "p:lib/**", "c:import os", "c:from .* import"]
        ms = build_matcher_set_from_strings(original)
        assert build_strings_from_matcher_set(ms) == original

    def test_description_only(self):
        ms = build_matcher_set_from_strings(["d:(?i)deploy"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["d:(?i)deploy"]

    def test_canonical_order_path_content_description(self):
        """Serialization order: paths, then content, then description."""
        ms = build_matcher_set_from_strings(
            ["d:(?i)deploy", "c:import os", "p:**/*.py"]
        )
        result = build_strings_from_matcher_set(ms)
        assert result == ["p:**/*.py", "c:import os", "d:(?i)deploy"]

    def test_roundtrip_all_types(self):
        original = ["p:**/*.py", "c:import os", "d:(?i)deploy"]
        ms = build_matcher_set_from_strings(original)
        assert build_strings_from_matcher_set(ms) == original

    def test_command_only(self):
        ms = build_matcher_set_from_strings(["x:rm -rf"])
        result = build_strings_from_matcher_set(ms)
        assert result == ["x:rm -rf"]

    def test_canonical_order_all_four_types(self):
        ms = build_matcher_set_from_strings(
            ["x:rm -rf", "d:(?i)deploy", "c:import os", "p:**/*.py"]
        )
        result = build_strings_from_matcher_set(ms)
        assert result == [
            "p:**/*.py",
            "c:import os",
            "d:(?i)deploy",
            "x:rm -rf",
        ]

    def test_tool_only(self):
        ms = build_matcher_set_from_strings(["t:git push"])
        assert build_strings_from_matcher_set(ms) == ["t:git push"]

    def test_canonical_order_all_five_types(self):
        """Serialization order: path, content, description, command, tool."""
        ms = build_matcher_set_from_strings(
            ["t:git push", "x:rm -rf", "d:(?i)deploy", "c:import os", "p:**/*.py"]
        )
        result = build_strings_from_matcher_set(ms)
        assert result == [
            "p:**/*.py",
            "c:import os",
            "d:(?i)deploy",
            "x:rm -rf",
            "t:git push",
        ]

    def test_roundtrip_tool(self):
        original = ["t:kubectl|helm"]
        ms = build_matcher_set_from_strings(original)
        assert build_strings_from_matcher_set(ms) == original
