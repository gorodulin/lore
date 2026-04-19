from lore.facts.fact import Fact
from lore.facts.evaluate_fact_for_path import evaluate_fact_for_path


def find_matching_facts(facts: dict[str, Fact], path: str, content: str | None = None) -> list[str]:
    """Find all facts that match a given path.

    Iterates through all typed facts and returns IDs of facts where
    the path matches (satisfies incl and not excluded by skip).

    Args:
        facts: Dict mapping fact_id to typed Fact.
        path: Path to test (use trailing / for directories).
        content: Optional content to test regex matchers against.

    Returns:
        List of fact IDs that match the path.
    """
    matching_ids = []

    for fact_id, fact in facts.items():
        if evaluate_fact_for_path(fact, path, content=content):
            matching_ids.append(fact_id)

    return matching_ids
