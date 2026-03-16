from lore.validation.find_duplicate_matchers import find_duplicate_matchers


def find_duplicate_matchers_across_facts(fact_set: dict[str, dict]) -> dict[str, dict[str, list[str]]]:
    """Find duplicate matchers across all facts in a fact set.

    Args:
        fact_set: Dict mapping fact_id to fact dict

    Returns:
        Dict mapping fact_id to their duplicate matchers.
        Only includes facts that have duplicates.

    Example:
        >>> find_duplicate_matchers_across_facts({
        ...     'f1': {'fact': 'Test', 'incl': ['g:**/*.js', 'g:**/*.js']},
        ...     'f2': {'fact': 'Test', 'incl': ['g:**/*.ts']},
        ... })
        {'f1': {'g:**/*.js': ['g:**/*.js', 'g:**/*.js']}}
    """
    result = {}
    for fact_id, fact in fact_set.items():
        duplicates = find_duplicate_matchers(fact)
        if duplicates:
            result[fact_id] = duplicates
    return result
