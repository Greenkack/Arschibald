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


def xl_COUNT(*args):
    """Zählt die Anzahl der Zellen mit Zahlen"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    count = 0
    for v in vals:
        try:
            float(v)
            count += 1
        except (ValueError, TypeError):
            pass
    return count


def xl_COUNTA(*args):
    """Zählt die Anzahl nicht-leerer Zellen"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    return sum(1 for v in vals if v is not None and v != '')


def xl_COUNTIF(range_vals, criteria):
    """Zählt Zellen die ein Kriterium erfüllen"""
    rv = pd.Series(list(range_vals))
    crit = str(criteria).strip()
    ops = ['>=', '<=', '<>', '>', '<', '=']
    op = next((o for o in ops if crit.startswith(o)), '=')
    rhs = crit[len(op):]
    as_num = pd.to_numeric(rv, errors='coerce')
    if op == '=':
        mask = (rv.astype(str) == rhs) if not rhs.replace(
            '.', '', 1).isdigit() else (as_num == float(rhs))
    elif op == '<>':
        mask = (rv.astype(str) != rhs) if not rhs.replace(
            '.', '', 1).isdigit() else (as_num != float(rhs))
    elif op == '>':
        mask = (as_num > float(rhs))
    elif op == '>=':
        mask = (as_num >= float(rhs))
    elif op == '<':
        mask = (as_num < float(rhs))
    elif op == '<=':
        mask = (as_num <= float(rhs))
    return int(mask.sum())


def xl_ABS(number):
    """Gibt den Absolutwert einer Zahl zurück"""
    return abs(float(number))


def xl_POWER(number, power):
    """Potenziert eine Zahl"""
    return float(number) ** float(power)


def xl_SQRT(number):
    """Gibt die Quadratwurzel zurück"""
    return math.sqrt(float(number))


def xl_LN(number):
    """Gibt den natürlichen Logarithmus zurück"""
    return math.log(float(number))


def xl_LOG(number, base=10):
    """Gibt den Logarithmus zur angegebenen Basis zurück"""
    return math.log(float(number), float(base))


def xl_LOG10(number):
    """Gibt den Logarithmus zur Basis 10 zurück"""
    return math.log10(float(number))


def xl_EXP(number):
    """Gibt e hoch der angegebenen Zahl zurück"""
    return math.exp(float(number))


def xl_PI():
    """Gibt die Zahl Pi zurück"""
    return math.pi


def xl_SIN(number):
    """Gibt den Sinus zurück"""
    return math.sin(float(number))


def xl_COS(number):
    """Gibt den Kosinus zurück"""
    return math.cos(float(number))


def xl_TAN(number):
    """Gibt den Tangens zurück"""
    return math.tan(float(number))


def xl_ASIN(number):
    """Gibt den Arkussinus zurück"""
    return math.asin(float(number))


def xl_ACOS(number):
    """Gibt den Arkuskosinus zurück"""
    return math.acos(float(number))


def xl_ATAN(number):
    """Gibt den Arkustangens zurück"""
    return math.atan(float(number))


def xl_ATAN2(x_num, y_num):
    """Gibt den Arkustangens von x- und y-Koordinaten zurück"""
    return math.atan2(float(y_num), float(x_num))


def xl_DEGREES(angle):
    """Konvertiert Bogenmaß in Grad"""
    return math.degrees(float(angle))


def xl_RADIANS(angle):
    """Konvertiert Grad in Bogenmaß"""
    return math.radians(float(angle))


def xl_CEILING(number, significance=1):
    """Rundet eine Zahl auf das nächste Vielfache auf"""
    sig = float(significance)
    return math.ceil(float(number) / sig) * sig


def xl_FLOOR(number, significance=1):
    """Rundet eine Zahl auf das nächste Vielfache ab"""
    sig = float(significance)
    return math.floor(float(number) / sig) * sig


def xl_INT(number):
    """Rundet eine Zahl auf die nächste ganze Zahl ab"""
    return int(math.floor(float(number)))


def xl_TRUNC(number, num_digits=0):
    """Schneidet eine Zahl auf eine bestimmte Anzahl Dezimalstellen ab"""
    scale = 10 ** int(num_digits)
    return int(float(number) * scale) / scale


def xl_SIGN(number):
    """Gibt das Vorzeichen einer Zahl zurück"""
    n = float(number)
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


def xl_RAND():
    """Gibt eine Zufallszahl zwischen 0 und 1 zurück"""
    import random
    return random.random()


def xl_RANDBETWEEN(bottom, top):
    """Gibt eine ganzzahlige Zufallszahl im angegebenen Bereich zurück"""
    import random
    return random.randint(int(bottom), int(top))


def xl_NOT(logical):
    """Kehrt den Wahrheitswert um"""
    return not bool(logical)


def xl_XOR(*args):
    """Gibt ein exklusives ODER zurück"""
    count = sum(1 for a in args if bool(a))
    return count % 2 == 1


def xl_TRUE():
    """Gibt den Wahrheitswert WAHR zurück"""
    return True


def xl_FALSE():
    """Gibt den Wahrheitswert FALSCH zurück"""
    return False


def xl_CONCATENATE(*args):
    """Verknüpft mehrere Textwerte"""
    return ''.join(str(a) for a in args)


def xl_LEFT(text, num_chars=1):
    """Gibt die ersten Zeichen eines Textes zurück"""
    return str(text)[:int(num_chars)]


def xl_RIGHT(text, num_chars=1):
    """Gibt die letzten Zeichen eines Textes zurück"""
    return str(text)[-int(num_chars):]


def xl_MID(text, start_num, num_chars):
    """Gibt Zeichen aus der Mitte eines Textes zurück"""
    start = int(start_num) - 1  # Excel ist 1-basiert
    return str(text)[start:start + int(num_chars)]


def xl_LEN(text):
    """Gibt die Länge eines Textes zurück"""
    return len(str(text))


def xl_LOWER(text):
    """Konvertiert Text in Kleinbuchstaben"""
    return str(text).lower()


def xl_UPPER(text):
    """Konvertiert Text in Großbuchstaben"""
    return str(text).upper()


def xl_PROPER(text):
    """Konvertiert Text so dass jedes Wort mit Großbuchstaben beginnt"""
    return str(text).title()


def xl_TRIM(text):
    """Entfernt überflüssige Leerzeichen"""
    return ' '.join(str(text).split())


def xl_SUBSTITUTE(text, old_text, new_text, instance_num=None):
    """Ersetzt Text durch neuen Text"""
    text_str = str(text)
    old_str = str(old_text)
    new_str = str(new_text)
    if instance_num is None:
        return text_str.replace(old_str, new_str)
    else:
        parts = text_str.split(old_str)
        instance = int(instance_num)
        if instance <= 0 or instance > len(parts) - 1:
            return text_str
        parts[instance] = new_str + parts[instance]
        return old_str.join(parts[:instance]) + parts[instance] + old_str.join(
            parts[instance + 1:])


def xl_FIND(find_text, within_text, start_num=1):
    """Findet einen Text in einem anderen Text (Groß-/Kleinschreibung beachten)"""
    within = str(within_text)
    find = str(find_text)
    start = int(start_num) - 1  # Excel ist 1-basiert
    pos = within.find(find, start)
    if pos == -1:
        raise ValueError(f"Text '{find}' nicht gefunden")
    return pos + 1  # Excel ist 1-basiert


def xl_SEARCH(find_text, within_text, start_num=1):
    """Findet einen Text (Groß-/Kleinschreibung ignorieren)"""
    within = str(within_text).lower()
    find = str(find_text).lower()
    start = int(start_num) - 1
    pos = within.find(find, start)
    if pos == -1:
        raise ValueError(f"Text '{find}' nicht gefunden")
    return pos + 1


def xl_REPLACE(old_text, start_num, num_chars, new_text):
    """Ersetzt Zeichen in einem Text"""
    old = str(old_text)
    start = int(start_num) - 1  # Excel ist 1-basiert
    num = int(num_chars)
    new = str(new_text)
    return old[:start] + new + old[start + num:]


def xl_REPT(text, number_times):
    """Wiederholt Text eine bestimmte Anzahl von Malen"""
    return str(text) * int(number_times)


def xl_VALUE(text):
    """Konvertiert Text in eine Zahl"""
    text_str = str(text).strip()
    # Entferne Tausendertrennzeichen
    text_str = text_str.replace(',', '').replace(' ', '')
    try:
        if '.' in text_str:
            return float(text_str)
        else:
            return int(text_str)
    except ValueError:
        raise ValueError(f"'{text}' kann nicht in eine Zahl konvertiert werden")


def xl_ISBLANK(value):
    """Prüft ob ein Wert leer ist"""
    return value is None or value == ''


def xl_ISNUMBER(value):
    """Prüft ob ein Wert eine Zahl ist"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def xl_ISTEXT(value):
    """Prüft ob ein Wert Text ist"""
    return isinstance(value, str)


def xl_ISERROR(value):
    """Prüft ob ein Wert ein Fehler ist"""
    if isinstance(value, str):
        return value.startswith('#')
    return False


def xl_NOW():
    """Gibt das aktuelle Datum und die aktuelle Uhrzeit zurück"""
    return dt.datetime.now()


def xl_DATEDIF(start_date, end_date, unit):
    """Berechnet die Differenz zwischen zwei Daten"""
    if not isinstance(start_date, (date, datetime)):
        raise ValueError("start_date muss ein Datum sein")
    if not isinstance(end_date, (date, datetime)):
        raise ValueError("end_date muss ein Datum sein")

    unit = str(unit).upper()

    if unit == 'D':
        # Tage
        return (end_date - start_date).days
    elif unit == 'M':
        # Monate
        months = (end_date.year - start_date.year) * 12
        months += end_date.month - start_date.month
        return months
    elif unit == 'Y':
        # Jahre
        return end_date.year - start_date.year
    elif unit == 'MD':
        # Tage ohne Monate und Jahre
        return (end_date.day - start_date.day) % 30
    elif unit == 'YM':
        # Monate ohne Jahre
        return (end_date.month - start_date.month) % 12
    elif unit == 'YD':
        # Tage ohne Jahre
        start_this_year = start_date.replace(year=end_date.year)
        return (end_date - start_this_year).days
    else:
        raise ValueError(f"Ungültige Einheit: {unit}")


def xl_EDATE(start_date, months):
    """Gibt ein Datum zurück das eine bestimmte Anzahl Monate vor/nach liegt"""
    if not isinstance(start_date, (date, datetime)):
        raise ValueError("start_date muss ein Datum sein")

    months_to_add = int(months)
    new_month = start_date.month + months_to_add
    new_year = start_date.year

    while new_month > 12:
        new_month -= 12
        new_year += 1
    while new_month < 1:
        new_month += 12
        new_year -= 1

    # Behandle Tage die im neuen Monat nicht existieren
    try:
        return start_date.replace(year=new_year, month=new_month)
    except ValueError:
        # Tag existiert nicht im neuen Monat (z.B. 31. Feb)
        # Verwende letzten Tag des Monats
        import calendar
        last_day = calendar.monthrange(new_year, new_month)[1]
        return start_date.replace(year=new_year, month=new_month, day=last_day)


def xl_EOMONTH(start_date, months):
    """Gibt den letzten Tag des Monats zurück"""
    import calendar
    if not isinstance(start_date, (date, datetime)):
        raise ValueError("start_date muss ein Datum sein")

    # Berechne Zielmonat
    months_to_add = int(months)
    new_month = start_date.month + months_to_add
    new_year = start_date.year

    while new_month > 12:
        new_month -= 12
        new_year += 1
    while new_month < 1:
        new_month += 12
        new_year -= 1

    # Letzter Tag des Monats
    last_day = calendar.monthrange(new_year, new_month)[1]
    return date(new_year, new_month, last_day)


def xl_NETWORKDAYS(start_date, end_date, holidays=None):
    """Berechnet die Anzahl der Arbeitstage zwischen zwei Daten"""
    if not isinstance(start_date, (date, datetime)):
        raise ValueError("start_date muss ein Datum sein")
    if not isinstance(end_date, (date, datetime)):
        raise ValueError("end_date muss ein Datum sein")

    holidays_set = set()
    if holidays:
        if isinstance(holidays, (list, tuple)):
            holidays_set = set(holidays)
        else:
            holidays_set = {holidays}

    current = start_date
    workdays = 0

    while current <= end_date:
        # Montag = 0, Sonntag = 6
        if current.weekday() < 5 and current not in holidays_set:
            workdays += 1
        current += dt.timedelta(days=1)

    return workdays


# ============================================================================
# ERWEITERTE EXCEL-FUNKTIONEN (20+ zusätzliche Funktionen)
# ============================================================================

def xl_MEDIAN(*args):
    """Gibt den Median (mittleren Wert) zurück"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.median(arr)) if arr.size else float('nan')


def xl_MODE(* args):
    """Gibt den häufigsten Wert zurück"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    s = pd.Series(vals)
    return s.mode()[0] if not s.mode().empty else None


def xl_STDEV(*args):
    """Gibt die Standardabweichung zurück (Stichprobe)"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.std(arr, ddof=1)) if arr.size > 1 else float('nan')


def xl_STDEVP(*args):
    """Gibt die Standardabweichung zurück (Grundgesamtheit)"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.std(arr, ddof=0)) if arr.size else float('nan')


def xl_VAR(*args):
    """Gibt die Varianz zurück (Stichprobe)"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.var(arr, ddof=1)) if arr.size > 1 else float('nan')


def xl_VARP(*args):
    """Gibt die Varianz zurück (Grundgesamtheit)"""
    vals = []
    for a in args:
        if isinstance(a, (list, tuple)):
            vals.extend(a)
        else:
            vals.append(a)
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.var(arr, ddof=0)) if arr.size else float('nan')


def xl_PERCENTILE(array, k):
    """Gibt das k-te Perzentil zurück"""
    vals = list(array) if isinstance(array, (list, tuple)) else [array]
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    return float(np.percentile(arr, float(k) * 100)) if arr.size else float('nan')


def xl_QUARTILE(array, quart):
    """Gibt das Quartil zurück"""
    vals = list(array) if isinstance(array, (list, tuple)) else [array]
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    q = int(quart)
    if q == 0:
        return float(np.min(arr))
    elif q == 1:
        return float(np.percentile(arr, 25))
    elif q == 2:
        return float(np.percentile(arr, 50))
    elif q == 3:
        return float(np.percentile(arr, 75))
    elif q == 4:
        return float(np.max(arr))
    else:
        raise ValueError("Quartil muss zwischen 0 und 4 liegen")


def xl_RANK(number, ref, order=0):
    """Gibt den Rang einer Zahl zurück"""
    vals = list(ref) if isinstance(ref, (list, tuple)) else [ref]
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    num = float(number)
    
    if int(order) == 0:
        # Absteigende Reihenfolge (größte Zahl = Rang 1)
        sorted_arr = np.sort(arr)[::-1]
    else:
        # Aufsteigende Reihenfolge (kleinste Zahl = Rang 1)
        sorted_arr = np.sort(arr)
    
    rank = np.where(sorted_arr == num)[0]
    return int(rank[0] + 1) if rank.size > 0 else None


def xl_LARGE(array, k):
    """Gibt den k-größten Wert zurück"""
    vals = list(array) if isinstance(array, (list, tuple)) else [array]
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    sorted_arr = np.sort(arr)[::-1]
    k_idx = int(k) - 1
    return float(sorted_arr[k_idx]) if k_idx < len(sorted_arr) else float('nan')


def xl_SMALL(array, k):
    """Gibt den k-kleinsten Wert zurück"""
    vals = list(array) if isinstance(array, (list, tuple)) else [array]
    arr = np.array([float(v) for v in vals if v is not None], dtype=float)
    sorted_arr = np.sort(arr)
    k_idx = int(k) - 1
    return float(sorted_arr[k_idx]) if k_idx < len(sorted_arr) else float('nan')


def xl_COUNTBLANK(range_vals):
    """Zählt leere Zellen"""
    vals = list(range_vals) if isinstance(range_vals, (list, tuple)) else [range_vals]
    return sum(1 for v in vals if v is None or v == '')


def xl_AVERAGEIF(range_vals, criteria, average_range=None):
    """Berechnet den Durchschnitt von Zellen die ein Kriterium erfüllen"""
    rv = pd.Series(list(range_vals))
    ar = pd.Series(list(average_range)) if average_range is not None else rv
    crit = str(criteria).strip()
    ops = ['>=', '<=', '<>', '>', '<', '=']
    op = next((o for o in ops if crit.startswith(o)), '=')
    rhs = crit[len(op):]
    as_num = pd.to_numeric(rv, errors='coerce')
    
    if op == '=':
        mask = (rv.astype(str) == rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num == float(rhs))
    elif op == '<>':
        mask = (rv.astype(str) != rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num != float(rhs))
    elif op == '>':
        mask = (as_num > float(rhs))
    elif op == '>=':
        mask = (as_num >= float(rhs))
    elif op == '<':
        mask = (as_num < float(rhs))
    elif op == '<=':
        mask = (as_num <= float(rhs))
    
    filtered = pd.to_numeric(ar[mask], errors='coerce')
    return float(filtered.mean()) if not filtered.empty else float('nan')


def xl_AVERAGEIFS(average_range, *criteria_pairs):
    """Berechnet den Durchschnitt mit mehreren Kriterien"""
    ar = pd.Series(list(average_range))
    mask = pd.Series([True] * len(ar))
    
    for i in range(0, len(criteria_pairs), 2):
        rng = pd.Series(list(criteria_pairs[i]))
        crit = str(criteria_pairs[i + 1]).strip()
        ops = ['>=', '<=', '<>', '>', '<', '=']
        op = next((o for o in ops if crit.startswith(o)), '=')
        rhs = crit[len(op):]
        as_num = pd.to_numeric(rng, errors='coerce')
        
        if op == '=':
            m = (rng.astype(str) == rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num == float(rhs))
        elif op == '<>':
            m = (rng.astype(str) != rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num != float(rhs))
        elif op == '>':
            m = (as_num > float(rhs))
        elif op == '>=':
            m = (as_num >= float(rhs))
        elif op == '<':
            m = (as_num < float(rhs))
        elif op == '<=':
            m = (as_num <= float(rhs))
        mask &= m
    
    filtered = pd.to_numeric(ar[mask], errors='coerce')
    return float(filtered.mean()) if not filtered.empty else float('nan')


def xl_MAXIFS(max_range, *criteria_pairs):
    """Gibt den Maximalwert mit mehreren Kriterien zurück"""
    mr = pd.Series(list(max_range))
    mask = pd.Series([True] * len(mr))
    
    for i in range(0, len(criteria_pairs), 2):
        rng = pd.Series(list(criteria_pairs[i]))
        crit = str(criteria_pairs[i + 1]).strip()
        ops = ['>=', '<=', '<>', '>', '<', '=']
        op = next((o for o in ops if crit.startswith(o)), '=')
        rhs = crit[len(op):]
        as_num = pd.to_numeric(rng, errors='coerce')
        
        if op == '=':
            m = (rng.astype(str) == rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num == float(rhs))
        elif op == '<>':
            m = (rng.astype(str) != rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num != float(rhs))
        elif op == '>':
            m = (as_num > float(rhs))
        elif op == '>=':
            m = (as_num >= float(rhs))
        elif op == '<':
            m = (as_num < float(rhs))
        elif op == '<=':
            m = (as_num <= float(rhs))
        mask &= m
    
    filtered = pd.to_numeric(mr[mask], errors='coerce')
    return float(filtered.max()) if not filtered.empty else float('nan')


def xl_MINIFS(min_range, *criteria_pairs):
    """Gibt den Minimalwert mit mehreren Kriterien zurück"""
    mr = pd.Series(list(min_range))
    mask = pd.Series([True] * len(mr))
    
    for i in range(0, len(criteria_pairs), 2):
        rng = pd.Series(list(criteria_pairs[i]))
        crit = str(criteria_pairs[i + 1]).strip()
        ops = ['>=', '<=', '<>', '>', '<', '=']
        op = next((o for o in ops if crit.startswith(o)), '=')
        rhs = crit[len(op):]
        as_num = pd.to_numeric(rng, errors='coerce')
        
        if op == '=':
            m = (rng.astype(str) == rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num == float(rhs))
        elif op == '<>':
            m = (rng.astype(str) != rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num != float(rhs))
        elif op == '>':
            m = (as_num > float(rhs))
        elif op == '>=':
            m = (as_num >= float(rhs))
        elif op == '<':
            m = (as_num < float(rhs))
        elif op == '<=':
            m = (as_num <= float(rhs))
        mask &= m
    
    filtered = pd.to_numeric(mr[mask], errors='coerce')
    return float(filtered.min()) if not filtered.empty else float('nan')


def xl_COUNTIFS(*criteria_pairs):
    """Zählt Zellen mit mehreren Kriterien"""
    if len(criteria_pairs) < 2:
        return 0
    
    first_range = pd.Series(list(criteria_pairs[0]))
    mask = pd.Series([True] * len(first_range))
    
    for i in range(0, len(criteria_pairs), 2):
        rng = pd.Series(list(criteria_pairs[i]))
        crit = str(criteria_pairs[i + 1]).strip()
        ops = ['>=', '<=', '<>', '>', '<', '=']
        op = next((o for o in ops if crit.startswith(o)), '=')
        rhs = crit[len(op):]
        as_num = pd.to_numeric(rng, errors='coerce')
        
        if op == '=':
            m = (rng.astype(str) == rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num == float(rhs))
        elif op == '<>':
            m = (rng.astype(str) != rhs) if not rhs.replace('.', '', 1).isdigit() else (as_num != float(rhs))
        elif op == '>':
            m = (as_num > float(rhs))
        elif op == '>=':
            m = (as_num >= float(rhs))
        elif op == '<':
            m = (as_num < float(rhs))
        elif op == '<=':
            m = (as_num <= float(rhs))
        mask &= m
    
    return int(mask.sum())


def xl_CHOOSE(index_num, *values):
    """Wählt einen Wert aus einer Liste basierend auf dem Index"""
    idx = int(index_num) - 1  # Excel ist 1-basiert
    if 0 <= idx < len(values):
        return values[idx]
    else:
        raise ValueError(f"Index {index_num} außerhalb des gültigen Bereichs")


def xl_SWITCH(expression, *args):
    """Vergleicht einen Ausdruck mit mehreren Werten und gibt das Ergebnis zurück"""
    if len(args) < 2:
        raise ValueError("SWITCH benötigt mindestens ein Wert-Ergebnis-Paar")
    
    # Letztes Argument könnte der Default-Wert sein
    has_default = len(args) % 2 == 1
    default_value = args[-1] if has_default else None
    pairs = args[:-1] if has_default else args
    
    # Durchsuche Paare
    for i in range(0, len(pairs), 2):
        if expression == pairs[i]:
            return pairs[i + 1]
    
    # Kein Match gefunden
    if default_value is not None:
        return default_value
    else:
        raise ValueError(f"Kein Match für '{expression}' gefunden")


def xl_IFS(*conditions_and_values):
    """Prüft mehrere Bedingungen und gibt den ersten wahren Wert zurück"""
    if len(conditions_and_values) % 2 != 0:
        raise ValueError("IFS benötigt Paare von Bedingung und Wert")
    
    for i in range(0, len(conditions_and_values), 2):
        condition = conditions_and_values[i]
        value = conditions_and_values[i + 1]
        if bool(condition):
            return value
    
    raise ValueError("Keine Bedingung ist wahr")


def xl_TEXTJOIN(delimiter, ignore_empty, *text_values):
    """Verbindet Text mit einem Trennzeichen"""
    delim = str(delimiter)
    ignore = bool(ignore_empty)
    
    texts = []
    for val in text_values:
        if isinstance(val, (list, tuple)):
            texts.extend(val)
        else:
            texts.append(val)
    
    if ignore:
        texts = [str(t) for t in texts if t is not None and t != '']
    else:
        texts = [str(t) if t is not None else '' for t in texts]
    
    return delim.join(texts)


def xl_CONCAT(*text_values):
    """Verbindet Text (moderne Version von CONCATENATE)"""
    texts = []
    for val in text_values:
        if isinstance(val, (list, tuple)):
            texts.extend(val)
        else:
            texts.append(val)
    
    return ''.join(str(t) for t in texts if t is not None)


def xl_EXACT(text1, text2):
    """Vergleicht zwei Texte (Groß-/Kleinschreibung beachten)"""
    return str(text1) == str(text2)


def xl_CHAR(number):
    """Gibt das Zeichen für einen ASCII-Code zurück"""
    return chr(int(number))


def xl_CODE(text):
    """Gibt den ASCII-Code des ersten Zeichens zurück"""
    text_str = str(text)
    return ord(text_str[0]) if text_str else 0


def xl_CLEAN(text):
    """Entfernt nicht druckbare Zeichen"""
    text_str = str(text)
    return ''.join(char for char in text_str if char.isprintable())


def xl_DOLLAR(number, decimals=2):
    """Formatiert eine Zahl als Währung"""
    num = float(number)
    dec = int(decimals)
    if dec >= 0:
        return f"${num:,.{dec}f}"
    else:
        # Runde auf Vielfache von 10^(-decimals)
        factor = 10 ** (-dec)
        if factor != 0:
            rounded = round(num / factor) * factor
        else:
            rounded = 0.0
        return f"${rounded:,.0f}"


def xl_FIXED(number, decimals=2, no_commas=False):
    """Formatiert eine Zahl mit fester Anzahl Dezimalstellen"""
    num = float(number)
    dec = int(decimals)
    no_comma = bool(no_commas)
    
    if no_comma:
        return f"{num:.{dec}f}"
    else:
        return f"{num:,.{dec}f}"


def xl_T(value):
    """Gibt Text zurück oder leeren String wenn kein Text"""
    return str(value) if isinstance(value, str) else ''


def xl_NUMBERVALUE(text, decimal_separator='.', group_separator=','):
    """Konvertiert Text in eine Zahl mit benutzerdefinierten Trennzeichen"""
    text_str = str(text).strip()
    dec_sep = str(decimal_separator)
    grp_sep = str(group_separator)
    
    # Ersetze Trennzeichen
    text_str = text_str.replace(grp_sep, '')
    text_str = text_str.replace(dec_sep, '.')
    
    try:
        return float(text_str)
    except ValueError:
        raise ValueError(f"'{text}' kann nicht in eine Zahl konvertiert werden")
