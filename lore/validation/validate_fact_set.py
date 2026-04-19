from lore.store.validate_fact_structure import validate_fact_structure


def validate_fact_set(fact_set: dict[str, dict]) -> tuple[bool, list[dict]]:
    """Validate all facts in a fact set.

    Performs structural validation on each fact, checking:
    - Required fields (fact, incl)
    - Valid matcher prefixes (g:, r:, s:)
    - Valid glob pattern syntax

    Args:
        fact_set: Dict mapping fact ID to fact dict

    Returns:
        Tuple of (all_valid, errors_list) where errors_list contains
        error dicts with fact_id set for each issue
    """
    all_errors = []

    for fact_id, fact in fact_set.items():
        errors = validate_fact_structure(fact_id, fact)
        all_errors.extend(errors)

    return (len(all_errors) == 0, all_errors)
