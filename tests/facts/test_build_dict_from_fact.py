from lore.facts.build_dict_from_fact import build_dict_from_fact
from lore.facts.build_fact_from_dict import build_fact_from_dict


class TestBuildDictFromFact:
    def test_minimal_fact(self):
        raw = {"fact": "Use snake_case", "incl": ["p:**/*.py"]}
        fact = build_fact_from_dict("f1", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_with_skip(self):
        raw = {
            "fact": "No tests here",
            "incl": ["p:src/**"],
            "skip": ["p:src/vendor/**"],
        }
        fact = build_fact_from_dict("f2", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_with_tags(self):
        raw = {
            "fact": "Tagged fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:read", "action:block"],
        }
        fact = build_fact_from_dict("f3", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_empty_skip_omitted(self):
        raw = {"fact": "Test", "incl": ["p:**"]}
        fact = build_fact_from_dict("f4", raw)
        result = build_dict_from_fact(fact)
        assert "skip" not in result

    def test_roundtrip_mixed_matchers(self):
        raw = {
            "fact": "Check imports",
            "incl": ["p:**/*.py", "c:import os"],
        }
        fact = build_fact_from_dict("f5", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_roundtrip_full(self):
        raw = {
            "fact": "Full fact",
            "incl": ["p:src/**/*.py", "c:import"],
            "skip": ["p:src/vendor/**", "c:__test__"],
            "tags": ["hook:read"],
        }
        fact = build_fact_from_dict("f6", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_roundtrip_tool_matcher(self):
        raw = {
            "fact": "Git push is risky",
            "incl": ["t:git push"],
            "tags": ["hook:bash"],
        }
        fact = build_fact_from_dict("f7", raw)
        result = build_dict_from_fact(fact)
        assert result == raw

    def test_roundtrip_mixed_including_tool(self):
        # Canonical order: p, c, d, x, t.
        raw = {
            "fact": "Complex fact",
            "incl": ["p:src/**", "d:(?i)deploy", "x:kubectl.*apply", "t:kubectl"],
        }
        fact = build_fact_from_dict("f8", raw)
        result = build_dict_from_fact(fact)
        assert result == raw
