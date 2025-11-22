"""Table finding helpers.

This module provides a single public function `find_tables_containing` and
several small helpers. The implementation defers optional dependencies
(pandas) and keeps responsibilities separated so the code is easier to
test and maintain (DRY, SRP, SOLID).
"""

from typing import Any, Dict, List, Sequence, Tuple
import pandas as pd


def _contains(text: str, search: str, case_sensitive: bool) -> bool:
    if case_sensitive:
        return search in text
    return search.lower() in text.lower()


def _match_in_dataframe(tbl: Any, search: str, case_sensitive: bool) -> bool:
    try:
        if not isinstance(tbl, pd.DataFrame):
            return False
        df = tbl.astype(str)
        if case_sensitive:
            mask = df.apply(lambda col: col.str.contains(search, na=False))
        else:
            mask = df.apply(lambda col: col.str.contains(search, case=False, na=False))
        return bool(mask.any().any())
    except Exception:
        return False


def _match_in_sequence(tbl: Sequence[Any], search: str, case_sensitive: bool) -> bool:
    # Avoid treating strings/bytes as sequences of cells
    if isinstance(tbl, (str, bytes)):
        return False

    for row in tbl:
        # row can be a sequence (row) or a single cell
        if isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
            for cell in row:
                try:
                    s = str(cell)
                except Exception:
                    continue
                if _contains(s, search, case_sensitive):
                    return True
        else:
            try:
                s = str(row)
            except Exception:
                continue
            if _contains(s, search, case_sensitive):
                return True
    return False


def _match_in_object(tbl: Any, search: str, case_sensitive: bool) -> bool:
    try:
        s = str(tbl)
    except Exception:
        return False
    return _contains(s, search, case_sensitive)


def find_tables_containing(
    news_data: Dict[str, Any], search: str, case_sensitive: bool = False
) -> List[Tuple[int, Any]]:
    """Return a list of (index, table) where any cell contains `search`.

    The function supports pandas DataFrame objects (if pandas is installed),
    nested sequences (lists/tuples of rows), and falls back to stringifying
    the table if necessary. Returns an empty list if `news_data` is falsy or
    contains no tables.
    """
    if not news_data:
        return []

    tables = news_data.get("tables", []) or []
    matches: List[Tuple[int, Any]] = []

    for i, tbl in enumerate(tables):
        # 1) pandas DataFrame path (preferred if available)
        if _match_in_dataframe(tbl, search, case_sensitive):
            matches.append((i, tbl))
            continue

        # 2) list-of-rows or nested sequences
        if _match_in_sequence(tbl, search, case_sensitive):
            matches.append((i, tbl))
            continue

        # 3) fallback: stringify whole table
        if _match_in_object(tbl, search, case_sensitive):
            matches.append((i, tbl))

    return matches


# Example usage (keep commented):
# search_str = "Berlin"
# matches = find_tables_containing(news_data, search_str)
# print(f"Found {len(matches)} matching table(s).")
