import os

from lore.paths.normalize_path import normalize_path


def resolve_relative_path(project_root: str, file_path: str) -> str | None:
    """Turn file_path into a project-relative normalised path.

    Returns None if the path is outside the project root.
    """
    if not os.path.isabs(file_path):
        rel = file_path
    else:
        root = os.path.normpath(project_root)
        fp = os.path.normpath(file_path)
        if not fp.startswith(root + os.sep) and fp != root:
            return None
        rel = os.path.relpath(fp, root)

    return normalize_path(rel, assume_dir=False)
