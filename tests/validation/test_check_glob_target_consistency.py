from lore.validation.check_glob_target_consistency import check_glob_target_consistency


class TestCheckGlobTargetConsistency:
    def test_all_files_consistent(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js", "g:**/*.ts"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_all_dirs_consistent(self):
        fact = {"fact": "Test", "incl": ["g:src/", "g:lib/"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_mixed_targets_inconsistent(self):
        fact = {"fact": "Test", "incl": ["g:**/*.js", "g:src/"]}
        result = check_glob_target_consistency(fact)
        assert result is not None
        assert "file_globs" in result
        assert "dir_globs" in result
        assert "g:**/*.js" in result["file_globs"]
        assert "g:src/" in result["dir_globs"]

    def test_mixed_in_incl_and_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js"],
            "skip": ["g:vendor/"],  # dir in skip
        }
        result = check_glob_target_consistency(fact)
        assert result is not None
        assert "g:**/*.js" in result["file_globs"]
        assert "g:vendor/" in result["dir_globs"]

    def test_only_incl_files(self):
        fact = {"fact": "Test", "incl": ["g:src/app.js"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_only_incl_dirs(self):
        fact = {"fact": "Test", "incl": ["g:src/"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_empty_fact(self):
        fact = {"fact": "Test", "incl": []}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_non_glob_matchers_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js", "r:.*\\.js$"],  # regex ignored
        }
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_invalid_matchers_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["g:**/*.js", "invalid"],
        }
        result = check_glob_target_consistency(fact)
        assert result is None
