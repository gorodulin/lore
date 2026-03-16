import os

from lore.store.load_facts_file import load_facts_file
from lore.paths.normalize_path import normalize_path


def load_facts_tree(root_dir: str, *, filename: str = ".lore.json") -> list[dict]:
    """Discover and load all facts files under a directory tree.

    Walks the directory tree finding all files with the given filename,
    loads each one, and returns them with their relative directory path.

    Args:
        root_dir: Root directory to search from
        filename: Name of facts files to find (default: ".lore.json")

    Returns:
        List of dicts, each containing:
        - 'file_path': absolute path to the facts file
        - 'rel_dir': directory path relative to root_dir (normalized)
        - 'facts': dict mapping fact ID to fact dict
    """
    root = os.path.abspath(root_dir)
    results = []

    for dirpath, _, filenames in os.walk(root):
        if filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # Compute relative directory path
            rel_dir = os.path.relpath(dirpath, root)
            if rel_dir == ".":
                rel_dir_str = ""
            else:
                rel_dir_str = normalize_path(rel_dir, assume_dir=False)

            facts = load_facts_file(file_path)

            results.append({
                "file_path": file_path,
                "rel_dir": rel_dir_str,
                "facts": facts,
            })

    return results
