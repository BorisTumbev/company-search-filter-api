import re
from typing import Any

from .common.parsing import OPS, match, parse_query

# Regex to extract <field><op><value>, where value may be quoted or contain spaces
CONDITION_PATTERN = re.compile(
    r'(\w+(?:>=|<=|:|=|>|<)(?:"[^"]+"|[^\s]+(?:\s[^\sANDOR][^\s]*)*))',
)


def extract_conditions(filter_string: str) -> list[str]:
    """
    Extracts field-operator-value expressions, handling quoted values and spaces.

    Example:
        'name="Alpha Corp" AND industry=Tech' -> ['name="Alpha Corp"', 'industry=Tech']
        'name=Alpha Corp AND industry=Tech' -> ['name=Alpha Corp', 'industry=Tech']
    """
    if not filter_string:
        return []
    # Find all conditions, including those with spaces or quotes
    matches = []
    idx = 0
    while idx < len(filter_string):
        m = CONDITION_PATTERN.match(filter_string, idx)
        if not m:
            idx += 1
            continue
        matches.append(m.group(1))
        idx = m.end()
        # Skip spaces and AND/OR
        while idx < len(filter_string) and filter_string[idx] in ' &|':
            idx += 1
    return matches


def parse_filter_expression(raw_query: str) -> list[str]:
    """
    Parses a filter string with AND/OR to a flat structure:
    E.g., 'A AND B OR C' -> ['A', 'AND', 'B', 'OR', 'C']
    Handles multi-word values in quotes or unquoted.
    """
    if not raw_query:
        return []
    # Normalize AND/OR (case-insensitive)
    norm = re.sub(
        r'\s+(AND|OR)\s+',
        lambda m: f' {m.group(1).upper()} ',
        raw_query,
        flags=re.IGNORECASE,
    )
    # Split on AND/OR, but keep them as tokens
    tokens = []
    parts = re.split(r'\s+(AND|OR)\s+', norm)
    for part in parts:
        if part in ('AND', 'OR'):
            tokens.append(part)
        elif part.strip():
            # Extract all conditions from this part
            tokens.extend(extract_conditions(part.strip()))
    return tokens


def strip_quotes(val: str) -> str:
    if isinstance(val, str) and val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    return val


def tokens_to_conditions(tokens: list[str]) -> list:
    """
    Converts a list of tokens (conditions and AND/OR) to a structured expression like:
    ['industry:Tech', 'AND', 'revenue>500000'] ->
    [{'field': 'industry', 'op': ':', 'value': 'Tech'}, 'AND', {'field': 'revenue', 'op': '>', 'value': 500000}]
    """
    result = []
    for t in tokens:
        if t in ('AND', 'OR'):
            result.append(t)
        else:
            cond = parse_query(t)[0]
            # Always strip quotes here!
            if isinstance(cond['value'], str):
                cond['value'] = strip_quotes(cond['value'])
            result.append(cond)
    return result


def evaluate_filter(obj: Any, expr: list) -> bool:
    """
    Evaluates an expression list like:
    [cond1, 'AND', cond2, 'OR', cond3] for an object.
    Uses OPS for both value and boolean operations.
    """
    result = None
    op = None
    for token in expr:
        if isinstance(token, dict):
            match_result = match(obj, token)
            if result is None:
                result = match_result
            elif op in ('AND', 'OR'):
                result = OPS[op](result, match_result)
        elif token in OPS:
            op = token
    return result


def apply_filter(objects: list, raw_query: str) -> list:
    """
    Top-level filter: parses filter string, evaluates for each object.
    Supports multi-word values in quotes and AND/OR logic.
    """
    if not raw_query:
        return objects
    tokens = parse_filter_expression(raw_query)
    expr = tokens_to_conditions(tokens)
    return [obj for obj in objects if evaluate_filter(obj, expr)]
