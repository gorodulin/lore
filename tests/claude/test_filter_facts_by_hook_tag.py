from lore.claude.filter_facts_by_hook_tag import filter_facts_by_hook_tag


class TestFilterFactsByHookTag:
    def test_none_hook_tag_returns_all(self):
        facts = {
            "a": {"fact": "A", "tags": ["hook:read"]},
            "b": {"fact": "B", "tags": ["hook:edit"]},
        }
        result = filter_facts_by_hook_tag(facts, None)
        assert result == facts

    def test_no_hook_tags_passes_all_filters(self):
        facts = {"a": {"fact": "A", "tags": ["kind:convention"]}}
        result = filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in result

    def test_no_tags_key_passes_all_filters(self):
        facts = {"a": {"fact": "A"}}
        result = filter_facts_by_hook_tag(facts, "hook:edit")
        assert "a" in result

    def test_matching_hook_tag_passes(self):
        facts = {"a": {"fact": "A", "tags": ["hook:read"]}}
        result = filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in result

    def test_non_matching_hook_tag_filtered(self):
        facts = {"a": {"fact": "A", "tags": ["hook:read"]}}
        result = filter_facts_by_hook_tag(facts, "hook:edit")
        assert result == {}

    def test_multiple_hook_tags_or_logic(self):
        facts = {"a": {"fact": "A", "tags": ["hook:read", "hook:edit"]}}
        assert "a" in filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in filter_facts_by_hook_tag(facts, "hook:edit")
        assert filter_facts_by_hook_tag(facts, "hook:write") == {}

    def test_kind_tags_ignored_for_filtering(self):
        facts = {"a": {"fact": "A", "tags": ["hook:read", "kind:convention"]}}
        result = filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in result

    def test_mixed_facts_filtered(self):
        facts = {
            "a": {"fact": "A", "tags": ["hook:read"]},
            "b": {"fact": "B", "tags": ["hook:edit"]},
            "c": {"fact": "C"},
        }
        result = filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in result
        assert "b" not in result
        assert "c" in result  # no hook tags = passes all

    def test_empty_tags_list_passes_all(self):
        facts = {"a": {"fact": "A", "tags": []}}
        result = filter_facts_by_hook_tag(facts, "hook:read")
        assert "a" in result
