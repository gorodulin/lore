"""End-to-end integration tests for the handle_claude_hook CLI entry point.

Invokes ``python -m lore.claude.cli.handle_claude_hook`` as a subprocess,
feeds stdin, and asserts the full stdout JSON matches expectations.

Scope limited to the binding surface that unit tests cannot reach: stdin
read, JSON encode/decode, error behavior at the entry point. Fact-matching
depth is covered in-process by :mod:`test_hook_event_dispatch_scenarios`,
which avoids paying the subprocess startup cost on every assertion.
"""

import json
import subprocess
import sys


HOOK_ENTRYPOINT = [sys.executable, "-m", "lore.claude.cli.handle_claude_hook"]


def _run(stdin: str) -> str:
    result = subprocess.run(
        HOOK_ENTRYPOINT,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
    )
    return result.stdout.strip()


class TestHookCLIEndToEnd:
    def test_blank_stdin_returns_empty_object(self):
        assert _run("") == "{}"

    def test_invalid_json_returns_empty_object(self):
        assert _run("not json at all") == "{}"

    def test_unknown_event_returns_empty_object(self):
        """SessionStart has no registered collector; CLI still emits valid JSON."""
        payload = {"hook_event_name": "SessionStart"}
        out = _run(json.dumps(payload))
        assert json.loads(out) == {}

    def test_bash_missing_cmdmeta_returns_deny_payload(self, tmp_path):
        """CLI correctly serializes deny responses as JSON on stdout."""
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "session_id": "cli-deny",
            "cwd": str(tmp_path),
            "tool_input": {"command": "ls"},
        }
        response = json.loads(_run(json.dumps(payload)))
        out = response["hookSpecificOutput"]
        assert out["permissionDecision"] == "deny"
        assert "CMD-META block missing" in out["permissionDecisionReason"]
