from lore.matchers.match_segment_to_wildcard import match_segment_to_wildcard


class TestLiteralWildcard:
    def test_exact_match(self):
        assert match_segment_to_wildcard("file.ts", "file.ts") is True

    def test_no_match(self):
        assert match_segment_to_wildcard("file.ts", "file.js") is False


class TestSuffixWildcard:
    def test_suffix_match(self):
        assert match_segment_to_wildcard("*.ts", "file.ts") is True

    def test_suffix_no_match(self):
        assert match_segment_to_wildcard("*.ts", "file.js") is False

    def test_suffix_empty_name(self):
        assert match_segment_to_wildcard("*.ts", ".ts") is True


class TestPrefixWildcard:
    def test_prefix_match(self):
        assert match_segment_to_wildcard("test_*", "test_foo") is True

    def test_prefix_no_match(self):
        assert match_segment_to_wildcard("test_*", "spec_foo") is False

    def test_prefix_exact(self):
        assert match_segment_to_wildcard("test_*", "test_") is True


class TestInfixWildcard:
    def test_infix_match(self):
        assert match_segment_to_wildcard("f*o", "foo") is True
        assert match_segment_to_wildcard("f*o", "foooo") is True
        assert match_segment_to_wildcard("f*o", "fxxxxxxxo") is True

    def test_infix_no_match(self):
        assert match_segment_to_wildcard("f*o", "bar") is False
        assert match_segment_to_wildcard("f*o", "fo") is True  # * matches empty

    def test_infix_overlap_prevention(self):
        # wildcard "ab*ba" should not match "aba" - prefix/suffix would overlap
        assert match_segment_to_wildcard("ab*ba", "aba") is False
        assert match_segment_to_wildcard("ab*ba", "abba") is True
        assert match_segment_to_wildcard("ab*ba", "abxba") is True


class TestWildcardOnly:
    def test_star_matches_anything(self):
        assert match_segment_to_wildcard("*", "anything") is True
        assert match_segment_to_wildcard("*", "") is True
        assert match_segment_to_wildcard("*", "file.ts") is True
