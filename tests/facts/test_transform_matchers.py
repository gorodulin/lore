from lore.facts.transform_matchers import transform_matchers


class TestTransformMatchers:
    def test_transform_glob_only(self):
        result = transform_matchers(
            ["g:src/**/*.py", "r:import os"],
            {"glob": lambda v: f"app/{v}"},
        )
        assert result == ["g:app/src/**/*.py", "r:import os"]

    def test_transform_regex_only(self):
        result = transform_matchers(
            ["g:**/*.py", "r:import os"],
            {"regex": lambda v: v.upper()},
        )
        assert result == ["g:**/*.py", "r:IMPORT OS"]

    def test_transform_multiple_types(self):
        result = transform_matchers(
            ["g:src/**/*.py", "r:import os"],
            {"glob": lambda v: f"app/{v}", "regex": lambda v: v.upper()},
        )
        assert result == ["g:app/src/**/*.py", "r:IMPORT OS"]

    def test_no_matching_transform_passes_through(self):
        result = transform_matchers(
            ["g:**/*.py", "r:import os"],
            {"string": lambda v: v.upper()},
        )
        assert result == ["g:**/*.py", "r:import os"]

    def test_empty_transforms(self):
        result = transform_matchers(["g:**/*.py"], {})
        assert result == ["g:**/*.py"]

    def test_empty_matchers(self):
        result = transform_matchers([], {"glob": lambda v: f"x/{v}"})
        assert result == []

    def test_transform_returning_none_keeps_original(self):
        result = transform_matchers(
            ["g:src/**/*.py", "g:**/*.js"],
            {"glob": lambda v: None if v.startswith("**") else f"app/{v}"},
        )
        assert result == ["g:app/src/**/*.py", "g:**/*.js"]

    def test_invalid_matcher_passed_through(self):
        result = transform_matchers(
            ["g:**/*.py", "bad_matcher", "r:test"],
            {"glob": lambda v: f"x/{v}"},
        )
        assert result == ["g:x/**/*.py", "bad_matcher", "r:test"]

    def test_preserves_order(self):
        result = transform_matchers(
            ["r:first", "g:second", "r:third"],
            {"glob": lambda v: v.upper()},
        )
        assert result == ["r:first", "g:SECOND", "r:third"]
