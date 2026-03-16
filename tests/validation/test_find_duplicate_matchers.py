from lore.validation.find_duplicate_matchers import find_duplicate_matchers


class TestFindDuplicateMatchers:
    def test_no_duplicates(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.ts"]}
        result = find_duplicate_matchers(fact)
        assert result == {}

    def test_duplicate_in_incl(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert "g:**/*.js" in result
        assert len(result["g:**/*.js"]) == 2

    def test_duplicate_in_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*"],
            "skip": ["g:vendor/**", "g:vendor/**"],
        }
        result = find_duplicate_matchers(fact)
        assert "g:vendor/**" in result
        assert len(result["g:vendor/**"]) == 2

    def test_duplicate_across_incl_and_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js"],
            "skip": ["g:**/*.js"],  # same pattern in skip
        }
        result = find_duplicate_matchers(fact)
        assert "g:**/*.js" in result
        assert len(result["g:**/*.js"]) == 2

    def test_multiple_duplicates(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js", "g:**/*.js", "g:**/*.ts", "g:**/*.ts"],
        }
        result = find_duplicate_matchers(fact)
        assert len(result) == 2
        assert "g:**/*.js" in result
        assert "g:**/*.ts" in result

    def test_triple_duplicate(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.js", "g:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert len(result["g:**/*.js"]) == 3

    def test_empty_fact(self):
        fact = {"fact": "Test", "incl": []}
        result = find_duplicate_matchers(fact)
        assert result == {}

    def test_missing_skip(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js"]}
        result = find_duplicate_matchers(fact)
        assert result == {}
