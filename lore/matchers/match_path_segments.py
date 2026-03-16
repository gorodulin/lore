from lore.matchers.match_segment_to_wildcard import match_segment_to_wildcard


def match_path_segments(compiled: dict, segments: list[str], *, is_dir: bool) -> bool:
    """Low-level matcher operating on pre-split path segments.

    Uses a simple algorithm:
    - If no globstar: segments must match 1:1
    - If globstar: try all possible positions where ** consumes 0..N segments

    Note: This is an internal function. Prefer match_path_to_glob() which detects
    is_dir from trailing slash automatically.

    Args:
        compiled: Compiled pattern dict from compile_glob_pattern
        segments: List of path segments to match
        is_dir: True if path is a directory

    Returns:
        True if the path segments match the pattern
    """
    if not compiled.get("valid", False):
        return False

    pattern_segments = compiled["segments"]
    is_dir_pattern = compiled["is_dir"]

    # Directory pattern should only match directories
    if is_dir_pattern and not is_dir:
        return False

    globstar_index = compiled["globstar_index"]

    if globstar_index == -1:
        # No globstar: exact segment count match required
        return _match_without_globstar(pattern_segments, segments)
    else:
        # With globstar: try all possible expansions
        return _match_with_globstar(pattern_segments, segments, globstar_index)


def _match_segment(pattern_seg: dict, path_seg: str) -> bool:
    """Match a single pattern segment against a path segment."""
    seg_type = pattern_seg["type"]

    if seg_type == "literal":
        return pattern_seg["value"] == path_seg
    elif seg_type == "wildcard":
        return match_segment_to_wildcard(pattern_seg["value"], path_seg)
    elif seg_type == "globstar":
        # Globstar handled at path level, not segment level
        return True

    return False


def _match_without_globstar(pattern_segments: list[dict], path_segments: list[str]) -> bool:
    """Match when pattern has no globstar - requires exact segment count."""
    if len(pattern_segments) != len(path_segments):
        return False

    for pat_seg, path_seg in zip(pattern_segments, path_segments):
        if not _match_segment(pat_seg, path_seg):
            return False

    return True


def _match_with_globstar(pattern_segments: list[dict], path_segments: list[str], globstar_index: int) -> bool:
    """Match when pattern has globstar - try all possible expansions.

    Globstar matches 0 or more complete segments.
    """
    before_globstar = pattern_segments[:globstar_index]
    after_globstar = pattern_segments[globstar_index + 1:]

    # Minimum path length needed (globstar consuming 0 segments)
    min_path_len = len(before_globstar) + len(after_globstar)

    if len(path_segments) < min_path_len:
        return False

    # Check prefix match (segments before globstar)
    for i, pat_seg in enumerate(before_globstar):
        if not _match_segment(pat_seg, path_segments[i]):
            return False

    # Check suffix match (segments after globstar)
    # Try all possible positions where globstar ends
    max_globstar_consume = len(path_segments) - min_path_len

    for consume in range(max_globstar_consume + 1):
        # Globstar consumes 'consume' segments starting at globstar_index
        suffix_start = globstar_index + consume

        match = True
        for j, pat_seg in enumerate(after_globstar):
            path_idx = suffix_start + j
            if not _match_segment(pat_seg, path_segments[path_idx]):
                match = False
                break

        if match:
            return True

    return False
