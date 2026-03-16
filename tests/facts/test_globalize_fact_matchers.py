import os

from lore.facts.globalize_fact_matchers import globalize_fact_matchers


def test_root_level_fact_unchanged(tmp_path):
    """Facts at project root keep their patterns as-is."""
    file_path = os.path.join(str(tmp_path), ".lore.json")
    disk_result = {
        "fact_id": "f1",
        "file_path": file_path,
        "fact": {"fact": "test", "incl": ["g:**/*.py"]},
    }

    out = globalize_fact_matchers(disk_result, str(tmp_path))

    assert out["fact_id"] == "f1"
    assert out["file_path"] == file_path
    assert out["incl"] == ["g:**/*.py"]
    assert out["fact"] == "test"


def test_subdir_fact_globalized(tmp_path):
    """Facts in a subdirectory get their glob patterns prefixed."""
    file_path = os.path.join(str(tmp_path), "src", ".lore.json")
    disk_result = {
        "fact_id": "f2",
        "file_path": file_path,
        "fact": {"fact": "use types", "incl": ["g:**/*.ts"]},
    }

    out = globalize_fact_matchers(disk_result, str(tmp_path))

    assert out["incl"] == ["g:src/**/*.ts"]


def test_skip_patterns_globalized(tmp_path):
    """Skip patterns are also prefixed with the rel_dir."""
    file_path = os.path.join(str(tmp_path), "lib", ".lore.json")
    disk_result = {
        "fact_id": "f3",
        "file_path": file_path,
        "fact": {
            "fact": "no vendor",
            "incl": ["g:**/*.py"],
            "skip": ["g:vendor/**"],
        },
    }

    out = globalize_fact_matchers(disk_result, str(tmp_path))

    assert out["incl"] == ["g:lib/**/*.py"]
    assert out["skip"] == ["g:lib/vendor/**"]


def test_tags_preserved(tmp_path):
    """Tags pass through unchanged."""
    file_path = os.path.join(str(tmp_path), ".lore.json")
    disk_result = {
        "fact_id": "f4",
        "file_path": file_path,
        "fact": {
            "fact": "tagged",
            "incl": ["g:**/*.py"],
            "tags": ["hook:read"],
        },
    }

    out = globalize_fact_matchers(disk_result, str(tmp_path))

    assert out["tags"] == ["hook:read"]


def test_regex_pattern_unchanged(tmp_path):
    """Regex patterns pass through - only glob patterns get prefixed."""
    file_path = os.path.join(str(tmp_path), "sub", ".lore.json")
    disk_result = {
        "fact_id": "f5",
        "file_path": file_path,
        "fact": {"fact": "check imports", "incl": ["g:**/*.py", "r:import os"]},
    }

    out = globalize_fact_matchers(disk_result, str(tmp_path))

    assert "g:sub/**/*.py" in out["incl"]
    assert "r:import os" in out["incl"]
