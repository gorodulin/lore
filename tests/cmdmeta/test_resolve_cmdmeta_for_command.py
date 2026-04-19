from lore.cmdmeta.cmdmeta import CmdMeta
from lore.cmdmeta.resolve_cmdmeta_for_command import resolve_cmdmeta_for_command


class TestResolveCmdmetaForCommand:
    def test_no_block_present_empty_command(self):
        result = resolve_cmdmeta_for_command("")
        assert result.bare_command == ""
        assert result.meta is None
        assert result.block_present is False
        assert result.errors == ()

    def test_no_block_present_with_command(self):
        result = resolve_cmdmeta_for_command("ls -la")
        assert result.bare_command == "ls -la"
        assert result.meta is None
        assert result.block_present is False
        assert result.errors == ()

    def test_valid_block(self):
        cmd = (
            "git push  # ---CMD-META-BEGIN---\n"
            "# tools: git push\n"
            "# flags: mutates, network\n"
            "# ---CMD-META-END---"
        )
        result = resolve_cmdmeta_for_command(cmd)
        assert result.bare_command == "git push"
        assert result.meta == CmdMeta(
            tools=("git push",),
            flags=("mutates", "network"),
        )
        assert result.block_present is True
        assert result.errors == ()

    def test_valid_block_empty_tools(self):
        """Trivial commands are allowed to declare empty tools list."""
        cmd = "echo hi  # ---CMD-META-BEGIN---\n# tools:\n# ---CMD-META-END---"
        result = resolve_cmdmeta_for_command(cmd)
        assert result.bare_command == "echo hi"
        assert result.meta == CmdMeta()
        assert result.block_present is True
        assert result.errors == ()

    def test_parse_error_missing_end_sentinel(self):
        cmd = "ls  # ---CMD-META-BEGIN---\n# tools: ls"
        result = resolve_cmdmeta_for_command(cmd)
        assert result.bare_command == "ls"
        assert result.meta is None
        assert result.block_present is True
        assert len(result.errors) == 1
        assert "END sentinel" in result.errors[0]

    def test_parse_error_missing_tools_key(self):
        cmd = (
            "ls  # ---CMD-META-BEGIN---\n"
            "# flags: slow\n"
            "# ---CMD-META-END---"
        )
        result = resolve_cmdmeta_for_command(cmd)
        assert result.meta is None
        assert result.block_present is True
        assert any("'tools'" in e for e in result.errors)

    def test_semantic_error_unknown_flag(self):
        cmd = (
            "ls  # ---CMD-META-BEGIN---\n"
            "# tools: ls\n"
            "# flags: bogus_flag\n"
            "# ---CMD-META-END---"
        )
        result = resolve_cmdmeta_for_command(cmd)
        assert result.meta is None
        assert result.block_present is True
        assert any("bogus_flag" in e for e in result.errors)

    def test_bare_command_trailing_whitespace_trimmed(self):
        cmd = (
            "git commit -m 'fix'   # ---CMD-META-BEGIN---\n"
            "# tools: git commit\n"
            "# ---CMD-META-END---"
        )
        result = resolve_cmdmeta_for_command(cmd)
        assert result.bare_command == "git commit -m 'fix'"
