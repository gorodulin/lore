# Single source of truth for the CMD-META flag vocabulary. Ordered
# groups drive the display order in the instruction text; the derived
# frozenset is used for O(1) validation lookups.
#
# Vocabulary follows command-hooks-plan.md "Flag assessment checklist".

FLAG_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("State", ("mutates", "irreversible", "partial_reversible", "blast_repo", "blast_remote")),
    ("Safety", ("sensitive", "elevated_privileges")),
    ("Execution", ("network", "non_idempotent", "depends_on_prior", "retry")),
    ("Cost", ("slow", "heavy")),
    ("Trust", ("medium_confidence", "low_confidence")),
    ("Provenance", ("agent_initiated",)),
)

FLAG_VOCABULARY: frozenset[str] = frozenset(
    flag for _group, flags in FLAG_GROUPS for flag in flags
)
