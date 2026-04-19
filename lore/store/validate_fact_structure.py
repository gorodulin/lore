import re

from lore.store.parse_matcher_string import parse_matcher_string
from lore.globs.validate_glob_pattern import validate_glob_pattern
from lore.errors.create_error import create_error
from lore import error_codes


def validate_fact_structure(fact_id: str, fact: dict) -> list[dict]:
    """Validate the structural correctness of a single fact.

    Checks:
    - fact dict has required 'fact' field (string)
    - fact dict has required 'incl' field (non-empty list)
    - all matchers in 'incl' and 'skip' have valid prefixes
    - all glob matchers have valid glob syntax

    Args:
        fact_id: ID of the fact being validated
        fact: Fact dict with 'fact', 'incl', and optional 'skip'

    Returns:
        List of error dicts. Empty list means valid.
    """
    errors = []

    # Check fact is a dict
    if not isinstance(fact, dict):
        errors.append(create_error(
            error_codes.INVALID_FACT_STRUCTURE,
            f"Fact '{fact_id}' must be a dict, got {type(fact).__name__}",
            fact_id=fact_id,
        ))
        return errors

    # Check 'fact' field
    if "fact" not in fact:
        errors.append(create_error(
            error_codes.MISSING_FACT_FIELD,
            f"Fact '{fact_id}' missing required 'fact' field",
            fact_id=fact_id,
        ))
    elif not isinstance(fact["fact"], str):
        errors.append(create_error(
            error_codes.INVALID_FACT_STRUCTURE,
            f"Fact '{fact_id}' field 'fact' must be a string",
            fact_id=fact_id,
        ))

    # Check 'incl' field
    if "incl" not in fact:
        errors.append(create_error(
            error_codes.MISSING_INCL_FIELD,
            f"Fact '{fact_id}' missing required 'incl' field",
            fact_id=fact_id,
        ))
    elif not isinstance(fact["incl"], list):
        errors.append(create_error(
            error_codes.INVALID_FACT_STRUCTURE,
            f"Fact '{fact_id}' field 'incl' must be a list",
            fact_id=fact_id,
        ))
    elif len(fact["incl"]) == 0:
        errors.append(create_error(
            error_codes.EMPTY_INCL_LIST,
            f"Fact '{fact_id}' field 'incl' must have at least one matcher",
            fact_id=fact_id,
        ))
    else:
        # Validate each incl matcher
        for i, matcher in enumerate(fact["incl"]):
            matcher_errors = _validate_matcher(fact_id, "incl", i, matcher)
            errors.extend(matcher_errors)

    # Check 'skip' field if present
    if "skip" in fact:
        if not isinstance(fact["skip"], list):
            errors.append(create_error(
                error_codes.INVALID_FACT_STRUCTURE,
                f"Fact '{fact_id}' field 'skip' must be a list",
                fact_id=fact_id,
            ))
        else:
            for i, matcher in enumerate(fact["skip"]):
                matcher_errors = _validate_matcher(fact_id, "skip", i, matcher)
                errors.extend(matcher_errors)

    # Check 'tags' field if present
    if "tags" in fact:
        if not isinstance(fact["tags"], list):
            errors.append(create_error(
                error_codes.INVALID_TAGS_FIELD,
                f"Fact '{fact_id}' field 'tags' must be a list",
                fact_id=fact_id,
            ))
        else:
            for i, tag in enumerate(fact["tags"]):
                if not isinstance(tag, str):
                    errors.append(create_error(
                        error_codes.INVALID_TAGS_FIELD,
                        f"Fact '{fact_id}' tags[{i}] must be a string, got {type(tag).__name__}",
                        fact_id=fact_id,
                    ))

    return errors


def _validate_matcher(fact_id: str, field: str, index: int, matcher: str) -> list[dict]:
    """Validate a single matcher string."""
    errors = []

    if not isinstance(matcher, str):
        errors.append(create_error(
            error_codes.INVALID_MATCHER_FORMAT,
            f"Fact '{fact_id}' {field}[{index}] must be a string, got {type(matcher).__name__}",
            fact_id=fact_id,
            field=field,
            index=index,
        ))
        return errors

    try:
        matcher_type, value = parse_matcher_string(matcher)
    except ValueError as e:
        errors.append(create_error(
            error_codes.INVALID_MATCHER_PREFIX,
            f"Fact '{fact_id}' {field}[{index}]: {e}",
            fact_id=fact_id,
            field=field,
            index=index,
            matcher=matcher,
        ))
        return errors

    # Validate glob syntax
    if matcher_type == "path":
        is_valid, pattern_errors = validate_glob_pattern(value)
        if not is_valid:
            for err in pattern_errors:
                errors.append(create_error(
                    err["code"],
                    f"Fact '{fact_id}' {field}[{index}]: {err['message']}",
                    fact_id=fact_id,
                    field=field,
                    index=index,
                    matcher=matcher,
                ))

    # Validate regex syntax for regex-based targets
    if matcher_type in {"content", "description"}:
        try:
            re.compile(value)
        except re.error as e:
            errors.append(create_error(
                error_codes.INVALID_REGEX_PATTERN,
                f"Fact '{fact_id}' {field}[{index}]: invalid regex: {e}",
                fact_id=fact_id,
                field=field,
                index=index,
                matcher=matcher,
            ))

    return errors
