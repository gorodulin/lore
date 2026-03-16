import json


def decode_fact_response(data: bytes) -> tuple[str, dict | None, dict | None]:
    """Decode newline-delimited JSON bytes into (request_id, result_or_None, error_or_None).

    Raises ValueError on malformed input.
    """
    try:
        msg = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    if not isinstance(msg, dict):
        raise ValueError("Response must be a JSON object")

    request_id = msg.get("id")
    if not isinstance(request_id, str):
        raise ValueError("Response must have a string 'id' field")

    result = msg.get("result")
    error = msg.get("error")

    return (request_id, result, error)
