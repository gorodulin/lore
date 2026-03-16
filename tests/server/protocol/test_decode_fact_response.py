import json

import pytest

from lore.server.protocol.decode_fact_response import decode_fact_response


def test_decode_result_response():
    data = json.dumps({"id": "r1", "result": {"status": "ok"}}).encode()
    req_id, result, error = decode_fact_response(data)
    assert req_id == "r1"
    assert result == {"status": "ok"}
    assert error is None


def test_decode_error_response():
    data = json.dumps({"id": "r1", "error": {"code": "bad", "message": "nope"}}).encode()
    req_id, result, error = decode_fact_response(data)
    assert req_id == "r1"
    assert result is None
    assert error["code"] == "bad"


def test_decode_invalid_json():
    with pytest.raises(ValueError, match="Invalid JSON"):
        decode_fact_response(b"broken")


def test_decode_missing_id():
    data = json.dumps({"result": {}}).encode()
    with pytest.raises(ValueError, match="'id'"):
        decode_fact_response(data)


def test_round_trip_with_encode():
    from lore.server.protocol.encode_fact_response import encode_fact_response
    encoded = encode_fact_response("r5", result={"x": 42})
    req_id, result, error = decode_fact_response(encoded.strip())
    assert req_id == "r5"
    assert result == {"x": 42}
    assert error is None
