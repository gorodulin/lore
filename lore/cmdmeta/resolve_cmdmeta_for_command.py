from dataclasses import dataclass

from lore.cmdmeta.cmdmeta import CmdMeta
from lore.cmdmeta.extract_cmdmeta_block import extract_cmdmeta_block
from lore.cmdmeta.parse_cmdmeta_block import CmdMetaParseError, parse_cmdmeta_block
from lore.cmdmeta.validate_cmdmeta import validate_cmdmeta


@dataclass(frozen=True)
class CmdMetaResolution:
    """Resolved view of a command's CMD-META state.

    Three distinct states encoded jointly by ``block_present`` and ``errors``:

    * No BEGIN sentinel present (non-Bash event, or Bash without META):
      ``block_present=False``, ``meta is None``, ``errors=()``.
    * Block present but malformed or semantically invalid:
      ``block_present=True``, ``meta is None``, ``errors`` non-empty.
    * Block present and fully valid:
      ``block_present=True``, ``meta is not None``, ``errors=()``.
    """

    bare_command: str
    meta: CmdMeta | None
    block_present: bool
    errors: tuple[str, ...]


def resolve_cmdmeta_for_command(raw_command: str) -> CmdMetaResolution:
    """Extract, parse, and validate a CMD-META trailer in one pass.

    Thin façade over :func:`extract_cmdmeta_block`, :func:`parse_cmdmeta_block`,
    and :func:`validate_cmdmeta`. Exists so the Bash gate and the fact
    collector share one resolution instead of each running the three-stage
    pipeline independently.
    """
    bare_command, block_text = extract_cmdmeta_block(raw_command)

    if block_text is None:
        return CmdMetaResolution(
            bare_command=bare_command,
            meta=None,
            block_present=False,
            errors=(),
        )

    try:
        meta = parse_cmdmeta_block(block_text)
    except CmdMetaParseError as exc:
        return CmdMetaResolution(
            bare_command=bare_command,
            meta=None,
            block_present=True,
            errors=(f"CMD-META parse error: {exc}",),
        )

    semantic_errors = validate_cmdmeta(meta)
    if semantic_errors:
        return CmdMetaResolution(
            bare_command=bare_command,
            meta=None,
            block_present=True,
            errors=tuple(semantic_errors),
        )

    return CmdMetaResolution(
        bare_command=bare_command,
        meta=meta,
        block_present=True,
        errors=(),
    )
