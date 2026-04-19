from lore.store.load_facts_tree import load_facts_tree
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.validation.validate_fact_set import validate_fact_set
from lore.facts.find_matching_facts import find_matching_facts
from lore.paths.resolve_relative_path import resolve_relative_path


def match_facts_for_path(project_root: str, file_path: str, content: str | None = None, description: str | None = None, command: str | None = None, tools: tuple[str, ...] | None = None, endpoints: tuple[str, ...] | None = None) -> dict[str, dict]:
    """Run the full matching pipeline and return facts matching a tool event.

    Loads all .lore.json files under project_root, merges, validates,
    builds typed Facts, and matches against the given event fields.

    Args:
        project_root: Absolute path to the project root directory
        file_path: Path to match (absolute or relative to project_root).
            Pass empty string for events without a path (e.g. Bash).
        content: Optional file content for content regexes
        description: Optional description text for description regexes
        command: Optional raw command text for command regexes
        tools: Optional per-item tool entries from CMD-META for ``t:`` matchers
        endpoints: Optional per-item endpoint entries for ``e:`` matchers

    Returns:
        Dict mapping fact_id to raw fact dict for every matching fact.

    Raises:
        ValueError: If project_root is empty, file_path is outside project,
                     or validation fails.
    """
    if not project_root:
        raise ValueError("project_root must not be empty")

    if file_path:
        normalized = resolve_relative_path(project_root, file_path)
        if normalized is None:
            raise ValueError(f"file_path '{file_path}' is outside project root '{project_root}'")
    else:
        normalized = ""

    fact_files = load_facts_tree(project_root)
    if not fact_files:
        return {}

    merged = merge_fact_tree_to_global_matchers(fact_files)

    valid, errors = validate_fact_set(merged)
    if not valid:
        messages = [f"[{e['code']}] {e.get('fact_id', '?')}: {e['message']}" for e in errors]
        raise ValueError(f"Invalid facts: {'; '.join(messages)}")

    typed_facts = {fid: build_fact_from_dict(fid, fact) for fid, fact in merged.items()}

    matching_ids = find_matching_facts(typed_facts, normalized, content=content, description=description, command=command, tools=tools, endpoints=endpoints)
    if not matching_ids:
        return {}

    return {fid: merged[fid] for fid in matching_ids}
