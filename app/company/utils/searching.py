import operator
import re
from typing import Any

from .common import try_cast, get_all_related_field_values, get_nested_field_generic

OPS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '=': operator.eq,
}
FILTER_PATTERN = re.compile(r'(?P<field>\w+)(?P<op>>=|<=|:|>|<|=)(?P<value>.+)')


def parse_search_query(raw_query: str) -> list[dict]:
    """
    Parses a filter string like:
        "industry:Tech revenue>500000 founded_year<=2015"
    Into:
        [{'field': 'industry', 'op': ':', 'value': 'Tech'}, ...]
    """
    if not raw_query:
        return []

    conditions = []
    expressions = raw_query.strip().split()

    for expr in expressions:
        match = FILTER_PATTERN.match(expr)
        if not match:
            raise ValueError(f"Invalid expression in filter query: '{expr}'")

        field = match.group('field')
        op = match.group('op')
        value = match.group('value').strip()
        value = try_cast(value)  # Try to convert value to int/float if possible

        conditions.append({'field': field, 'op': op, 'value': value})

    return conditions


def _compare(attr: Any, op: str, val: Any) -> bool:
    if attr is None:
        return False

    if op == ':' and isinstance(attr, str) and isinstance(val, str):
        return val.lower() in attr.lower()

    if (op == ':' or op == '=') and attr == val:
        return True

    if op in OPS and isinstance(attr, (int, float)) and isinstance(val, (int, float)):
        return OPS[op](attr, val)
    return False


def match(company: Any, cond: dict) -> bool:
    """
    Matches condition by:
    1. Checking nested fields
    2. If field not found, scanning related objects (e.g., financials)
    """
    field = cond['field']
    op = cond['op']
    value = cond['value']

    attr = get_nested_field_generic(company, field)

    # If not found, try searching related fields dynamically
    if attr is None:
        attr = get_all_related_field_values(company, field)

    if isinstance(attr, list):
        return any(_compare(a, op, value) for a in attr)
    return _compare(attr, op, value)


def apply_search(companies: list, conditions: list[dict]) -> list:
    """
    Filters a list of companies using AND logic — all conditions must match.

    Args:
        companies: List of Company instances.
        conditions: List of dicts with 'field', 'op', 'value'.

    Returns:
        Filtered list of companies.
    """
    if not conditions:
        return companies
    return [c for c in companies if all(match(c, cond) for cond in conditions)]
