"""
Report columns that have no filled (non-null, non-empty) values in a catalog DataFrame.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import pandas as pd


def columns_with_no_filled_values(df: pd.DataFrame) -> list[str]:
    """
    Return list of column names for which no row has a filled value.

    Filled = numeric: not null; object/string: not null and non-empty after strip.
    """
    if df.empty:
        return list(df.columns) if len(df.columns) else []
    empty_cols: list[str] = []
    for col in df.columns:
        ser = df[col]
        if ser.dtype.kind in ("i", "u", "f", "c"):
            if not ser.notna().any():
                empty_cols.append(col)
        else:
            non_null = ser.notna()
            non_empty = ser.astype(str).str.strip().ne("")
            if not (non_null & non_empty).any():
                empty_cols.append(col)
    return empty_cols


def print_empty_columns_report(
    df: pd.DataFrame, title: str = "Columns with no filled values"
) -> None:
    """Print column names that have no filled values; print nothing if all have data."""
    empty = columns_with_no_filled_values(df)
    if empty:
        print(f"{title}: {', '.join(empty)}")
    else:
        print(f"{title}: (none)")
