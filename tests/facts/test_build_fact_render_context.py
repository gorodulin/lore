from lore.facts.build_fact_render_context import build_fact_render_context


def test_relative_path():
    ctx = build_fact_render_context("lore/facts/locate_facts_by_id.py")
    assert ctx["filepath"] == "lore/facts/locate_facts_by_id.py"
    assert ctx["fullpath"] == "lore/facts/locate_facts_by_id.py"
    assert ctx["folder"] == "lore/facts/"
    assert ctx["filename"] == "locate_facts_by_id.py"
    assert ctx["ext"] == ".py"
    assert ctx["basename"] == "locate_facts_by_id"


def test_absolute_path_with_project_root():
    ctx = build_fact_render_context("/repo/src/app.py", project_root="/repo")
    assert ctx["filepath"] == "src/app.py"
    assert ctx["fullpath"] == "/repo/src/app.py"
    assert ctx["folder"] == "src/"
    assert ctx["filename"] == "app.py"
    assert ctx["ext"] == ".py"
    assert ctx["basename"] == "app"


def test_absolute_path_without_project_root():
    ctx = build_fact_render_context("/repo/src/app.py")
    assert ctx["filepath"] == "/repo/src/app.py"
    assert ctx["fullpath"] == "/repo/src/app.py"


def test_absolute_path_outside_project():
    ctx = build_fact_render_context("/other/app.py", project_root="/repo")
    assert ctx["filepath"] == "/other/app.py"
    assert ctx["fullpath"] == "/other/app.py"


def test_root_level_file():
    ctx = build_fact_render_context("README.md")
    assert ctx["filepath"] == "README.md"
    assert ctx["folder"] == ""
    assert ctx["filename"] == "README.md"
    assert ctx["ext"] == ".md"
    assert ctx["basename"] == "README"


def test_no_extension():
    ctx = build_fact_render_context("bin/manage_facts")
    assert ctx["folder"] == "bin/"
    assert ctx["filename"] == "manage_facts"
    assert ctx["ext"] == ""
    assert ctx["basename"] == "manage_facts"


def test_dotfile():
    ctx = build_fact_render_context("src/.gitignore")
    assert ctx["filename"] == ".gitignore"
    assert ctx["ext"] == ""
    assert ctx["basename"] == ".gitignore"


def test_multiple_dots():
    ctx = build_fact_render_context("lib/data.test.js")
    assert ctx["filename"] == "data.test.js"
    assert ctx["ext"] == ".js"
    assert ctx["basename"] == "data.test"
