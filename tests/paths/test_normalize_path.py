from lore.paths.normalize_path import normalize_path


def test_normalize_simple_path():
    assert normalize_path("src/utils/file.ts") == "src/utils/file.ts"


def test_normalize_backslashes():
    assert normalize_path("src\\utils\\file.ts") == "src/utils/file.ts"


def test_normalize_leading_dot_slash():
    assert normalize_path("./src/file.ts") == "src/file.ts"


def test_normalize_multiple_leading_dot_slash():
    assert normalize_path("././src/file.ts") == "src/file.ts"


def test_normalize_double_slashes():
    assert normalize_path("src//utils//file.ts") == "src/utils/file.ts"


def test_normalize_trailing_slash_preserved():
    assert normalize_path("src/utils/") == "src/utils/"


def test_normalize_assume_dir_true():
    assert normalize_path("src/utils", assume_dir=True) == "src/utils/"


def test_normalize_assume_dir_false():
    assert normalize_path("src/utils/", assume_dir=False) == "src/utils"


def test_normalize_empty():
    assert normalize_path("") == "."


def test_normalize_dot():
    assert normalize_path(".") == "."


def test_normalize_dot_slash():
    assert normalize_path("./") == "."


def test_normalize_unicode_nfc():
    # é composed vs decomposed
    composed = "caf\u00e9"
    decomposed = "cafe\u0301"
    assert normalize_path(composed) == normalize_path(decomposed)
