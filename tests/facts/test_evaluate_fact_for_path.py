from lore.facts.compile_fact_matchers import compile_fact_matchers
from lore.facts.evaluate_fact_for_path import evaluate_fact_for_path


class TestEvaluateFactForPath:
    def test_matches_simple_glob(self):
        fact = {"fact": "JS files", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.js") is True

    def test_no_match_different_extension(self):
        fact = {"fact": "JS files", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.ts") is False

    def test_exclusion_prevents_match(self):
        fact = {
            "fact": "JS files except vendor",
            "incl": ["g:**/*.js"],
            "skip": ["g:vendor/*"],  # exclude direct children of vendor/
        }
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.js") is True
        assert evaluate_fact_for_path(compiled, "vendor/lib.js") is False

    def test_exclusion_checked_first(self):
        # Even if incl matches, skip should veto
        fact = {
            "fact": "Test",
            "incl": ["g:**/*"],  # matches everything
            "skip": ["g:**/*.min.js"],
        }
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "app.min.js") is False

    def test_multiple_incl_any_matches(self):
        fact = {
            "fact": "Frontend files",
            "incl": ["g:**/*.js", "g:**/*.ts", "g:**/*.css"],
        }
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.js") is True
        assert evaluate_fact_for_path(compiled, "src/app.ts") is True
        assert evaluate_fact_for_path(compiled, "src/app.css") is True
        assert evaluate_fact_for_path(compiled, "src/app.py") is False

    def test_multiple_skip_any_excludes(self):
        fact = {
            "fact": "JS files",
            "incl": ["g:**/*.js"],
            "skip": ["g:vendor/**", "g:node_modules/**"],  # exclude from root
        }
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "vendor/lib.js") is False
        assert evaluate_fact_for_path(compiled, "node_modules/pkg/index.js") is False
        assert evaluate_fact_for_path(compiled, "src/app.js") is True

    def test_directory_matching(self):
        fact = {"fact": "Source dirs", "incl": ["g:src/**/"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/api/") is True
        assert evaluate_fact_for_path(compiled, "src/api/users.ts") is False  # file, not dir

    def test_file_matching(self):
        fact = {"fact": "Config files", "incl": ["g:*.config.js"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "webpack.config.js") is True
        assert evaluate_fact_for_path(compiled, "configs/") is False  # dir

    def test_empty_skip_no_exclusions(self):
        fact = {"fact": "All JS", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "any/path/file.js") is True

    def test_literal_path_match(self):
        fact = {"fact": "Specific file", "incl": ["g:src/main.ts"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/main.ts") is True
        assert evaluate_fact_for_path(compiled, "src/other.ts") is False

    # --- Content regex matcher tests ---

    def test_glob_only_still_works_without_content(self):
        fact = {"fact": "JS files", "incl": ["g:**/*.js"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.js") is True
        assert evaluate_fact_for_path(compiled, "src/app.js", content=None) is True

    def test_regex_only_incl_matches_content(self):
        fact = {"fact": "Raise usage", "incl": ["r:raise\\s+"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "any/path.py", content="raise ValueError") is True

    def test_regex_only_incl_no_content_match(self):
        fact = {"fact": "Raise usage", "incl": ["r:raise\\s+"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "any/path.py", content="return 42") is False

    def test_mixed_glob_and_regex_incl_both_must_match(self):
        fact = {"fact": "PY raise", "incl": ["g:**/*.py", "r:raise\\s+"]}
        compiled = compile_fact_matchers(fact)

        # Both match
        assert evaluate_fact_for_path(compiled, "src/app.py", content="raise ValueError") is True
        # Path matches, content doesn't
        assert evaluate_fact_for_path(compiled, "src/app.py", content="return 42") is False
        # Content matches, path doesn't
        assert evaluate_fact_for_path(compiled, "src/app.js", content="raise ValueError") is False

    def test_content_none_with_regex_matchers_no_match(self):
        fact = {"fact": "Test", "incl": ["r:something"]}
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "any/path.py", content=None) is False

    def test_skip_with_regex_content_exclusion(self):
        fact = {
            "fact": "All PY",
            "incl": ["g:**/*.py"],
            "skip": ["r:# generated"],
        }
        compiled = compile_fact_matchers(fact)

        assert evaluate_fact_for_path(compiled, "src/app.py", content="# generated file") is False
        assert evaluate_fact_for_path(compiled, "src/app.py", content="normal code") is True

    def test_skip_with_mixed_glob_and_regex_and_logic(self):
        fact = {
            "fact": "All PY",
            "incl": ["g:**/*.py"],
            "skip": ["g:vendor/**", "r:# generated"],
        }
        compiled = compile_fact_matchers(fact)

        # Skip requires both path AND content group to match
        # vendor path + generated content → skip fires
        assert evaluate_fact_for_path(compiled, "vendor/lib.py", content="# generated") is False
        # vendor path + normal content → skip doesn't fire (content group fails)
        assert evaluate_fact_for_path(compiled, "vendor/lib.py", content="normal") is True
        # non-vendor path + generated content → skip doesn't fire (path group fails)
        assert evaluate_fact_for_path(compiled, "src/lib.py", content="# generated") is True
