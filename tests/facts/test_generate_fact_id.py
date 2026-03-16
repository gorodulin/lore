import re

from lore.facts.generate_fact_id import generate_fact_id


def test_generate_fact_id_length():
    result = generate_fact_id()
    assert len(result) == 10


def test_generate_fact_id_alphanumeric():
    result = generate_fact_id()
    assert re.fullmatch(r"[a-zA-Z0-9]{10}", result)


def test_generate_fact_id_unique():
    ids = {generate_fact_id() for _ in range(100)}
    # With 62^10 possibilities, 100 IDs should all be unique
    assert len(ids) == 100
