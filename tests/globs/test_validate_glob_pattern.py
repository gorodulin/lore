from lore.globs.validate_glob_pattern import validate_glob_pattern
from lore.error_codes import INVALID_EMPTY_PATTERN, INVALID_DOUBLE_SLASH, INVALID_GLOBSTAR_POSITION, INVALID_MULTIPLE_GLOBSTARS, INVALID_MULTIPLE_WILDCARDS_IN_SEGMENT, INVALID_UNSUPPORTED_METACHARACTER


class TestValidPatterns:
    def test_literal_path(self):
        valid, errors = validate_glob_pattern("src/utils/file.ts")
        assert valid is True
        assert errors == []

    def test_single_wildcard(self):
        valid, errors = validate_glob_pattern("src/*.ts")
        assert valid is True

    def test_prefix_wildcard(self):
        valid, errors = validate_glob_pattern("src/test_*")
        assert valid is True

    def test_infix_wildcard(self):
        valid, errors = validate_glob_pattern("src/f*o.ts")
        assert valid is True

    def test_globstar_prefix(self):
        valid, errors = validate_glob_pattern("**/test/*.ts")
        assert valid is True

    def test_globstar_infix(self):
        valid, errors = validate_glob_pattern("src/**/test.ts")
        assert valid is True

    def test_globstar_suffix(self):
        valid, errors = validate_glob_pattern("docs/**")
        assert valid is True

    def test_directory_pattern(self):
        valid, errors = validate_glob_pattern("src/utils/")
        assert valid is True

    def test_multiple_single_wildcards_different_segments(self):
        valid, errors = validate_glob_pattern("src/*/test_*.ts")
        assert valid is True

    def test_globstar_only(self):
        valid, errors = validate_glob_pattern("**")
        assert valid is True


class TestInvalidPatterns:
    def test_empty_pattern(self):
        valid, errors = validate_glob_pattern("")
        assert valid is False
        assert errors[0]["code"] == INVALID_EMPTY_PATTERN

    def test_whitespace_pattern(self):
        valid, errors = validate_glob_pattern("   ")
        assert valid is False
        assert errors[0]["code"] == INVALID_EMPTY_PATTERN

    def test_just_slash(self):
        valid, errors = validate_glob_pattern("/")
        assert valid is False
        assert errors[0]["code"] == INVALID_EMPTY_PATTERN

    def test_double_slash(self):
        valid, errors = validate_glob_pattern("src//utils/file.ts")
        assert valid is False
        assert errors[0]["code"] == INVALID_DOUBLE_SLASH
        assert errors[0]["at"] == 3

    def test_multiple_globstars(self):
        valid, errors = validate_glob_pattern("src/**/**/file.ts")
        assert valid is False
        assert errors[0]["code"] == INVALID_MULTIPLE_GLOBSTARS

    def test_globstar_mixed_with_chars(self):
        valid, errors = validate_glob_pattern("src/**.ts")
        assert valid is False
        assert errors[0]["code"] == INVALID_GLOBSTAR_POSITION

    def test_globstar_mixed_prefix(self):
        valid, errors = validate_glob_pattern("src/test**")
        assert valid is False
        assert errors[0]["code"] == INVALID_GLOBSTAR_POSITION

    def test_multiple_wildcards_in_segment(self):
        valid, errors = validate_glob_pattern("src/*test*.ts")
        assert valid is False
        assert errors[0]["code"] == INVALID_MULTIPLE_WILDCARDS_IN_SEGMENT

    def test_brace_expansion(self):
        valid, errors = validate_glob_pattern("**/*.{ts,tsx}")
        assert valid is False
        assert errors[0]["code"] == INVALID_UNSUPPORTED_METACHARACTER
        assert errors[0]["at"] == 5

    def test_character_class(self):
        valid, errors = validate_glob_pattern("src/[a-z]*.py")
        assert valid is False
        assert errors[0]["code"] == INVALID_UNSUPPORTED_METACHARACTER
        assert errors[0]["at"] == 4

    def test_closing_brace_alone(self):
        valid, errors = validate_glob_pattern("src/foo}.py")
        assert valid is False
        assert errors[0]["code"] == INVALID_UNSUPPORTED_METACHARACTER

    def test_closing_bracket_alone(self):
        valid, errors = validate_glob_pattern("src/foo].py")
        assert valid is False
        assert errors[0]["code"] == INVALID_UNSUPPORTED_METACHARACTER
