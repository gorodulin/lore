from lore.facts.matcher_set import MatcherSet
from lore.matchers.compile_matcher import compile_matcher
from lore.matchers.parse_matcher_string import parse_matcher_string


def build_matcher_set_from_strings(matchers: list[str]) -> MatcherSet:
    """Convert a list of prefixed matcher strings into a typed MatcherSet.

    Parses each string to extract its type and value, compiles the value
    into its executable form, and groups results into the appropriate
    MatcherSet field.

    Args:
        matchers: List of prefixed matcher strings (e.g., ["p:**/*.py", "c:import os"])

    Returns:
        MatcherSet with compiled matchers grouped by type.

    Raises:
        ValueError: If any matcher has an invalid prefix or value.
    """
    path_globs = []
    content_regexes = []
    description_regexes = []
    command_regexes = []
    tool_regexes = []
    endpoint_regexes = []
    flag_literals = []

    for matcher in matchers:
        matcher_type, value = parse_matcher_string(matcher)
        compiled = compile_matcher(matcher_type, value)

        if matcher_type == "path":
            path_globs.append(compiled)
        elif matcher_type == "content":
            content_regexes.append(compiled)
        elif matcher_type == "description":
            description_regexes.append(compiled)
        elif matcher_type == "command":
            command_regexes.append(compiled)
        elif matcher_type == "tool":
            tool_regexes.append(compiled)
        elif matcher_type == "endpoint":
            endpoint_regexes.append(compiled)
        elif matcher_type == "flag":
            flag_literals.append(compiled)

    return MatcherSet(
        path_globs=tuple(path_globs),
        content_regexes=tuple(content_regexes),
        description_regexes=tuple(description_regexes),
        command_regexes=tuple(command_regexes),
        tool_regexes=tuple(tool_regexes),
        endpoint_regexes=tuple(endpoint_regexes),
        flag_literals=tuple(flag_literals),
    )
