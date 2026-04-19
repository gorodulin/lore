from lore.validation.is_action_block_ineffective import is_action_block_ineffective


class TestIsActionBlockIneffective:
    def test_action_block_with_hook_read_only(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["hook:read", "action:block"]}
        assert is_action_block_ineffective(fact) is True

    def test_action_block_with_hook_edit(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["hook:edit", "action:block"]}
        assert is_action_block_ineffective(fact) is False

    def test_action_block_with_hook_write(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["hook:write", "action:block"]}
        assert is_action_block_ineffective(fact) is False

    def test_action_block_with_hook_read_and_edit(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["hook:read", "hook:edit", "action:block"]}
        assert is_action_block_ineffective(fact) is False

    def test_action_block_with_no_hook_tags(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["action:block"]}
        assert is_action_block_ineffective(fact) is False

    def test_no_action_block(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": ["hook:read"]}
        assert is_action_block_ineffective(fact) is False

    def test_no_tags_at_all(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"]}
        assert is_action_block_ineffective(fact) is False

    def test_empty_tags(self):
        fact = {"fact": "X", "incl": ["p:**/*.py"], "tags": []}
        assert is_action_block_ineffective(fact) is False
