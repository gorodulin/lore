from lore.validation.check_glob_target_consistency_across_facts import (
    check_glob_target_consistency_across_facts,
)


class TestCheckGlobTargetConsistencyAcrossFacts:
    def test_all_consistent(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["p:**/*.js"]},
            "f2": {"fact": "Test", "incl": ["p:**/*.ts"]},
        }
        result = check_glob_target_consistency_across_facts(fact_set)
        assert result == {}

    def test_one_inconsistent(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["p:**/*.js", "p:src/"]},  # mixed
            "f2": {"fact": "Test", "incl": ["p:**/*.ts"]},
        }
        result = check_glob_target_consistency_across_facts(fact_set)
        assert "f1" in result
        assert "f2" not in result

    def test_multiple_inconsistent(self):
        fact_set = {
            "f1": {"fact": "Test", "incl": ["p:**/*.js", "p:src/"]},
            "f2": {"fact": "Test", "incl": ["p:**/*.ts", "p:lib/"]},
        }
        result = check_glob_target_consistency_across_facts(fact_set)
        assert "f1" in result
        assert "f2" in result

    def test_empty_fact_set(self):
        result = check_glob_target_consistency_across_facts({})
        assert result == {}
