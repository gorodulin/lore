from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.matchers.match_path_segments import match_path_segments


class TestLiteralPatterns:
    def test_exact_match(self):
        compiled = compile_glob_pattern("src/utils/file.ts")
        assert match_path_segments(compiled, ["src", "utils", "file.ts"], is_dir=False) is True

    def test_no_match_different_segment(self):
        compiled = compile_glob_pattern("src/utils/file.ts")
        assert match_path_segments(compiled, ["src", "utils", "other.ts"], is_dir=False) is False

    def test_no_match_different_length(self):
        compiled = compile_glob_pattern("src/utils/file.ts")
        assert match_path_segments(compiled, ["src", "file.ts"], is_dir=False) is False


class TestWildcardPatterns:
    def test_suffix_wildcard(self):
        compiled = compile_glob_pattern("src/*.ts")
        assert match_path_segments(compiled, ["src", "file.ts"], is_dir=False) is True
        assert match_path_segments(compiled, ["src", "file.js"], is_dir=False) is False

    def test_prefix_wildcard(self):
        compiled = compile_glob_pattern("src/test_*")
        assert match_path_segments(compiled, ["src", "test_foo"], is_dir=False) is True
        assert match_path_segments(compiled, ["src", "spec_foo"], is_dir=False) is False


class TestGlobstarPatterns:
    def test_globstar_zero_segments(self):
        # ** can match zero segments
        compiled = compile_glob_pattern("src/**/file.ts")
        assert match_path_segments(compiled, ["src", "file.ts"], is_dir=False) is True

    def test_globstar_one_segment(self):
        compiled = compile_glob_pattern("src/**/file.ts")
        assert match_path_segments(compiled, ["src", "utils", "file.ts"], is_dir=False) is True

    def test_globstar_multiple_segments(self):
        compiled = compile_glob_pattern("src/**/file.ts")
        assert match_path_segments(compiled, ["src", "a", "b", "c", "file.ts"], is_dir=False) is True

    def test_globstar_at_start(self):
        compiled = compile_glob_pattern("**/file.ts")
        assert match_path_segments(compiled, ["file.ts"], is_dir=False) is True
        assert match_path_segments(compiled, ["src", "file.ts"], is_dir=False) is True
        assert match_path_segments(compiled, ["a", "b", "c", "file.ts"], is_dir=False) is True

    def test_globstar_at_end(self):
        compiled = compile_glob_pattern("src/**")
        assert match_path_segments(compiled, ["src"], is_dir=False) is True
        assert match_path_segments(compiled, ["src", "file.ts"], is_dir=False) is True
        assert match_path_segments(compiled, ["src", "a", "b"], is_dir=False) is True

    def test_globstar_with_wildcard(self):
        compiled = compile_glob_pattern("**/src/*.js")
        assert match_path_segments(compiled, ["src", "app.js"], is_dir=False) is True
        assert match_path_segments(compiled, ["app", "src", "app.js"], is_dir=False) is True
        assert match_path_segments(compiled, ["app", "src", "app.ts"], is_dir=False) is False


class TestDirectoryPatterns:
    def test_dir_pattern_matches_dir(self):
        compiled = compile_glob_pattern("src/utils/")
        assert match_path_segments(compiled, ["src", "utils"], is_dir=True) is True

    def test_dir_pattern_not_matches_file(self):
        compiled = compile_glob_pattern("src/utils/")
        assert match_path_segments(compiled, ["src", "utils"], is_dir=False) is False


class TestInvalidPatterns:
    def test_invalid_pattern_returns_false(self):
        compiled = compile_glob_pattern("")
        assert match_path_segments(compiled, ["src"], is_dir=False) is False
