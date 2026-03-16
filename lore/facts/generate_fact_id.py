import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def generate_fact_id() -> str:
    """Generate a random 10-character alphanumeric fact ID.

    Uses cryptographically secure randomness via secrets.choice.

    Returns:
        A 10-character string of [a-zA-Z0-9].
    """
    return "".join(secrets.choice(_ALPHABET) for _ in range(10))
