from lore.facts.fact import Fact
from lore.facts.evaluate_fact_for_path import evaluate_fact_for_path


def find_matching_facts(facts: dict[str, Fact], path: str, content: str | None = None, description: str | None = None, command: str | None = None, tools: tuple[str, ...] | None = None, endpoints: tuple[str, ...] | None = None, flags: tuple[str, ...] | None = None, affected_paths: tuple[str, ...] | None = None) -> list[str]:
    """Find all facts that match a given tool event.

    Iterates through all typed facts and returns IDs of facts where
    the event matches (satisfies incl and not excluded by skip).

    Args:
        facts: Dict mapping fact_id to typed Fact.
        path: Path to test (use trailing / for directories).
            Pass empty string for events without a path.
        content: Optional content to test content regexes against.
        description: Optional description text to test description regexes.
        command: Optional raw command text to test command regexes.
        tools: Optional per-item tool entries from CMD-META for ``t:`` matchers.
        endpoints: Optional per-item endpoint entries for ``e:`` matchers.
        flags: Optional per-item flag literals from CMD-META for ``f:`` matchers.
        affected_paths: Optional per-item path source for ``p:`` on Bash events
            (from ``CmdMeta.affected_paths``).

    Returns:
        List of fact IDs that match the event.
    """
    matching_ids = []

    for fact_id, fact in facts.items():
        if evaluate_fact_for_path(fact, path, content=content, description=description, command=command, tools=tools, endpoints=endpoints, flags=flags, affected_paths=affected_paths):
            matching_ids.append(fact_id)

    return matching_ids
