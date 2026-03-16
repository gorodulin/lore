import re


def render_fact_text(template: str, context: dict[str, str]) -> str:
    """Render template variables in a fact text string.

    Replaces ``{{variable}}`` placeholders with values from *context*.
    Unknown variables are left as-is for forward compatibility.

    Args:
        template: Fact text, possibly containing ``{{...}}`` placeholders
        context: Variable name → value mapping

    Returns:
        Rendered string.
    """
    # Nested closure is intentional - regex single-pass is more performant
    # than looping str.replace per key, and extracting the closure would
    # require functools.partial to thread `context` through re.sub.
    def _replacer(match: re.Match) -> str:
        key = match.group(1)
        return context.get(key, match.group(0))

    return re.sub(r"\{\{(\w+)\}\}", _replacer, template)
