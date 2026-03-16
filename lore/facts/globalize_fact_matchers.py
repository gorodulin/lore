from lore.paths.compute_rel_dir import compute_rel_dir
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers


def globalize_fact_matchers(disk_result: dict, project_root: str) -> dict:
    """Convert a CRUD disk result's local patterns to project-root scope.

    Takes a dict with 'fact_id', 'file_path', and 'fact' (local-scoped)
    and returns a flat dict with globalized incl/skip patterns.
    """
    file_path = disk_result["file_path"]
    fact_id = disk_result["fact_id"]
    local_fact = disk_result["fact"]

    rel_dir = compute_rel_dir(file_path, project_root)
    globalized = merge_fact_tree_to_global_matchers([{
        "rel_dir": rel_dir,
        "facts": {fact_id: local_fact},
    }])

    return {
        "fact_id": fact_id,
        "file_path": file_path,
        **globalized[fact_id],
    }
