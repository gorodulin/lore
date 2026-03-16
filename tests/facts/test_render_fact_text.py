from lore.facts.render_fact_text import render_fact_text


def test_single_variable():
    result = render_fact_text("{{filepath}} is important", {"filepath": "src/app.py"})
    assert result == "src/app.py is important"


def test_multiple_variables():
    ctx = {"filepath": "src/app.py", "basename": "app", "ext": ".py"}
    result = render_fact_text("{{basename}} ({{ext}}) at {{filepath}}", ctx)
    assert result == "app (.py) at src/app.py"


def test_no_template():
    result = render_fact_text("Plain fact text", {"filepath": "src/app.py"})
    assert result == "Plain fact text"


def test_unknown_variable_left_as_is():
    result = render_fact_text("{{unknown}} stays", {"filepath": "src/app.py"})
    assert result == "{{unknown}} stays"


def test_adjacent_variables():
    ctx = {"basename": "app", "ext": ".py"}
    result = render_fact_text("{{basename}}{{ext}}", ctx)
    assert result == "app.py"


def test_empty_context():
    result = render_fact_text("{{filepath}} here", {})
    assert result == "{{filepath}} here"


def test_empty_template():
    result = render_fact_text("", {"filepath": "src/app.py"})
    assert result == ""
