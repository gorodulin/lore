from lore.globs.prepend_glob_prefix import prepend_glob_prefix
from lore.facts.transform_matchers import transform_matchers


def merge_fact_tree_to_global_matchers(fact_files: list[dict]) -> dict[str, dict]:
    """Merge local-root facts into a global-root fact set.

    Takes the output of load_facts_tree and prefixes glob patterns within
    each fact's incl/skip with their directory path to create globally-scoped
    patterns.

    Args:
        fact_files: List of dicts from load_facts_tree, each with:
            - 'rel_dir': relative directory path
            - 'facts': dict of {fact_id: fact_dict}

    Returns:
        Dict mapping fact ID to fact dict with globally-prefixed patterns

    Raises:
        ValueError: If duplicate fact IDs are found
    """
    merged = {}

    for fact_file in fact_files:
        rel_dir = fact_file["rel_dir"]
        facts = fact_file["facts"]

        for fact_id, fact in facts.items():
            if fact_id in merged:
                raise ValueError(f"Duplicate fact ID: {fact_id}")

            if rel_dir:
                merged_fact = _prefix_fact_matchers(fact, rel_dir)
            else:
                merged_fact = _copy_fact(fact)

            merged[fact_id] = merged_fact

    return merged


def _prefix_fact_matchers(fact: dict, prefix_dir: str) -> dict:
    """Create a copy of fact with glob matchers prefixed."""
    transforms = {"glob": lambda v: prepend_glob_prefix(v, prefix_dir)}
    result = {"fact": fact.get("fact", "")}

    if "incl" in fact:
        result["incl"] = transform_matchers(fact["incl"], transforms)

    if "skip" in fact:
        result["skip"] = transform_matchers(fact["skip"], transforms)

    if "tags" in fact:
        result["tags"] = list(fact["tags"])

    return result


def _copy_fact(fact: dict) -> dict:
    """Create a shallow copy of a fact dict."""
    result = {"fact": fact.get("fact", "")}

    if "incl" in fact:
        result["incl"] = list(fact["incl"])

    if "skip" in fact:
        result["skip"] = list(fact["skip"])

    if "tags" in fact:
        result["tags"] = list(fact["tags"])

    return result
