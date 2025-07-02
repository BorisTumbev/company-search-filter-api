from .common.parsing import match


def apply_search(objects: list, conditions: list[dict]) -> list:
    """
    Filters a list of companies using AND logic — all conditions must match.

    Args:
        objects: List of Company instances.
        conditions: List of dicts with 'field', 'op', 'value'.

    Returns:
        Filtered list of companies.
    """
    if not conditions:
        return objects
    return [c for c in objects if all(match(c, cond) for cond in conditions)]
