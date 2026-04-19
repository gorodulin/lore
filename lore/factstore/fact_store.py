import os

from lore.facts.fact import Fact
from lore.store.load_facts_tree import load_facts_tree
from lore.store.load_facts_file import load_facts_file
from lore.store.merge_fact_tree_to_global_matchers import merge_fact_tree_to_global_matchers
from lore.facts.build_fact_from_dict import build_fact_from_dict
from lore.facts.build_dict_from_fact import build_dict_from_fact
from lore.validation.validate_fact_set import validate_fact_set
from lore.facts.find_matching_facts import find_matching_facts
from lore.facts.create_fact import create_fact as create_fact_on_disk
from lore.facts.edit_fact import edit_fact as edit_fact_on_disk
from lore.facts.delete_fact import delete_fact as delete_fact_on_disk
from lore.paths.compute_rel_dir import compute_rel_dir
from lore.paths.resolve_relative_path import resolve_relative_path


class FactStore:
    """In-memory cache of typed facts for a project.

    Wraps the load -> merge -> validate -> build pipeline and keeps
    typed Fact objects in memory so repeated queries avoid re-reading
    the filesystem and re-compiling matchers.

    All mutations use synchronous file I/O. Do not introduce await
    between state dict updates - the single-threaded event loop
    serializes operations only between await points.
    """

    def __init__(self, project_root: str):
        self._project_root = os.path.abspath(project_root)
        # These three dicts must stay in sync. _reload_facts_file and
        # _remove_facts_file are the only mutation points.
        self._file_registry: dict[str, FileEntry] = {}
        self._facts: dict[str, Fact] = {}
        self._file_for_fact: dict[str, str] = {}

    def load_all_facts(self) -> None:
        """Load every .lore.json under the project root into memory."""
        fact_files = load_facts_tree(self._project_root)
        if not fact_files:
            return

        merged = merge_fact_tree_to_global_matchers(fact_files)
        valid, errors = validate_fact_set(merged)
        if not valid:
            messages = [
                f"[{e['code']}] {e.get('fact_id', '?')}: {e['message']}"
                for e in errors
            ]
            raise ValueError(f"Invalid facts: {'; '.join(messages)}")

        self._file_registry.clear()
        self._facts.clear()
        self._file_for_fact.clear()

        for ff in fact_files:
            abs_path = ff["file_path"]
            mtime = os.path.getmtime(abs_path)
            fact_ids = set(ff["facts"].keys())
            self._file_registry[abs_path] = FileEntry(mtime=mtime, fact_ids=fact_ids)

            for fid in fact_ids:
                self._file_for_fact[fid] = abs_path

        for fid, raw in merged.items():
            self._facts[fid] = build_fact_from_dict(fid, raw)

    def refresh_facts_for_path(self, file_path: str) -> None:
        """Incrementally refresh facts along the ancestor/descendant branch of file_path.

        Only scans ancestors + descendants of file_path, never the full tree.
        """
        branch_files = self._scan_facts_branch(file_path)
        known_files = set(self._file_registry.keys())

        for abs_path in branch_files:
            if abs_path in known_files:
                current_mtime = os.path.getmtime(abs_path)
                entry = self._file_registry[abs_path]
                if current_mtime != entry.mtime:
                    self._reload_facts_file(abs_path)
                known_files.discard(abs_path)
            else:
                self._reload_facts_file(abs_path)

        for abs_path in known_files:
            if not os.path.exists(abs_path):
                self._remove_facts_file(abs_path)

    def find_matching_facts(self, file_path: str, content: str | None = None, description: str | None = None, command: str | None = None, tools: tuple[str, ...] | None = None, endpoints: tuple[str, ...] | None = None, flags: tuple[str, ...] | None = None, affected_paths: tuple[str, ...] | None = None, tags: list[str] | None = None) -> dict[str, dict]:
        """Find facts matching a tool event, optionally filtered by tags.

        For events without a file path (e.g. Bash), pass an empty string
        for file_path; the full tree will be scanned for matches.

        Returns raw dicts for backward compatibility with consumers.
        """
        if file_path:
            self.refresh_facts_for_path(file_path)
            rel_path = resolve_relative_path(self._project_root, file_path)
            if rel_path is None:
                return {}
        else:
            rel_path = ""

        matching_ids = find_matching_facts(self._facts, rel_path, content=content, description=description, command=command, tools=tools, endpoints=endpoints, flags=flags, affected_paths=affected_paths)
        if not matching_ids:
            return {}

        result = {fid: build_dict_from_fact(self._facts[fid]) for fid in matching_ids}

        if tags:
            result = _filter_by_tags(result, tags)

        return result

    def get_fact(self, fact_id: str) -> dict | None:
        """Return fact as raw dict for fact_id, or None if not found."""
        fact = self._facts.get(fact_id)
        if fact is None:
            return None
        return build_dict_from_fact(fact)

    def create_fact(self, fact_text: str, incl: list[str], skip: list[str] | None = None, fact_id: str | None = None, tags: list[str] | None = None) -> dict:
        """Create a fact on disk and update in-memory state."""
        result = create_fact_on_disk(
            self._project_root, fact_text, incl, skip,
            fact_id=fact_id, tags=tags,
        )
        self._reload_facts_file(result["file_path"])
        return result

    def edit_fact(self, fact_id: str, fact_text: str | None = None, incl: list[str] | None = None, skip: list[str] | None = None, tags: list[str] | None = None) -> dict:
        """Edit a fact on disk and update in-memory state.

        Changing incl patterns may relocate the fact to a different
        .lore.json (different common parent). Both old and new files
        must be reloaded/evicted.
        """
        old_path = self._file_for_fact.get(fact_id)

        result = edit_fact_on_disk(
            self._project_root, fact_id,
            fact_text=fact_text, incl=incl, skip=skip, tags=tags,
        )

        new_path = result["file_path"]
        if old_path and old_path != new_path:
            if os.path.exists(old_path):
                self._reload_facts_file(old_path)
            else:
                self._remove_facts_file(old_path)
        self._reload_facts_file(new_path)
        return result

    def delete_fact(self, fact_id: str) -> dict:
        """Delete a fact from disk and update in-memory state."""
        result = delete_fact_on_disk(self._project_root, fact_id)
        file_path = result["file_path"]

        if os.path.exists(file_path):
            self._reload_facts_file(file_path)
        else:
            self._remove_facts_file(file_path)
        return result

    def validate_all_facts(self) -> dict:
        """Re-validate all in-memory facts and return {valid, errors}."""
        raw_facts = {fid: build_dict_from_fact(f) for fid, f in self._facts.items()}
        valid, errors = validate_fact_set(raw_facts)
        return {"valid": valid, "errors": errors}

    def _reload_facts_file(self, facts_json_path: str) -> None:
        """Evict old facts from a file, then load+merge+build replacements."""
        self._remove_facts_file(facts_json_path)

        if not os.path.exists(facts_json_path):
            return

        raw_facts = load_facts_file(facts_json_path)
        rel_dir = compute_rel_dir(facts_json_path, self._project_root)
        merged_chunk = merge_fact_tree_to_global_matchers([{
            "file_path": facts_json_path,
            "rel_dir": rel_dir,
            "facts": raw_facts,
        }])

        valid, errors = validate_fact_set(merged_chunk)
        if not valid:
            return

        mtime = os.path.getmtime(facts_json_path)
        fact_ids = set(raw_facts.keys())
        self._file_registry[facts_json_path] = FileEntry(mtime=mtime, fact_ids=fact_ids)

        for fid, raw in merged_chunk.items():
            self._facts[fid] = build_fact_from_dict(fid, raw)
            self._file_for_fact[fid] = facts_json_path

    def _remove_facts_file(self, facts_json_path: str) -> None:
        """Evict all facts associated with a .lore.json path."""
        entry = self._file_registry.pop(facts_json_path, None)
        if entry is None:
            return

        for fid in entry.fact_ids:
            self._facts.pop(fid, None)
            self._file_for_fact.pop(fid, None)

    def _scan_facts_branch(self, file_path: str) -> list[str]:
        """Find .lore.json paths along ancestors and descendants of file_path."""
        if os.path.isabs(file_path):
            abs_path = file_path
        else:
            abs_path = os.path.join(self._project_root, file_path)
        abs_path = os.path.normpath(abs_path)

        results = []

        # Walk ancestors from file up to project root
        current = os.path.dirname(abs_path)
        root = os.path.normpath(self._project_root)
        while True:
            candidate = os.path.join(current, ".lore.json")
            if os.path.exists(candidate):
                results.append(candidate)
            if os.path.normpath(current) == root:
                break
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

        # Walk descendants from file's directory downward
        file_dir = os.path.dirname(abs_path)
        if os.path.isdir(file_dir):
            for dirpath, _, filenames in os.walk(file_dir):
                if dirpath == file_dir:
                    continue
                if ".lore.json" in filenames:
                    results.append(os.path.join(dirpath, ".lore.json"))

        return list(dict.fromkeys(results))


def _filter_by_tags(facts: dict[str, dict], tags: list[str]) -> dict[str, dict]:
    """Filter facts that match all given tags using hook-tag OR logic per tag."""
    result = facts
    for tag in tags:
        filtered = {}
        for fid, fact in result.items():
            fact_tags = fact.get("tags", [])
            hook_tags = [t for t in fact_tags if t.startswith("hook:")]
            if not hook_tags or tag in hook_tags:
                filtered[fid] = fact
        result = filtered
    return result


class FileEntry:
    """Tracks mtime and fact IDs for a single .lore.json file."""

    __slots__ = ("mtime", "fact_ids")

    def __init__(self, *, mtime: float, fact_ids: set[str]):
        self.mtime = mtime
        self.fact_ids = fact_ids
