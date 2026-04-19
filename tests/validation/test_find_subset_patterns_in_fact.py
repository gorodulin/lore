from lore.validation.find_subset_patterns_in_fact import find_subset_patterns_in_fact


class TestFindSubsetPatternsInFact:
    def test_finds_subsets_in_incl(self):
        fact = {
            "fact": "Test",
            "incl": ["p:src/**/*.js", "p:**/*.js"],
        }
        result = find_subset_patterns_in_fact(fact)
        assert ("p:src/**/*.js", "p:**/*.js") in result

    def test_ignores_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js"],
            "skip": ["p:src/**/*.js"],  # not checked
        }
        result = find_subset_patterns_in_fact(fact)
        assert result == []

    def test_empty_incl(self):
        fact = {"fact": "Test", "incl": []}
        result = find_subset_patterns_in_fact(fact)
        assert result == []
