from lore.facts.locate_facts_by_id import locate_facts_by_id


def locate_fact_by_id(root_dir: str, fact_id: str) -> dict | None:
    """Scan all .lore.json files to locate a fact by ID.

    Thin wrapper around locate_facts_by_id() for single-ID lookup.

    Args:
        root_dir: Project root directory to search
        fact_id: The fact ID to find

    Returns:
        Dict with 'file_path', 'rel_dir', and 'fact' if found,
        or None if the fact ID doesn't exist in any facts file.
    """
    results = locate_facts_by_id(root_dir, {fact_id})
    return results.get(fact_id)
