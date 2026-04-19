"""
Scenario-based acceptance tests.

Loads YAML scenario files from tests/acceptance/scenarios/ and runs them.
Each scenario defines:
- rules: A ruleset with facts
- paths: List of paths to test (optional for validation-only scenarios)
- expected: Mapping of path -> list of matching fact IDs (optional)
- expected_warnings: Expected validation warnings (optional)
- tree: Directory structure for merge testing (optional)
"""

import json
import pytest
import yaml
from pathlib import Path

from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.find_matching_facts import find_matching_facts
from lore.store.load_facts_tree import load_facts_tree
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.validation.find_duplicate_matchers_across_facts import find_duplicate_matchers_across_facts
from lore.validation.find_dead_skip_matchers import find_dead_skip_matchers
from lore.validation.find_subset_patterns_in_fact import find_subset_patterns_in_fact
from lore.validation.check_glob_target_consistency_across_facts import check_glob_target_consistency_across_facts


SCENARIOS_DIR = Path(__file__).parent / "scenarios"


def load_scenario(scenario_path: Path) -> dict:
    """Load a YAML scenario file."""
    with open(scenario_path, "r") as f:
        return yaml.safe_load(f)


def get_scenario_files():
    """Discover all scenario YAML files."""
    return list(SCENARIOS_DIR.glob("*.yaml"))


def get_matching_scenarios():
    """Get scenarios that test matching (have paths and expected)."""
    return [p for p in get_scenario_files()
            if "paths" in load_scenario(p) and "expected" in load_scenario(p)]


def get_validation_scenarios():
    """Get scenarios that test validation (have expected_warnings)."""
    return [p for p in get_scenario_files()
            if "expected_warnings" in load_scenario(p)]


def get_merge_scenarios():
    """Get scenarios that test merging (have tree)."""
    return [p for p in get_scenario_files()
            if "tree" in load_scenario(p)]


def scenario_id(scenario_path: Path) -> str:
    """Generate test ID from scenario filename."""
    return scenario_path.stem


class TestMatchingScenarios:
    """Run matching-based tests."""

    @pytest.mark.parametrize("scenario_path", get_matching_scenarios(), ids=scenario_id)
    def test_scenario_matching(self, scenario_path):
        """Test that paths match expected facts according to scenario."""
        scenario = load_scenario(scenario_path)

        # Build typed facts
        typed_facts = {
            fact_id: build_fact_from_dict(fact_id, fact)
            for fact_id, fact in scenario["rules"].items()
        }

        # Test each path
        for path, expected_facts in scenario["expected"].items():
            actual_facts = find_matching_facts(typed_facts, path)

            # Sort for comparison (order doesn't matter)
            expected_sorted = sorted(expected_facts) if expected_facts else []
            actual_sorted = sorted(actual_facts)

            assert actual_sorted == expected_sorted, (
                f"Scenario '{scenario['description']}' failed for path '{path}':\n"
                f"  Expected: {expected_sorted}\n"
                f"  Actual: {actual_sorted}"
            )


class TestValidationScenarios:
    """Run validation warning tests."""

    @pytest.mark.parametrize("scenario_path", get_validation_scenarios(), ids=scenario_id)
    def test_scenario_validation(self, scenario_path):
        """Test that rules produce expected validation warnings."""
        scenario = load_scenario(scenario_path)
        expected = scenario["expected_warnings"]
        rules = scenario["rules"]

        # Check duplicates
        if "duplicates" in expected:
            actual_dups = find_duplicate_matchers_across_facts(rules)
            expected_dups = expected["duplicates"]

            for fact_id, matchers in expected_dups.items():
                assert fact_id in actual_dups, (
                    f"Expected duplicates in fact '{fact_id}' but found none"
                )
                for matcher in matchers:
                    assert matcher in actual_dups[fact_id], (
                        f"Expected duplicate matcher '{matcher}' in fact '{fact_id}'"
                    )

        # Check dead negatives
        if "dead_negatives" in expected:
            for fact_id, expected_dead in expected["dead_negatives"].items():
                actual_dead = find_dead_skip_matchers(rules[fact_id])
                assert set(actual_dead) == set(expected_dead), (
                    f"Dead negatives mismatch for fact '{fact_id}':\n"
                    f"  Expected: {expected_dead}\n"
                    f"  Actual: {actual_dead}"
                )

        # Check subsets
        if "subsets" in expected:
            for fact_id, expected_pairs in expected["subsets"].items():
                actual_pairs = find_subset_patterns_in_fact(rules[fact_id])
                actual_set = {(a, b) for a, b in actual_pairs}
                expected_set = {(a, b) for a, b in expected_pairs}
                assert actual_set == expected_set, (
                    f"Subset patterns mismatch for fact '{fact_id}':\n"
                    f"  Expected: {expected_set}\n"
                    f"  Actual: {actual_set}"
                )

        # Check mixed targets
        if "mixed_targets" in expected:
            actual_mixed = check_glob_target_consistency_across_facts(rules)
            expected_facts = set(expected["mixed_targets"])
            actual_facts = set(actual_mixed.keys())
            assert actual_facts == expected_facts, (
                f"Mixed target facts mismatch:\n"
                f"  Expected: {expected_facts}\n"
                f"  Actual: {actual_facts}"
            )


class TestMergeScenarios:
    """Run merge/prefix tests using directory trees."""

    @pytest.mark.parametrize("scenario_path", get_merge_scenarios(), ids=scenario_id)
    def test_scenario_merge(self, scenario_path, tmp_path):
        """Test that rules merge correctly from directory tree."""
        scenario = load_scenario(scenario_path)

        # Create directory tree
        _create_tree(tmp_path, scenario["tree"])

        # Load and merge
        fact_files = load_facts_tree(str(tmp_path))
        merged = merge_fact_tree_to_global_matchers(fact_files)

        # Check expected merged patterns
        for fact_id, expected_fact in scenario["expected_merged"].items():
            assert fact_id in merged, f"Expected fact '{fact_id}' not in merged"

            if "incl" in expected_fact:
                assert merged[fact_id]["incl"] == expected_fact["incl"], (
                    f"Fact '{fact_id}' incl mismatch:\n"
                    f"  Expected: {expected_fact['incl']}\n"
                    f"  Actual: {merged[fact_id]['incl']}"
                )

            if "skip" in expected_fact:
                assert merged[fact_id].get("skip") == expected_fact["skip"], (
                    f"Fact '{fact_id}' skip mismatch:\n"
                    f"  Expected: {expected_fact['skip']}\n"
                    f"  Actual: {merged[fact_id].get('skip')}"
                )


def _create_tree(base_path: Path, tree: dict):
    """Recursively create directory tree from dict structure."""
    for name, content in tree.items():
        path = base_path / name

        if name == ".lore.json":
            # Write .lore.json file
            path.write_text(json.dumps(content))
        elif isinstance(content, dict):
            # Create directory and recurse
            path.mkdir(exist_ok=True)
            _create_tree(path, content)
        else:
            # Write file content
            path.write_text(str(content))


class TestScenarioFormat:
    """Validate scenario file format."""

    @pytest.mark.parametrize("scenario_path", get_scenario_files(), ids=scenario_id)
    def test_scenario_has_description(self, scenario_path):
        """Each scenario must have a description."""
        scenario = load_scenario(scenario_path)
        assert "description" in scenario, f"{scenario_path.name} missing 'description'"

    @pytest.mark.parametrize("scenario_path", get_matching_scenarios(), ids=scenario_id)
    def test_matching_scenario_expected_covers_all_paths(self, scenario_path):
        """Each path in 'paths' must have an entry in 'expected'."""
        scenario = load_scenario(scenario_path)

        for path in scenario["paths"]:
            assert path in scenario["expected"], (
                f"{scenario_path.name}: path '{path}' not in expected"
            )
