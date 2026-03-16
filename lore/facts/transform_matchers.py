from lore.facts.parse_matcher_string import parse_matcher_string
from lore.facts.build_matcher_string import build_matcher_string


def transform_matchers(matchers: list[str], transforms: dict) -> list[str]:
    """Transform matcher values by type, passing unmatched types through.

    Dispatches each matcher to a type-specific transform function.
    Matchers whose type has no entry in transforms, or whose transform
    returns None, are kept unchanged.

    Args:
        matchers: List of prefixed matcher strings (e.g., ["g:**/*.py", "r:import os"])
        transforms: Dict mapping matcher type to transform function.
            Each function takes a raw value and returns a transformed value,
            or None to keep the original matcher unchanged.

    Returns:
        List of matcher strings with transforms applied.

    Examples:
        >>> transform_matchers(
        ...     ["g:src/**/*.py", "r:import os"],
        ...     {"glob": lambda v: f"app/{v}"},
        ... )
        ['g:app/src/**/*.py', 'r:import os']
    """
    result = []
    for matcher in matchers:
        try:
            matcher_type, value = parse_matcher_string(matcher)
        except ValueError:
            result.append(matcher)
            continue

        transform_fn = transforms.get(matcher_type)
        if transform_fn is None:
            result.append(matcher)
            continue

        transformed = transform_fn(value)
        if transformed is None:
            result.append(matcher)
        else:
            result.append(build_matcher_string(matcher_type, transformed))

    return result
