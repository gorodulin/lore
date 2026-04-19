import pytest

from lore.cmdmeta.build_cmdmeta_instruction import build_cmdmeta_instruction
from lore.cmdmeta.flag_vocabulary import FLAG_GROUPS, FLAG_VOCABULARY


class TestBuildCmdMetaInstruction:
    def test_errors_header_present(self):
        text = build_cmdmeta_instruction(("CMD-META block missing",))
        assert "CMD-META gate denied" in text
        assert "CMD-META block missing" in text

    def test_multiple_errors_listed(self):
        text = build_cmdmeta_instruction(("first thing", "second thing"))
        assert "first thing" in text
        assert "second thing" in text

    def test_contains_sentinels_in_example(self):
        text = build_cmdmeta_instruction(("x",))
        assert "# ---CMD-META-BEGIN---" in text
        assert "# ---CMD-META-END---" in text

    def test_contains_every_group_label(self):
        text = build_cmdmeta_instruction(("x",))
        for label, _flags in FLAG_GROUPS:
            assert label in text

    def test_contains_every_flag_in_vocabulary(self):
        text = build_cmdmeta_instruction(("x",))
        for flag in FLAG_VOCABULARY:
            assert flag in text

    def test_mentions_required_tools_key(self):
        text = build_cmdmeta_instruction(("x",))
        assert "Required field: tools" in text

    def test_rejects_empty_errors(self):
        with pytest.raises(ValueError):
            build_cmdmeta_instruction(())
