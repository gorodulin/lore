from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet


class TestFact:
    def test_minimal_construction(self):
        incl = MatcherSet()
        fact = Fact(fact_id="test_id", text="Test fact", incl=incl)
        assert fact.fact_id == "test_id"
        assert fact.text == "Test fact"
        assert fact.incl == incl
        assert fact.skip == MatcherSet()
        assert fact.tags == ()

    def test_with_all_fields(self):
        incl = MatcherSet()
        skip = MatcherSet()
        fact = Fact(
            fact_id="test_id",
            text="Test fact",
            incl=incl,
            skip=skip,
            tags=("tag1", "tag2"),
        )
        assert fact.tags == ("tag1", "tag2")
        assert fact.skip == skip

    def test_frozen(self):
        fact = Fact(fact_id="id", text="text", incl=MatcherSet())
        try:
            fact.text = "changed"
            assert False, "Should raise FrozenInstanceError"
        except AttributeError:
            pass

    def test_equality(self):
        incl = MatcherSet()
        f1 = Fact(fact_id="id", text="text", incl=incl)
        f2 = Fact(fact_id="id", text="text", incl=incl)
        assert f1 == f2
