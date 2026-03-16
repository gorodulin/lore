from lore.validation.find_subset_patterns_in_fact import find_subset_patterns_in_fact


class TestFindSubsetPatternsInFact:
    def test_finds_subsets_in_incl(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js", "g:**/*.js"],
        }
        result = find_subset_patterns_in_fact(fact)
        assert ("g:src/**/*.js", "g:**/*.js") in result

    def test_ignores_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js"],
            "skip": ["g:src/**/*.js"],  # not checked
        }
        result = find_subset_patterns_in_fact(fact)
        assert result == []

    def test_empty_incl(self):
        fact = {"fact": "Test", "incl": []}
        result = find_subset_patterns_in_fact(fact)
        assert result == []
