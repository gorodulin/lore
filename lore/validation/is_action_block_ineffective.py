def is_action_block_ineffective(fact: dict) -> bool:
    """Check if a fact's action:block tag can never take effect.

    A fact with action:block is ineffective when it only fires on
    non-blockable events. Specifically: tagged hook:read but missing
    both hook:edit and hook:write. PostToolUse/Read cannot block
    because the tool already ran.

    Facts with no hook:* tags fire on all events (including PreToolUse),
    so action:block is effective for those.

    Args:
        fact: Fact dict with optional 'tags' list

    Returns:
        True if action:block is present but can never block.
    """
    tags = fact.get("tags", [])

    if "action:block" not in tags:
        return False

    hook_tags = [t for t in tags if t.startswith("hook:")]

    if not hook_tags:
        return False

    has_blockable = "hook:edit" in hook_tags or "hook:write" in hook_tags
    return not has_blockable
