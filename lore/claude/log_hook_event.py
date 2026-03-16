import json
import os
import sys
import traceback
from datetime import datetime, timezone


def log_hook_event(event_data: dict, *, project_root: str, log_path: str, hook_tag: str | None = None, display_rate: int = 1) -> None:
    """Append a timestamped hook event as a JSONL line.

    Creates the parent directory if it does not exist. Silently returns
    on any error (empty log_path, I/O failure, etc.) so the hook never
    blocks Claude.

    Args:
        event_data: Raw hook event dict from stdin
        project_root: Absolute path to the project root (unused here)
        log_path: Absolute path to the JSONL log file
    """
    if not log_path:
        return

    try:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event_data,
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return
