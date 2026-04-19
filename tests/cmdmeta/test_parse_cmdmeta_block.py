import pytest

from lore.cmdmeta.parse_cmdmeta_block import parse_cmdmeta_block, CmdMetaParseError


def _block(*lines: str) -> str:
    return "\n".join(lines) + "\n# ---CMD-META-END---"


class TestParseCmdMetaBlock:
    def test_minimal_valid_block(self):
        meta = parse_cmdmeta_block(_block("# tools: git push"))
        assert meta.tools == ("git push",)
        assert meta.endpoints == ()
        assert meta.flags == ()
        assert meta.affected_paths == ()

    def test_all_fields(self):
        meta = parse_cmdmeta_block(_block(
            "# tools: git push",
            "# endpoints: github.com:org/repo",
            "# flags: mutates, network",
            "# affected_paths: src/a.py, src/b.py",
        ))
        assert meta.tools == ("git push",)
        assert meta.endpoints == ("github.com:org/repo",)
        assert meta.flags == ("mutates", "network")
        assert meta.affected_paths == ("src/a.py", "src/b.py")

    def test_empty_tools_allowed(self):
        meta = parse_cmdmeta_block(_block("# tools:"))
        assert meta.tools == ()

    def test_blank_lines_ignored(self):
        meta = parse_cmdmeta_block(_block("# tools: ls", "", "# flags: slow"))
        assert meta.tools == ("ls",)
        assert meta.flags == ("slow",)

    def test_trimmed_whitespace_around_values(self):
        meta = parse_cmdmeta_block(_block("# tools:  git push ,  kubectl apply "))
        assert meta.tools == ("git push", "kubectl apply")

    def test_missing_end_sentinel(self):
        with pytest.raises(CmdMetaParseError, match="END sentinel"):
            parse_cmdmeta_block("# tools: ls")

    def test_missing_required_tools_key(self):
        with pytest.raises(CmdMetaParseError, match="'tools' is missing"):
            parse_cmdmeta_block(_block("# flags: mutates"))

    def test_unknown_key(self):
        with pytest.raises(CmdMetaParseError, match="unknown CMD-META key"):
            parse_cmdmeta_block(_block("# tools: ls", "# bogus: x"))

    def test_duplicate_key(self):
        with pytest.raises(CmdMetaParseError, match="duplicate CMD-META key"):
            parse_cmdmeta_block(_block("# tools: a", "# tools: b"))

    def test_line_missing_hash(self):
        with pytest.raises(CmdMetaParseError, match="does not start with '#'"):
            parse_cmdmeta_block(_block("# tools: ls", "flags: mutates"))

    def test_line_missing_colon(self):
        with pytest.raises(CmdMetaParseError, match="missing ':'"):
            parse_cmdmeta_block(_block("# tools: ls", "# flags mutates"))

    def test_trailing_whitespace_after_end_allowed(self):
        parse_cmdmeta_block("# tools: ls\n# ---CMD-META-END---   \n\n")

    def test_non_whitespace_after_end_rejected(self):
        body = "# tools: ls\n# ---CMD-META-END---\nextra garbage"
        with pytest.raises(CmdMetaParseError, match="content after END sentinel"):
            parse_cmdmeta_block(body)

    def test_shell_command_after_end_rejected(self):
        body = "# tools: ls\n# ---CMD-META-END---\nrm -rf /"
        with pytest.raises(CmdMetaParseError, match="content after END sentinel"):
            parse_cmdmeta_block(body)

    def test_second_begin_inside_block(self):
        body = (
            "# tools: ls\n"
            "# ---CMD-META-BEGIN---\n"
            "# tools: other\n"
            "# ---CMD-META-END---"
        )
        with pytest.raises(CmdMetaParseError, match="second BEGIN sentinel"):
            parse_cmdmeta_block(body)
