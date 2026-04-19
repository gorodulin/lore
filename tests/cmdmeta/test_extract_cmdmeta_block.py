from lore.cmdmeta.extract_cmdmeta_block import extract_cmdmeta_block


class TestExtractCmdMetaBlock:
    def test_no_sentinel_returns_command_and_none(self):
        assert extract_cmdmeta_block("ls -la") == ("ls -la", None)

    def test_empty_command(self):
        assert extract_cmdmeta_block("") == ("", None)

    def test_basic_block(self):
        command = (
            "ls -la  # ---CMD-META-BEGIN---\n"
            "# tools: ls\n"
            "# ---CMD-META-END---"
        )
        bare, block = extract_cmdmeta_block(command)
        assert bare == "ls -la"
        assert block is not None
        assert "# tools: ls" in block
        assert "# ---CMD-META-END---" in block

    def test_strips_trailing_whitespace_before_sentinel(self):
        command = "ls   \t # ---CMD-META-BEGIN---\n# tools: ls\n# ---CMD-META-END---"
        bare, _ = extract_cmdmeta_block(command)
        assert bare == "ls"

    def test_no_whitespace_before_sentinel(self):
        command = "ls# ---CMD-META-BEGIN---\n# tools: ls\n# ---CMD-META-END---"
        bare, _ = extract_cmdmeta_block(command)
        assert bare == "ls"

    def test_sentinel_at_start(self):
        command = "# ---CMD-META-BEGIN---\n# tools:\n# ---CMD-META-END---"
        bare, block = extract_cmdmeta_block(command)
        assert bare == ""
        assert block is not None

    def test_block_text_excludes_begin_sentinel(self):
        command = "ls # ---CMD-META-BEGIN---\n# tools: ls\n# ---CMD-META-END---"
        _, block = extract_cmdmeta_block(command)
        assert block is not None
        assert "---CMD-META-BEGIN---" not in block

    def test_begin_without_end_returns_tail_as_block(self):
        """The parser, not the extractor, is responsible for reporting missing END."""
        command = "ls # ---CMD-META-BEGIN---\n# tools: ls"
        bare, block = extract_cmdmeta_block(command)
        assert bare == "ls"
        assert block == "# tools: ls"

    def test_multiline_bare_command(self):
        command = (
            "git status\ngit diff   # ---CMD-META-BEGIN---\n"
            "# tools: git status, git diff\n"
            "# ---CMD-META-END---"
        )
        bare, _ = extract_cmdmeta_block(command)
        assert bare == "git status\ngit diff"
