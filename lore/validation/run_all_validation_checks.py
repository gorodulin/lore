from lore.store.load_facts_tree import load_facts_tree
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.validation.find_duplicate_matchers_across_facts import find_duplicate_matchers_across_facts
from lore.validation.check_glob_target_consistency_across_facts import check_glob_target_consistency_across_facts
from lore.validation.find_dead_skip_matchers import find_dead_skip_matchers
from lore.validation.find_subset_patterns_in_fact import find_subset_patterns_in_fact
from lore.validation.is_action_block_ineffective import is_action_block_ineffective


def run_all_validation_checks(root: str) -> dict:
    """Run all validation checks on facts under root.

    Args:
        root: Project root directory path

    Returns:
        Dict with 'issues' list and 'count' of total issues found.
    """
    tree = load_facts_tree(root)
    if not tree:
        return {"issues": [], "count": 0}

    all_facts = merge_fact_tree_to_global_matchers(tree)

    issues = []

    duplicates = find_duplicate_matchers_across_facts(all_facts)
    if duplicates:
        issues.append({"check": "duplicate_matchers", "results": duplicates})

    consistency = check_glob_target_consistency_across_facts(all_facts)
    if consistency:
        issues.append({"check": "glob_target_consistency", "results": consistency})

    for fact_id, fact in all_facts.items():
        dead = find_dead_skip_matchers(fact)
        if dead:
            issues.append(
                {"check": "dead_skip_matchers", "fact_id": fact_id, "matchers": dead}
            )

        subsets = find_subset_patterns_in_fact(fact)
        if subsets:
            issues.append(
                {
                    "check": "subset_patterns",
                    "fact_id": fact_id,
                    "pairs": [list(p) for p in subsets],
                }
            )

        if is_action_block_ineffective(fact):
            issues.append(
                {
                    "check": "action_block_ineffective",
                    "fact_id": fact_id,
                    "message": "action:block has no effect - fact only fires on non-blockable events (e.g. PostToolUse/Read)",
                }
            )

    return {"issues": issues, "count": len(issues)}
