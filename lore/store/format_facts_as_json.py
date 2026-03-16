import json


def format_facts_as_json(fact_set: dict[str, dict]) -> str:
    """Format a fact set dict as a JSON string with compact arrays.

    Produces deterministic output with:
    - Top-level keys sorted alphabetically
    - Inner fact keys sorted alphabetically
    - 2-space indentation for structure
    - Arrays rendered on a single line
    - All value escaping handled by json.dumps

    Args:
        fact_set: Dict mapping fact ID to fact dict

    Returns:
        JSON string with trailing newline.
    """
    if not fact_set:
        return "{}\n"

    lines = ["{"]
    sorted_ids = sorted(fact_set.keys())

    for id_idx, fact_id in enumerate(sorted_ids):
        fact = fact_set[fact_id]
        id_json = json.dumps(fact_id, ensure_ascii=False)
        lines.append(f"  {id_json}: {{")

        sorted_keys = sorted(fact.keys())
        for key_idx, key in enumerate(sorted_keys):
            value = sorted(fact[key]) if isinstance(fact[key], list) else fact[key]
            key_json = json.dumps(key, ensure_ascii=False)
            value_json = json.dumps(value, ensure_ascii=False)
            comma = "," if key_idx < len(sorted_keys) - 1 else ""
            lines.append(f"    {key_json}: {value_json}{comma}")

        fact_comma = "," if id_idx < len(sorted_ids) - 1 else ""
        lines.append(f"  }}{fact_comma}")

    lines.append("}")
    return "\n".join(lines) + "\n"
