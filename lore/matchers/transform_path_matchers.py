from collections.abc import Callable

from lore.matchers.transform_matchers import transform_matchers


def transform_path_matchers(matchers: list[str], transform: Callable[[str], str | None]) -> list[str]:
    """Apply a transform to every path matcher's raw value, passing others through.

    Thin wrapper over :func:`transform_matchers` that encapsulates the
    matcher-type name for the path target (``"path"``). Callers get to
    stay agnostic of the internal matcher-type vocabulary: they express
    intent ("transform path matcher values") without hardcoding the
    schema key.

    Args:
        matchers: List of prefixed matcher strings (e.g.
            ``["p:**/*.py", "c:import os"]``).
        transform: Function applied to the raw glob value of each path
            matcher. Return ``None`` to leave a matcher unchanged.
            Non-path matchers are always passed through.

    Returns:
        List of matcher strings with the transform applied to path
        matchers only.

    Examples:
        >>> transform_path_matchers(
        ...     ["p:src/**/*.py", "c:import os"],
        ...     lambda v: f"app/{v}",
        ... )
        ['p:app/src/**/*.py', 'c:import os']
    """
    return transform_matchers(matchers, {"path": transform})
