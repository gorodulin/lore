from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet
from lore.store.build_matcher_set_from_strings import build_matcher_set_from_strings


def build_fact_from_dict(fact_id: str, raw: dict) -> Fact:
    """Convert a raw fact dict into a typed Fact.

    Assumes the dict has already been validated via validate_fact_structure.
    Compiles all matchers into their executable forms.

    Args:
        fact_id: Fact identifier.
        raw: Raw fact dict with 'fact', 'incl', and optional 'skip'/'tags'.

    Returns:
        Typed Fact with compiled MatcherSets.
    """
    incl = build_matcher_set_from_strings(raw["incl"])

    skip_strings = raw.get("skip", [])
    skip = build_matcher_set_from_strings(skip_strings) if skip_strings else MatcherSet()

    tags = tuple(raw.get("tags", []))

    return Fact(
        fact_id=fact_id,
        text=raw["fact"],
        incl=incl,
        skip=skip,
        tags=tags,
    )
