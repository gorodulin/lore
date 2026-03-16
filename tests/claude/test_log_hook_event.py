import json

from lore.claude.log_hook_event import log_hook_event


def test_creates_log_file(tmp_path):
    log_path = str(tmp_path / "logs" / "hook_events.jsonl")
    event = {"hook_event_name": "SessionStart"}

    log_hook_event(event, project_root=str(tmp_path), log_path=log_path)

    assert (tmp_path / "logs" / "hook_events.jsonl").exists()


def test_appends_jsonl_lines(tmp_path):
    log_path = str(tmp_path / "events.jsonl")

    log_hook_event({"hook_event_name": "A"}, project_root=str(tmp_path), log_path=log_path)
    log_hook_event({"hook_event_name": "B"}, project_root=str(tmp_path), log_path=log_path)

    lines = (tmp_path / "events.jsonl").read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["event"]["hook_event_name"] == "A"
    assert json.loads(lines[1])["event"]["hook_event_name"] == "B"


def test_adds_timestamp(tmp_path):
    log_path = str(tmp_path / "events.jsonl")

    log_hook_event({"hook_event_name": "X"}, project_root=str(tmp_path), log_path=log_path)

    entry = json.loads((tmp_path / "events.jsonl").read_text().strip())
    assert "ts" in entry
    # ISO 8601 UTC timestamp contains "T" and ends with "+00:00"
    assert "T" in entry["ts"]


def test_empty_log_path_is_noop(tmp_path):
    # Should not raise or create any file
    log_hook_event({"hook_event_name": "X"}, project_root=str(tmp_path), log_path="")


def test_creates_parent_directories(tmp_path):
    log_path = str(tmp_path / "a" / "b" / "c" / "events.jsonl")

    log_hook_event({"hook_event_name": "X"}, project_root=str(tmp_path), log_path=log_path)

    assert (tmp_path / "a" / "b" / "c" / "events.jsonl").exists()
