# Vulture whitelist - names used only in code vulture can't trace.
# Never add names just to make Vulture shut up. :-)

from lore.client.ensure_lore_server import ensure_lore_server  # noqa: F401  # Public API for external callers
Fact  # noqa: F821  # Domain type, imported by store/ builders
MatcherSet.path_globs  # noqa: F821  # Domain type field
MatcherSet.content_regexes  # noqa: F821  # Domain type field
