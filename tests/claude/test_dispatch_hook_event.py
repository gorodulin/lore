from lore.claude.dispatch_hook_event import dispatch_hook_event, _matches


class TestMatches:
    def test_wildcard_matches_all_events(self):
        assert _matches("SessionStart", "", "*", None) is True
        assert _matches("PostToolUse", "Read", "*", None) is True

    def test_exact_event_matches(self):
        assert _matches("PostToolUse", "Read", "PostToolUse", None) is True

    def test_event_mismatch(self):
        assert _matches("SessionStart", "", "PostToolUse", None) is False

    def test_tool_pattern_filters(self):
        assert _matches("PostToolUse", "Read", "PostToolUse", "Read") is True
        assert _matches("PostToolUse", "Write", "PostToolUse", "Read") is False

    def test_none_tool_matches_any(self):
        assert _matches("PostToolUse", "Read", "PostToolUse", None) is True
        assert _matches("PostToolUse", "", "PostToolUse", None) is True


class TestDispatchHookEvent:
    def test_wildcard_handler_runs_for_all(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")

        dispatch_hook_event(
            {"hook_event_name": "SessionStart"},
            project_root=str(tmp_path),
            log_path=log_path,
        )

        # The log handler should have written the event
        assert (tmp_path / "events.jsonl").exists()

    def test_tool_pattern_filters_correctly(self, tmp_path):
        log_path = str(tmp_path / "events.jsonl")

        # A Write event should not trigger the Read handler
        result = dispatch_hook_event(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": "foo.ts"},
            },
            project_root=str(tmp_path),
            log_path=log_path,
        )

        # No additionalContext since collect_facts only matches Read
        assert "additionalContext" not in result

    def test_merges_hook_specific_additional_context(self, tmp_path, monkeypatch):
        from lore.claude import dispatch_hook_event as mod

        def handler_a(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "context-a"}}

        def handler_b(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "context-b"}}

        monkeypatch.setattr(
            mod,
            "HANDLERS",
            [
                ("*", None, None, handler_a, 1),
                ("*", None, None, handler_b, 1),
            ],
        )

        result = dispatch_hook_event(
            {"hook_event_name": "SessionStart"},
            project_root=str(tmp_path),
            log_path="",
        )

        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "context-a" in ctx
        assert "context-b" in ctx

    def test_none_results_ignored(self, tmp_path, monkeypatch):
        from lore.claude import dispatch_hook_event as mod

        def noop_handler(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            return None

        monkeypatch.setattr(
            mod,
            "HANDLERS",
            [("*", None, None, noop_handler, 1)],
        )

        result = dispatch_hook_event(
            {"hook_event_name": "SessionStart"},
            project_root=str(tmp_path),
            log_path="",
        )
        assert result == {}

    def test_handler_exception_does_not_crash(self, tmp_path, monkeypatch):
        from lore.claude import dispatch_hook_event as mod

        def bad_handler(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            raise RuntimeError("boom")

        def good_handler(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "ok"}}

        monkeypatch.setattr(
            mod,
            "HANDLERS",
            [
                ("*", None, None, bad_handler, 1),
                ("*", None, None, good_handler, 1),
            ],
        )

        result = dispatch_hook_event(
            {"hook_event_name": "SessionStart"},
            project_root=str(tmp_path),
            log_path="",
        )
        assert result["hookSpecificOutput"]["additionalContext"] == "ok"

    def test_bash_without_cmdmeta_is_denied_by_gate(self, tmp_path):
        """Default HANDLERS registry routes Bash through the CMD-META gate."""
        result = dispatch_hook_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "ls"},
            },
            project_root=str(tmp_path),
            log_path=str(tmp_path / "events.jsonl"),
        )
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "CMD-META" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_bash_with_valid_cmdmeta_passes_gate(self, tmp_path):
        """Valid META block means the gate returns {} and collector handles the event."""
        command = "ls  # ---CMD-META-BEGIN---\n# tools: ls\n# ---CMD-META-END---"
        result = dispatch_hook_event(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": command},
            },
            project_root=str(tmp_path),
            log_path=str(tmp_path / "events.jsonl"),
        )
        # No facts in empty project → no additionalContext; and no deny either.
        hook_output = result.get("hookSpecificOutput", {})
        assert hook_output.get("permissionDecision") != "deny"

    def test_hook_tag_passed_to_handler(self, tmp_path, monkeypatch):
        from lore.claude import dispatch_hook_event as mod

        received_tags = []

        def capture_handler(event_data, *, project_root, log_path, hook_tag=None, display_rate=1):
            received_tags.append(hook_tag)
            return None

        monkeypatch.setattr(
            mod,
            "HANDLERS",
            [
                ("*", None, None, capture_handler, 1),
                ("PostToolUse", "Read", "hook:read", capture_handler, 1),
            ],
        )

        dispatch_hook_event(
            {"hook_event_name": "PostToolUse", "tool_name": "Read"},
            project_root=str(tmp_path),
            log_path="",
        )

        assert received_tags == [None, "hook:read"]
