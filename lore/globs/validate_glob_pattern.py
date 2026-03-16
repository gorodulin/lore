from lore.errors.create_error import create_error
from lore.error_codes import INVALID_EMPTY_PATTERN, INVALID_DOUBLE_SLASH, INVALID_GLOBSTAR_POSITION, INVALID_MULTIPLE_GLOBSTARS, INVALID_MULTIPLE_WILDCARDS_IN_SEGMENT, INVALID_UNSUPPORTED_METACHARACTER

_UNSUPPORTED_METACHARACTERS = set("{}[]")


def validate_glob_pattern(glob_pattern: str) -> tuple[bool, list[dict]]:
    """Validate a glob pattern against the supported glob subset.

    Supported features:
    - Literal path segments
    - Single `*` per segment (matches any chars except /)
    - Single `**` per pattern (must occupy entire segment, matches 0+ segments)
    - Trailing `/` for directory patterns

    Not supported:
    - Character classes [a-z], brace expansion {a,b}
    - Negation !pattern
    - Multiple `**` in one pattern
    - `**` combined with other chars in same segment

    Args:
        glob_pattern: Glob pattern string

    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []

    # Empty pattern check
    if not glob_pattern or glob_pattern.isspace():
        errors.append(
            create_error(
                INVALID_EMPTY_PATTERN,
                "Pattern cannot be empty",
                pattern=glob_pattern,
            )
        )
        return (False, errors)

    # Check for double slashes
    if "//" in glob_pattern:
        errors.append(
            create_error(
                INVALID_DOUBLE_SLASH,
                "Pattern contains double slashes",
                pattern=glob_pattern,
                at=glob_pattern.index("//"),
            )
        )
        return (False, errors)

    # Check for unsupported metacharacters ({, }, [, ])
    for i, ch in enumerate(glob_pattern):
        if ch in _UNSUPPORTED_METACHARACTERS:
            errors.append(
                create_error(
                    INVALID_UNSUPPORTED_METACHARACTER,
                    f"Unsupported glob syntax '{ch}' - brace expansion and character classes are not supported",
                    pattern=glob_pattern,
                    at=i,
                )
            )
            return (False, errors)

    # Remove trailing slash for segment analysis
    trimmed = glob_pattern.rstrip("/")

    if not trimmed:
        # Pattern was just "/" which is invalid
        errors.append(
            create_error(
                INVALID_EMPTY_PATTERN,
                "Pattern cannot be just a slash",
                pattern=glob_pattern,
            )
        )
        return (False, errors)

    segments = trimmed.split("/")
    globstar_count = 0

    for i, segment in enumerate(segments):
        if not segment:
            continue

        # Check for ** (globstar)
        if segment == "**":
            globstar_count += 1
            if globstar_count > 1:
                errors.append(
                    create_error(
                        INVALID_MULTIPLE_GLOBSTARS,
                        "Pattern contains multiple ** (only one allowed)",
                        pattern=glob_pattern,
                    )
                )
                return (False, errors)
            continue

        # Check for ** mixed with other characters (invalid)
        if "**" in segment:
            errors.append(
                create_error(
                    INVALID_GLOBSTAR_POSITION,
                    "** must occupy an entire path segment",
                    pattern=glob_pattern,
                    at=_find_segment_position(glob_pattern, i),
                )
            )
            return (False, errors)

        # Count single wildcards in segment
        wildcard_count = segment.count("*")
        if wildcard_count > 1:
            errors.append(
                create_error(
                    INVALID_MULTIPLE_WILDCARDS_IN_SEGMENT,
                    f"Segment '{segment}' contains multiple * (only one allowed per segment)",
                    pattern=glob_pattern,
                    at=_find_segment_position(glob_pattern, i),
                )
            )
            return (False, errors)

    return (True, [])


def _find_segment_position(glob_pattern: str, segment_index: int) -> int:
    """Find the character position where a segment starts in the pattern."""
    pos = 0
    for i, segment in enumerate(glob_pattern.split("/")):
        if i == segment_index:
            return pos
        pos += len(segment) + 1  # +1 for the /
    return pos
