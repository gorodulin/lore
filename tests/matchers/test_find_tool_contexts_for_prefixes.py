import pytest
from itertools import combinations

from lore.matchers.find_tool_contexts_for_prefixes import find_tool_contexts_for_prefixes, PREFIX_TO_TOOL_CONTEXTS, ALL_PREFIXES


def test_empty_prefixes_returns_empty():
    assert find_tool_contexts_for_prefixes(set()) == frozenset()


def test_unknown_prefix_raises():
    with pytest.raises(ValueError, match="Unknown prefixes"):
        find_tool_contexts_for_prefixes({"z"})


def test_single_prefix_returns_its_full_context_set():
    for prefix, expected in PREFIX_TO_TOOL_CONTEXTS.items():
        assert find_tool_contexts_for_prefixes({prefix}) == expected


def test_file_world_path_and_content():
    result = find_tool_contexts_for_prefixes({"p", "c"})
    assert result == frozenset({"Read", "Edit", "Write"})


def test_content_incompatible_with_all_command_prefixes():
    for cmd_prefix in ("d", "t", "e", "f", "x"):
        result = find_tool_contexts_for_prefixes({"c", cmd_prefix})
        assert result == frozenset(), f"c + {cmd_prefix} should be empty"


def test_description_and_endpoint_spans_bash_and_webfetch():
    result = find_tool_contexts_for_prefixes({"d", "e"})
    assert result == frozenset({"Bash", "WebFetch"})


def test_adding_tool_to_description_endpoint_narrows_to_bash():
    result = find_tool_contexts_for_prefixes({"d", "e", "t"})
    assert result == frozenset({"Bash"})


def test_all_command_prefixes_together():
    result = find_tool_contexts_for_prefixes({"p", "d", "t", "e", "f", "x"})
    assert result == frozenset({"Bash"})


def test_all_prefixes_together():
    result = find_tool_contexts_for_prefixes(set(ALL_PREFIXES))
    assert result == frozenset(), "c makes the full set empty"


def test_exhaustive_all_combinations():
    """Test every possible subset of prefixes (2^7 = 128 combinations).

    For each subset, independently computes the expected intersection
    from PREFIX_TO_TOOL_CONTEXTS and verifies the function agrees.
    """
    all_prefixes = sorted(ALL_PREFIXES)
    for size in range(1, len(all_prefixes) + 1):
        for combo in combinations(all_prefixes, size):
            prefix_set = set(combo)
            expected = frozenset.intersection(*(PREFIX_TO_TOOL_CONTEXTS[p] for p in prefix_set))
            result = find_tool_contexts_for_prefixes(prefix_set)
            assert result == expected, f"Mismatch for {prefix_set}: got {result}, expected {expected}"
