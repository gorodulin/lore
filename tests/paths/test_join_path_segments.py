from lore.paths.join_path_segments import join_path_segments


def test_join_basic():
    assert join_path_segments(["src", "utils"]) == "src/utils"


def test_join_single():
    assert join_path_segments(["src"]) == "src"


def test_join_empty():
    assert join_path_segments([]) == "."


def test_join_trailing_slash():
    assert join_path_segments(["src", "utils"], trailing_slash=True) == "src/utils/"


def test_join_trailing_slash_single():
    assert join_path_segments(["src"], trailing_slash=True) == "src/"


def test_join_trailing_slash_empty():
    assert join_path_segments([], trailing_slash=False) == "."


def test_join_deep_path():
    assert join_path_segments(["a", "b", "c", "d"]) == "a/b/c/d"
