from lore.store.load_facts_tree import load_facts_tree
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers


def locate_facts_by_id(root_dir: str, fact_ids: set[str]) -> dict[str, dict]:
    """Scan all .lore.json files to locate multiple facts by ID in a single pass.

    Loads the facts tree once and checks all requested IDs against each file,
    using set intersection for efficient lookup. Exits early when all IDs are found.

    Returned facts have global-scoped (project-root-relative) matchers.

    Args:
        root_dir: Project root directory to search
        fact_ids: Set of fact IDs to find

    Returns:
        Dict mapping found fact_id to {"file_path", "rel_dir", "fact"}.
        Missing IDs are absent from the result.
    """
    if not fact_ids:
        return {}

    remaining = set(fact_ids)
    results = {}
    fact_files = load_facts_tree(root_dir)

    for fact_file in fact_files:
        facts = fact_file["facts"]
        found = remaining & facts.keys()
        if found:
            globalized = merge_fact_tree_to_global_matchers([{
                "rel_dir": fact_file["rel_dir"],
                "facts": {fid: facts[fid] for fid in found},
            }])
            for fid in found:
                results[fid] = {
                    "file_path": fact_file["file_path"],
                    "rel_dir": fact_file["rel_dir"],
                    "fact": globalized[fid],
                }
            remaining -= found
            if not remaining:
                break

    return results
