import json


def encode_fact_response(request_id: str, result: dict | None = None, error: dict | None = None) -> bytes:
    """Encode a fact response as newline-delimited JSON bytes."""
    msg = {"id": request_id}
    if error is not None:
        msg["error"] = error
    elif result is not None:
        msg["result"] = result
    else:
        msg["result"] = {}
    return json.dumps(msg, separators=(",", ":")).encode("utf-8") + b"\n"
