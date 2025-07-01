from typing import Any
from .utils.searching import apply_search, parse_search_query
from .utils.sorting import merge_sort, create_sort_key


class SearchQuerySet:
    def __init__(self, data: list[Any]):
        self._data = data

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def to_list(self) -> list:
        return self._data

    def search(self, raw_query: str):
        conditions = parse_search_query(raw_query)
        filtered = apply_search(self._data, conditions)
        return SearchQuerySet(filtered)

    def sort(self, sort_fields: list[str]):
        sort_key = create_sort_key(sort_fields)
        sorted_data = merge_sort(self._data, key=sort_key)
        return SearchQuerySet(sorted_data)
