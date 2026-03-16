import json
import os

from lore.errors.create_error import create_error
from lore.error_codes import FACTS_FILE_NOT_FOUND, FACTS_PARSE_ERROR


def load_facts_file(file_path: str) -> dict[str, dict]:
    """Load a single .lore.json file containing facts.

    Expected format:
    {
        "fact_id": {
            "fact": "Human-readable description",
            "incl": ["g:pattern1", "g:pattern2"],
            "skip": ["g:pattern3"]  // optional
        }
    }

    Args:
        file_path: Path to a .lore.json file

    Returns:
        Dict mapping fact ID to fact dict

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is not valid JSON or malformed
    """
    if not os.path.exists(file_path):
        err = create_error(
            FACTS_FILE_NOT_FOUND,
            f"Facts file not found: {file_path}",
        )
        raise FileNotFoundError(err["message"])

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        err = create_error(
            FACTS_PARSE_ERROR,
            f"Invalid JSON in facts file: {e}",
        )
        raise ValueError(err["message"]) from e

    if not isinstance(data, dict):
        err = create_error(
            FACTS_PARSE_ERROR,
            "Facts file must contain a JSON object",
        )
        raise ValueError(err["message"])

    # Validate each fact has required structure
    result = {}
    for fact_id, fact in data.items():
        if not isinstance(fact, dict):
            err = create_error(
                FACTS_PARSE_ERROR,
                f"Fact '{fact_id}' must be an object",
            )
            raise ValueError(err["message"])
        result[str(fact_id)] = fact

    return result
