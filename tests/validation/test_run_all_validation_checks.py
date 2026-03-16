import json

from lore.validation.run_all_validation_checks import run_all_validation_checks


class TestRunAllValidationChecks:
    def test_empty_directory(self, tmp_path):
        result = run_all_validation_checks(str(tmp_path))
        assert result == {"issues": [], "count": 0}

    def test_clean_facts(self, tmp_path):
        facts = {
            "f1": {"fact": "Fact one", "incl": ["g:src/**/*.py"]},
            "f2": {"fact": "Fact two", "incl": ["g:lib/**/*.js"]},
        }
        (tmp_path / ".lore.json").write_text(json.dumps(facts))

        result = run_all_validation_checks(str(tmp_path))
        assert result["count"] == 0
        assert result["issues"] == []

    def test_detects_duplicate_matchers(self, tmp_path):
        facts = {
            "f1": {"fact": "Fact one", "incl": ["g:**/*.py", "g:**/*.py"]},
        }
        (tmp_path / ".lore.json").write_text(json.dumps(facts))

        result = run_all_validation_checks(str(tmp_path))
        checks = [i["check"] for i in result["issues"]]
        assert "duplicate_matchers" in checks
        assert result["count"] > 0

    def test_detects_dead_skip_matchers(self, tmp_path):
        facts = {
            "f1": {
                "fact": "Fact one",
                "incl": ["g:src/**/*.py"],
                "skip": ["g:vendor/**"],
            },
        }
        (tmp_path / ".lore.json").write_text(json.dumps(facts))

        result = run_all_validation_checks(str(tmp_path))
        checks = [i["check"] for i in result["issues"]]
        assert "dead_skip_matchers" in checks

    def test_detects_subset_patterns(self, tmp_path):
        facts = {
            "f1": {
                "fact": "Fact one",
                "incl": ["g:**/*.py", "g:src/**/*.py"],
            },
        }
        (tmp_path / ".lore.json").write_text(json.dumps(facts))

        result = run_all_validation_checks(str(tmp_path))
        checks = [i["check"] for i in result["issues"]]
        assert "subset_patterns" in checks

    def test_globalizes_before_validation(self, tmp_path):
        """Facts in subdirectory should be globalized before cross-fact checks."""
        # Two facts in different directories with the same local matcher
        # After globalization they should NOT be duplicates
        (tmp_path / "src").mkdir()
        (tmp_path / "lib").mkdir()
        src_facts = {"f1": {"fact": "Src fact", "incl": ["g:**/*.py"]}}
        lib_facts = {"f2": {"fact": "Lib fact", "incl": ["g:**/*.py"]}}
        (tmp_path / "src" / ".lore.json").write_text(json.dumps(src_facts))
        (tmp_path / "lib" / ".lore.json").write_text(json.dumps(lib_facts))

        result = run_all_validation_checks(str(tmp_path))
        # After globalization: f1 has g:src/**/*.py, f2 has g:lib/**/*.py
        # These are NOT duplicates
        dup_issues = [i for i in result["issues"] if i["check"] == "duplicate_matchers"]
        assert dup_issues == []

    def test_multiple_issue_types(self, tmp_path):
        facts = {
            "f1": {
                "fact": "Fact one",
                "incl": ["g:**/*.py", "g:src/**/*.py"],
                "skip": ["g:vendor/**"],
            },
            "f2": {"fact": "Fact two", "incl": ["g:**/*.js", "g:**/*.js"]},
        }
        (tmp_path / ".lore.json").write_text(json.dumps(facts))

        result = run_all_validation_checks(str(tmp_path))
        assert result["count"] >= 2
        checks = [i["check"] for i in result["issues"]]
        assert "duplicate_matchers" in checks
        assert "subset_patterns" in checks
