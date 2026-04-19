import pytest

from lore.cmdmeta.cmdmeta import CmdMeta


class TestCmdMeta:
    def test_default_fields_are_empty_tuples(self):
        meta = CmdMeta()
        assert meta.tools == ()
        assert meta.endpoints == ()
        assert meta.flags == ()
        assert meta.affected_paths == ()

    def test_all_fields_typed_tuples(self):
        meta = CmdMeta(
            tools=("git push",),
            endpoints=("github.com:org/repo",),
            flags=("mutates", "network"),
            affected_paths=("src/a.py",),
        )
        assert meta.tools == ("git push",)
        assert meta.endpoints == ("github.com:org/repo",)
        assert meta.flags == ("mutates", "network")
        assert meta.affected_paths == ("src/a.py",)

    def test_frozen(self):
        meta = CmdMeta()
        with pytest.raises(Exception):
            meta.tools = ("x",)  # type: ignore[misc]

    def test_equality(self):
        assert CmdMeta(tools=("git push",)) == CmdMeta(tools=("git push",))
        assert CmdMeta(tools=("a",)) != CmdMeta(tools=("b",))
