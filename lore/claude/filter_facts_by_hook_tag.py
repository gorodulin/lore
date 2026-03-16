def filter_facts_by_hook_tag(facts: dict[str, dict], hook_tag: str | None) -> dict[str, dict]:
    """Filter facts by hook tag.

    Logic:
    - hook_tag is None → return all facts
    - Fact has no hook:* tags → passes all filters (backward compatible)
    - Fact has hook:* tags → passes only if hook_tag is among them (OR logic)
    - kind:* and other non-hook tags are ignored for filtering

    Args:
        facts: Dict mapping fact_id to full fact dict
        hook_tag: Tag to filter by (e.g. "hook:read"), or None for all

    Returns:
        Filtered dict of facts
    """
    if hook_tag is None:
        return facts

    result = {}
    for fact_id, fact in facts.items():
        tags = fact.get("tags", [])
        hook_tags = [t for t in tags if t.startswith("hook:")]

        if not hook_tags:
            # No hook tags = show on all hooks (backward compatible)
            result[fact_id] = fact
        elif hook_tag in hook_tags:
            # Has hook tags and matches
            result[fact_id] = fact

    return result
