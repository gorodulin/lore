from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.matchers.match_path_to_glob import match_path_to_glob


class TestPathMatches:
    def test_literal_match(self):
        compiled = compile_glob_pattern("src/utils/file.ts")
        assert match_path_to_glob(compiled, "src/utils/file.ts") is True

    def test_wildcard_match(self):
        compiled = compile_glob_pattern("src/*.ts")
        assert match_path_to_glob(compiled, "src/file.ts") is True

    def test_globstar_match(self):
        compiled = compile_glob_pattern("**/api.js")
        assert match_path_to_glob(compiled, "app/backend/api.js") is True
        assert match_path_to_glob(compiled, "api.js") is True

    def test_complex_pattern(self):
        compiled = compile_glob_pattern("app/**/src/*.js")
        assert match_path_to_glob(compiled, "app/frontend/src/api.js") is True
        assert match_path_to_glob(compiled, "app/src/api.js") is True
        assert match_path_to_glob(compiled, "app/frontend/src/api.ts") is False

    def test_dir_pattern_matches_dir(self):
        compiled = compile_glob_pattern("src/")
        assert match_path_to_glob(compiled, "src/") is True

    def test_dir_pattern_not_matches_file(self):
        compiled = compile_glob_pattern("src/")
        assert match_path_to_glob(compiled, "src") is False

    def test_file_path_no_trailing_slash(self):
        compiled = compile_glob_pattern("src/**/file.ts")
        assert match_path_to_glob(compiled, "src/utils/file.ts") is True
