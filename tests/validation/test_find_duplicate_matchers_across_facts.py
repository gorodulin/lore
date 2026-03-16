from lore.validation.find_duplicate_matchers_across_facts import (
    find_duplicate_matchers_across_facts,
)


class TestFindDuplicateMatchersAcrossFacts:
    def test_no_duplicates_any_fact(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["g:**/*.js"]},
            "f2": {"fact": "Test", "incl": ["g:**/*.ts"]},
        }
        result = find_duplicate_matchers_across_facts(fact_set)
        assert result == {}

    def test_duplicate_in_one_fact(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.js"]},
            "f2": {"fact": "Test", "incl": ["g:**/*.ts"]},
        }
        result = find_duplicate_matchers_across_facts(fact_set)
        assert "f1" in result
        assert "f2" not in result

    def test_duplicates_in_multiple_facts(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.js"]},
            "f2": {"fact": "Test", "incl": ["g:**/*.ts", "g:**/*.ts"]},
        }
        result = find_duplicate_matchers_across_facts(fact_set)
        assert "f1" in result
        assert "f2" in result

    def test_empty_fact_set(self):
        result = find_duplicate_matchers_across_facts({})
        assert result == {}
