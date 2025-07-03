from typing import Any

from .utils.common.parsing import parse_query
from .utils.filtering import apply_filter
from .utils.searching import apply_search
from .utils.sorting import create_sort_key, merge_sort


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
        conditions = parse_query(raw_query)
        filtered = apply_search(self._data, conditions)
        return SearchQuerySet(filtered)

    def sort(self, sort_param: str):
        sort_fields = [f.strip() for f in sort_param.split(',') if f.strip()] if sort_param else []
        sort_key = create_sort_key(sort_fields)
        sorted_data = merge_sort(self._data, key=sort_key)
        return SearchQuerySet(sorted_data)

    def filter(self, raw_query: str):
        filtered = apply_filter(self._data, raw_query)
        return SearchQuerySet(filtered)
