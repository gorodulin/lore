from lore.validation.find_subset_patterns import find_subset_patterns


def find_subset_patterns_in_fact(fact: dict) -> list[tuple[str, str]]:
    """Find subset patterns within a single fact's incl list.

    Only checks positive matchers (incl) since those define what the
    fact matches. Subset positives are redundant.

    Args:
        fact: Fact dict with 'incl' list

    Returns:
        List of (subset, superset) tuples from incl matchers.
    """
    return find_subset_patterns(fact.get("incl", []))
