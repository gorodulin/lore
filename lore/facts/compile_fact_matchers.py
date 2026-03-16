import re

from lore.facts.parse_matcher_string import parse_matcher_string
from lore.globs.compile_glob_pattern import compile_glob_pattern


def compile_fact_matchers(fact: dict) -> dict:
    """Compile all matchers in a fact for efficient evaluation.

    Takes a validated fact dict and compiles all matchers in 'incl' and 'skip'
    into their executable forms.

    Args:
        fact: Validated fact dict with 'fact', 'incl', and optional 'skip'

    Returns:
        Dict with compiled matchers:
        {
            'incl': [(original_matcher, compiled), ...],
            'skip': [(original_matcher, compiled), ...],
        }

    Note:
        Currently only glob matchers are supported. Regex and string matchers
        will raise NotImplementedError until implemented.
    """
    compiled = {
        "incl": [],
        "skip": [],
    }

    for matcher in fact.get("incl", []):
        matcher_type, value = parse_matcher_string(matcher)
        compiled_matcher = _compile_single_matcher(matcher_type, value)
        compiled["incl"].append((matcher, compiled_matcher))

    for matcher in fact.get("skip", []):
        matcher_type, value = parse_matcher_string(matcher)
        compiled_matcher = _compile_single_matcher(matcher_type, value)
        compiled["skip"].append((matcher, compiled_matcher))

    return compiled


def _compile_single_matcher(matcher_type: str, value: str):
    """Compile a single matcher value based on its type."""
    if matcher_type == "glob":
        return compile_glob_pattern(value)
    elif matcher_type == "regex":
        return {"regex": re.compile(value, re.MULTILINE)}
    elif matcher_type == "string":
        raise NotImplementedError("String matchers not yet implemented")
    else:
        raise ValueError(f"Unknown matcher type: {matcher_type}")
