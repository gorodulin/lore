import os

from lore.paths.normalize_path import normalize_path


def compute_rel_dir(facts_json_path: str, project_root: str) -> str:
    """Compute the relative directory from project root to a .lore.json file.

    Returns empty string for .lore.json at the project root.
    """
    facts_dir = os.path.dirname(facts_json_path)
    rel = os.path.relpath(facts_dir, project_root)
    if rel == ".":
        return ""
    return normalize_path(rel, assume_dir=False)
