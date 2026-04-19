from lore.validation.check_glob_target_consistency import check_glob_target_consistency


class TestCheckGlobTargetConsistency:
    def test_all_files_consistent(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js", "p:**/*.ts"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_all_dirs_consistent(self):
        fact = {"fact": "Test", "incl": ["p:src/", "p:lib/"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_mixed_targets_inconsistent(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js", "p:src/"]}
        result = check_glob_target_consistency(fact)
        assert result is not None
        assert "file_globs" in result
        assert "dir_globs" in result
        assert "p:**/*.js" in result["file_globs"]
        assert "p:src/" in result["dir_globs"]

    def test_mixed_in_incl_and_skip(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js"],
            "skip": ["p:vendor/"],  # dir in skip
        }
        result = check_glob_target_consistency(fact)
        assert result is not None
        assert "p:**/*.js" in result["file_globs"]
        assert "p:vendor/" in result["dir_globs"]

    def test_only_incl_files(self):
        fact = {"fact": "Test", "incl": ["p:src/app.js"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_only_incl_dirs(self):
        fact = {"fact": "Test", "incl": ["p:src/"]}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_empty_fact(self):
        fact = {"fact": "Test", "incl": []}
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_non_glob_matchers_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js", "c:.*\\.js$"],  # regex ignored
        }
        result = check_glob_target_consistency(fact)
        assert result is None

    def test_invalid_matchers_ignored(self):
        fact = {
            "fact": "Test",
            "incl": ["p:**/*.js", "invalid"],
        }
        result = check_glob_target_consistency(fact)
        assert result is None
