import os
import tempfile

from lore.validation.validate_fact_structure import validate_fact_structure
from lore.store.format_facts_as_json import format_facts_as_json


def save_facts_file(file_path: str, fact_set: dict[str, dict]) -> None:
    """Write a fact set to a .lore.json file atomically.

    Validates all facts before writing. Uses a temp file + os.replace()
    for atomic writes.

    Args:
        file_path: Destination path for the .lore.json file
        fact_set: Dict mapping fact ID to fact dict

    Raises:
        ValueError: If any fact fails structural validation
    """
    # Validate all facts before writing
    all_errors = []
    for fact_id, fact in fact_set.items():
        errors = validate_fact_structure(fact_id, fact)
        all_errors.extend(errors)

    if all_errors:
        messages = [e["message"] for e in all_errors]
        raise ValueError(f"Invalid facts: {'; '.join(messages)}")

    # Deterministic JSON output with compact arrays
    content = format_facts_as_json(fact_set)

    # Create parent directories
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    # Atomic write: temp file + replace
    fd, tmp_path = tempfile.mkstemp(
        dir=parent_dir or ".",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, file_path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass  # Best-effort cleanup - ignore if temp file already removed
        raise
