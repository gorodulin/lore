import os
import sys

from lore.facts.generate_fact_id import generate_fact_id
from lore.paths.compute_rel_dir import compute_rel_dir
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.store.validate_fact_structure import validate_fact_structure
from lore.store.transform_matchers import transform_matchers
from lore.store.load_facts_tree import load_facts_tree
from lore.store.load_facts_file import load_facts_file
from lore.store.save_facts_file import save_facts_file
from lore.globs.compute_common_dir_from_matchers import compute_common_dir_from_matchers
from lore.globs.relativize_glob_to_root import relativize_glob_to_root
from lore.validation.validate_skip_matchers_scope import validate_skip_matchers_scope
from lore.errors.create_error import create_error
from lore import error_codes


def create_fact(root_dir: str, fact_text: str, incl: list[str], skip: list[str] | None = None, *, fact_id: str | None = None, tags: list[str] | None = None) -> dict:
    """Create a new fact and write it to the appropriate .lore.json file.

    Auto-determines the target .lore.json based on the common prefix of
    the inclusion patterns. Patterns are relativized so stored patterns
    stay local to their .lore.json directory.

    Args:
        root_dir: Project root directory
        fact_text: Human-readable fact description
        incl: List of inclusion matchers (e.g., ["p:lore/globs/**/*.py"])
        skip: Optional list of exclusion matchers
        fact_id: Optional explicit ID (auto-generated if not provided)

    Returns:
        Dict with 'fact_id', 'file_path', and 'fact' keys.

    Raises:
        ValueError: If fact_id already exists, or fact structure is invalid,
                    or patterns can't be relativized.
    """
    if skip is None:
        skip = []

    # 1. Generate or use provided ID
    if fact_id is None:
        fact_id = generate_fact_id()

    # 2. Build fact dict
    fact = {"fact": fact_text, "incl": list(incl)}
    if skip:
        fact["skip"] = list(skip)
    if tags:
        fact["tags"] = list(tags)

    # 3. Validate structure early
    errors = validate_fact_structure(fact_id, fact)
    if errors:
        messages = [e["message"] for e in errors]
        raise ValueError(f"Invalid fact: {'; '.join(messages)}")

    # 3b. Check skip pattern scope (logical validation - warning only)
    if skip:
        scope_issues = validate_skip_matchers_scope(incl, skip)
        for skip_pattern, issue in scope_issues:
            print(
                f"Warning: fact '{fact_id}' skip pattern '{skip_pattern}' {issue}",
                file=sys.stderr,
            )

    # 4. Check for ID collision across all existing facts
    fact_files = load_facts_tree(root_dir)
    for fact_file in fact_files:
        if fact_id in fact_file["facts"]:
            err = create_error(
                error_codes.DUPLICATE_FACT_ID,
                f"Fact ID '{fact_id}' already exists in {fact_file['file_path']}",
                fact_id=fact_id,
            )
            raise ValueError(err["message"])

    # 5. Compute target directory from incl patterns
    target_dir = compute_common_dir_from_matchers(incl)

    # 6. Relativize patterns to target directory
    transforms = {"path": lambda v: relativize_glob_to_root(v, target_dir)}
    local_incl = transform_matchers(incl, transforms)
    local_skip = transform_matchers(skip, transforms) if skip else []

    # 7. Build local fact
    local_fact = {"fact": fact_text, "incl": local_incl}
    if local_skip:
        local_fact["skip"] = local_skip
    if tags:
        local_fact["tags"] = list(tags)

    # 8. Determine target file path
    if target_dir == ".":
        target_file = os.path.join(root_dir, ".lore.json")
    else:
        target_file = os.path.join(root_dir, target_dir, ".lore.json")

    # 9. Load existing fact set or start fresh
    if os.path.exists(target_file):
        existing = load_facts_file(target_file)
    else:
        existing = {}

    # 10. Add fact and save
    existing[fact_id] = local_fact
    save_facts_file(target_file, existing)

    rel_dir = compute_rel_dir(target_file, root_dir)
    globalized = merge_fact_tree_to_global_matchers([{
        "rel_dir": rel_dir,
        "facts": {fact_id: local_fact},
    }])

    return {
        "fact_id": fact_id,
        "file_path": target_file,
        **globalized[fact_id],
    }
