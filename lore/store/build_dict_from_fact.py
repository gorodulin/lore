from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet
from lore.store.build_strings_from_matcher_set import build_strings_from_matcher_set


def build_dict_from_fact(fact: Fact) -> dict:
    """Convert a typed Fact back into a raw dict suitable for serialization.

    Inverse of build_fact_from_dict.

    Args:
        fact: Typed Fact with compiled MatcherSets.

    Returns:
        Raw dict with 'fact', 'incl', and optional 'skip'/'tags' keys.
    """
    result = {
        "fact": fact.text,
        "incl": build_strings_from_matcher_set(fact.incl),
    }

    if fact.skip != MatcherSet():
        result["skip"] = build_strings_from_matcher_set(fact.skip)

    if fact.tags:
        result["tags"] = list(fact.tags)

    return result
