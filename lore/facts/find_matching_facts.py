from lore.facts.evaluate_fact_for_path import evaluate_fact_for_path


def find_matching_facts(compiled_facts: dict[str, dict], path: str, content: str | None = None) -> list[str]:
    """Find all facts that match a given path.

    Iterates through all compiled facts and returns IDs of facts where
    the path matches (satisfies incl and not excluded by skip).

    Args:
        compiled_facts: Dict mapping fact_id to compiled fact
        path: Path to test (use trailing / for directories)

    Returns:
        List of fact IDs that match the path

    Example:
        >>> compiled = {
        ...     'f1': compile_fact_matchers({'fact': 'JS', 'incl': ['g:**/*.js']}),
        ...     'f2': compile_fact_matchers({'fact': 'TS', 'incl': ['g:**/*.ts']}),
        ... }
        >>> find_matching_facts(compiled, 'src/app.js')
        ['f1']
        >>> find_matching_facts(compiled, 'src/app.ts')
        ['f2']
    """
    matching_ids = []

    for fact_id, compiled_fact in compiled_facts.items():
        if evaluate_fact_for_path(compiled_fact, path, content=content):
            matching_ids.append(fact_id)

    return matching_ids
