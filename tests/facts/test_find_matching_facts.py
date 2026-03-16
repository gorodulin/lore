from lore.facts.compile_fact_matchers import compile_fact_matchers
from lore.facts.find_matching_facts import find_matching_facts


class TestFindMatchingFacts:
    def test_single_matching_fact(self):
        compiled = {
            "f1": compile_fact_matchers({"fact": "JS", "incl": ["g:**/*.js"]}),
            "f2": compile_fact_matchers({"fact": "TS", "incl": ["g:**/*.ts"]}),
        }

        result = find_matching_facts(compiled, "src/app.js")
        assert result == ["f1"]

    def test_multiple_matching_facts(self):
        compiled = {
            "f1": compile_fact_matchers({"fact": "All source", "incl": ["g:src/**/*"]}),
            "f2": compile_fact_matchers({"fact": "JS files", "incl": ["g:**/*.js"]}),
            "f3": compile_fact_matchers({"fact": "TS files", "incl": ["g:**/*.ts"]}),
        }

        result = find_matching_facts(compiled, "src/app.js")
        assert "f1" in result
        assert "f2" in result
        assert "f3" not in result

    def test_no_matching_facts(self):
        compiled = {
            "f1": compile_fact_matchers({"fact": "JS", "incl": ["g:**/*.js"]}),
            "f2": compile_fact_matchers({"fact": "TS", "incl": ["g:**/*.ts"]}),
        }

        result = find_matching_facts(compiled, "src/app.py")
        assert result == []

    def test_empty_compiled_facts(self):
        result = find_matching_facts({}, "src/app.js")
        assert result == []

    def test_exclusions_respected(self):
        compiled = {
            "f1": compile_fact_matchers({
                "fact": "JS except vendor",
                "incl": ["g:**/*.js"],
                "skip": ["g:vendor/**"],  # exclude from root
            }),
        }

        assert find_matching_facts(compiled, "src/app.js") == ["f1"]
        assert find_matching_facts(compiled, "vendor/lib.js") == []

    def test_facts_evaluated_independently(self):
        # Two facts with different exclusions
        compiled = {
            "f1": compile_fact_matchers({
                "fact": "JS except vendor",
                "incl": ["g:**/*.js"],
                "skip": ["g:vendor/**"],  # exclude from root
            }),
            "f2": compile_fact_matchers({
                "fact": "JS except node_modules",
                "incl": ["g:**/*.js"],
                "skip": ["g:node_modules/**"],  # exclude from root
            }),
        }

        # vendor/lib.js matches f2 but not f1
        result = find_matching_facts(compiled, "vendor/lib.js")
        assert result == ["f2"]

        # node_modules/pkg.js matches f1 but not f2
        result = find_matching_facts(compiled, "node_modules/pkg.js")
        assert result == ["f1"]

    def test_content_filtering(self):
        compiled = {
            "f1": compile_fact_matchers({
                "fact": "PY with raise",
                "incl": ["g:**/*.py", "r:raise\\s+"],
            }),
            "f2": compile_fact_matchers({
                "fact": "All PY",
                "incl": ["g:**/*.py"],
            }),
        }

        # With matching content: both match
        result = find_matching_facts(compiled, "src/app.py", content="raise ValueError")
        assert "f1" in result
        assert "f2" in result

        # With non-matching content: only glob-only fact matches
        result = find_matching_facts(compiled, "src/app.py", content="return 42")
        assert "f1" not in result
        assert "f2" in result

    def test_directory_path(self):
        compiled = {
            "f1": compile_fact_matchers({"fact": "Src dirs", "incl": ["g:src/**/"]}),
            "f2": compile_fact_matchers({"fact": "All files", "incl": ["g:**/*"]}),
        }

        result = find_matching_facts(compiled, "src/api/")
        assert "f1" in result
