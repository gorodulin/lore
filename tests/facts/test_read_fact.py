import json

import pytest

from lore.facts.read_fact import read_fact


def test_read_existing_fact(tmp_path):
    facts = {"f1": {"fact": "Use types", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    result = read_fact(str(tmp_path), "f1")

    assert result["fact_id"] == "f1"
    assert result["fact"] == "Use types"
    assert result["incl"] == ["p:**/*.py"]
    assert "file_path" in result


def test_read_subdir_fact_globalized(tmp_path):
    sub = tmp_path / "src"
    sub.mkdir()
    facts = {"f1": {"fact": "Local", "incl": ["p:**/*.ts"]}}
    (sub / ".lore.json").write_text(json.dumps(facts))

    result = read_fact(str(tmp_path), "f1")

    assert result["incl"] == ["p:src/**/*.ts"]


def test_read_missing_fact_raises(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))

    with pytest.raises(ValueError, match="not found"):
        read_fact(str(tmp_path), "missing")
