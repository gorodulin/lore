import json
import pytest

from lore.store.save_facts_file import save_facts_file
from lore.store.load_facts_file import load_facts_file
from tests.test_helpers.build_test_fact import build_test_fact
from tests.test_helpers.build_test_fact_set import build_test_fact_set


def test_save_basic(tmp_path):
    rules_file = tmp_path / ".lore.json"
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    ruleset = {"f1": fact}

    save_facts_file(str(rules_file), ruleset)

    loaded = load_facts_file(str(rules_file))
    assert "f1" in loaded
    assert loaded["f1"]["fact"] == "Test fact"


def test_save_deterministic_output(tmp_path):
    rules_file = tmp_path / ".lore.json"
    ruleset = build_test_fact_set(
        build_test_fact(fact_id="b_fact", incl=["p:**/*.py"]),
        build_test_fact(fact_id="a_fact", incl=["p:**/*.js"]),
    )

    save_facts_file(str(rules_file), ruleset)

    content = rules_file.read_text(encoding="utf-8")
    # Keys should be sorted
    assert content.index('"a_fact"') < content.index('"b_fact"')
    # Should end with newline
    assert content.endswith("\n")
    # Should be indented with 2 spaces
    assert '  "a_fact"' in content


def test_save_creates_parent_dirs(tmp_path):
    rules_file = tmp_path / "deep" / "nested" / ".lore.json"
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])

    save_facts_file(str(rules_file), {"f1": fact})

    assert rules_file.exists()
    loaded = load_facts_file(str(rules_file))
    assert "f1" in loaded


def test_save_overwrites_existing(tmp_path):
    rules_file = tmp_path / ".lore.json"
    _, fact1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    _, fact2 = build_test_fact(fact_id="f2", incl=["p:**/*.js"])

    save_facts_file(str(rules_file), {"f1": fact1})
    save_facts_file(str(rules_file), {"f2": fact2})

    loaded = load_facts_file(str(rules_file))
    assert "f1" not in loaded
    assert "f2" in loaded


def test_save_validates_facts(tmp_path):
    rules_file = tmp_path / ".lore.json"
    # Missing 'fact' field
    bad_ruleset = {"f1": {"incl": ["p:**/*.py"]}}

    with pytest.raises(ValueError, match="Invalid facts"):
        save_facts_file(str(rules_file), bad_ruleset)

    # File should not have been created
    assert not rules_file.exists()


def test_save_empty_ruleset(tmp_path):
    rules_file = tmp_path / ".lore.json"
    save_facts_file(str(rules_file), {})

    content = rules_file.read_text(encoding="utf-8")
    assert json.loads(content) == {}


def test_save_unicode_content(tmp_path):
    rules_file = tmp_path / ".lore.json"
    _, fact = build_test_fact(fact_id="f1", fact_text="日本語テスト", incl=["p:**/*.py"])

    save_facts_file(str(rules_file), {"f1": fact})

    content = rules_file.read_text(encoding="utf-8")
    # ensure_ascii=False means unicode chars are preserved
    assert "日本語テスト" in content
