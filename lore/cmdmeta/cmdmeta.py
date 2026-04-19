from dataclasses import dataclass


@dataclass(frozen=True)
class CmdMeta:
    """Typed representation of a parsed CMD-META block.

    Companion to the `Fact` / `MatcherSet` value objects — same
    frozen-dataclass + immutable-tuple convention.

    Fields:
        tools: Recognised command entry-points the agent emitted
            (e.g. ``("git push",)``). Required key in the grammar;
            may be an empty tuple for trivial commands like ``echo``.
        endpoints: URLs, hosts, SSH targets, etc. Optional.
        flags: Applied flags from the closed vocabulary. Optional.
        affected_paths: Files or globs the command writes to. Optional.
    """

    tools: tuple[str, ...] = ()
    endpoints: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()
    affected_paths: tuple[str, ...] = ()
