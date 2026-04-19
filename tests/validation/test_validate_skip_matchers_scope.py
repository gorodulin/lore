
from lore.validation.validate_skip_matchers_scope import validate_skip_matchers_scope


class TestValidateSkipPatternsScope:
    """Test skip pattern scope validation."""

    def test_empty_skip_patterns(self):
        """No skip patterns should return no issues."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.py"],
            skip=[],
        )
        assert result == []

    def test_skip_within_incl_scope(self):
        """Skip pattern within incl scope should be valid."""
        result = validate_skip_matchers_scope(
            incl=["p:src/api/**/*.ts"],
            skip=["p:src/api/**/*.test.ts"],
        )
        assert result == []

    def test_skip_parent_of_incl(self):
        """Skip pattern broader than incl should be valid."""
        result = validate_skip_matchers_scope(
            incl=["p:src/api/handlers/**/*.ts"],
            skip=["p:src/**/*.test.ts"],
        )
        assert result == []

    def test_skip_outside_incl_scope(self):
        """Skip pattern in different directory should be flagged."""
        result = validate_skip_matchers_scope(
            incl=["p:src/api/**/*.ts"],
            skip=["p:vendor/**"],
        )
        assert len(result) == 1
        assert result[0][0] == "p:vendor/**"
        assert "does not overlap" in result[0][1]

    def test_skip_different_subdirectory(self):
        """Skip in sibling directory should be flagged."""
        result = validate_skip_matchers_scope(
            incl=["p:src/api/**/*.ts"],
            skip=["p:src/admin/**"],
        )
        assert len(result) == 1

    def test_skip_with_globstar_pattern(self):
        """Skip with ** at start should be valid (matches everything)."""
        result = validate_skip_matchers_scope(
            incl=["p:src/api/**/*.ts"],
            skip=["p:**/*.test.ts"],
        )
        assert result == []

    def test_incl_with_globstar_pattern(self):
        """Incl with ** at start should make all skip valid."""
        result = validate_skip_matchers_scope(
            incl=["p:**/*.ts"],
            skip=["p:vendor/**", "p:node_modules/**"],
        )
        assert result == []

    def test_multiple_incl_patterns_one_valid(self):
        """Skip valid against any incl pattern should pass."""
        result = validate_skip_matchers_scope(
            incl=["p:other/**/*.ts", "p:src/api/**/*.ts"],
            skip=["p:src/**/*.test.ts"],
        )
        # Skip overlaps with second incl pattern
        assert result == []

    def test_multiple_incl_patterns_none_valid(self):
        """Skip outside all incl patterns should be flagged."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts", "p:lib/**/*.ts"],
            skip=["p:vendor/**"],
        )
        assert len(result) == 1

    def test_multiple_skip_patterns_mixed(self):
        """Only invalid skip patterns should be returned."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts"],
            skip=[
                "p:src/**/*.test.ts",      # Valid - within scope
                "p:vendor/**",              # Invalid - outside scope
                "p:**/node_modules/**",     # Valid - has globstar
                "p:lib/**",                 # Invalid - outside scope
            ],
        )
        assert len(result) == 2
        assert result[0][0] == "p:vendor/**"
        assert result[1][0] == "p:lib/**"

    def test_regex_skip_pattern_assumed_valid(self):
        """Regex skip patterns can't be analyzed, assume valid."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts"],
            skip=["c:.*test.*"],
        )
        # Can't validate regex, so assume it's fine
        assert result == []

    def test_mixed_matcher_types(self):
        """Mix of glob and regex patterns."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts", "c:.*vendor.*"],
            skip=["p:lib/**", "c:.*test.*"],
        )
        # Only g:lib is invalid (outside glob incl, and regex incl can't be analyzed)
        # Actually, since we have a regex in incl, we can't validate against it
        # So we should assume all skips are potentially valid when facing regex incl
        assert len(result) == 0  # regex incl makes us assume validity

    def test_identical_patterns(self):
        """Identical incl and skip patterns should be valid."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts"],
            skip=["p:src/**/*.ts"],
        )
        assert result == []

    def test_specific_vs_general_skip(self):
        """More specific skip should still be valid if it overlaps incl."""
        result = validate_skip_matchers_scope(
            incl=["p:src/**/*.ts"],
            skip=["p:src/api/admin/**"],
        )
        # Skip is more specific but still within src scope
        assert result == []

    def test_root_level_patterns(self):
        """Patterns without path prefix (globstar start)."""
        result = validate_skip_matchers_scope(
            incl=["p:**/*.py"],
            skip=["p:vendor/**"],
        )
        # Incl starts with globstar, so skip is valid
        assert result == []

    def test_deeply_nested_paths(self):
        """Deeply nested path patterns."""
        result = validate_skip_matchers_scope(
            incl=["p:a/b/c/d/e/**/*.ts"],
            skip=["p:a/b/c/d/f/**"],
        )
        # Different at depth 5, so no overlap
        assert len(result) == 1

    def test_single_character_segments(self):
        """Path segments with single characters."""
        result = validate_skip_matchers_scope(
            incl=["p:a/b/**"],
            skip=["p:a/c/**"],
        )
        # Overlap at 'a' but diverge at second level
        assert len(result) == 1
