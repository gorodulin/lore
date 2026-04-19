from lore.validation.find_subset_patterns import find_subset_patterns


class TestFindSubsetPatterns:
    def test_no_subsets(self):
        matchers = ["p:**/*.js", "p:**/*.ts"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_prefix_subset(self):
        # src/**/*.js is subset of **/*.js
        matchers = ["p:src/**/*.js", "p:**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("p:src/**/*.js", "p:**/*.js") in result

    def test_deeper_prefix_subset(self):
        # src/api/**/*.js is subset of src/**/*.js
        matchers = ["p:src/api/**/*.js", "p:src/**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("p:src/api/**/*.js", "p:src/**/*.js") in result

    def test_identical_not_subset_of_self(self):
        matchers = ["p:**/*.js", "p:**/*.js"]
        result = find_subset_patterns(matchers)
        # Identical patterns are both subsets of each other
        assert len(result) == 2  # a⊆b and b⊆a

    def test_disjoint_extensions_not_subsets(self):
        matchers = ["p:**/*.js", "p:**/*.py"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_different_target_types_not_subsets(self):
        # File pattern and dir pattern can't be subsets
        matchers = ["p:src/**/*.js", "p:src/**/"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_multiple_subsets(self):
        matchers = ["p:a/**/*.js", "p:b/**/*.js", "p:**/*.js"]
        result = find_subset_patterns(matchers)
        assert ("p:a/**/*.js", "p:**/*.js") in result
        assert ("p:b/**/*.js", "p:**/*.js") in result

    def test_chain_of_subsets(self):
        # a/b/** ⊆ a/** ⊆ **/*
        matchers = ["p:a/b/**/*", "p:a/**/*", "p:**/*"]
        result = find_subset_patterns(matchers)
        assert ("p:a/b/**/*", "p:a/**/*") in result
        assert ("p:a/**/*", "p:**/*") in result
        assert ("p:a/b/**/*", "p:**/*") in result

    def test_invalid_matcher_ignored(self):
        matchers = ["p:src/**/*.js", "invalid"]
        result = find_subset_patterns(matchers)
        assert result == []

    def test_non_glob_ignored(self):
        matchers = ["p:src/**/*.js", "c:.*\\.js$"]
        result = find_subset_patterns(matchers)
        assert result == []
