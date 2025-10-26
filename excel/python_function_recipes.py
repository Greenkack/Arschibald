# Excel→Python Funktionsrezepte (auto-generiert aus excel_functions_used.csv)

from datetime import time
import math
import numpy as np
import pandas as pd
from datetime import date, datetime
import datetime as dt


def xl_AND(*args):
    return all(bool(a) for a in args)


def xl_AVERAGE(*args):
    import numpy as np
    import pandas as pd
    vals = []
    for a in args:
        if isinstance(a, (list, tuple, pd.Series)):
            vals.extend(a)
        else:
            vals.append(a)
    s = pd.Series(vals, dtype='float64')
    return float(np.nanmean(s.values))


def xl_DATE(year, month, day):
    return dt.date(int(year), int(month), int(day))


def xl_DAY(d):
    if isinstance(d, (datetime, date)):
        return d.day
    return None


def xl_HLOOKUP(lookup_value, table, row_index, approximate=False):
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    key_row = table.iloc[0, :]
    if approximate:
        pos = key_row.sort_values(
            kind='mergesort').searchsorted(
            lookup_value,
            side='right') - 1
        if pos < 0:
            return None
        col_idx = key_row.sort_values(kind='mergesort').index[pos]
    else:
        hits = key_row[key_row == lookup_value]
        if hits.empty:
            return None
        col_idx = hits.index[0]
    return table.iloc[row_index - 1, col_idx]


def xl_HOUR(d):
    if hasattr(d, 'hour'):
        return int(d.hour)
    return None


def xl_IF(cond, val_true, val_false):
    return val_true if bool(cond) else val_false


def xl_IFERROR(value, fallback):
    try:
        return value() if callable(value) else value
    except Exception:
        return fallback


def xl_INDEX(array, row_num, column_num=None):
    a = np.array(array, dtype=object)
    return a[row_num -
             1] if column_num is None else a[row_num -
                                             1, column_num -
                                             1]


def xl_LOOKUP(lookup_value, lookup_vector, result_vector=None):
    lv = pd.Series(list(lookup_vector)).sort_values(kind='mergesort')
    pos = lv.searchsorted(lookup_value, side='right') - 1
    if pos < 0:
        return None
    idx = lv.index[pos]
    if result_vector is None:
        return lv.loc[idx]
    rv = pd.Series(list(result_vector))
    return rv.loc[idx]


def xl_MATCH(lookup_value, lookup_array, match_type=1):
    s = pd.Series(list(lookup_array))
    if match_type == 0:
        hits = s[s == lookup_value]
        if hits.empty:
            raise KeyError('not found')
        return int(hits.index[0] + 1)
    srt = s.sort_values(kind='mergesort')
    pos = srt.searchsorted(lookup_value, side='left' if match_type == -
                           1 else 'right') - (0 if match_type == -1 else 1)
    if pos < 0 or pos >= len(srt):
        raise KeyError('no match')
    return int(srt.index[pos] + 1)


def xl_MAX(*args):
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array(vals, dtype=float)
    return float(np.nanmax(arr)) if arr.size else float('nan')


def xl_MIN(*args):
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array(vals, dtype=float)
    return float(np.nanmin(arr)) if arr.size else float('nan')


def xl_MOD(a, b):
    return float(a) % float(b)


def xl_MONTH(d):
    if isinstance(d, (datetime, date)):
        return d.month
    return None


def xl_OFFSET(reference, rows, cols, height=None, width=None):
    import pandas as pd
    if hasattr(reference, 'iloc'):
        ref = reference
    else:
        ref = pd.DataFrame(reference)
    r0, c0 = int(rows), int(cols)
    r1 = r0 + (int(height) if height is not None else ref.shape[0] - r0)
    c1 = c0 + (int(width) if width is not None else ref.shape[1] - c0)
    return ref.iloc[r0:r1, c0:c1]


def xl_OR(*args):
    return any(bool(a) for a in args)


def xl_ROUND(number, num_digits=0):
    return round(float(number), int(num_digits))


def xl_ROUNDDOWN(number, num_digits=0):
    scale = 10 ** int(num_digits)
    return math.floor(float(number) * scale) / scale


def xl_ROUNDUP(number, num_digits=0):
    scale = 10 ** int(num_digits)
    return math.ceil(float(number) * scale) / scale


def xl_SUM(*args):
    import numpy as np
    import pandas as pd
    vals = []
    for a in args:
        if isinstance(a, (list, tuple, pd.Series)):
            vals.extend(a)
        else:
            vals.append(a)
    s = pd.Series(vals, dtype='float64')
    return float(np.nansum(s.values))


def xl_SUMIF(range_vals, criteria, sum_range=None):
    rv = pd.Series(list(range_vals))
    sr = pd.Series(list(sum_range)) if sum_range is not None else rv
    crit = str(criteria).strip()
    ops = ['>=', '<=', '<>', '>', '<', '=']
    op = next((o for o in ops if crit.startswith(o)), '=')
    rhs = crit[len(op):]
    as_num = pd.to_numeric(rv, errors='coerce')
    if op == '=':
        mask = (
            rv.astype(str) == rhs) if not rhs.replace(
            '.',
            '',
            1).isdigit() else (
            as_num == float(rhs))
    elif op == '<>':
        mask = (
            rv.astype(str) != rhs) if not rhs.replace(
            '.',
            '',
            1).isdigit() else (
            as_num != float(rhs))
    elif op == '>':
        mask = (as_num > float(rhs))
    elif op == '>=':
        mask = (as_num >= float(rhs))
    elif op == '<':
        mask = (as_num < float(rhs))
    elif op == '<=':
        mask = (as_num <= float(rhs))
    return float(pd.to_numeric(sr[mask], errors='coerce').sum())


def xl_SUMIFS(sum_range, *criteria_pairs):
    sr = pd.Series(list(sum_range))
    mask = pd.Series([True] * len(sr))
    for i in range(0, len(criteria_pairs), 2):
        rng = pd.Series(list(criteria_pairs[i]))
        crit = str(criteria_pairs[i + 1]).strip()
        ops = ['>=', '<=', '<>', '>', '<', '=']
        op = next((o for o in ops if crit.startswith(o)), '=')
        rhs = crit[len(op):]
        as_num = pd.to_numeric(rng, errors='coerce')
        if op == '=':
            m = (
                rng.astype(str) == rhs) if not rhs.replace(
                '.',
                '',
                1).isdigit() else (
                as_num == float(rhs))
        elif op == '<>':
            m = (
                rng.astype(str) != rhs) if not rhs.replace(
                '.',
                '',
                1).isdigit() else (
                as_num != float(rhs))
        elif op == '>':
            m = (as_num > float(rhs))
        elif op == '>=':
            m = (as_num >= float(rhs))
        elif op == '<':
            m = (as_num < float(rhs))
        elif op == '<=':
            m = (as_num <= float(rhs))
        mask &= m
    return float(pd.to_numeric(sr[mask], errors='coerce').sum())


def xl_SUMPRODUCT(*arrays):
    mats = [np.array(a, dtype=float) for a in arrays]
    if not mats:
        return 0.0
    res = mats[0]
    for m in mats[1:]:
        res = res * m
    return float(np.nansum(res))


def xl_TEXT(value, format_text):
    import datetime as dt
    if isinstance(value, (int, float)):
        if format_text in ('0', '0.00'):
            decimals = 0 if format_text == '0' else 2
            return f"{value:.{decimals}f}"
    if isinstance(value, (dt.date, dt.datetime)):
        return value.strftime('%d.%m.%Y')
    return str(value)


def xl_TIME(hour, minute, second):
    return time(int(hour), int(minute), int(second))


def xl_TODAY():
    return dt.date.today()


def xl_VLOOKUP(lookup_value, table, col_index, approximate=False):
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    key_col = table.iloc[:, 0]
    if approximate:
        pos = key_col.searchsorted(lookup_value, side='right') - 1
        if pos < 0:
            return None
        return table.iloc[pos, col_index - 1]
    hits = table[key_col == lookup_value]
    return None if hits.empty else hits.iloc[0, col_index - 1]


def xl_WEEKDAY(d, return_type=1):
    if not isinstance(d, (datetime, date)):
        return None
    wd = d.weekday()
    if return_type == 1:
        return (wd + 1) % 7 + 1
    if return_type == 2:
        return wd + 1
    if return_type == 3:
        return wd
    return wd + 1


def xl_YEAR(d):
    if isinstance(d, (datetime, date)):
        return d.year
    return None
