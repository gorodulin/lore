import json

import pytest

from lore.server.protocol.decode_fact_request import decode_fact_request


def test_decode_valid_request():
    data = json.dumps({"id": "r1", "method": "ping", "params": {"x": 1}}).encode()
    req_id, method, params, project_root = decode_fact_request(data)
    assert req_id == "r1"
    assert method == "ping"
    assert params == {"x": 1}
    assert project_root is None


def test_decode_missing_params_defaults_to_empty():
    data = json.dumps({"id": "r1", "method": "ping"}).encode()
    _, _, params, _ = decode_fact_request(data)
    assert params == {}


def test_decode_with_project_root():
    data = json.dumps({"id": "r1", "method": "find_facts", "project_root": "/projects/app"}).encode()
    _, _, _, project_root = decode_fact_request(data)
    assert project_root == "/projects/app"


def test_decode_invalid_project_root():
    data = json.dumps({"id": "r1", "method": "ping", "project_root": 123}).encode()
    with pytest.raises(ValueError, match="project_root"):
        decode_fact_request(data)


def test_decode_invalid_json():
    with pytest.raises(ValueError, match="Invalid JSON"):
        decode_fact_request(b"not json")


def test_decode_missing_id():
    data = json.dumps({"method": "ping"}).encode()
    with pytest.raises(ValueError, match="'id'"):
        decode_fact_request(data)


def test_decode_missing_method():
    data = json.dumps({"id": "r1"}).encode()
    with pytest.raises(ValueError, match="'method'"):
        decode_fact_request(data)


def test_decode_non_object():
    data = json.dumps([1, 2, 3]).encode()
    with pytest.raises(ValueError, match="JSON object"):
        decode_fact_request(data)
