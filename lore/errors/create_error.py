def create_error(code: str, message: str, **context) -> dict:
    """Create a structured, serializable error with optional context.

    Args:
        code: Error code from error_codes.py
        message: Human-readable error message
        **context: Additional context fields (e.g., fact_id, pattern_id, matcher)

    Returns:
        A dict with 'code', 'message', and any additional context fields
    """
    err = {"code": code, "message": message}
    for key, value in context.items():
        if value is not None:
            err[key] = value
    return err
