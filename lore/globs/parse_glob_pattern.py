def parse_glob_pattern(glob_pattern: str) -> dict:
    """Parse a validated glob pattern into segment tokens.

    Assumes pattern has already been validated by validate_glob_pattern.

    Args:
        glob_pattern: A valid glob pattern string

    Returns:
        Dict with:
        - 'raw': original pattern string
        - 'is_dir': True if pattern targets directories (trailing /)
        - 'segments': list of segment dicts, each with:
            - 'type': 'literal' | 'wildcard' | 'globstar'
            - 'value': original segment string
            - 'prefix': for wildcard, chars before *
            - 'suffix': for wildcard, chars after *
    """
    is_dir = glob_pattern.endswith("/")
    trimmed = glob_pattern.rstrip("/")

    segment_strs = trimmed.split("/") if trimmed else []
    segments = []

    for seg_str in segment_strs:
        if seg_str == "**":
            segments.append({
                "type": "globstar",
                "value": "**",
            })
        elif "*" in seg_str:
            star_pos = seg_str.index("*")
            segments.append({
                "type": "wildcard",
                "value": seg_str,
                "prefix": seg_str[:star_pos],
                "suffix": seg_str[star_pos + 1:],
            })
        else:
            segments.append({
                "type": "literal",
                "value": seg_str,
            })

    return {
        "raw": glob_pattern,
        "is_dir": is_dir,
        "segments": segments,
    }
