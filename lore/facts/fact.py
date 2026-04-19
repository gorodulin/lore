from dataclasses import dataclass, field

from lore.facts.matcher_set import MatcherSet


@dataclass(frozen=True)
class Fact:
    fact_id: str
    text: str
    incl: MatcherSet
    skip: MatcherSet = field(default_factory=MatcherSet)
    tags: tuple[str, ...] = ()
