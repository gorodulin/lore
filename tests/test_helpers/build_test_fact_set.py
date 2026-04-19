def build_test_fact_set(*facts: tuple[str, dict]) -> dict:
    """Combine fact entries into a fact set dict.

    Args:
        *facts: Tuples of (fact_id, fact_dict) from build_test_fact()

    Returns:
        Fact set dict mapping fact IDs to fact dicts

    Example:
        >>> fact_set = build_test_fact_set(
        ...     build_test_fact(fact_id="f1", incl=["p:**/*.js"]),
        ...     build_test_fact(fact_id="f2", incl=["p:**/*.ts"]),
        ... )
        >>> list(fact_set.keys())
        ['f1', 'f2']
    """
    return {fact_id: fact_dict for fact_id, fact_dict in facts}
