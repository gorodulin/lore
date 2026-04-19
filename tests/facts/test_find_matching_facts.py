from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.find_matching_facts import find_matching_facts


class TestFindMatchingFacts:
    def test_single_matching_fact(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "JS", "incl": ["p:**/*.js"]}),
            "f2": build_fact_from_dict("f2", {"fact": "TS", "incl": ["p:**/*.ts"]}),
        }

        result = find_matching_facts(facts, "src/app.js")
        assert result == ["f1"]

    def test_multiple_matching_facts(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "All source", "incl": ["p:src/**/*"]}),
            "f2": build_fact_from_dict("f2", {"fact": "JS files", "incl": ["p:**/*.js"]}),
            "f3": build_fact_from_dict("f3", {"fact": "TS files", "incl": ["p:**/*.ts"]}),
        }

        result = find_matching_facts(facts, "src/app.js")
        assert "f1" in result
        assert "f2" in result
        assert "f3" not in result

    def test_no_matching_facts(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "JS", "incl": ["p:**/*.js"]}),
            "f2": build_fact_from_dict("f2", {"fact": "TS", "incl": ["p:**/*.ts"]}),
        }

        result = find_matching_facts(facts, "src/app.py")
        assert result == []

    def test_empty_facts(self):
        result = find_matching_facts({}, "src/app.js")
        assert result == []

    def test_exclusions_respected(self):
        facts = {
            "f1": build_fact_from_dict("f1", {
                "fact": "JS except vendor",
                "incl": ["p:**/*.js"],
                "skip": ["p:vendor/**"],
            }),
        }

        assert find_matching_facts(facts, "src/app.js") == ["f1"]
        assert find_matching_facts(facts, "vendor/lib.js") == []

    def test_facts_evaluated_independently(self):
        facts = {
            "f1": build_fact_from_dict("f1", {
                "fact": "JS except vendor",
                "incl": ["p:**/*.js"],
                "skip": ["p:vendor/**"],
            }),
            "f2": build_fact_from_dict("f2", {
                "fact": "JS except node_modules",
                "incl": ["p:**/*.js"],
                "skip": ["p:node_modules/**"],
            }),
        }

        result = find_matching_facts(facts, "vendor/lib.js")
        assert result == ["f2"]

        result = find_matching_facts(facts, "node_modules/pkg.js")
        assert result == ["f1"]

    def test_content_filtering(self):
        facts = {
            "f1": build_fact_from_dict("f1", {
                "fact": "PY with raise",
                "incl": ["p:**/*.py", "c:raise\\s+"],
            }),
            "f2": build_fact_from_dict("f2", {
                "fact": "All PY",
                "incl": ["p:**/*.py"],
            }),
        }

        result = find_matching_facts(facts, "src/app.py", content="raise ValueError")
        assert "f1" in result
        assert "f2" in result

        result = find_matching_facts(facts, "src/app.py", content="return 42")
        assert "f1" not in result
        assert "f2" in result

    def test_directory_path(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "Src dirs", "incl": ["p:src/**/"]}),
            "f2": build_fact_from_dict("f2", {"fact": "All files", "incl": ["p:**/*"]}),
        }

        result = find_matching_facts(facts, "src/api/")
        assert "f1" in result
