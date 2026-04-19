from lore.matchers.parse_matcher_string import parse_matcher_string
from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.globs.extract_glob_fixed_prefix import extract_glob_fixed_prefix


def find_subset_patterns(matchers: list[str]) -> list[tuple[str, str]]:
    """Find glob patterns where one is a subset of another.

    Uses a heuristic approach that catches common cases:
    - Patterns with identical structure but different literal prefixes
      (e.g., 'src/**/*.js' is subset of '**/*.js')
    - Patterns with longer fixed prefix are more specific

    This is conservative - it may miss some subset relationships
    but won't report false positives.

    Args:
        matchers: List of matchers to check (with prefixes like 'p:')

    Returns:
        List of (subset, superset) tuples indicating subset relationships.

    Example:
        >>> find_subset_patterns(['p:src/**/*.js', 'p:**/*.js'])
        [('p:src/**/*.js', 'p:**/*.js')]
    """
    # Extract glob patterns with their compiled info
    globs = []
    for matcher in matchers:
        info = _analyze_glob(matcher)
        if info:
            globs.append((matcher, info))

    # Compare all pairs
    subsets = []
    for i, (matcher_a, info_a) in enumerate(globs):
        for j, (matcher_b, info_b) in enumerate(globs):
            if i == j:
                continue
            if _is_subset(info_a, info_b):
                subsets.append((matcher_a, matcher_b))

    return subsets



def _analyze_glob(matcher: str) -> dict | None:
    """Analyze a glob matcher for subset comparison."""
    try:
        matcher_type, value = parse_matcher_string(matcher)
    except ValueError:
        return None

    if matcher_type != "path":
        return None

    try:
        compiled = compile_glob_pattern(value)
        if not compiled.get("valid"):
            return None

        return {
            "raw": value,
            "is_dir": compiled.get("is_dir", False),
            "fixed_prefix": extract_glob_fixed_prefix(compiled),
            "segments": compiled.get("segments", []),
            "globstar_index": compiled.get("globstar_index", -1),
        }
    except Exception:
        return None


def _is_subset(info_a: dict, info_b: dict) -> bool:
    """Check if pattern A is a subset of pattern B.

    A is subset of B if everything A matches, B also matches.

    Heuristic rules:
    1. If A has fixed prefix and B starts with **, and suffix after ** is same,
       A is subset of B.
    2. If A's prefix starts with B's prefix and is longer, and suffix is same,
       A is subset of B.
    3. If patterns are identical, they are subsets of each other.
    """
    # Must have same target type (file vs dir)
    if info_a["is_dir"] != info_b["is_dir"]:
        return False

    prefix_a = info_a["fixed_prefix"]
    prefix_b = info_b["fixed_prefix"]
    segments_a = info_a["segments"]
    segments_b = info_b["segments"]

    # Case 0: Identical patterns
    if info_a["raw"] == info_b["raw"]:
        return True

    # Case 1: B has empty prefix (starts with **) and A has non-empty prefix
    # e.g., src/**/*.js is subset of **/*.js
    if not prefix_b and prefix_a:
        # Both patterns should have a globstar, compare suffix after globstar
        suffix_a = _get_suffix_after_globstar(segments_a)
        suffix_b = _get_suffix_after_globstar(segments_b)

        if suffix_a is not None and suffix_b is not None:
            if _suffixes_match(suffix_a, suffix_b):
                return True

    # Case 2: A's prefix starts with B's prefix and is longer
    # e.g., src/api/**/*.js is subset of src/**/*.js
    if prefix_b and prefix_a:
        if _is_prefix_of(prefix_b, prefix_a) and len(prefix_a) > len(prefix_b):
            # Check if suffix after globstar is same
            suffix_a = _get_suffix_after_globstar(segments_a)
            suffix_b = _get_suffix_after_globstar(segments_b)

            if suffix_a is not None and suffix_b is not None:
                if _suffixes_match(suffix_a, suffix_b):
                    return True

    return False


def _is_prefix_of(shorter: list[str], longer: list[str]) -> bool:
    """Check if shorter is a prefix of longer."""
    if len(shorter) > len(longer):
        return False
    return all(shorter[i] == longer[i] for i in range(len(shorter)))


def _get_suffix_after_globstar(segments: list[dict]) -> list[dict] | None:
    """Get segments after the first globstar."""
    for i, seg in enumerate(segments):
        if seg.get("type") == "globstar":
            return segments[i + 1:]
    return None


def _suffixes_match(suffix_a: list[dict], suffix_b: list[dict]) -> bool:
    """Check if two segment suffixes are equivalent."""
    if len(suffix_a) != len(suffix_b):
        return False

    for seg_a, seg_b in zip(suffix_a, suffix_b):
        if seg_a.get("type") != seg_b.get("type"):
            return False
        if seg_a.get("value") != seg_b.get("value"):
            return False

    return True
