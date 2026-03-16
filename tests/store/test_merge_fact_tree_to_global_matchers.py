import pytest

from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from tests.test_helpers.build_test_fact import build_test_fact


def test_merge_root_rules():
    _, fact = build_test_fact(incl=["g:**/api.js", "g:*.html"])
    rule_files = [{"rel_dir": "", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:**/api.js", "g:*.html"]


def test_merge_prefixes_patterns():
    _, fact = build_test_fact(incl=["g:**/api.js", "g:*.html"])
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:app/**/api.js", "g:app/*.html"]


def test_merge_prefixes_skip_patterns():
    _, fact = build_test_fact(incl=["g:**/*.js"], skip=["g:vendor/**"])
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:app/**/*.js"]
    assert merged["1"]["skip"] == ["g:app/vendor/**"]


def test_merge_multiple_files():
    _, fact1 = build_test_fact(incl=["g:*.ts"])
    _, fact2 = build_test_fact(incl=["g:**/api.js"])
    _, fact3 = build_test_fact(incl=["g:src/*.js"])

    rule_files = [
        {"rel_dir": "", "facts": {"1": fact1}},
        {"rel_dir": "app", "facts": {"2": fact2}},
        {"rel_dir": "lib", "facts": {"3": fact3}},
    ]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:*.ts"]
    assert merged["2"]["incl"] == ["g:app/**/api.js"]
    assert merged["3"]["incl"] == ["g:lib/src/*.js"]


def test_merge_duplicate_ids_raises():
    _, fact1 = build_test_fact(incl=["g:*.ts"])
    _, fact2 = build_test_fact(incl=["g:*.js"])

    rule_files = [
        {"rel_dir": "", "facts": {"1": fact1}},
        {"rel_dir": "app", "facts": {"1": fact2}},  # Duplicate ID
    ]

    with pytest.raises(ValueError, match="Duplicate fact ID"):
        merge_fact_tree_to_global_matchers(rule_files)


def test_merge_deeply_nested():
    _, fact = build_test_fact(incl=["g:*.tsx"])
    rule_files = [{"rel_dir": "app/frontend/src", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:app/frontend/src/*.tsx"]


def test_merge_preserves_fact_text():
    _, fact = build_test_fact(fact_text="Important rule", incl=["g:*.js"])
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["fact"] == "Important rule"


def test_merge_non_glob_matchers_not_prefixed():
    # Regex matchers should not be prefixed
    fact = {"fact": "Test", "incl": ["r:.*\\.js$"]}
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["r:.*\\.js$"]  # unchanged


def test_merge_mixed_matchers():
    fact = {"fact": "Test", "incl": ["g:**/*.js", "r:.*\\.ts$"]}
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["incl"] == ["g:app/**/*.js", "r:.*\\.ts$"]


def test_merge_preserves_tags():
    _, fact = build_test_fact(incl=["g:**/*.py"])
    fact["tags"] = ["hook:read", "kind:convention"]
    rule_files = [{"rel_dir": "", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["tags"] == ["hook:read", "kind:convention"]


def test_merge_preserves_tags_with_prefix():
    _, fact = build_test_fact(incl=["g:**/*.py"])
    fact["tags"] = ["hook:edit"]
    rule_files = [{"rel_dir": "app", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert merged["1"]["tags"] == ["hook:edit"]
    assert merged["1"]["incl"] == ["g:app/**/*.py"]


def test_merge_no_tags_key_when_absent():
    _, fact = build_test_fact(incl=["g:**/*.py"])
    rule_files = [{"rel_dir": "", "facts": {"1": fact}}]

    merged = merge_fact_tree_to_global_matchers(rule_files)
    assert "tags" not in merged["1"]
