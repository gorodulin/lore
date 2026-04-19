import json

from lore.claude.match_facts_for_path import match_facts_for_path


def test_returns_matching_facts_with_dicts(tmp_path):
    rules = {
        "api-handlers": {
            "fact": "This module handles API routing",
            "incl": ["p:src/api/**/*.ts"],
        },
        "db-layer": {
            "fact": "Database layer",
            "incl": ["p:src/db/**/*.ts"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "src/api/users.ts")

    assert "api-handlers" in result
    assert result["api-handlers"]["fact"] == "This module handles API routing"
    assert "db-layer" not in result


def test_no_rules_returns_empty(tmp_path):
    result = match_facts_for_path(str(tmp_path), "src/foo.ts")
    assert result == {}


def test_invalid_root_returns_empty():
    result = match_facts_for_path("/nonexistent/path/xyz", "foo.ts")
    assert result == {}


def test_file_outside_project_returns_empty(tmp_path):
    rules = {"a": {"fact": "A", "incl": ["p:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "/outside/project/foo.ts")
    assert result == {}


def test_relative_path(tmp_path):
    rules = {"js": {"fact": "JavaScript files", "incl": ["p:**/*.js"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "lib/utils.js")
    assert result["js"]["fact"] == "JavaScript files"


def test_absolute_path_within_project(tmp_path):
    rules = {"py": {"fact": "Python files", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    abs_path = str(tmp_path / "src" / "main.py")
    result = match_facts_for_path(str(tmp_path), abs_path)
    assert result["py"]["fact"] == "Python files"


def test_no_matches_returns_empty(tmp_path):
    rules = {"ts": {"fact": "TypeScript", "incl": ["p:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "readme.md")
    assert result == {}


def test_regex_matcher_with_content(tmp_path):
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["p:**/*.py", "c:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    # Content matches regex
    result = match_facts_for_path(str(tmp_path), "src/app.py", content="raise ValueError")
    assert "raise-fact" in result

    # Content doesn't match regex
    result = match_facts_for_path(str(tmp_path), "src/app.py", content="return 42")
    assert result == {}

    # No content with regex matcher → no match
    result = match_facts_for_path(str(tmp_path), "src/app.py")
    assert result == {}


def test_tags_in_returned_dict(tmp_path):
    rules = {
        "tagged": {
            "fact": "Tagged fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:read", "kind:convention"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "src/main.py")
    assert result["tagged"]["tags"] == ["hook:read", "kind:convention"]
