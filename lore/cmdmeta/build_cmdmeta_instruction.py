from lore.cmdmeta.flag_vocabulary import FLAG_GROUPS


_GRAMMAR_EXAMPLE = """\
  git push origin main  # ---CMD-META-BEGIN---
  # tools: git push
  # endpoints: github.com:org/repo
  # flags: mutates, network, irreversible, blast_remote
  # ---CMD-META-END---\
"""


_CHECKLIST = """\
Assessment checklist — for each command, ask each dimension independently:
  State:     Does it change anything? -> mutates
               Undoable? No -> irreversible. Partially -> partial_reversible
               Scope? Whole repo -> blast_repo. Beyond this machine -> blast_remote
  Safety:    Contains, reads, or exposes secrets/tokens/PII? -> sensitive
               Needs sudo, writes system paths, modifies global config? -> elevated_privileges
  Execution: Reaches the network? -> network
               Running twice is not safe? -> non_idempotent
               Depends on a prior command succeeding? -> depends_on_prior
               Re-attempting something that failed this session? -> retry
  Cost:      Takes more than a few seconds? -> slow
               Significant CPU/memory/network cost? -> heavy
  Trust:     Fairly sure but unverified? -> medium_confidence
               Guessing at syntax or behavior? -> low_confidence
  Provenance: You decided to run this, user didn't ask? -> agent_initiated

Include only flags that apply. Omit the flags line entirely when nothing fires.\
"""


def build_cmdmeta_instruction(errors: tuple[str, ...]) -> str:
    """Compose the instruction returned when the CMD-META gate denies a Bash command.

    Assembled from:
      1. A header listing what went wrong this attempt.
      2. A concrete grammar example.
      3. Field documentation (required vs optional).
      4. Flag vocabulary — rendered from :data:`FLAG_GROUPS` so the text
         stays in lockstep with the validator.
      5. The assessment checklist.

    Args:
        errors: Human-readable error strings collected by the gate.
            Must be non-empty; the gate always knows at least
            ``"CMD-META block missing"``.

    Returns:
        The full instruction string, suitable for use as
        ``permissionDecisionReason``.
    """
    if not errors:
        raise ValueError("build_cmdmeta_instruction requires at least one error")

    header = "CMD-META gate denied this command. Errors:\n" + "\n".join(
        f"  - {err}" for err in errors
    )

    grammar = (
        "Bash commands in this project require a CMD-META trailer. "
        "Re-issue your command with a trailing block like this:\n\n"
        + _GRAMMAR_EXAMPLE
    )

    fields = (
        "Required field: tools (comma-separated recognised command entry-points, "
        'e.g. "git push", "kubectl apply", "psql"). An empty list is allowed '
        "for trivial commands but the field must appear.\n"
        "Optional (when non-applicable) fields: endpoints (URLs / hosts / SSH targets), "
        "affected_paths (files or globs the command writes to), flags "
        "(any that apply from the vocabulary below)."
    )

    vocabulary_lines = ["Flag vocabulary:"]
    for group_name, flags in FLAG_GROUPS:
        vocabulary_lines.append(f"  {group_name}: {', '.join(flags)}")
    vocabulary = "\n".join(vocabulary_lines)

    return "\n\n".join([header, grammar, fields, vocabulary, _CHECKLIST])
