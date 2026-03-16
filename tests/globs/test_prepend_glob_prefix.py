from lore.globs.prepend_glob_prefix import prepend_glob_prefix


def test_prepend_simple():
    assert prepend_glob_prefix("*.html", "app") == "app/*.html"


def test_prepend_globstar():
    assert prepend_glob_prefix("**/api.js", "app") == "app/**/api.js"


def test_prepend_literal():
    assert prepend_glob_prefix("src/file.ts", "app") == "app/src/file.ts"


def test_prepend_complex():
    assert prepend_glob_prefix("**/src/*.js", "app") == "app/**/src/*.js"


def test_prepend_empty():
    assert prepend_glob_prefix("*.js", "") == "*.js"


def test_prepend_dot():
    assert prepend_glob_prefix("*.js", ".") == "*.js"


def test_prepend_with_trailing_slash():
    # Trailing slash is normalized away
    assert prepend_glob_prefix("*.js", "app/") == "app/*.js"


def test_prepend_deep():
    assert prepend_glob_prefix("*.js", "app/frontend/src") == "app/frontend/src/*.js"
