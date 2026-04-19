from lore.cmdmeta.cmdmeta import CmdMeta
from lore.cmdmeta.flag_vocabulary import FLAG_VOCABULARY


def validate_cmdmeta(meta: CmdMeta) -> list[str]:
    """Semantic validation of a parsed CmdMeta.

    Structural parsing is handled by :func:`parse_cmdmeta_block`; this
    function checks only properties that require vocabulary knowledge:
    unknown flag values, and empty string entries anywhere in the list
    fields (which the parser cannot prevent without per-field rules).

    Args:
        meta: A CmdMeta produced by :func:`parse_cmdmeta_block`.

    Returns:
        A list of human-readable error strings. An empty list means
        the CmdMeta is semantically valid.
    """
    errors: list[str] = []

    for flag in meta.flags:
        if flag not in FLAG_VOCABULARY:
            errors.append(
                f"unknown flag {flag!r}; expected one of {sorted(FLAG_VOCABULARY)}"
            )

    for field_name, values in (
        ("tools", meta.tools),
        ("endpoints", meta.endpoints),
        ("flags", meta.flags),
        ("affected_paths", meta.affected_paths),
    ):
        if any(v == "" for v in values):
            errors.append(f"empty string value in {field_name!r}")

    return errors
