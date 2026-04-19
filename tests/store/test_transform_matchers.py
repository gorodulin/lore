from lore.store.transform_matchers import transform_matchers


class TestTransformMatchers:
    def test_transform_path_only(self):
        result = transform_matchers(
            ["p:src/**/*.py", "c:import os"],
            {"path": lambda v: f"app/{v}"},
        )
        assert result == ["p:app/src/**/*.py", "c:import os"]

    def test_transform_content_only(self):
        result = transform_matchers(
            ["p:**/*.py", "c:import os"],
            {"content": lambda v: v.upper()},
        )
        assert result == ["p:**/*.py", "c:IMPORT OS"]

    def test_transform_multiple_types(self):
        result = transform_matchers(
            ["p:src/**/*.py", "c:import os"],
            {"path": lambda v: f"app/{v}", "content": lambda v: v.upper()},
        )
        assert result == ["p:app/src/**/*.py", "c:IMPORT OS"]

    def test_no_matching_transform_passes_through(self):
        result = transform_matchers(
            ["p:**/*.py", "c:import os"],
            {"string": lambda v: v.upper()},
        )
        assert result == ["p:**/*.py", "c:import os"]

    def test_empty_transforms(self):
        result = transform_matchers(["p:**/*.py"], {})
        assert result == ["p:**/*.py"]

    def test_empty_matchers(self):
        result = transform_matchers([], {"path": lambda v: f"x/{v}"})
        assert result == []

    def test_transform_returning_none_keeps_original(self):
        result = transform_matchers(
            ["p:src/**/*.py", "p:**/*.js"],
            {"path": lambda v: None if v.startswith("**") else f"app/{v}"},
        )
        assert result == ["p:app/src/**/*.py", "p:**/*.js"]

    def test_invalid_matcher_passed_through(self):
        result = transform_matchers(
            ["p:**/*.py", "bad_matcher", "c:test"],
            {"path": lambda v: f"x/{v}"},
        )
        assert result == ["p:x/**/*.py", "bad_matcher", "c:test"]

    def test_preserves_order(self):
        result = transform_matchers(
            ["c:first", "p:second", "c:third"],
            {"path": lambda v: v.upper()},
        )
        assert result == ["c:first", "p:SECOND", "c:third"]
