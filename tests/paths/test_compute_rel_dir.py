import os

from lore.paths.compute_rel_dir import compute_rel_dir


def test_root_level_returns_empty(tmp_path):
    facts_path = os.path.join(str(tmp_path), ".lore.json")
    assert compute_rel_dir(facts_path, str(tmp_path)) == ""


def test_subdir_returns_relative(tmp_path):
    facts_path = os.path.join(str(tmp_path), "src", ".lore.json")
    assert compute_rel_dir(facts_path, str(tmp_path)) == "src"


def test_nested_subdir(tmp_path):
    facts_path = os.path.join(str(tmp_path), "src", "lib", ".lore.json")
    assert compute_rel_dir(facts_path, str(tmp_path)) == "src/lib"
