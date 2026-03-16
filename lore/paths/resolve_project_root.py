import os


def resolve_project_root(explicit_path: str | None = None) -> str:
    """Resolve project root from an explicit path, LORE_PROJECT_ROOT env var, or cwd."""
    if explicit_path:
        return os.path.realpath(explicit_path)
    env_root = os.environ.get("LORE_PROJECT_ROOT", "")
    if env_root:
        return os.path.realpath(env_root)
    return os.getcwd()
