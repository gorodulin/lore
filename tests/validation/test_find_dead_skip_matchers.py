from lore.validation.find_dead_skip_matchers import find_dead_skip_matchers


class TestFindDeadNegatives:
    def test_no_exclusions(self):
        fact = {"fact": "Test", "incl": ["g:src/**/*.js"]}
        result = find_dead_skip_matchers(fact)
        assert result == []

    def test_valid_exclusion_overlaps_with_incl(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["g:src/vendor/**"],  # overlaps with src/
        }
        result = find_dead_skip_matchers(fact)
        assert result == []

    def test_dead_exclusion_no_overlap(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["g:vendor/**"],  # doesn't overlap with src/
        }
        result = find_dead_skip_matchers(fact)
        assert result == ["g:vendor/**"]

    def test_multiple_dead_exclusions(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["g:vendor/**", "g:lib/**"],  # neither overlaps
        }
        result = find_dead_skip_matchers(fact)
        assert set(result) == {"g:vendor/**", "g:lib/**"}

    def test_mixed_valid_and_dead(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["g:src/test/**", "g:vendor/**"],  # first valid, second dead
        }
        result = find_dead_skip_matchers(fact)
        assert result == ["g:vendor/**"]

    def test_globstar_incl_matches_any_skip(self):
        # If incl starts with **, it could match anything
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js"],
            "skip": ["g:vendor/**"],
        }
        result = find_dead_skip_matchers(fact)
        assert result == []  # vendor/** could overlap with **/*.js

    def test_multiple_incl_patterns(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js", "g:lib/**/*.js"],
            "skip": ["g:src/vendor/**"],  # overlaps with first incl
        }
        result = find_dead_skip_matchers(fact)
        assert result == []

    def test_dead_skip_no_incl_overlap(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js", "g:lib/**/*.js"],
            "skip": ["g:vendor/**"],  # doesn't overlap with either
        }
        result = find_dead_skip_matchers(fact)
        assert result == ["g:vendor/**"]

    def test_invalid_matcher_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["invalid-no-prefix"],  # invalid, should be ignored
        }
        result = find_dead_skip_matchers(fact)
        assert result == []  # can't determine, so don't report as dead

    def test_non_glob_matcher_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["g:src/**/*.js"],
            "skip": ["r:vendor/.*"],  # regex, can't analyze
        }
        result = find_dead_skip_matchers(fact)
        assert result == []  # can't determine
