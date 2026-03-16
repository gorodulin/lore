from lore.validation.find_subset_patterns import find_subset_patterns


class TestFindSubsetPatterns:
    def test_no_subsets(self):
        matchers = ["g:**/*.js", "g:**/*.ts"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_prefix_subset(self):
        # src/**/*.js is subset of **/*.js
        matchers = ["g:src/**/*.js", "g:**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("g:src/**/*.js", "g:**/*.js") in result

    def test_deeper_prefix_subset(self):
        # src/api/**/*.js is subset of src/**/*.js
        matchers = ["g:src/api/**/*.js", "g:src/**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("g:src/api/**/*.js", "g:src/**/*.js") in result

    def test_identical_not_subset_of_self(self):
        matchers = ["g:**/*.js", "g:**/*.js"]
        result = find_subset_patterns(matchers)
        # Identical patterns are both subsets of each other
        assert len(result) == 2  # a⊆b and b⊆a

    def test_disjoint_extensions_not_subsets(self):
        matchers = ["g:**/*.js", "g:**/*.py"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_different_target_types_not_subsets(self):
        # File pattern and dir pattern can't be subsets
        matchers = ["g:src/**/*.js", "g:src/**/"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_multiple_subsets(self):
        matchers = ["g:a/**/*.js", "g:b/**/*.js", "g:**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("g:a/**/*.js", "g:**/*.js") in result
        assert ("g:b/**/*.js", "g:**/*.js") in result

    def test_chain_of_subsets(self):
        # a/b/** ⊆ a/** ⊆ **/*
        matchers = ["g:a/b/**/*", "g:a/**/*", "g:**/*"]
        result = find_subset_patterns(matchers)
        assert ("g:a/b/**/*", "g:a/**/*") in result
        assert ("g:a/**/*", "g:**/*") in result
        assert ("g:a/b/**/*", "g:**/*") in result

    def test_invalid_matcher_ignored(self):
        matchers = ["g:src/**/*.js", "invalid"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_non_glob_ignored(self):
        matchers = ["g:src/**/*.js", "r:.*\\.js$"]
        result = find_subset_patterns(matchers)
        assert result == []
