import uuid


def build_test_fact(
    fact_id: str = None,
    fact_text: str = "Test fact",
    incl: list[str] = None,
    skip: list[str] = None,
    tags: list[str] = None,
) -> tuple[str, dict]:
    """Build a fact entry for testing.

    Args:
        fact_id: Unique ID for the fact (auto-generated UUID if not provided)
        fact_text: Human-readable description of the fact
        incl: List of positive matchers (required, must have prefix like "p:")
        skip: List of negative matchers (optional, must have prefix like "p:")

    Returns:
        Tuple of (fact_id, fact_dict) ready to be added to a ruleset

    Example:
        >>> fact_id, fact = build_test_fact(
        ...     incl=["p:**/*.js"],
        ...     skip=["p:**/vendor/**"],
        ... )
        >>> fact
        {'fact': 'Test fact', 'incl': ['p:**/*.js'], 'skip': ['p:**/vendor/**']}
    """
    if incl is None:
        incl = ["p:**/*"]

    if fact_id is None:
        fact_id = str(uuid.uuid4())[:8]

    fact_dict = {
        "fact": fact_text,
        "incl": incl,
    }

    if skip:
        fact_dict["skip"] = skip

    if tags:
        fact_dict["tags"] = tags

    return fact_id, fact_dict
