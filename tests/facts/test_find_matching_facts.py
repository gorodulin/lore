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

    def test_tools_filtering(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "Git push", "incl": ["t:git push"]}),
            "f2": build_fact_from_dict("f2", {"fact": "Kubectl", "incl": ["t:kubectl"]}),
        }

        result = find_matching_facts(facts, "", tools=("git push",))
        assert result == ["f1"]

        result = find_matching_facts(facts, "", tools=("kubectl apply",))
        assert result == ["f2"]

    def test_tools_none_filters_out_tool_facts(self):
        facts = {
            "f1": build_fact_from_dict("f1", {"fact": "Git push", "incl": ["t:git push"]}),
            "f2": build_fact_from_dict("f2", {"fact": "All PY", "incl": ["p:**/*.py"]}),
        }

        # File event (no tools): t: fact must not fire; p: fact must.
        result = find_matching_facts(facts, "src/app.py", tools=None)
        assert "f1" not in result
        assert "f2" in result

    def test_endpoints_filtering(self):
        facts = {
            "prod": build_fact_from_dict("prod", {"fact": "Prod", "incl": ["e:\\.prod\\."]}),
            "staging": build_fact_from_dict("staging", {"fact": "Staging", "incl": ["e:\\.staging\\."]}),
        }

        result = find_matching_facts(facts, "", endpoints=("api.prod.com",))
        assert result == ["prod"]

        result = find_matching_facts(facts, "", endpoints=("api.staging.com",))
        assert result == ["staging"]

    def test_flags_filtering(self):
        facts = {
            "mut": build_fact_from_dict("mut", {"fact": "Mutates", "incl": ["f:mutates"]}),
            "net": build_fact_from_dict("net", {"fact": "Network", "incl": ["f:network"]}),
        }

        result = find_matching_facts(facts, "", flags=("mutates",))
        assert result == ["mut"]

        result = find_matching_facts(facts, "", flags=("network",))
        assert result == ["net"]

        result = find_matching_facts(facts, "", flags=("mutates", "network"))
        assert sorted(result) == ["mut", "net"]

    def test_affected_paths_filtering(self):
        facts = {
            "pay": build_fact_from_dict(
                "pay", {"fact": "Payments", "incl": ["p:src/payments/**"]}
            ),
            "api": build_fact_from_dict(
                "api", {"fact": "API", "incl": ["p:src/api/**"]}
            ),
        }

        result = find_matching_facts(
            facts, "", affected_paths=("src/payments/charge.py",)
        )
        assert result == ["pay"]

        result = find_matching_facts(
            facts, "", affected_paths=("src/api/users.py",)
        )
        assert result == ["api"]

    def test_affected_paths_does_not_leak_to_file_path_events(self):
        """File events (no affected_paths) fire p: against single path."""
        facts = {
            "pay": build_fact_from_dict(
                "pay", {"fact": "Payments", "incl": ["p:src/payments/**"]}
            ),
        }

        result = find_matching_facts(facts, "src/payments/charge.py")
        assert result == ["pay"]

        result = find_matching_facts(facts, "src/api/users.py")
        assert result == []
