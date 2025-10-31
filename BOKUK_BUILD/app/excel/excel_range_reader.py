
import re
from pathlib import Path

import pandas as pd

BASE = Path("/mnt/data")

_A1_COL_RE = re.compile(r"([A-Z]+)")
_A1_ROW_RE = re.compile(r"(\d+)")


def col_to_idx(col_letters: str) -> int:
    col_letters = col_letters.upper()
    n = 0
    for ch in col_letters:
        n = n * 26 + (ord(ch) - 64)
    return n


def idx_to_col(idx: int) -> str:
    out = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        out = chr(65 + rem) + out
    return out


def parse_a1_range(a1: str):
    a1 = a1.replace("$", "").strip()
    if ":" in a1:
        left, right = a1.split(":")
    else:
        left = right = a1
    col1 = _A1_COL_RE.match(left).group(1)
    row1 = int(_A1_ROW_RE.search(left).group(1))
    col2 = _A1_COL_RE.match(right).group(1)
    row2 = int(_A1_ROW_RE.search(right).group(1))
    return col_to_idx(col1), row1, col_to_idx(col2), row2


def _load_sheet_cells(sheet_name: str) -> pd.DataFrame:
    path = BASE / f"cells_{sheet_name}.csv.gz"
    if not path.exists():
        raise FileNotFoundError(f"cells CSV not found for sheet: {sheet_name}")
    df = pd.read_csv(path, dtype=str).fillna("")
    return df


def range_values(sheet_name: str, a1_range: str):
    df = _load_sheet_cells(sheet_name)
    c1, r1, c2, r2 = parse_a1_range(a1_range)
    values = []
    coord_map = dict(zip(df["cell"].astype(str), df["value"], strict=False))
    for r in range(r1, r2 + 1):
        row_vals = []
        for c in range(c1, c2 + 1):
            coord = f"{idx_to_col(c)}{r}"
            row_vals.append(coord_map.get(coord, ""))
        values.append(row_vals)
    return values


def range_dataframe(sheet_name: str, a1_range: str) -> pd.DataFrame:
    vals = range_values(sheet_name, a1_range)
    if not vals:
        return pd.DataFrame()
    first_row = vals[0]

    def is_number(x):
        try:
            float(str(x).replace(",", "."))
            return True
        except BaseException:
            return False
    if any([not is_number(x) for x in first_row]):
        data = vals[1:]
        cols = [str(x) for x in first_row]
        df = pd.DataFrame(data, columns=cols)
    else:
        df = pd.DataFrame(vals)
    df = df.apply(pd.to_numeric, errors="ignore")
    return df
