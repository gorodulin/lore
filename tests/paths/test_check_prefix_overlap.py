from lore.paths.check_prefix_overlap import check_prefix_overlap


def test_identical_prefixes():
    assert check_prefix_overlap(["src", "api"], ["src", "api"]) is True


def test_one_is_ancestor():
    assert check_prefix_overlap(["src"], ["src", "api"]) is True


def test_one_is_descendant():
    assert check_prefix_overlap(["src", "api"], ["src"]) is True


def test_divergent_prefixes():
    assert check_prefix_overlap(["src", "vendor"], ["src", "api"]) is False


def test_completely_different():
    assert check_prefix_overlap(["lib"], ["src"]) is False


def test_empty_first_overlaps_everything():
    assert check_prefix_overlap([], ["src", "api"]) is True


def test_empty_second_overlaps_everything():
    assert check_prefix_overlap(["src"], []) is True


def test_both_empty():
    assert check_prefix_overlap([], []) is True
