from lore.paths.split_path_segments import split_path_segments


def test_split_simple():
    assert split_path_segments("src/utils/file.ts") == ["src", "utils", "file.ts"]


def test_split_single_segment():
    assert split_path_segments("file.ts") == ["file.ts"]


def test_split_with_trailing_slash():
    assert split_path_segments("src/utils/") == ["src", "utils"]


def test_split_empty():
    assert split_path_segments("") == []


def test_split_dot():
    assert split_path_segments(".") == []


def test_split_deep_path():
    assert split_path_segments("a/b/c/d/e") == ["a", "b", "c", "d", "e"]
