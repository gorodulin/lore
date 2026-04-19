from lore.validation.find_duplicate_matchers import find_duplicate_matchers


class TestFindDuplicateMatchers:
    def test_no_duplicates(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js", "p:**/*.ts"]}
        result = find_duplicate_matchers(fact)
        assert result == {}

    def test_duplicate_in_incl(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js", "p:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert "p:**/*.js" in result
        assert len(result["p:**/*.js"]) == 2

    def test_duplicate_in_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*"],
            "skip": ["p:vendor/**", "p:vendor/**"],
        }
        result = find_duplicate_matchers(fact)
        assert "p:vendor/**" in result
        assert len(result["p:vendor/**"]) == 2

    def test_duplicate_across_incl_and_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js"],
            "skip": ["p:**/*.js"],  # same pattern in skip
        }
        result = find_duplicate_matchers(fact)
        assert "p:**/*.js" in result
        assert len(result["p:**/*.js"]) == 2

    def test_multiple_duplicates(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js", "p:**/*.js", "p:**/*.ts", "p:**/*.ts"],
        }
        result = find_duplicate_matchers(fact)
        assert len(result) == 2
        assert "p:**/*.js" in result
        assert "p:**/*.ts" in result

    def test_triple_duplicate(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js", "p:**/*.js", "p:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert len(result["p:**/*.js"]) == 3

    def test_empty_fact(self):
        fact = {"fact": "Test", "incl": []}
        result = find_duplicate_matchers(fact)
        assert result == {}

    def test_missing_skip(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert result == {}
