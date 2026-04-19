import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MatcherSet:
    path_globs: tuple[dict, ...] = ()
    content_regexes: tuple[re.Pattern, ...] = ()
    description_regexes: tuple[re.Pattern, ...] = ()
    command_regexes: tuple[re.Pattern, ...] = ()
