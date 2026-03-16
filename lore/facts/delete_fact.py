import os

from lore.facts.locate_fact_by_id import locate_fact_by_id
from lore.store.load_facts_file import load_facts_file
from lore.store.save_facts_file import save_facts_file
from lore.errors.create_error import create_error
from lore import error_codes


def delete_fact(root_dir: str, fact_id: str) -> dict:
    """Delete a fact from its .lore.json file.

    If the fact set becomes empty after deletion, the file is removed.

    Args:
        root_dir: Project root directory
        fact_id: ID of the fact to delete

    Returns:
        Dict with 'fact_id', 'file_path', and 'fact' (the deleted fact).

    Raises:
        ValueError: If fact not found.
    """
    # 1. Locate the fact
    location = locate_fact_by_id(root_dir, fact_id)
    if location is None:
        err = create_error(
            error_codes.FACT_NOT_FOUND,
            f"Fact ID '{fact_id}' not found",
            fact_id=fact_id,
        )
        raise ValueError(err["message"])

    file_path = location["file_path"]
    deleted_fact = location["fact"]

    # 2. Load full fact set and remove the fact
    fact_set = load_facts_file(file_path)
    del fact_set[fact_id]

    # 3. Save or delete file
    if fact_set:
        save_facts_file(file_path, fact_set)
    else:
        os.remove(file_path)

    return {
        "fact_id": fact_id,
        "file_path": file_path,
        **deleted_fact,
    }
