from lore.validation.validate_fact_set import validate_fact_set
from lore import error_codes
from tests.test_helpers.build_test_fact import build_test_fact
from tests.test_helpers.build_test_fact_set import build_test_fact_set


def test_validate_all_valid():
    ruleset = build_test_fact_set(
        build_test_fact(fact_id="1", incl=["p:**/api.js"]),
        build_test_fact(fact_id="2", incl=["p:src/*.ts"]),
        build_test_fact(fact_id="3", incl=["p:lib/utils/file.ts"]),
    )

    valid, errors = validate_fact_set(ruleset)
    assert valid is True
    assert errors == []


def test_validate_missing_incl():
    ruleset = {
        "1": {"fact": "Test"},  # Missing incl
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == error_codes.MISSING_INCL_FIELD


def test_validate_empty_incl():
    ruleset = {
        "1": {"fact": "Test", "incl": []},  # Empty incl
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert len(errors) == 1
    assert errors[0]["code"] == error_codes.EMPTY_INCL_LIST


def test_validate_invalid_glob():
    ruleset = {
        "1": {"fact": "Test", "incl": ["p:**/**/*.js"]},  # Multiple globstars
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert any(e["code"] == error_codes.INVALID_MULTIPLE_GLOBSTARS for e in errors)


def test_validate_invalid_matcher_prefix():
    ruleset = {
        "1": {"fact": "Test", "incl": ["**/*.js"]},  # Missing g: prefix
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert any(e["code"] == error_codes.INVALID_MATCHER_PREFIX for e in errors)


def test_validate_multiple_invalid():
    ruleset = {
        "1": {"fact": "Test", "incl": []},  # Empty incl
        "2": {"fact": "Test", "incl": ["p:**/**/*.js"]},  # Invalid glob
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert len(errors) >= 2


def test_validate_with_skip():
    ruleset = build_test_fact_set(
        build_test_fact(fact_id="1", incl=["p:**/*.js"], skip=["p:vendor/**"]),
    )

    valid, errors = validate_fact_set(ruleset)
    assert valid is True
    assert errors == []


def test_validate_invalid_skip():
    ruleset = {
        "1": {"fact": "Test", "incl": ["p:**/*.js"], "skip": ["invalid"]},
    }

    valid, errors = validate_fact_set(ruleset)
    assert valid is False
    assert any(e["code"] == error_codes.INVALID_MATCHER_PREFIX for e in errors)
