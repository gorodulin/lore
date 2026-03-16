from lore.validation.check_glob_target_consistency import check_glob_target_consistency


def check_glob_target_consistency_across_facts(fact_set: dict[str, dict]) -> dict[str, dict]:
    """Check glob target consistency across all facts in a fact set.

    Args:
        fact_set: Dict mapping fact_id to fact dict

    Returns:
        Dict mapping fact_id to their inconsistency details.
        Only includes facts that have inconsistencies.
    """
    result = {}
    for fact_id, fact in fact_set.items():
        issue = check_glob_target_consistency(fact)
        if issue:
            result[fact_id] = issue
    return result
