import json

import pytest

from lore.facts.match_facts_for_path import match_facts_for_path


def test_returns_matching_facts(tmp_path):
    rules = {
        "api-handlers": {
            "fact": "API routing",
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
    assert result["api-handlers"]["fact"] == "API routing"
    assert "db-layer" not in result


def test_no_matches_returns_empty(tmp_path):
    rules = {"ts": {"fact": "TypeScript", "incl": ["p:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "readme.md")
    assert result == {}


def test_no_facts_returns_empty(tmp_path):
    result = match_facts_for_path(str(tmp_path), "src/foo.ts")
    assert result == {}


def test_empty_root_raises():
    with pytest.raises(ValueError, match="project_root must not be empty"):
        match_facts_for_path("", "foo.ts")


def test_path_outside_project_raises(tmp_path):
    rules = {"a": {"fact": "A", "incl": ["p:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    with pytest.raises(ValueError, match="outside project root"):
        match_facts_for_path(str(tmp_path), "/outside/project/foo.ts")


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


def test_regex_with_content(tmp_path):
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["p:**/*.py", "c:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "src/app.py", content="raise ValueError")
    assert "raise-fact" in result

    result = match_facts_for_path(str(tmp_path), "src/app.py", content="return 42")
    assert result == {}

    result = match_facts_for_path(str(tmp_path), "src/app.py")
    assert result == {}


def test_subdirectory_facts(tmp_path):
    sub = tmp_path / "lib"
    sub.mkdir()
    rules = {"local": {"fact": "Lib-local fact", "incl": ["p:**/*.py"]}}
    (sub / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "lib/utils.py")
    assert "local" in result
    assert result["local"]["fact"] == "Lib-local fact"

    result = match_facts_for_path(str(tmp_path), "other/file.py")
    assert "local" not in result


def test_tags_preserved(tmp_path):
    rules = {
        "tagged": {
            "fact": "Tagged fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:read"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "src/main.py")
    assert result["tagged"]["tags"] == ["hook:read"]


def test_tools_param_matches_tool_fact(tmp_path):
    rules = {
        "git-push": {
            "fact": "Git push is risky",
            "incl": ["t:git push"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "", tools=("git push",))
    assert "git-push" in result

    result = match_facts_for_path(str(tmp_path), "", tools=("ls",))
    assert result == {}


def test_tools_none_skips_tool_fact(tmp_path):
    rules = {
        "git-push": {
            "fact": "Git push is risky",
            "incl": ["t:git push"],
        },
        "py-files": {
            "fact": "Python files",
            "incl": ["p:**/*.py"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    # File event: t: fact must not fire (decision 10).
    result = match_facts_for_path(str(tmp_path), "src/app.py")
    assert "git-push" not in result
    assert "py-files" in result


def test_endpoints_param_matches_endpoint_fact(tmp_path):
    rules = {
        "prod": {
            "fact": "Talking to prod",
            "incl": ["e:\\.prod\\."],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "", endpoints=("api.prod.com",))
    assert "prod" in result

    result = match_facts_for_path(str(tmp_path), "", endpoints=("api.staging.com",))
    assert result == {}


def test_flags_param_matches_flag_fact(tmp_path):
    rules = {
        "mutates": {
            "fact": "Command mutates state",
            "incl": ["f:mutates"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(str(tmp_path), "", flags=("mutates", "network"))
    assert "mutates" in result

    result = match_facts_for_path(str(tmp_path), "", flags=("network",))
    assert result == {}


def test_affected_paths_param_matches_path_fact(tmp_path):
    rules = {
        "payments": {
            "fact": "Payments touched",
            "incl": ["p:src/payments/**"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    result = match_facts_for_path(
        str(tmp_path), "", affected_paths=("src/payments/charge.py",)
    )
    assert "payments" in result

    result = match_facts_for_path(
        str(tmp_path), "", affected_paths=("src/api/users.py",)
    )
    assert result == {}
