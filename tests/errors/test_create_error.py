from lore.errors.create_error import create_error
from lore.error_codes import INVALID_EMPTY_PATTERN


def test_create_error_minimal():
    err = create_error("TEST_CODE", "Test message")
    assert err == {"code": "TEST_CODE", "message": "Test message"}


def test_create_error_with_pattern_id():
    err = create_error("TEST_CODE", "Test message", pattern_id="rule-1")
    assert err["pattern_id"] == "rule-1"


def test_create_error_with_pattern():
    err = create_error("TEST_CODE", "Test message", pattern="**/*.js")
    assert err["pattern"] == "**/*.js"


def test_create_error_with_at():
    err = create_error("TEST_CODE", "Test message", at=5)
    assert err["at"] == 5


def test_create_error_full():
    err = create_error(
        INVALID_EMPTY_PATTERN,
        "Pattern cannot be empty",
        pattern_id="rule-1",
        pattern="",
        at=0,
    )
    assert err == {
        "code": INVALID_EMPTY_PATTERN,
        "message": "Pattern cannot be empty",
        "pattern_id": "rule-1",
        "pattern": "",
        "at": 0,
    }
