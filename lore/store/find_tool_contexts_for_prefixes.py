# Determines which tool contexts a fact can participate in based on its
# matcher prefixes. Used for fact validation and routing - a fact whose
# prefix combination resolves to an empty set can never fire.
#
# Part of the command hooks extension plan (see command-hooks-plan.md).
# Will be used by fact creation/validation to warn about incompatible
# prefix combinations, and by the dispatch layer to skip facts that
# cannot match the current event type.

# Which tool contexts provide data for each matcher prefix.
#
# Prefixes follow the target-named scheme (not strategy-named):
#   p: path (glob)        c: content (regex)     d: description (regex)
#   t: tool (regex)       e: endpoint (regex)    f: flag (exact)
#   x: raw command (regex)
PREFIX_TO_TOOL_CONTEXTS = {
    "p": frozenset({"Read", "Edit", "Write", "Grep", "Glob", "Bash"}),
    "c": frozenset({"Read", "Edit", "Write"}),
    "d": frozenset({"Bash", "Agent", "WebFetch", "WebSearch"}),
    "t": frozenset({"Bash"}),
    "e": frozenset({"Bash", "WebFetch"}),
    "f": frozenset({"Bash"}),
    "x": frozenset({"Bash"}),
}

ALL_PREFIXES = frozenset(PREFIX_TO_TOOL_CONTEXTS.keys())


def find_tool_contexts_for_prefixes(prefixes: set[str]) -> frozenset[str]:
    """Return the set of tool contexts where all given prefixes have data.

    Each prefix maps to a set of tool contexts that provide its target
    field. A fact with multiple prefixes (AND logic) can only fire in
    contexts present in the intersection of all its prefix sets.

    Args:
        prefixes: Set of single-char prefix strings (e.g. {"p", "d", "t"}).

    Returns:
        Frozenset of tool context strings. Empty means the prefix
        combination can never fire.

    Raises:
        ValueError: If any prefix is unknown.

    Examples:
        >>> find_tool_contexts_for_prefixes({"p", "c"})
        frozenset({'Read', 'Edit', 'Write'})
        >>> find_tool_contexts_for_prefixes({"c", "x"})
        frozenset()
        >>> find_tool_contexts_for_prefixes({"d", "e"})
        frozenset({'Bash', 'WebFetch'})
    """
    if not prefixes:
        return frozenset()

    unknown = prefixes - ALL_PREFIXES
    if unknown:
        raise ValueError(f"Unknown prefixes: {sorted(unknown)}")

    context_sets = [PREFIX_TO_TOOL_CONTEXTS[p] for p in prefixes]
    return frozenset.intersection(*context_sets)
