import os

from lore.store.load_facts_file import load_facts_file
from lore.store.format_facts_as_json import format_facts_as_json
from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.build_dict_from_fact import build_dict_from_fact


class TestLoadSaveRoundtrip:
    """Byte-equality round-trip: load → build typed → build dict → format JSON.

    Safety net for the 'compiled-only, no raw preservation' decision.
    Uses real .lore.json files as fixtures.
    """

    def test_roundtrip_root_lore_json(self):
        _assert_roundtrip_for_file(_find_lore_json("lore/.lore.json"))

    def test_roundtrip_validation_lore_json(self):
        _assert_roundtrip_for_file(_find_lore_json("lore/validation/.lore.json"))

    def test_roundtrip_hook_handler_lore_json(self):
        _assert_roundtrip_for_file(_find_lore_json("lore/server/.lore.json"))

    def test_roundtrip_synthetic_mixed(self):
        """Round-trip a synthetic fact set with all field types."""
        original = {
            "f1": {
                "fact": "Glob only",
                "incl": ["p:**/*.py"],
            },
            "f2": {
                "fact": "Regex only",
                "incl": ["c:import os"],
            },
            "f3": {
                "fact": "Mixed with skip and tags",
                "incl": ["p:src/**", "c:TODO"],
                "skip": ["p:src/vendor/**"],
                "tags": ["hook:read", "action:block"],
            },
        }
        _assert_roundtrip_for_fact_set(original)


def _find_lore_json(relative_path: str) -> str:
    """Resolve a .lore.json path relative to the lore package root."""
    tests_dir = os.path.dirname(os.path.dirname(__file__))
    lore_root = os.path.dirname(tests_dir)
    path = os.path.join(lore_root, relative_path)
    assert os.path.exists(path), f"Fixture not found: {path}"
    return path


def _assert_roundtrip_for_file(file_path: str) -> None:
    """Assert that load → typed → dict → format produces identical bytes."""
    with open(file_path, "r", encoding="utf-8") as f:
        original_bytes = f.read()

    raw_facts = load_facts_file(file_path)
    roundtripped = _roundtrip_fact_set(raw_facts)
    result_bytes = format_facts_as_json(roundtripped)

    assert result_bytes == original_bytes, (
        f"Round-trip mismatch for {file_path}"
    )


def _assert_roundtrip_for_fact_set(fact_set: dict) -> None:
    """Assert round-trip via canonical formatting."""
    original_bytes = format_facts_as_json(fact_set)

    roundtripped = _roundtrip_fact_set(fact_set)
    result_bytes = format_facts_as_json(roundtripped)

    assert result_bytes == original_bytes


def _roundtrip_fact_set(raw_facts: dict) -> dict:
    """Convert raw → typed → raw."""
    result = {}
    for fact_id, raw in raw_facts.items():
        typed = build_fact_from_dict(fact_id, raw)
        result[fact_id] = build_dict_from_fact(typed)
    return result
