"""
Smart Dataset Cache Manager
"""

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CacheEntry:

    dataset: object
    created: datetime
    last_access: datetime


class CacheManager:

    def __init__(self, max_items=10):

        self.max_items = max_items
        self._cache = OrderedDict()

    def add(self, key, dataset):

        now = datetime.utcnow()

        if key in self._cache:
            del self._cache[key]

        self._cache[key] = CacheEntry(
            dataset=dataset,
            created=now,
            last_access=now,
        )

        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)

    def get(self, key):

        if key not in self._cache:
            return None

        entry = self._cache.pop(key)

        entry.last_access = datetime.utcnow()

        self._cache[key] = entry

        return entry.dataset

    def exists(self, key):

        return key in self._cache

    def remove(self, key):

        self._cache.pop(key, None)

    def clear(self):

        self._cache.clear()

    def size(self):

        return len(self._cache)

    def keys(self):

        return list(self._cache.keys())
