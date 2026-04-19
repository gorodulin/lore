from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.evaluate_fact_for_path import evaluate_fact_for_path


def _build(raw: dict):
    return build_fact_from_dict("test", raw)


class TestEvaluateFactForPath:
    def test_matches_simple_glob(self):
        fact = _build({"fact": "JS files", "incl": ["p:**/*.js"]})
        assert evaluate_fact_for_path(fact, "src/app.js") is True

    def test_no_match_different_extension(self):
        fact = _build({"fact": "JS files", "incl": ["p:**/*.js"]})
        assert evaluate_fact_for_path(fact, "src/app.ts") is False

    def test_exclusion_prevents_match(self):
        fact = _build({
            "fact": "JS files except vendor",
            "incl": ["p:**/*.js"],
            "skip": ["p:vendor/*"],
        })
        assert evaluate_fact_for_path(fact, "src/app.js") is True
        assert evaluate_fact_for_path(fact, "vendor/lib.js") is False

    def test_exclusion_checked_first(self):
        fact = _build({
            "fact": "Test",
            "incl": ["p:**/*"],
            "skip": ["p:**/*.min.js"],
        })
        assert evaluate_fact_for_path(fact, "app.min.js") is False

    def test_multiple_incl_any_matches(self):
        fact = _build({
            "fact": "Frontend files",
            "incl": ["p:**/*.js", "p:**/*.ts", "p:**/*.css"],
        })
        assert evaluate_fact_for_path(fact, "src/app.js") is True
        assert evaluate_fact_for_path(fact, "src/app.ts") is True
        assert evaluate_fact_for_path(fact, "src/app.css") is True
        assert evaluate_fact_for_path(fact, "src/app.py") is False

    def test_multiple_skip_any_excludes(self):
        fact = _build({
            "fact": "JS files",
            "incl": ["p:**/*.js"],
            "skip": ["p:vendor/**", "p:node_modules/**"],
        })
        assert evaluate_fact_for_path(fact, "vendor/lib.js") is False
        assert evaluate_fact_for_path(fact, "node_modules/pkg/index.js") is False
        assert evaluate_fact_for_path(fact, "src/app.js") is True

    def test_directory_matching(self):
        fact = _build({"fact": "Source dirs", "incl": ["p:src/**/"]})
        assert evaluate_fact_for_path(fact, "src/api/") is True
        assert evaluate_fact_for_path(fact, "src/api/users.ts") is False

    def test_file_matching(self):
        fact = _build({"fact": "Config files", "incl": ["p:*.config.js"]})
        assert evaluate_fact_for_path(fact, "webpack.config.js") is True
        assert evaluate_fact_for_path(fact, "configs/") is False

    def test_empty_skip_no_exclusions(self):
        fact = _build({"fact": "All JS", "incl": ["p:**/*.js"]})
        assert evaluate_fact_for_path(fact, "any/path/file.js") is True

    def test_literal_path_match(self):
        fact = _build({"fact": "Specific file", "incl": ["p:src/main.ts"]})
        assert evaluate_fact_for_path(fact, "src/main.ts") is True
        assert evaluate_fact_for_path(fact, "src/other.ts") is False

    # --- Content regex matcher tests ---

    def test_glob_only_still_works_without_content(self):
        fact = _build({"fact": "JS files", "incl": ["p:**/*.js"]})
        assert evaluate_fact_for_path(fact, "src/app.js") is True
        assert evaluate_fact_for_path(fact, "src/app.js", content=None) is True

    def test_regex_only_incl_matches_content(self):
        fact = _build({"fact": "Raise usage", "incl": ["c:raise\\s+"]})
        assert evaluate_fact_for_path(fact, "any/path.py", content="raise ValueError") is True

    def test_regex_only_incl_no_content_match(self):
        fact = _build({"fact": "Raise usage", "incl": ["c:raise\\s+"]})
        assert evaluate_fact_for_path(fact, "any/path.py", content="return 42") is False

    def test_mixed_glob_and_regex_incl_both_must_match(self):
        fact = _build({"fact": "PY raise", "incl": ["p:**/*.py", "c:raise\\s+"]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="raise ValueError") is True
        assert evaluate_fact_for_path(fact, "src/app.py", content="return 42") is False
        assert evaluate_fact_for_path(fact, "src/app.js", content="raise ValueError") is False

    def test_content_none_with_regex_matchers_no_match(self):
        fact = _build({"fact": "Test", "incl": ["c:something"]})
        assert evaluate_fact_for_path(fact, "any/path.py", content=None) is False

    def test_skip_with_regex_content_exclusion(self):
        fact = _build({
            "fact": "All PY",
            "incl": ["p:**/*.py"],
            "skip": ["c:# generated"],
        })
        assert evaluate_fact_for_path(fact, "src/app.py", content="# generated file") is False
        assert evaluate_fact_for_path(fact, "src/app.py", content="normal code") is True

    def test_skip_with_mixed_glob_and_regex_and_logic(self):
        fact = _build({
            "fact": "All PY",
            "incl": ["p:**/*.py"],
            "skip": ["p:vendor/**", "c:# generated"],
        })
        # Skip requires both path AND content group to match
        assert evaluate_fact_for_path(fact, "vendor/lib.py", content="# generated") is False
        assert evaluate_fact_for_path(fact, "vendor/lib.py", content="normal") is True
        assert evaluate_fact_for_path(fact, "src/lib.py", content="# generated") is True

    # --- Description regex matcher tests (d:) ---

    def test_description_only_matches(self):
        fact = _build({"fact": "Deploys", "incl": ["d:(?i)deploy"]})
        assert evaluate_fact_for_path(fact, "", description="Deploy to production") is True

    def test_description_only_no_match(self):
        fact = _build({"fact": "Deploys", "incl": ["d:(?i)deploy"]})
        assert evaluate_fact_for_path(fact, "", description="Run tests") is False

    def test_description_none_with_description_regex_no_match(self):
        fact = _build({"fact": "Deploys", "incl": ["d:(?i)deploy"]})
        assert evaluate_fact_for_path(fact, "", description=None) is False

    def test_description_missing_on_file_event_means_no_match(self):
        # Decision 10: no source -> False when matchers of that target exist
        fact = _build({"fact": "Deploys", "incl": ["d:(?i)deploy"]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="anything") is False

    def test_description_combined_with_path_both_required(self):
        fact = _build({"fact": "Py deploys", "incl": ["p:**/*.py", "d:(?i)deploy"]})
        assert evaluate_fact_for_path(fact, "src/app.py", description="Deploy") is True
        assert evaluate_fact_for_path(fact, "src/app.py", description="Test") is False
        assert evaluate_fact_for_path(fact, "src/app.js", description="Deploy") is False

    def test_multiple_description_regexes_or(self):
        fact = _build({"fact": "Install/remove", "incl": ["d:(?i)install", "d:(?i)remove"]})
        assert evaluate_fact_for_path(fact, "", description="Install deps") is True
        assert evaluate_fact_for_path(fact, "", description="Remove old files") is True
        assert evaluate_fact_for_path(fact, "", description="Run tests") is False

    def test_skip_description_excludes(self):
        fact = _build({
            "fact": "All bash",
            "incl": ["d:.*"],
            "skip": ["d:(?i)dry-run"],
        })
        assert evaluate_fact_for_path(fact, "", description="kubectl apply") is True
        assert evaluate_fact_for_path(fact, "", description="kubectl apply --dry-run") is False

    # --- Command regex matcher tests (x:) ---

    def test_command_only_matches(self):
        fact = _build({"fact": "rm -rf", "incl": ["x:rm -rf"]})
        assert evaluate_fact_for_path(fact, "", command="rm -rf /tmp/cache") is True

    def test_command_only_no_match(self):
        fact = _build({"fact": "rm -rf", "incl": ["x:rm -rf"]})
        assert evaluate_fact_for_path(fact, "", command="ls -la") is False

    def test_command_none_with_command_regex_no_match(self):
        fact = _build({"fact": "rm -rf", "incl": ["x:rm -rf"]})
        assert evaluate_fact_for_path(fact, "", command=None) is False

    def test_command_missing_on_file_event_means_no_match(self):
        # Decision 10: no source -> False when matchers of that target exist
        fact = _build({"fact": "rm -rf", "incl": ["x:rm -rf"]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="anything") is False

    def test_command_combined_with_description(self):
        fact = _build({
            "fact": "Dangerous delete",
            "incl": ["d:(?i)delete", "x:rm -rf"],
        })
        assert evaluate_fact_for_path(
            fact, "", description="Delete cache", command="rm -rf cache/"
        ) is True
        assert evaluate_fact_for_path(
            fact, "", description="Delete cache", command="ls cache/"
        ) is False
        assert evaluate_fact_for_path(
            fact, "", description="List files", command="rm -rf cache/"
        ) is False

    def test_multiple_command_regexes_or(self):
        fact = _build({"fact": "Dangerous", "incl": ["x:rm -rf", "x:\\|\\s*sh"]})
        assert evaluate_fact_for_path(fact, "", command="rm -rf /") is True
        assert evaluate_fact_for_path(fact, "", command="curl foo | sh") is True
        assert evaluate_fact_for_path(fact, "", command="ls -la") is False

    def test_skip_command_excludes(self):
        fact = _build({
            "fact": "All rm",
            "incl": ["x:rm"],
            "skip": ["x:rm -i"],
        })
        assert evaluate_fact_for_path(fact, "", command="rm -rf cache/") is True
        assert evaluate_fact_for_path(fact, "", command="rm -i old.txt") is False

    # --- Tool regex matcher tests (t:) — per-item against meta.tools ---

    def test_tool_only_single_entry_match(self):
        fact = _build({"fact": "Git push", "incl": ["t:git push"]})
        assert evaluate_fact_for_path(fact, "", tools=("git push",)) is True

    def test_tool_only_matches_among_multiple_entries(self):
        fact = _build({"fact": "Git push", "incl": ["t:git push"]})
        assert evaluate_fact_for_path(fact, "", tools=("echo", "git push", "ls")) is True

    def test_tool_no_match_different_entry(self):
        fact = _build({"fact": "Git push", "incl": ["t:git push"]})
        assert evaluate_fact_for_path(fact, "", tools=("git commit",)) is False

    def test_tool_none_means_no_source(self):
        # Decision 10: tools=None on non-Bash events → False.
        fact = _build({"fact": "Git push", "incl": ["t:git push"]})
        assert evaluate_fact_for_path(fact, "", tools=None) is False

    def test_tool_empty_tuple_means_nothing_to_match(self):
        # Valid META for a trivial command: tools=() → no tool can satisfy t:.
        fact = _build({"fact": "Any tool", "incl": ["t:.*"]})
        assert evaluate_fact_for_path(fact, "", tools=()) is False

    def test_tool_substring_regex_matches_entry(self):
        # Decision 7: regex per-entry; substring search is the documented behavior.
        fact = _build({"fact": "Push", "incl": ["t:push"]})
        assert evaluate_fact_for_path(fact, "", tools=("git push",)) is True

    def test_tool_regex_alternation_matches_any(self):
        fact = _build({"fact": "k8s/helm", "incl": ["t:kubectl|helm"]})
        assert evaluate_fact_for_path(fact, "", tools=("helm",)) is True
        assert evaluate_fact_for_path(fact, "", tools=("kubectl apply",)) is True
        assert evaluate_fact_for_path(fact, "", tools=("docker",)) is False

    def test_multiple_tool_regexes_or(self):
        fact = _build({"fact": "Destructive", "incl": ["t:git push", "t:kubectl apply"]})
        assert evaluate_fact_for_path(fact, "", tools=("git push",)) is True
        assert evaluate_fact_for_path(fact, "", tools=("kubectl apply",)) is True
        assert evaluate_fact_for_path(fact, "", tools=("ls",)) is False

    def test_tool_missing_on_file_event_means_no_match(self):
        # Decision 10: no source on file events → False.
        fact = _build({"fact": "Git push", "incl": ["t:git push"]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="anything") is False

    def test_tool_combined_with_x_both_required(self):
        fact = _build({"fact": "kubectl delete", "incl": ["t:kubectl", "x:delete"]})
        assert evaluate_fact_for_path(
            fact, "", command="kubectl delete pod foo", tools=("kubectl",)
        ) is True
        # Tools match but command doesn't.
        assert evaluate_fact_for_path(
            fact, "", command="kubectl get pod", tools=("kubectl",)
        ) is False
        # Command matches but tools don't.
        assert evaluate_fact_for_path(
            fact, "", command="kubectl delete pod foo", tools=("helm",)
        ) is False

    def test_tool_plus_content_never_fires(self):
        # Two-worlds invariant: c: requires file content, t: requires Bash+META.
        # No event carries both, so the fact is structurally dead.
        fact = _build({"fact": "Dead", "incl": ["t:git push", "c:import"]})
        # File event: tools=None → False.
        assert evaluate_fact_for_path(fact, "src/app.py", content="import os") is False
        # Bash event: content=None → False.
        assert evaluate_fact_for_path(fact, "", tools=("git push",), command="git push") is False

    def test_skip_tool_excludes(self):
        fact = _build({
            "fact": "Bash warnings",
            "incl": ["x:."],
            "skip": ["t:echo"],
        })
        # echo tool is in the skip list → excluded even though x: matches.
        assert evaluate_fact_for_path(fact, "", command="echo hi", tools=("echo",)) is False
        # git commit isn't excluded.
        assert evaluate_fact_for_path(fact, "", command="git commit", tools=("git commit",)) is True

    # --- Endpoint regex matcher tests (e:) — per-item against endpoints ---

    def test_endpoint_only_single_entry_match(self):
        fact = _build({"fact": "Prod endpoint", "incl": ["e:\\.prod\\."]})
        assert evaluate_fact_for_path(fact, "", endpoints=("api.prod.com",)) is True

    def test_endpoint_matches_among_multiple_entries(self):
        fact = _build({"fact": "Prod", "incl": ["e:\\.prod\\."]})
        assert evaluate_fact_for_path(
            fact, "", endpoints=("api.staging.com", "api.prod.com")
        ) is True

    def test_endpoint_no_match_on_non_prod(self):
        fact = _build({"fact": "Prod", "incl": ["e:\\.prod\\."]})
        assert evaluate_fact_for_path(fact, "", endpoints=("api.staging.com",)) is False

    def test_endpoint_none_means_no_source(self):
        # Decision 10.
        fact = _build({"fact": "Prod", "incl": ["e:\\.prod\\."]})
        assert evaluate_fact_for_path(fact, "", endpoints=None) is False

    def test_endpoint_empty_tuple_means_nothing_to_match(self):
        fact = _build({"fact": "Any", "incl": ["e:.*"]})
        assert evaluate_fact_for_path(fact, "", endpoints=()) is False

    def test_endpoint_missing_on_file_event(self):
        fact = _build({"fact": "Prod", "incl": ["e:\\.prod\\."]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="anything") is False

    def test_endpoint_combined_with_tool(self):
        fact = _build({
            "fact": "Kubectl against prod",
            "incl": ["t:kubectl", "e:\\.prod\\."],
        })
        assert evaluate_fact_for_path(
            fact, "", tools=("kubectl",), endpoints=("api.prod.com",)
        ) is True
        # Tool matches but endpoint doesn't.
        assert evaluate_fact_for_path(
            fact, "", tools=("kubectl",), endpoints=("api.staging.com",)
        ) is False
        # Endpoint matches but tool doesn't.
        assert evaluate_fact_for_path(
            fact, "", tools=("helm",), endpoints=("api.prod.com",)
        ) is False

    def test_multiple_endpoint_regexes_or(self):
        fact = _build({
            "fact": "Prod or staging",
            "incl": ["e:\\.prod\\.", "e:\\.staging\\."],
        })
        assert evaluate_fact_for_path(fact, "", endpoints=("api.prod.com",)) is True
        assert evaluate_fact_for_path(fact, "", endpoints=("api.staging.com",)) is True
        assert evaluate_fact_for_path(fact, "", endpoints=("api.dev.com",)) is False

    def test_skip_endpoint_excludes_local(self):
        fact = _build({
            "fact": "External calls",
            "incl": ["t:curl"],
            "skip": ["e:localhost|127\\.0\\.0\\.1"],
        })
        assert evaluate_fact_for_path(
            fact, "", tools=("curl",), endpoints=("api.prod.com",)
        ) is True
        assert evaluate_fact_for_path(
            fact, "", tools=("curl",), endpoints=("localhost:8080",)
        ) is False

    # --- Flag literal matcher tests (f:) — exact-match against flags ---

    def test_flag_only_match(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(fact, "", flags=("mutates",)) is True

    def test_flag_matches_among_multiple(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(
            fact, "", flags=("network", "mutates", "irreversible")
        ) is True

    def test_flag_no_match(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(fact, "", flags=("network",)) is False

    def test_flag_exact_match_not_substring(self):
        """f: is literal equality — no substring semantics."""
        fact = _build({"fact": "Network", "incl": ["f:network"]})
        # "network" doesn't match the literal "networking" (not in vocab
        # but this asserts semantics regardless).
        assert evaluate_fact_for_path(fact, "", flags=("networking",)) is False

    def test_flag_none_means_no_source(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(fact, "", flags=None) is False

    def test_flag_empty_tuple_means_no_match(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(fact, "", flags=()) is False

    def test_flag_missing_on_file_event(self):
        fact = _build({"fact": "Mutating", "incl": ["f:mutates"]})
        assert evaluate_fact_for_path(fact, "src/app.py", content="anything") is False

    def test_multiple_flag_literals_or(self):
        fact = _build({"fact": "Risky", "incl": ["f:mutates", "f:network"]})
        assert evaluate_fact_for_path(fact, "", flags=("mutates",)) is True
        assert evaluate_fact_for_path(fact, "", flags=("network",)) is True
        assert evaluate_fact_for_path(fact, "", flags=("slow",)) is False

    def test_flag_combined_with_tool(self):
        fact = _build({
            "fact": "Destructive git push",
            "incl": ["t:git push", "f:irreversible"],
        })
        assert evaluate_fact_for_path(
            fact, "", tools=("git push",), flags=("mutates", "irreversible")
        ) is True
        assert evaluate_fact_for_path(
            fact, "", tools=("git push",), flags=("mutates",)
        ) is False

    def test_skip_flag_excludes_agent_initiated(self):
        """Canonical skip example from the plan."""
        fact = _build({
            "fact": "User-initiated find",
            "incl": ["t:find"],
            "skip": ["f:agent_initiated"],
        })
        assert evaluate_fact_for_path(fact, "", tools=("find",), flags=()) is True
        assert evaluate_fact_for_path(
            fact, "", tools=("find",), flags=("agent_initiated",)
        ) is False
