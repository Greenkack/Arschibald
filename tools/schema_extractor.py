
# DEF — Datei 2: `C:\Users\win10\Desktop\Kakerlake 1\tools\schema_extractor.py`


# tools/schema_extractor.py
"""
Scannt rekursiv das Repo nach SQLite-Tabellen (CREATE TABLE ...),
parst Spalten/PK/FK/UNIQUE/INDEX und erzeugt schema.json im Repo-Root.

Nutzt robuste Regex-Heuristiken für .py- und .sql-Dateien.
Ändert NICHTS am Projekt; rein lesend.
"""

import json
import re
from pathlib import Path
from typing import Any

RE_CREATE = re.compile(
    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z0-9_]+)\s*\((.*?)\);',
    re.IGNORECASE | re.DOTALL)
RE_COLUMN = re.compile(r'^\s*([A-Za-z0-9_]+)\s+([^,]+)$')
RE_FK = re.compile(
    r'FOREIGN\s+KEY\s*\(\s*([A-Za-z0-9_]+)\s*\)\s+REFERENCES\s+([A-Za-z0-9_]+)\s*\(\s*([A-Za-z0-9_]+)\s*\)(?:\s+ON\s+DELETE\s+(CASCADE|SET\s+NULL|RESTRICT|NO\s+ACTION))?',
    re.IGNORECASE)
RE_INDEX = re.compile(
    r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?[A-Za-z0-9_]+\s+ON\s+([A-Za-z0-9_]+)\s*\(([^)]+)\);',
    re.IGNORECASE)

SCHEMA: dict[str, Any] = {"tables": {}, "crud": {}}
INDEXES: dict[str, list[str]] = {}


def extract_creates(sql: str) -> list[dict[str, Any]]:
    creates = []
    for m in RE_CREATE.finditer(sql):
        tname = m.group(1)
        body = m.group(2)
        creates.append({"table": tname, "body": body})
    return creates


def parse_table(create) -> dict[str, Any]:
    body = create["body"]
    table: dict[str, Any] = {"columns": {}, "fks": [], "indexes": []}
    parts = [p.strip() for p in split_top_level(body)]
    for p in parts:
        # FK constraint
        fkm = RE_FK.search(p)
        if fkm:
            col, reft, refc, ondel = fkm.groups()
            table["fks"].append({"column": col,
                                 "refTable": reft,
                                 "refColumn": refc,
                                 "onDelete": (ondel or "").upper() or None})
            continue
        # column def
        cm = RE_COLUMN.match(p)
        if cm:
            col = cm.group(1)
            rest = cm.group(2).strip()
            table["columns"][col] = interpret_col(rest)
    return table


def interpret_col(defn: str) -> dict[str, Any]:
    out: dict[str, Any] = {"type": None}
    tokens = defn.replace("\n", " ").split()
    if tokens:
        out["type"] = tokens[0].upper()
    s = defn.upper()
    out["notNull"] = "NOT NULL" in s
    out["pk"] = "PRIMARY KEY" in s
    # default literal
    m = re.search(r'DEFAULT\s+([^\s,]+)', s)
    if m:
        out["default"] = m.group(1)
    return out


def split_top_level(body: str) -> list[str]:
    res, buf, lvl = [], [], 0
    for ch in body:
        if ch == '(':
            lvl += 1
            buf.append(ch)
        elif ch == ')':
            lvl -= 1
            buf.append(ch)
        elif ch == ',' and lvl == 0:
            res.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        res.append("".join(buf).strip())
    return res


def scan_file(path: Path):
    try:
        txt = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return
    # Sammle Indizes
    for im in RE_INDEX.finditer(txt):
        tname = im.group(1)
        cols = [c.strip() for c in im.group(2).split(',')]
        INDEXES.setdefault(tname, [])
        INDEXES[tname].extend(cols)
    for c in extract_creates(txt):
        tname = c["table"]
        table = parse_table(c)
        SCHEMA["tables"][tname] = table


def main():
    root = Path(__file__).resolve().parents[1]
    for p in root.rglob('*'):
        if p.is_dir():
            # überspringe Cache/Build
            if p.name in (
                'node_modules',
                '.git',
                '.yarn',
                'dist',
                'build',
                    '__pycache__'):
                continue
            continue
        if p.suffix.lower() in ('.py', '.sql'):
            scan_file(p)
    # Indizes anhängen
    for t, cols in INDEXES.items():
        if t in SCHEMA["tables"]:
            uniq = []
            for c in cols:
                if c not in uniq:
                    uniq.append(c)
            SCHEMA["tables"][t].setdefault("indexes", [])
            SCHEMA["tables"][t]["indexes"].extend(uniq)

    out = Path(root, 'schema.json')
    out.write_text(
        json.dumps(
            SCHEMA,
            indent=2,
            ensure_ascii=False),
        encoding='utf-8')
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
