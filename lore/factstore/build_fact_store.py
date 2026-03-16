from lore.factstore.fact_store import FactStore


def build_fact_store(project_root: str) -> FactStore:
    """Construct a FactStore, load all facts, and return it."""
    store = FactStore(project_root)
    store.load_all_facts()
    return store
