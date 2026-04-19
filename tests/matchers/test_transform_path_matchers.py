from lore.matchers.transform_path_matchers import transform_path_matchers


class TestTransformPathMatchers:
    def test_transforms_path_only(self):
        result = transform_path_matchers(
            ["p:src/**/*.py", "c:import os", "d:(?i)deploy"],
            lambda v: f"app/{v}",
        )
        assert result == ["p:app/src/**/*.py", "c:import os", "d:(?i)deploy"]

    def test_none_return_keeps_matcher(self):
        result = transform_path_matchers(
            ["p:**/*.py", "p:src/app.py"],
            lambda v: None if v.startswith("**") else f"app/{v}",
        )
        assert result == ["p:**/*.py", "p:app/src/app.py"]

    def test_non_path_matchers_untouched(self):
        result = transform_path_matchers(
            ["c:import os", "d:(?i)deploy", "x:rm -rf"],
            lambda v: v.upper(),
        )
        assert result == ["c:import os", "d:(?i)deploy", "x:rm -rf"]

    def test_empty_input(self):
        assert transform_path_matchers([], lambda v: f"x/{v}") == []

    def test_invalid_matcher_passed_through(self):
        result = transform_path_matchers(
            ["p:**/*.py", "bad_matcher"],
            lambda v: f"app/{v}",
        )
        assert result == ["p:app/**/*.py", "bad_matcher"]
