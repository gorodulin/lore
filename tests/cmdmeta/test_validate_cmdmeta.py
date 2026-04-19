from lore.cmdmeta.cmdmeta import CmdMeta
from lore.cmdmeta.validate_cmdmeta import validate_cmdmeta


class TestValidateCmdMeta:
    def test_empty_meta_is_valid(self):
        assert validate_cmdmeta(CmdMeta()) == []

    def test_valid_flags(self):
        meta = CmdMeta(tools=("git push",), flags=("mutates", "network"))
        assert validate_cmdmeta(meta) == []

    def test_unknown_flag_reported(self):
        meta = CmdMeta(tools=("ls",), flags=("bogus_flag",))
        errors = validate_cmdmeta(meta)
        assert len(errors) == 1
        assert "bogus_flag" in errors[0]
        assert "unknown flag" in errors[0]

    def test_multiple_unknown_flags(self):
        meta = CmdMeta(tools=("ls",), flags=("bogus1", "bogus2", "mutates"))
        errors = validate_cmdmeta(meta)
        assert len(errors) == 2

    def test_empty_string_in_tools_reported(self):
        meta = CmdMeta(tools=("git push", ""))
        errors = validate_cmdmeta(meta)
        assert any("'tools'" in e and "empty string" in e for e in errors)

    def test_empty_string_in_flags_reported(self):
        meta = CmdMeta(tools=("ls",), flags=("mutates", ""))
        errors = validate_cmdmeta(meta)
        assert any("'flags'" in e and "empty string" in e for e in errors)

    def test_empty_string_in_endpoints_reported(self):
        meta = CmdMeta(tools=("ls",), endpoints=("",))
        errors = validate_cmdmeta(meta)
        assert any("'endpoints'" in e for e in errors)

    def test_empty_string_in_affected_paths_reported(self):
        meta = CmdMeta(tools=("ls",), affected_paths=("src/a.py", ""))
        errors = validate_cmdmeta(meta)
        assert any("'affected_paths'" in e for e in errors)
