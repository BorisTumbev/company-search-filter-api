from collections.abc import Callable
from typing import Any

from .common.fields import get_all_related_field_values, get_nested_field_generic


def merge_sort(
    lst: list[Any],
    key: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False,
) -> list[Any]:
    """
    Sorts a list using the merge sort algorithm.

    Args:
        lst: list of objects to sort.
        key: A callable that extracts a comparison key from each element.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list (does not mutate the original).

    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if len(lst) <= 1:
        return lst

    mid = len(lst) // 2
    left = merge_sort(lst[:mid], key=key, reverse=reverse)
    right = merge_sort(lst[mid:], key=key, reverse=reverse)

    return _merge(left, right, key, reverse)


def _merge(
    left: list[Any],
    right: list[Any],
    key: Callable[[Any], Any],
    reverse: bool,
) -> list[Any]:
    """
    Helper function to merge two sorted lists.

    Args:
        left: Left sorted sublist.
        right: Right sorted sublist.
        key: Comparison key function.
        reverse: Sort descending if True.

    Returns:
        Merged sorted list.
    """
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if (key(left[i]) <= key(right[j])) ^ reverse:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def create_sort_key(sort_fields: list[str]) -> Callable[[Any], tuple]:
    """
    Creates a sorting key function for multi-field sorting.

    Args:
        sort_fields: Fields to sort by. Use '-' prefix for descending.

    Returns:
        A key function that returns a tuple for sorting.
    """

    def key_fn(obj: Any) -> tuple:
        result = []
        for field in sort_fields:
            descending = field.startswith('-')
            actual_field = field[1:] if descending else field
            # value = get_nested_field(obj, actual_field)

            # First try direct/nested fields
            value = get_nested_field_generic(obj, actual_field)
            print(value)
            if value is None:
                # Check reverse-related fields dynamically
                related_values = get_all_related_field_values(obj, actual_field)
                if related_values:
                    # Decide how to aggregate related values generically (here: max)
                    numeric_values = [v for v in related_values if isinstance(v, (int, float))]
                    if numeric_values:
                        value = max(numeric_values)
                    else:
                        # If no numeric, take first non-numeric
                        value = related_values[0]

            if value is None:
                sort_val = (1, None) if descending else (-1, None)
            elif isinstance(value, (int, float)):
                sort_val = -value if descending else value
            elif isinstance(value, str):
                if descending:
                    # Simple numeric inversion of Unicode chars
                    sort_val = tuple(255 - ord(c) for c in value.lower())
                else:
                    sort_val = tuple(ord(c) for c in value.lower())
            else:
                str_value = str(value).lower()
                if descending:
                    sort_val = tuple(255 - ord(c) for c in str_value)
                else:
                    sort_val = tuple(ord(c) for c in str_value)

            result.append(sort_val)
        return tuple(result)

    return key_fn
