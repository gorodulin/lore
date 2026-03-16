import pytest
from lore.facts.compile_fact_matchers import compile_fact_matchers


class TestCompileFactMatchers:
    def test_compiles_incl_matchers(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert len(compiled["incl"]) == 1
        original, matcher = compiled["incl"][0]
        assert original == "g:**/*.js"
        assert "segments" in matcher  # compiled glob has segments

    def test_compiles_skip_matchers(self):
        fact = {"fact": "Test", "incl": ["g:**/*"], "skip": ["g:**/vendor/**"]}
        compiled = compile_fact_matchers(fact)

        assert len(compiled["skip"]) == 1
        original, matcher = compiled["skip"][0]
        assert original == "g:**/vendor/**"
        assert "segments" in matcher

    def test_compiles_multiple_matchers(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js", "g:**/*.ts"],
            "skip": ["g:**/vendor/**", "g:**/node_modules/**"],
        }
        compiled = compile_fact_matchers(fact)

        assert len(compiled["incl"]) == 2
        assert len(compiled["skip"]) == 2

    def test_empty_skip_returns_empty_list(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert compiled["skip"] == []

    def test_preserves_original_matcher_string(self):
        fact = {"fact": "Test", "incl": ["g:src/**/*.js"]}
        compiled = compile_fact_matchers(fact)

        original, _ = compiled["incl"][0]
        assert original == "g:src/**/*.js"

    def test_compiles_regex_matcher(self):
        fact = {"fact": "Test", "incl": ["r:.*\\.js$"]}
        compiled = compile_fact_matchers(fact)

        assert len(compiled["incl"]) == 1
        original, matcher = compiled["incl"][0]
        assert original == "r:.*\\.js$"
        assert "regex" in matcher

    def test_regex_invalid_pattern_raises(self):
        fact = {"fact": "Test", "incl": ["r:[invalid"]}
        with pytest.raises(Exception):
            compile_fact_matchers(fact)

    def test_regex_value_starting_with_r_colon(self):
        fact = {"fact": "Test", "incl": ["r:r:something"]}
        compiled = compile_fact_matchers(fact)

        original, matcher = compiled["incl"][0]
        assert original == "r:r:something"
        assert "regex" in matcher

    def test_regex_compiled_with_multiline(self):
        fact = {"fact": "Test", "incl": ["r:^\\s*def \\w+\\([^)]*$"]}
        compiled = compile_fact_matchers(fact)

        _, matcher = compiled["incl"][0]
        import re
        assert matcher["regex"].flags & re.MULTILINE

    def test_string_matcher_not_implemented(self):
        fact = {"fact": "Test", "incl": ["s:exact/path.txt"]}
        with pytest.raises(NotImplementedError, match="String"):
            compile_fact_matchers(fact)
