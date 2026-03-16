import json

from lore.factstore.build_fact_store import build_fact_store


def test_build_fact_store_returns_loaded_store(tmp_path):
    facts = {"f1": {"fact": "Python files", "incl": ["g:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = build_fact_store(str(tmp_path))

    result = store.find_matching_facts("src/app.py")
    assert "f1" in result
    assert result["f1"]["fact"] == "Python files"
