import os
import sys

from lore import error_codes
from lore.errors.create_error import create_error
from lore.facts.create_fact import create_fact
from lore.facts.delete_fact import delete_fact
from lore.facts.locate_fact_by_id import locate_fact_by_id
from lore.store.load_facts_file import load_facts_file
from lore.store.save_facts_file import save_facts_file
from lore.validation.validate_fact_structure import validate_fact_structure
from lore.validation.validate_skip_matchers_scope import validate_skip_matchers_scope


def edit_fact(root_dir: str, fact_id: str, *, fact_text: str | None = None, incl: list[str] | None = None, skip: list[str] | None = None, tags: list[str] | None = None) -> dict:
    """Edit an existing fact by deleting and recreating it.

    Merges provided updates with the existing fact, then deletes from
    the old location and creates in the new location (which may be the
    same folder if patterns didn't change).

    The operation is atomic: if creation of the replacement fact fails,
    the original fact is restored from a captured snapshot.

    Patterns are expected in project-root format (e.g., "g:src/api/**/*.ts").
    They will be relativized and stored in the appropriate .lore.json file
    based on their common directory prefix.

    Args:
        root_dir: Project root directory
        fact_id: ID of the fact to edit
        fact_text: New fact text (None = keep existing)
        incl: New inclusion patterns in project-root format (None = keep existing)
        skip: New exclusion patterns in project-root format (None = keep existing)
        tags: New tags (None = keep existing)

    Returns:
        Dict with 'fact_id', 'file_path', and 'fact' keys.

    Raises:
        ValueError: If fact not found or updated fact is invalid.
    """
    # 1. Locate the existing fact
    location = locate_fact_by_id(root_dir, fact_id)
    if location is None:
        err = create_error(
            error_codes.FACT_NOT_FOUND,
            f"Fact ID '{fact_id}' not found",
            fact_id=fact_id,
        )
        raise ValueError(err["message"])

    existing_fact = location["fact"]
    old_file_path = location["file_path"]

    # 2. Get existing patterns (already globalized by locate_fact_by_id)
    existing_incl = existing_fact.get("incl", [])
    existing_skip = existing_fact.get("skip", [])

    # 3. Merge updates with existing data
    merged_text = fact_text if fact_text is not None else existing_fact.get("fact", "")
    merged_incl = incl if incl is not None else existing_incl
    merged_skip = skip if skip is not None else existing_skip
    merged_tags = tags if tags is not None else existing_fact.get("tags")

    # 4. Validate merged fact structure before any mutation
    candidate = {"fact": merged_text, "incl": list(merged_incl)}
    if merged_skip:
        candidate["skip"] = list(merged_skip)
    if merged_tags:
        candidate["tags"] = list(merged_tags)

    errors = validate_fact_structure(fact_id, candidate)
    if errors:
        messages = [e["message"] for e in errors]
        raise ValueError(f"Invalid fact: {'; '.join(messages)}")

    # 4b. Check skip pattern scope (logical validation - warning only)
    if merged_skip:
        scope_issues = validate_skip_matchers_scope(merged_incl, merged_skip)
        for skip_pattern, issue in scope_issues:
            print(
                f"Warning: fact '{fact_id}' skip pattern '{skip_pattern}' {issue}",
                file=sys.stderr,
            )

    # 5. Capture old state for rollback
    old_fact_set = load_facts_file(old_file_path)
    old_local_fact = old_fact_set[fact_id]

    # 6. Delete the old fact
    try:
        delete_fact(root_dir, fact_id)
    except ValueError as e:
        raise ValueError(f"Failed to delete existing fact '{fact_id}'") from e

    # 7. Create the new fact with merged data, rolling back on failure
    try:
        return create_fact(
            root_dir,
            merged_text,
            merged_incl,
            merged_skip,
            fact_id=fact_id,
            tags=merged_tags,
        )
    except Exception as e:
        _restore_fact(old_file_path, fact_id, old_local_fact)
        raise ValueError(f"Failed to create replacement fact '{fact_id}': {e}") from e


def _restore_fact(file_path: str, fact_id: str, local_fact: dict) -> None:
    """Restore a fact to its original .lore.json file after a failed edit."""
    if os.path.exists(file_path):
        fact_set = load_facts_file(file_path)
    else:
        fact_set = {}
    fact_set[fact_id] = local_fact
    save_facts_file(file_path, fact_set)
