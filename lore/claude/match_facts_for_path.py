import sys
import traceback

from lore.facts.match_facts_for_path import match_facts_for_path as match_facts_impl


def match_facts_for_path(project_root: str, file_path: str, content: str | None = None, description: str | None = None, command: str | None = None, tools: tuple[str, ...] | None = None, endpoints: tuple[str, ...] | None = None, flags: tuple[str, ...] | None = None, affected_paths: tuple[str, ...] | None = None) -> dict[str, dict]:
    """Run the full matching pipeline and return facts matching a tool event.

    Thin error-swallowing wrapper around lore.facts.match_facts_for_path
    for use in Claude hook handlers where errors must never propagate.

    Returns ``{}`` on any error (invalid root, no facts, validation
    failure, path outside project, etc.).

    Args:
        project_root: Absolute path to the project root directory
        file_path: Path to match (absolute or relative to project_root).
            Pass empty string for events without a path.
        content: Optional file content for content regexes
        description: Optional description text for description regexes
        command: Optional raw command text for command regexes
        tools: Optional per-item tool entries from CMD-META for ``t:`` matchers
        endpoints: Optional per-item endpoint entries for ``e:`` matchers
        flags: Optional per-item flag literals from CMD-META for ``f:`` matchers
        affected_paths: Optional per-item affected_paths from CMD-META for
            ``p:`` matchers on Bash events
    """
    try:
        return match_facts_impl(project_root, file_path, content=content, description=description, command=command, tools=tools, endpoints=endpoints, flags=flags, affected_paths=affected_paths)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return {}
