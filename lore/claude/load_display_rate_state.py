import json
import os
import sys
import traceback

from lore.resolve_cache_dir import resolve_cache_dir


def load_display_rate_state(session_id: str, project_root: str) -> tuple[dict, str]:
    """Load display-rate counter state for a session.

    Resolves the state file path via :func:`resolve_cache_dir`,
    then loads and returns the JSON dict.

    Args:
        session_id: Hook session identifier
        project_root: Absolute path to the project root

    Returns:
        Tuple of (state dict, resolved file path).
        State is ``{}`` on any I/O or parse error.
    """
    path = os.path.join(resolve_cache_dir(), f"display_rate_{session_id}.json")
    try:
        with open(path) as f:
            return json.load(f), path
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return {}, path
