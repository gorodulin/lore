def check_prefix_overlap(prefix_a: list[str], prefix_b: list[str]) -> bool:
    """Check if two literal path prefixes could match overlapping paths.

    Returns True if one prefix is an ancestor of the other or they are
    identical, meaning patterns with these prefixes could affect the same
    files. Empty prefixes (from patterns starting with **) overlap everything.
    """
    if not prefix_a or not prefix_b:
        return True

    min_len = min(len(prefix_a), len(prefix_b))
    for i in range(min_len):
        if prefix_a[i] != prefix_b[i]:
            return False

    return True
