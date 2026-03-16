import json
import os
import sys
import traceback


def save_display_rate_state(state: dict, path: str) -> None:
    """Atomically save display-rate counter state to disk.

    Writes to a temporary file first, then replaces the target.
    Silently ignores errors so the hook never blocks Claude.

    Args:
        state: Counter dict to persist
        path: Absolute path to the state file (from ``load_display_rate_state``)
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(state, f, separators=(",", ":"))
        os.replace(tmp, path)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
