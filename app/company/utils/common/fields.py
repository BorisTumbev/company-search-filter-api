from typing import Any

from django.db.models import Model


def get_all_related_field_values(obj: Any, field: str) -> list | None:
    """
    Robustly searches ALL related fields (reverse & forward relationships).

    Returns all matching field values across:
      - Reverse-related (iterable) relationships (like `financials`)
      - Single-object (One-to-One/ForeignKey) related fields (`details`)
    """
    values = []

    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue  # Skip private/protected attrs

        rel_attr = getattr(obj, attr_name, None)

        # Reverse-related iterable (like financials.all())
        if hasattr(rel_attr, 'all') and callable(rel_attr.all):
            try:
                for item in rel_attr.all():
                    if hasattr(item, field):
                        values.append(getattr(item, field))
            except Exception:
                continue

        # Single-related object (One-to-One or ForeignKey)
        elif isinstance(rel_attr, Model):
            if hasattr(rel_attr, field):
                values.append(getattr(rel_attr, field))

    return values or None


def get_nested_field_generic(obj: Any, field: str) -> Any:
    """
    Supports nested field access, including reverse relations like financials__revenue.
    For reverse related managers, returns a list of values.

    Examples:
        - 'details__size' → obj.details.size
        - 'financials__revenue' → [f.revenue for f in obj.financials.all()]
    """
    parts = field.split('__')
    current = obj

    for i, part in enumerate(parts):
        if current is None:
            return None

        # If this is a reverse related manager (e.g., .financials), check if iterable
        if hasattr(current, part):
            current = getattr(current, part)
            if hasattr(current, 'all'):  # Reverse relation manager
                remaining = '__'.join(parts[i + 1 :])
                return [get_nested_field_generic(item, remaining) for item in current.all()]
        else:
            current = getattr(current, part, None)

    return current


def try_cast(val: str) -> Any:
    """
    Tries to convert a string value to int or float.
    Returns the original string if conversion fails.
    """
    val = val.strip()
    if val.lower() in {'true', 'false'}:
        return val.lower() == 'true'

    try:
        if '.' in val:
            return float(val)
        return int(val)
    except ValueError:
        return val  # fallback: keep as string
