from lore.store.parse_matcher_string import parse_matcher_string
from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.globs.extract_glob_fixed_prefix import extract_glob_fixed_prefix


def compute_common_dir_from_matchers(matchers: list[str]) -> str:
    """Compute the longest common directory prefix from a set of matchers.

    For each glob pattern, extracts the literal prefix segments.
    Finds the longest common directory prefix across all patterns,
    excluding the leaf (file) segment.

    Args:
        matchers: List of matcher strings (e.g., ["p:lore/globs/**/*.py"])

    Returns:
        Directory string (e.g., "lore/globs") or "." if no common prefix.
    """
    all_prefixes = []

    for matcher in matchers:
        try:
            matcher_type, value = parse_matcher_string(matcher)
        except ValueError:
            continue

        if matcher_type != "path":
            continue

        compiled = compile_glob_pattern(value)
        if not compiled["valid"]:
            continue

        fixed_segments = extract_glob_fixed_prefix(compiled)

        # Exclude the leaf segment (file name) - we want directory prefix only
        # If the pattern ends with a literal file segment (not a wildcard),
        # the last fixed segment is the filename, so exclude it
        # But if there's a wildcard after the fixed prefix, all fixed segments
        # are directory segments
        total_segments = len(compiled["segments"])
        fixed_count = len(fixed_segments)

        if fixed_count == total_segments and not compiled["is_dir"]:
            # All segments are literal and it's a file pattern —
            # last segment is the filename, exclude it
            dir_segments = fixed_segments[:-1]
        else:
            # Fixed prefix is followed by wildcards - all prefix segments
            # are directories
            dir_segments = fixed_segments

        all_prefixes.append(dir_segments)

    if not all_prefixes:
        return "."

    # Find longest common prefix across all directory segment lists
    common = all_prefixes[0]
    for prefix in all_prefixes[1:]:
        new_common = []
        for a, b in zip(common, prefix):
            if a == b:
                new_common.append(a)
            else:
                break
        common = new_common

    if not common:
        return "."

    return "/".join(common)
