import json

from lore.store.format_facts_as_json import format_facts_as_json


def test_format_empty():
    assert format_facts_as_json({}) == "{}\n"


def test_format_single_fact():
    ruleset = {
        "f1": {
            "fact": "Test fact",
            "incl": ["g:**/*.py"],
        }
    }
    result = format_facts_as_json(ruleset)
    # Should be valid JSON
    assert json.loads(result) == ruleset
    # Arrays should be on one line
    assert '["g:**/*.py"]' in result
    # Should end with newline
    assert result.endswith("\n")


def test_format_key_order():
    ruleset = {
        "f1": {
            "incl": ["g:**/*.py"],
            "fact": "Test fact",
            "skip": ["g:vendor/**"],
        }
    }
    result = format_facts_as_json(ruleset)
    # Inner keys sorted: fact < incl < skip
    fact_pos = result.index('"fact"')
    incl_pos = result.index('"incl"')
    skip_pos = result.index('"skip"')
    assert fact_pos < incl_pos < skip_pos


def test_format_fact_id_order():
    ruleset = {
        "z_fact": {"fact": "Z", "incl": ["g:**/*.py"]},
        "a_fact": {"fact": "A", "incl": ["g:**/*.js"]},
    }
    result = format_facts_as_json(ruleset)
    assert result.index('"a_fact"') < result.index('"z_fact"')


def test_format_roundtrip():
    ruleset = {
        "f1": {
            "fact": "A fact with \"quotes\" and \\ backslashes",
            "incl": ["g:**/*.py", "g:src/**/*.js"],
            "skip": ["g:vendor/**"],
        }
    }
    result = format_facts_as_json(ruleset)
    assert json.loads(result) == ruleset


def test_format_unicode():
    ruleset = {
        "f1": {
            "fact": "日本語テスト",
            "incl": ["g:**/*.py"],
        }
    }
    result = format_facts_as_json(ruleset)
    # Unicode preserved (ensure_ascii=False)
    assert "日本語テスト" in result
    assert json.loads(result) == ruleset


def test_format_compact_arrays():
    ruleset = {
        "f1": {
            "fact": "Test",
            "incl": ["g:src/**/*.py", "g:lib/**/*.py", "g:bin/**/*.py"],
        }
    }
    result = format_facts_as_json(ruleset)
    # All array items on one line
    assert '["g:bin/**/*.py", "g:lib/**/*.py", "g:src/**/*.py"]' in result
    # No multi-line array expansion
    lines = result.strip().split("\n")
    for line in lines:
        # No line should be just a quoted string (expanded array element)
        stripped = line.strip().rstrip(",")
        if stripped.startswith('"g:'):
            raise AssertionError(f"Array element on its own line: {line}")


def test_format_indentation():
    ruleset = {
        "f1": {"fact": "Test", "incl": ["g:**/*.py"]},
    }
    result = format_facts_as_json(ruleset)
    lines = result.strip().split("\n")
    # Line 0: {
    assert lines[0] == "{"
    # Line 1: 2-space indent for fact ID
    assert lines[1].startswith("  ")
    assert not lines[1].startswith("    ")
    # Line 2: 4-space indent for fact key
    assert lines[2].startswith("    ")
    # Last line: }
    assert lines[-1] == "}"
