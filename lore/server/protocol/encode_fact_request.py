import json


def encode_fact_request(request_id: str, method: str, params: dict | None = None, project_root: str | None = None) -> bytes:
    """Encode a fact request as newline-delimited JSON bytes."""
    msg = {"id": request_id, "method": method}
    if project_root is not None:
        msg["project_root"] = project_root
    if params is not None:
        msg["params"] = params
    return json.dumps(msg, separators=(",", ":")).encode("utf-8") + b"\n"
