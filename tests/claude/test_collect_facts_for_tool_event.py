import json

from lore.claude.collect_facts_for_tool_event import collect_facts_for_tool_event


def test_returns_additional_context_with_facts(tmp_path):
    rules = {
        "api-handlers": {
            "fact": "This module handles API routing",
            "incl": ["g:src/api/**/*.ts"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": "src/api/users.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "<F:api-handlers>This module handles API routing</F>" in ctx


def test_missing_file_path_returns_empty(tmp_path):
    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )
    assert result == {}


def test_no_matches_returns_empty(tmp_path):
    rules = {"ts": {"fact": "TypeScript", "incl": ["g:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": "readme.md"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )
    assert result == {}


def test_format_includes_lore_header(tmp_path):
    rules = {
        "a": {"fact": "Fact A", "incl": ["g:**/*.js"]},
        "b": {"fact": "Fact B", "incl": ["g:**/*.js"]},
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": "lib/app.js"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "<F:a>Fact A</F>" in ctx
    assert "<F:b>Fact B</F>" in ctx


def test_no_tool_input_returns_empty(tmp_path):
    event = {"hook_event_name": "PostToolUse", "tool_name": "Read"}

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )
    assert result == {}


def test_hook_tag_filters_facts(tmp_path):
    rules = {
        "read-only": {
            "fact": "Read-only fact",
            "incl": ["g:**/*.ts"],
            "tags": ["hook:read"],
        },
        "edit-only": {
            "fact": "Edit-only fact",
            "incl": ["g:**/*.ts"],
            "tags": ["hook:edit"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": "src/app.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:read"
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "Read-only fact" in ctx
    assert "Edit-only fact" not in ctx


def test_no_hook_tags_shown_on_all_events(tmp_path):
    rules = {
        "universal": {
            "fact": "Universal fact",
            "incl": ["g:**/*.ts"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": "src/app.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:edit"
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "Universal fact" in ctx


def test_read_event_with_content_regex(tmp_path):
    """PostToolUse/Read: reads file from disk, matches regex."""
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["g:**/*.py", "r:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    # Create the file on disk with matching content
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("def foo():\n    raise ValueError('bad')\n")

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": str(src / "app.py")},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "raise-fact" in ctx


def test_write_event_with_content_regex(tmp_path):
    """PreToolUse/Write: uses tool_input.content for regex matching."""
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["g:**/*.py", "r:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "src/app.py",
            "content": "def foo():\n    raise ValueError('bad')\n",
        },
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "raise-fact" in ctx


def test_edit_event_with_content_regex(tmp_path):
    """PreToolUse/Edit: uses tool_input.new_string for regex matching."""
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["g:**/*.py", "r:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "src/app.py",
            "new_string": "    raise TypeError('wrong type')\n",
        },
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    ctx = result["hookSpecificOutput"]["additionalContext"]
    assert "raise-fact" in ctx


def test_content_regex_no_match_filters_fact(tmp_path):
    """Content regex doesn't match → fact filtered out."""
    rules = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["g:**/*.py", "r:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "src/app.py",
            "content": "def foo():\n    return 42\n",
        },
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )
    assert result == {}


def test_hook_event_name_dynamic(tmp_path):
    rules = {"a": {"fact": "Fact A", "incl": ["g:**/*.ts"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": "src/app.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:edit"
    )

    assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_action_block_on_pretooluse_edit_denies(tmp_path):
    """PreToolUse/Edit with action:block fact returns permissionDecision deny."""
    rules = {
        "no-edit": {
            "fact": "Do not edit generated files",
            "incl": ["g:**/*.gen.ts"],
            "tags": ["hook:edit", "action:block"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": "src/api.gen.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:edit"
    )

    output = result["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "Do not edit generated files" in output["permissionDecisionReason"]
    assert "additionalContext" not in output


def test_action_block_on_pretooluse_write_denies(tmp_path):
    """PreToolUse/Write with action:block fact returns permissionDecision deny."""
    rules = {
        "no-write": {
            "fact": "Do not overwrite config",
            "incl": ["g:**/config.json"],
            "tags": ["hook:write", "action:block"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "app/config.json", "content": "{}"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:write"
    )

    output = result["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "Do not overwrite config" in output["permissionDecisionReason"]


def test_action_block_on_posttooluse_read_no_blocking(tmp_path):
    """PostToolUse/Read with action:block fact returns additionalContext, not deny."""
    rules = {
        "blocked": {
            "fact": "Blocked fact",
            "incl": ["g:**/*.ts"],
            "tags": ["action:block"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    src = tmp_path / "src"
    src.mkdir()
    (src / "app.ts").write_text("export default {}")

    event = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": str(src / "app.ts")},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path=""
    )

    output = result["hookSpecificOutput"]
    assert "additionalContext" in output
    assert "permissionDecision" not in output
    assert "Blocked fact" in output["additionalContext"]


def test_action_block_mixed_with_non_blocking_on_pretooluse(tmp_path):
    """Mix of blocking + non-blocking facts on PreToolUse: blocks."""
    rules = {
        "blocker": {
            "fact": "Blocked",
            "incl": ["g:**/*.ts"],
            "tags": ["hook:edit", "action:block"],
        },
        "advisor": {
            "fact": "Advisory",
            "incl": ["g:**/*.ts"],
            "tags": ["hook:edit"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(rules))

    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": "src/app.ts"},
    }

    result = collect_facts_for_tool_event(
        event, project_root=str(tmp_path), log_path="", hook_tag="hook:edit"
    )

    output = result["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "Blocked" in output["permissionDecisionReason"]
    assert "Advisory" not in output["permissionDecisionReason"]
