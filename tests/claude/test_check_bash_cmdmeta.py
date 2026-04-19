from lore.claude.check_bash_cmdmeta import check_bash_cmdmeta


def _bash_event(command: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "session_id": "t",
        "tool_input": {"command": command},
    }


def _invoke(event: dict) -> dict:
    return check_bash_cmdmeta(
        event, project_root="/x", log_path="", hook_tag=None, display_rate=1
    )


class TestCheckBashCmdMeta:
    def test_missing_block_denies(self):
        result = _invoke(_bash_event("ls"))
        output = result["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "CMD-META block missing" in output["permissionDecisionReason"]

    def test_valid_block_passes(self):
        cmd = "ls  # ---CMD-META-BEGIN---\n# tools: ls\n# ---CMD-META-END---"
        assert _invoke(_bash_event(cmd)) == {}

    def test_missing_end_denies_with_parse_error(self):
        cmd = "ls  # ---CMD-META-BEGIN---\n# tools: ls"
        output = _invoke(_bash_event(cmd))["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "END sentinel" in output["permissionDecisionReason"]

    def test_unknown_flag_denies_with_validation_error(self):
        cmd = (
            "ls  # ---CMD-META-BEGIN---\n"
            "# tools: ls\n"
            "# flags: bogus_flag\n"
            "# ---CMD-META-END---"
        )
        output = _invoke(_bash_event(cmd))["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "bogus_flag" in output["permissionDecisionReason"]

    def test_missing_tools_key_denies(self):
        cmd = (
            "ls  # ---CMD-META-BEGIN---\n"
            "# flags: slow\n"
            "# ---CMD-META-END---"
        )
        output = _invoke(_bash_event(cmd))["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "'tools' is missing" in output["permissionDecisionReason"]

    def test_empty_tools_list_passes(self):
        cmd = "echo hi  # ---CMD-META-BEGIN---\n# tools:\n# ---CMD-META-END---"
        assert _invoke(_bash_event(cmd)) == {}

    def test_no_command_field_still_denies(self):
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {}}
        output = _invoke(event)["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
