import os
import pytest

from lore.facts.create_fact import create_fact
from lore.store.load_facts_file import load_facts_file


def test_create_basic(tmp_path):
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:**/*.py"],
        fact_id="test1",
    )

    assert result["fact_id"] == "test1"
    assert result["fact"] == "Test fact"
    assert os.path.exists(result["file_path"])


def test_create_auto_id(tmp_path):
    result = create_fact(str(tmp_path), "Test fact", ["g:**/*.py"])

    assert len(result["fact_id"]) == 10
    assert result["fact"] == "Test fact"


def test_create_auto_placement(tmp_path):
    """Patterns with common prefix should go to that directory's .lore.json."""
    result = create_fact(
        str(tmp_path),
        "Glob module fact",
        ["g:lore/globs/**/*.py"],
        fact_id="test1",
    )

    expected_file = os.path.join(str(tmp_path), "lore", "globs", ".lore.json")
    assert result["file_path"] == expected_file

    # Pattern should be global (project-root-relative)
    assert result["incl"] == ["g:lore/globs/**/*.py"]


def test_create_auto_placement_multiple_patterns(tmp_path):
    result = create_fact(
        str(tmp_path),
        "Lore module fact",
        ["g:lore/globs/**/*.py", "g:lore/rules/**/*.py"],
        fact_id="test1",
    )

    expected_file = os.path.join(str(tmp_path), "lore", ".lore.json")
    assert result["file_path"] == expected_file

    # Patterns should be global (project-root-relative)
    assert result["incl"] == ["g:lore/globs/**/*.py", "g:lore/rules/**/*.py"]


def test_create_with_skip(tmp_path):
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:src/**/*.py"],
        ["g:src/vendor/**"],
        fact_id="test1",
    )

    assert "skip" in result
    assert result["skip"] == ["g:src/vendor/**"]


def test_create_root_level_patterns(tmp_path):
    """Patterns with no common prefix should go to root .lore.json."""
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:**/*.py"],
        fact_id="test1",
    )

    expected_file = os.path.join(str(tmp_path), ".lore.json")
    assert result["file_path"] == expected_file
    assert result["incl"] == ["g:**/*.py"]


def test_create_appends_to_existing(tmp_path):
    # Create first fact
    create_fact(str(tmp_path), "First", ["g:**/*.py"], fact_id="f1")

    # Create second fact in same location
    create_fact(str(tmp_path), "Second", ["g:**/*.js"], fact_id="f2")

    rules_file = os.path.join(str(tmp_path), ".lore.json")
    loaded = load_facts_file(rules_file)
    assert "f1" in loaded
    assert "f2" in loaded


def test_create_duplicate_id_raises(tmp_path):
    create_fact(str(tmp_path), "First", ["g:**/*.py"], fact_id="dup1")

    with pytest.raises(ValueError, match="already exists"):
        create_fact(str(tmp_path), "Second", ["g:**/*.js"], fact_id="dup1")


def test_create_invalid_fact_raises(tmp_path):
    with pytest.raises(ValueError, match="Invalid fact"):
        create_fact(str(tmp_path), "Test", ["bad_matcher"], fact_id="test1")


def test_create_with_tags(tmp_path):
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:**/*.py"],
        fact_id="test1",
        tags=["hook:read", "kind:convention"],
    )

    assert result["tags"] == ["hook:read", "kind:convention"]


def test_create_without_tags(tmp_path):
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:**/*.py"],
        fact_id="test1",
    )

    assert "tags" not in result


def test_create_tags_persisted(tmp_path):
    create_fact(
        str(tmp_path),
        "Test fact",
        ["g:**/*.py"],
        fact_id="test1",
        tags=["hook:edit"],
    )

    loaded = load_facts_file(str(tmp_path / ".lore.json"))
    assert loaded["test1"]["tags"] == ["hook:edit"]


def test_create_non_relativizable_skip(tmp_path):
    """If skip pattern can't be relativized, it stays as-is."""
    result = create_fact(
        str(tmp_path),
        "Test fact",
        ["g:src/**/*.py"],
        ["g:**/*.min.py"],
        fact_id="test1",
    )

    # Both incl and skip are returned as global (project-root-relative)
    assert result["incl"] == ["g:src/**/*.py"]
    assert result["skip"] == ["g:src/**/*.min.py"]
