import json


def decode_fact_request(data: bytes) -> tuple[str, str, dict, str | None]:
    """Decode newline-delimited JSON bytes into (request_id, method, params, project_root).

    Raises ValueError on malformed input.
    """
    try:
        msg = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    if not isinstance(msg, dict):
        raise ValueError("Request must be a JSON object")

    request_id = msg.get("id")
    if not isinstance(request_id, str):
        raise ValueError("Request must have a string 'id' field")

    method = msg.get("method")
    if not isinstance(method, str):
        raise ValueError("Request must have a string 'method' field")

    params = msg.get("params", {})
    if not isinstance(params, dict):
        raise ValueError("Request 'params' must be an object")

    project_root = msg.get("project_root")
    if project_root is not None and not isinstance(project_root, str):
        raise ValueError("Request 'project_root' must be a string")

    return (request_id, method, params, project_root)
