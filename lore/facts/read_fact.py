from lore.facts.locate_facts_by_id import locate_facts_by_id


def read_fact(project_root: str, fact_id: str) -> dict:
    """Read a fact by ID and return with globalized patterns.

    Returns dict with 'fact_id', 'file_path', and globalized
    'fact', 'incl', 'skip', 'tags' fields.

    Raises:
        ValueError: If fact_id is not found.
    """
    locations = locate_facts_by_id(project_root, {fact_id})
    if fact_id not in locations:
        raise ValueError(f"Fact ID '{fact_id}' not found")
    loc = locations[fact_id]
    return {"fact_id": fact_id, "file_path": loc["file_path"], **loc["fact"]}
