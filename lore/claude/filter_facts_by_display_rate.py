import hashlib

from lore.claude.load_display_rate_state import load_display_rate_state
from lore.claude.save_display_rate_state import save_display_rate_state


def filter_facts_by_display_rate(rendered_texts: dict[str, str], session_id: str, display_rate: int, project_root: str) -> dict[str, str]:
    """Filter rendered fact texts by display rate for session dedup.

    Tracks how many times each unique rendered text has been seen in the
    current session.  A fact is shown on the 1st occurrence, then every
    *display_rate*-th occurrence after that (i.e. 1, 1+N, 1+2N, ...).

    Args:
        rendered_texts: ``{fact_id: rendered_text}`` to filter
        session_id: Hook session identifier (empty → no filtering)
        display_rate: Show every Nth occurrence (< 1 or empty session → no filtering)
        project_root: Absolute path to the project root (for state file location)

    Returns:
        Subset of *rendered_texts* that should be displayed.
    """
    if not session_id or display_rate < 1:
        return dict(rendered_texts)

    state, state_path = load_display_rate_state(session_id, project_root)

    result = {}
    for fact_id, text in rendered_texts.items():
        key = _hash_key(text)
        count = state.get(key, 0) + 1
        state[key] = count
        if (count - 1) % display_rate == 0:
            result[fact_id] = text

    save_display_rate_state(state, state_path)
    return result


def _hash_key(text: str) -> str:
    """Return a short hash of rendered text for use as state dict key."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]
