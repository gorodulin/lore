import json

from lore.server.protocol.encode_fact_request import encode_fact_request


def test_encode_with_params():
    data = encode_fact_request("r1", "find_facts", {"file_path": "src/app.py"})
    msg = json.loads(data)
    assert msg["id"] == "r1"
    assert msg["method"] == "find_facts"
    assert msg["params"]["file_path"] == "src/app.py"
    assert data.endswith(b"\n")


def test_encode_without_params():
    data = encode_fact_request("r2", "ping")
    msg = json.loads(data)
    assert msg["id"] == "r2"
    assert msg["method"] == "ping"
    assert "params" not in msg


def test_encode_with_project_root():
    data = encode_fact_request("r3", "find_facts", {"file_path": "x.py"}, project_root="/projects/app")
    msg = json.loads(data)
    assert msg["project_root"] == "/projects/app"
    assert msg["params"]["file_path"] == "x.py"


def test_encode_without_project_root():
    data = encode_fact_request("r4", "ping")
    msg = json.loads(data)
    assert "project_root" not in msg
