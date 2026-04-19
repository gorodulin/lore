import json
import os
import time


from lore.factstore.fact_store import FactStore


def test_load_all_facts_populates_store(tmp_path):
    facts = {
        "f1": {"fact": "Python files", "incl": ["p:**/*.py"]},
        "f2": {"fact": "JS files", "incl": ["p:**/*.js"]},
    }
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.find_matching_facts("src/app.py")
    assert "f1" in result
    assert "f2" not in result


def test_find_matching_facts_filters_by_tags(tmp_path):
    facts = {
        "read-only": {
            "fact": "Read hook fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:read"],
        },
        "write-only": {
            "fact": "Write hook fact",
            "incl": ["p:**/*.py"],
            "tags": ["hook:write"],
        },
        "untagged": {
            "fact": "No hook tags",
            "incl": ["p:**/*.py"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.find_matching_facts("lib/util.py", tags=["hook:read"])
    assert "read-only" in result
    assert "untagged" in result
    assert "write-only" not in result


def test_find_matching_facts_with_content(tmp_path):
    facts = {
        "raise-fact": {
            "fact": "Files with raise",
            "incl": ["p:**/*.py", "c:raise\\s+"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.find_matching_facts("src/app.py", content="raise ValueError")
    assert "raise-fact" in result

    result = store.find_matching_facts("src/app.py", content="return 42")
    assert result == {}


def test_find_matching_facts_with_tools(tmp_path):
    facts = {
        "git-push": {
            "fact": "Git push is risky",
            "incl": ["t:git push"],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.find_matching_facts("", tools=("git push",))
    assert "git-push" in result

    result = store.find_matching_facts("", tools=("ls",))
    assert result == {}

    # File event with no tools source → t: fact must not fire.
    result = store.find_matching_facts("src/app.py")
    assert "git-push" not in result


def test_find_matching_facts_with_endpoints(tmp_path):
    facts = {
        "prod": {
            "fact": "Talking to prod",
            "incl": ["e:\\.prod\\."],
        },
    }
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.find_matching_facts("", endpoints=("api.prod.com",))
    assert "prod" in result

    result = store.find_matching_facts("", endpoints=("api.staging.com",))
    assert result == {}

    result = store.find_matching_facts("src/app.py")
    assert "prod" not in result


def test_refresh_facts_detects_mtime_change(tmp_path):
    facts = {"f1": {"fact": "Original", "incl": ["p:**/*.py"]}}
    facts_file = tmp_path / ".lore.json"
    facts_file.write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    assert store.find_matching_facts("x.py")["f1"]["fact"] == "Original"

    time.sleep(0.05)
    updated = {"f1": {"fact": "Updated", "incl": ["p:**/*.py"]}}
    facts_file.write_text(json.dumps(updated))

    result = store.find_matching_facts("x.py")
    assert result["f1"]["fact"] == "Updated"


def test_refresh_facts_detects_new_file(tmp_path):
    facts = {"f1": {"fact": "Root fact", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    sub = tmp_path / "sub"
    sub.mkdir()
    sub_facts = {"f2": {"fact": "Sub fact", "incl": ["p:**/*.py"]}}
    (sub / ".lore.json").write_text(json.dumps(sub_facts))

    result = store.find_matching_facts("sub/thing.py")
    assert "f1" in result
    assert "f2" in result


def test_refresh_facts_detects_removed_file(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / ".lore.json").write_text(json.dumps({
        "f1": {"fact": "Sub fact", "incl": ["p:**/*.py"]},
    }))

    store = FactStore(str(tmp_path))
    store.load_all_facts()
    assert "f1" in store.find_matching_facts("sub/thing.py")

    os.remove(str(sub / ".lore.json"))

    result = store.find_matching_facts("sub/thing.py")
    assert "f1" not in result


def test_create_fact_updates_store(tmp_path):
    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.create_fact("New fact", ["p:**/*.ts"])
    fid = result["fact_id"]

    assert store.get_fact(fid) is not None
    assert fid in store.find_matching_facts("src/app.ts")


def test_edit_fact_handles_relocation(tmp_path):
    facts = {"f1": {"fact": "Root fact", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    store.edit_fact("f1", incl=["p:lib/**/*.py"])

    assert "f1" not in store.find_matching_facts("src/app.py")
    assert "f1" in store.find_matching_facts("lib/util.py")


def test_delete_fact_updates_store(tmp_path):
    facts = {"f1": {"fact": "Doomed", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    store.delete_fact("f1")

    assert store.get_fact("f1") is None
    assert "f1" not in store.find_matching_facts("x.py")
    assert not (tmp_path / ".lore.json").exists()


def test_validate_all_facts(tmp_path):
    facts = {"f1": {"fact": "Valid", "incl": ["p:**/*.py"]}}
    (tmp_path / ".lore.json").write_text(json.dumps(facts))

    store = FactStore(str(tmp_path))
    store.load_all_facts()

    result = store.validate_all_facts()
    assert result["valid"] is True
    assert result["errors"] == []
