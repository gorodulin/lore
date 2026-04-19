from lore.cmdmeta.flag_vocabulary import FLAG_GROUPS, FLAG_VOCABULARY


class TestFlagVocabulary:
    def test_vocabulary_is_union_of_groups(self):
        flattened = {flag for _label, flags in FLAG_GROUPS for flag in flags}
        assert FLAG_VOCABULARY == frozenset(flattened)

    def test_group_labels_stable(self):
        labels = [label for label, _flags in FLAG_GROUPS]
        assert labels == ["State", "Safety", "Execution", "Cost", "Trust", "Provenance"]

    def test_every_plan_flag_present(self):
        expected = {
            "mutates", "irreversible", "partial_reversible",
            "blast_repo", "blast_remote",
            "sensitive", "elevated_privileges",
            "network", "non_idempotent", "depends_on_prior", "retry",
            "slow", "heavy",
            "medium_confidence", "low_confidence",
            "agent_initiated",
        }
        assert FLAG_VOCABULARY == frozenset(expected)

    def test_no_duplicate_flags_across_groups(self):
        all_flags = [flag for _label, flags in FLAG_GROUPS for flag in flags]
        assert len(all_flags) == len(set(all_flags))
