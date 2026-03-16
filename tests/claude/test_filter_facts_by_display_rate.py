from lore.claude.filter_facts_by_display_rate import filter_facts_by_display_rate


def test_rate_one_shows_all(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    rendered = {"a": "Fact A", "b": "Fact B"}
    result = filter_facts_by_display_rate(rendered, "sess1", 1, str(tmp_path))
    assert result == rendered


def test_rate_five_first_shown(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    rendered = {"a": "Fact A"}
    result = filter_facts_by_display_rate(rendered, "test-sess", 5, str(tmp_path))
    assert result == {"a": "Fact A"}


def test_rate_five_second_through_fifth_suppressed(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    rendered = {"a": "Fact A"}
    root = str(tmp_path)
    # 1st call - shown
    filter_facts_by_display_rate(rendered, "test-sess", 5, root)
    # 2nd through 5th - suppressed
    for _ in range(4):
        result = filter_facts_by_display_rate(rendered, "test-sess", 5, root)
        assert result == {}


def test_rate_five_sixth_shown(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    rendered = {"a": "Fact A"}
    root = str(tmp_path)
    for _ in range(5):
        filter_facts_by_display_rate(rendered, "test-sess", 5, root)
    # 6th call - shown again
    result = filter_facts_by_display_rate(rendered, "test-sess", 5, root)
    assert result == {"a": "Fact A"}


def test_empty_session_id_shows_all(tmp_path):
    rendered = {"a": "Fact A"}
    result = filter_facts_by_display_rate(rendered, "", 5, str(tmp_path))
    assert result == rendered


def test_rate_zero_shows_all(tmp_path):
    rendered = {"a": "Fact A"}
    result = filter_facts_by_display_rate(rendered, "sess1", 0, str(tmp_path))
    assert result == rendered


def test_different_texts_tracked_independently(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    root = str(tmp_path)
    # First call with text A - shown
    result = filter_facts_by_display_rate({"a": "Text A"}, "test-sess", 5, root)
    assert "a" in result
    # First call with text B - also shown (different text)
    result = filter_facts_by_display_rate({"b": "Text B"}, "test-sess", 5, root)
    assert "b" in result


def test_multiple_facts_all_tracked(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    root = str(tmp_path)
    rendered = {"a": "Fact A", "b": "Fact B", "c": "Fact C"}
    # 1st call - all shown
    result = filter_facts_by_display_rate(rendered, "test-sess", 5, root)
    assert result == rendered
    # 2nd call - all suppressed
    result = filter_facts_by_display_rate(rendered, "test-sess", 5, root)
    assert result == {}


def test_state_persists_to_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    filter_facts_by_display_rate({"a": "Fact A"}, "test-sess", 5, str(tmp_path))
    state_path = tmp_path / "display_rate_test-sess.json"
    assert state_path.exists()


def test_corrupt_state_file_recovery(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    (tmp_path / "display_rate_test-sess.json").write_text("NOT JSON")
    # Should recover and treat as first occurrence
    result = filter_facts_by_display_rate({"a": "Fact A"}, "test-sess", 5, str(tmp_path))
    assert result == {"a": "Fact A"}
