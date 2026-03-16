import os


def build_fact_render_context(file_path: str, project_root: str = "") -> dict[str, str]:
    """Build a template variable context dict from a file path.

    Variables:
        filepath - project-relative path (e.g. ``lore/facts/foo.py``)
        fullpath - absolute path as-is from the tool event
        folder   - directory of *filepath* with trailing ``/`` (empty for root files)
        filename - basename (e.g. ``foo.py``)
        ext      - extension with leading dot (empty if none)
        basename - filename without extension (e.g. ``foo``)

    Args:
        file_path: File path (absolute or relative)
        project_root: Absolute path to the project root; used to relativize
                       *file_path* for ``{{filepath}}``.

    Returns:
        Dict mapping variable names to their string values.
    """
    fullpath = file_path

    if project_root and os.path.isabs(file_path):
        root = os.path.normpath(project_root)
        fp = os.path.normpath(file_path)
        if fp.startswith(root + os.sep):
            rel = os.path.relpath(fp, root)
        elif fp == root:
            rel = ""
        else:
            rel = file_path
    else:
        rel = file_path

    folder = os.path.dirname(rel)
    if folder:
        folder += "/"
    filename = os.path.basename(rel)
    name, ext = os.path.splitext(filename)

    return {
        "filepath": rel,
        "fullpath": fullpath,
        "folder": folder,
        "filename": filename,
        "ext": ext,
        "basename": name,
    }
