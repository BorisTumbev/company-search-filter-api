import difflib
import operator
import re
from typing import Any

from ..common.fields import (
    get_all_related_field_values,
    get_nested_field_generic,
    try_cast,
)

OPS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '=': operator.eq,
    'AND': operator.and_,
    'OR': operator.or_,
}
FILTER_PATTERN = re.compile(r'(?P<field>\w+)(?P<op>>=|<=|:|>|<|=|~)(?P<value>.+)')


def match(obj: Any, cond: dict) -> bool:
    """
    Matches condition by:
    1. Checking nested fields
    2. If field not found, scanning related objects (e.g., financials)
    """
    field = cond['field']
    op = cond['op']
    value = cond['value']

    attr = get_nested_field_generic(obj, field)

    # If not found, try searching related fields dynamically
    if attr is None:
        attr = get_all_related_field_values(obj, field)

    if isinstance(attr, list):
        return any(_compare(a, op, value) for a in attr)
    return _compare(attr, op, value)


def _compare(attr: Any, op: str, val: Any) -> bool:
    if attr is None:
        return False

    # Fuzzy string contains
    if op == '~' and isinstance(attr, str) and isinstance(val, str):
        # Check if value is "close" to any substring in attr
        # Token-level matching (or use simple ratio for whole string)
        ratio = difflib.SequenceMatcher(None, attr.lower(), val.lower()).ratio()
        return ratio > 0.7  # 0.7 is a reasonable threshold; tune as needed

    if op == ':' and isinstance(attr, str) and isinstance(val, str):
        return val.lower() in attr.lower()

    if (op == ':' or op == '=') and attr == val:
        return True

    if op in OPS and isinstance(attr, (int, float)) and isinstance(val, (int, float)):
        return OPS[op](attr, val)
    return False


def parse_query(raw_query: str) -> list[dict]:
    """
    Parses a filter string like:
        "industry:Tech revenue>500000 founded_year<=2015"
    Into:
        [{'field': 'industry', 'op': ':', 'value': 'Tech'}, ...]
    """
    if not raw_query:
        return []

    conditions = []
    # Find all matches (handles quoted strings as one value)
    for match in FILTER_PATTERN.finditer(raw_query):
        field = match.group('field')
        op = match.group('op')
        value = match.group('value').strip()
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        value = try_cast(value)
        conditions.append({'field': field, 'op': op, 'value': value})

    return conditions
