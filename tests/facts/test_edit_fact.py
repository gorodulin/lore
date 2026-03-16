import json
import os

import pytest

from lore.facts.edit_fact import edit_fact
from lore.store.load_facts_file import load_facts_file
from tests.test_helpers.build_test_fact import build_test_fact


def _setup_fact(tmp_path, fact_id="f1", **kwargs):
    """Helper to write a fact to .lore.json in tmp_path."""
    _, fact = build_test_fact(fact_id=fact_id, **kwargs)
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({fact_id: fact}))
    return fact


def test_edit_fact_text(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    result = edit_fact(str(tmp_path), "f1", fact_text="Updated text")

    assert result["fact"] == "Updated text"
    assert result["incl"] == ["g:**/*.py"]


def test_edit_incl(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    result = edit_fact(str(tmp_path), "f1", incl=["g:**/*.js"])

    assert result["incl"] == ["g:**/*.js"]
    assert result["fact"] == "Test fact"


def test_edit_skip(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    result = edit_fact(str(tmp_path), "f1", skip=["g:vendor/**"])

    assert result["skip"] == ["g:vendor/**"]


def test_edit_remove_skip(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"], skip=["g:vendor/**"])

    result = edit_fact(str(tmp_path), "f1", skip=[])

    assert "skip" not in result


def test_edit_preserves_unmodified(tmp_path):
    _setup_fact(tmp_path, fact_text="Original", incl=["g:**/*.py"], skip=["g:vendor/**"])

    result = edit_fact(str(tmp_path), "f1", fact_text="New text")

    assert result["fact"] == "New text"
    assert result["incl"] == ["g:**/*.py"]
    assert result["skip"] == ["g:vendor/**"]


def test_edit_not_found(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    with pytest.raises(ValueError, match="not found"):
        edit_fact(str(tmp_path), "nonexistent", fact_text="New text")


def test_edit_invalid_update(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    with pytest.raises(ValueError, match="Invalid fact"):
        edit_fact(str(tmp_path), "f1", incl=[])


def test_edit_persists_to_file(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    edit_fact(str(tmp_path), "f1", fact_text="Persisted")

    loaded = load_facts_file(str(tmp_path / ".lore.json"))
    assert loaded["f1"]["fact"] == "Persisted"


def test_edit_add_tags(tmp_path):
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    result = edit_fact(str(tmp_path), "f1", tags=["hook:read"])

    assert result["tags"] == ["hook:read"]


def test_edit_remove_tags(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"], tags=["hook:read"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": fact}))

    result = edit_fact(str(tmp_path), "f1", tags=[])

    assert "tags" not in result


def test_edit_preserves_tags_when_none(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"], tags=["hook:edit"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": fact}))

    result = edit_fact(str(tmp_path), "f1", fact_text="Updated")

    assert result["tags"] == ["hook:edit"]
    assert result["fact"] == "Updated"


def test_edit_preserves_other_facts(tmp_path):
    _, fact1 = build_test_fact(fact_id="f1", incl=["g:**/*.py"])
    _, fact2 = build_test_fact(fact_id="f2", incl=["g:**/*.js"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact1, "f2": fact2}))

    edit_fact(str(tmp_path), "f1", fact_text="Updated f1")

    loaded = load_facts_file(str(rules_file))
    assert loaded["f1"]["fact"] == "Updated f1"
    assert loaded["f2"]["fact"] == "Test fact"


def test_edit_relocates_to_new_folder(tmp_path):
    """Test that editing patterns relocates the fact to a new folder."""
    # Create two facts in root (so root .lore.json doesn't get deleted)
    _, fact1 = build_test_fact(fact_id="api_fact", incl=["g:src/api/**/*.ts"])
    _, fact2 = build_test_fact(fact_id="other_fact", incl=["g:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"api_fact": fact1, "other_fact": fact2}))

    # Edit to move to src/api/ with more specific patterns
    result = edit_fact(
        str(tmp_path),
        "api_fact",
        fact_text="API handlers",
        incl=["g:src/api/handlers/**/*.ts", "g:src/api/routes/**/*.ts"],
    )

    # Fact should now be in src/api/.lore.json
    assert "src/api/.lore.json" in result["file_path"]

    # Root .lore.json should no longer have api_fact (but still have other_fact)
    root_rules = load_facts_file(str(tmp_path / ".lore.json"))
    assert "api_fact" not in root_rules
    assert "other_fact" in root_rules

    # src/api/.lore.json should have it with relativized patterns
    api_rules = load_facts_file(str(tmp_path / "src" / "api" / ".lore.json"))
    assert "api_fact" in api_rules
    assert api_rules["api_fact"]["fact"] == "API handlers"
    assert api_rules["api_fact"]["incl"] == ["g:handlers/**/*.ts", "g:routes/**/*.ts"]


def test_edit_stays_in_same_folder_when_patterns_unchanged(tmp_path):
    """Test that editing non-pattern fields keeps fact in same folder."""
    # Create fact in src/.lore.json
    (tmp_path / "src").mkdir()
    _, fact = build_test_fact(fact_id="src_fact", incl=["g:**/*.py"])
    (tmp_path / "src" / ".lore.json").write_text(json.dumps({"src_fact": fact}))

    # Edit only the fact text (patterns unchanged)
    result = edit_fact(
        str(tmp_path),
        "src_fact",
        fact_text="Updated source code fact",
    )

    # Should remain in src/.lore.json
    assert "src/.lore.json" in result["file_path"]
    assert result["fact"] == "Updated source code fact"
    # Patterns should be global (project-root-relative)
    assert result["incl"] == ["g:src/**/*.py"]


def test_edit_relocates_to_root_when_patterns_widen(tmp_path):
    """Test that widening patterns relocates to root if no common parent exists."""
    # Create two facts in src/api/ (so that folder doesn't get deleted)
    (tmp_path / "src" / "api").mkdir(parents=True)
    _, fact1 = build_test_fact(fact_id="api_fact", incl=["g:handlers/**/*.ts"])
    _, fact2 = build_test_fact(fact_id="other_api_fact", incl=["g:middleware/**/*.ts"])
    (tmp_path / "src" / "api" / ".lore.json").write_text(
        json.dumps({"api_fact": fact1, "other_api_fact": fact2})
    )

    # Edit to add patterns from different top-level folders
    result = edit_fact(
        str(tmp_path),
        "api_fact",
        incl=["g:src/**/*.ts", "g:lib/**/*.ts"],  # No common parent beyond root
    )

    # Should relocate to root
    assert result["file_path"].endswith(".lore.json")
    assert "/src/api/" not in result["file_path"]

    # src/api/.lore.json should no longer have api_fact (but still have other_api_fact)
    api_rules = load_facts_file(str(tmp_path / "src" / "api" / ".lore.json"))
    assert "api_fact" not in api_rules
    assert "other_api_fact" in api_rules

    # root .lore.json should have it
    root_rules = load_facts_file(str(tmp_path / ".lore.json"))
    assert "api_fact" in root_rules


def test_edit_with_new_skip_patterns_stays_in_place(tmp_path):
    """Test that adding skip patterns doesn't affect relocation (only incl matters)."""
    # Create fact in root
    _, fact = build_test_fact(fact_id="test_fact", incl=["g:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"test_fact": fact}))

    # Edit to add skip patterns (skip doesn't affect relocation, only incl does)
    result = edit_fact(
        str(tmp_path),
        "test_fact",
        skip=["g:vendor/**"],
    )

    # Should stay in root (skip patterns don't affect target folder calculation)
    assert result["file_path"].endswith(".lore.json")
    assert result["skip"] == ["g:vendor/**"]


def test_edit_invalid_update_preserves_original(tmp_path):
    """Structural validation rejects before any file mutation occurs."""
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    with pytest.raises(ValueError, match="Invalid fact"):
        edit_fact(str(tmp_path), "f1", incl=[])

    loaded = load_facts_file(str(tmp_path / ".lore.json"))
    assert "f1" in loaded
    assert loaded["f1"]["incl"] == ["g:**/*.py"]


@pytest.mark.skipif(os.getuid() == 0, reason="Cannot restrict permissions as root")
def test_edit_restores_original_on_create_failure(tmp_path):
    """Original fact is restored when create_fact fails after delete."""
    _setup_fact(tmp_path, incl=["g:**/*.py"])

    # Block writes to the relocation target
    blocked_dir = tmp_path / "blocked"
    blocked_dir.mkdir(mode=0o444)

    try:
        with pytest.raises(ValueError, match="Failed to create replacement"):
            edit_fact(str(tmp_path), "f1", incl=["g:blocked/sub/**/*.py"])

        # Original fact must be restored
        loaded = load_facts_file(str(tmp_path / ".lore.json"))
        assert "f1" in loaded
        assert loaded["f1"]["incl"] == ["g:**/*.py"]
    finally:
        blocked_dir.chmod(0o755)
