from lore.facts.matcher_set import MatcherSet
from lore.matchers.build_matcher_string import build_matcher_string


def build_strings_from_matcher_set(matcher_set: MatcherSet) -> list[str]:
    """Convert a typed MatcherSet back into a list of prefixed matcher strings.

    Iterates fields in a fixed order (paths, content, description, command)
    and recovers the source string from each compiled form. The output order
    is deterministic for canonical serialization.

    Args:
        matcher_set: Typed MatcherSet with compiled matchers.

    Returns:
        List of prefixed matcher strings (e.g., ["p:**/*.py", "c:import os"]).
    """
    result = []

    for compiled_glob in matcher_set.path_globs:
        result.append(build_matcher_string("path", compiled_glob["raw"]))

    for compiled_regex in matcher_set.content_regexes:
        result.append(build_matcher_string("content", compiled_regex.pattern))

    for compiled_regex in matcher_set.description_regexes:
        result.append(build_matcher_string("description", compiled_regex.pattern))

    for compiled_regex in matcher_set.command_regexes:
        result.append(build_matcher_string("command", compiled_regex.pattern))

    for compiled_regex in matcher_set.tool_regexes:
        result.append(build_matcher_string("tool", compiled_regex.pattern))

    for compiled_regex in matcher_set.endpoint_regexes:
        result.append(build_matcher_string("endpoint", compiled_regex.pattern))

    return result
