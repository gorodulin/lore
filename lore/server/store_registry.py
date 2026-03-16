import time
from dataclasses import dataclass

from lore.factstore.fact_store import FactStore
from lore.factstore.build_fact_store import build_fact_store


@dataclass
class StoreEntry:
    """Tracks a FactStore and when it was last accessed."""

    store: FactStore
    last_access: float


def get_or_build_store(stores: dict[str, StoreEntry], project_root: str) -> FactStore:
    """Return FactStore for project_root, building on first access."""
    entry = stores.get(project_root)
    if entry is not None:
        entry.last_access = time.monotonic()
        return entry.store
    store = build_fact_store(project_root)
    stores[project_root] = StoreEntry(store=store, last_access=time.monotonic())
    return store


def evict_idle_stores(stores: dict[str, StoreEntry], evict_after: float) -> list[str]:
    """Remove stores not accessed within evict_after seconds. Returns evicted roots."""
    cutoff = time.monotonic() - evict_after
    to_evict = [root for root, e in stores.items() if e.last_access < cutoff]
    for root in to_evict:
        del stores[root]
    return to_evict
