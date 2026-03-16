from lore.store.load_facts_tree import load_facts_tree
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.validation.validate_fact_set import validate_fact_set
from lore.facts.compile_fact_matchers import compile_fact_matchers
from lore.facts.find_matching_facts import find_matching_facts
from lore.paths.resolve_relative_path import resolve_relative_path


def match_facts_for_path(project_root: str, file_path: str, content: str | None = None) -> dict[str, dict]:
    """Run the full matching pipeline and return facts matching a file path.

    Loads all .lore.json files under project_root, merges, validates,
    compiles, and matches against the given file_path.

    Args:
        project_root: Absolute path to the project root directory
        file_path: Path to match (absolute or relative to project_root)
        content: Optional file content for regex matchers

    Returns:
        Dict mapping fact_id to full fact dict for every matching fact.

    Raises:
        ValueError: If project_root is empty, file_path is outside project,
                     or validation fails.
    """
    if not project_root:
        raise ValueError("project_root must not be empty")

    normalized = resolve_relative_path(project_root, file_path)
    if normalized is None:
        raise ValueError(f"file_path '{file_path}' is outside project root '{project_root}'")

    fact_files = load_facts_tree(project_root)
    if not fact_files:
        return {}

    merged = merge_fact_tree_to_global_matchers(fact_files)

    valid, errors = validate_fact_set(merged)
    if not valid:
        messages = [f"[{e['code']}] {e.get('fact_id', '?')}: {e['message']}" for e in errors]
        raise ValueError(f"Invalid facts: {'; '.join(messages)}")

    compiled = {fid: compile_fact_matchers(fact) for fid, fact in merged.items()}

    matching_ids = find_matching_facts(compiled, normalized, content=content)
    if not matching_ids:
        return {}

    return {fid: merged[fid] for fid in matching_ids}
