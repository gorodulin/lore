import json

from lore.server.protocol.encode_fact_response import encode_fact_response


def test_encode_result():
    data = encode_fact_response("r1", result={"status": "ok"})
    msg = json.loads(data)
    assert msg["id"] == "r1"
    assert msg["result"] == {"status": "ok"}
    assert "error" not in msg
    assert data.endswith(b"\n")


def test_encode_error():
    data = encode_fact_response("r1", error={"code": "not_found", "message": "gone"})
    msg = json.loads(data)
    assert msg["id"] == "r1"
    assert msg["error"]["code"] == "not_found"
    assert "result" not in msg


def test_encode_empty_result_when_no_args():
    data = encode_fact_response("r1")
    msg = json.loads(data)
    assert msg["result"] == {}
