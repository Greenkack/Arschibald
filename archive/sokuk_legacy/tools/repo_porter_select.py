#!/usr/bin/env python3
"""
repo_porter_select.py
Filtert einen 'out_porting'-Ordner auf eine gezielte Teilmenge:
- nimmt nur die gewünschten Zeilen aus placement_instructions.csv
- schreibt dazu passende, reduzierte patches/<modul>.insert.py (nur ausgewählte DEF-Blöcke)
- optional: Lese Include-Patterns aus Datei

Pattern-Formate für --include:
  - "qualname"                 (z.B. Analyzer.run)
  - "module_rel:qualname"      (z.B. services/main.py:Analyzer.run)
Beide Seiten unterstützen fnmatch-Globs (*) – Beispiel:
  - "services/*.py:*"          → alles aus services/
  - "*:calc_*"                 → alle qualnames mit Prefix calc_
  - "utils/*.py:*normalize*"   → alle DEFs mit 'normalize' in utils

Beispiel:
  py tools/repo_porter_select.py ^
     --from_out "C:\\Pfad\\out_porting" ^
     --out "C:\\Pfad\\out_selected" ^
     --include "services/main.py:Analyzer.run" ^
     --include "*:calc_total"

Danach:
  py tools/repo_porter.py apply --dst "C:\\Pfad\\Repo1" --from_out "C:\\Pfad\\out_selected" --apply-methods
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import shutil
from pathlib import Path

HDR = [
    "module_rel",
    "kind",
    "qualname",
    "dst_anchor_line",
    "insert_type",
    "parent_class",
    "ctx_before",
    "ctx_after"]


def load_patterns(args: argparse.Namespace) -> list[str]:
    pats = list(args.include or [])
    if args.include_file:
        p = Path(args.include_file)
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                pats.append(s)
    if not pats:
        raise SystemExit("Keine --include Patterns angegeben.")
    return pats


def match_row(row: dict[str, str], pattern: str) -> bool:
    # pattern: "qual" oder "module:qual" (fnmatch)
    if ":" in pattern:
        mod_pat, qual_pat = pattern.split(":", 1)
        return fnmatch.fnmatch(
            row["module_rel"],
            mod_pat) and fnmatch.fnmatch(
            row["qualname"],
            qual_pat)
    # Nur qualname
    return fnmatch.fnmatch(row["qualname"], pattern)


def parse_blocks(patch_text: str) -> dict[tuple[str, str], list[str]]:
    """
    Liefert {(kind, qualname): [block_lines]} ohne Headerzeile '# --- DEF BLOCK START ...'
    Erhält auch Import-Sektion (separat) via Rückgabewert None/None.
    """
    lines = patch_text.splitlines()
    blocks: dict[tuple[str, str], list[str]] = {}
    cur_key = None
    cur: list[str] = []
    for line in lines:
        ls = line.strip()
        if ls.startswith("# --- DEF BLOCK START:"):
            # neuen Block beginnen
            if cur_key and cur:
                blocks[cur_key] = cur
            cur = []
            # parse kind + qual
            # Format: "# --- DEF BLOCK START: {kind} {qual} ---"
            try:
                label = ls[len("# --- DEF BLOCK START:"):].strip()
                label = label[:-3].strip() if label.endswith("---") else label
                kind, qual = label.split(" ", 1)
                cur_key = (kind.strip(), qual.strip())
            except Exception:
                cur_key = ("unknown", "unknown")
        elif ls.startswith("# --- DEF BLOCK END ---"):
            if cur_key is not None:
                blocks[cur_key] = cur
                cur_key = None
                cur = []
        else:
            if cur_key is not None:
                cur.append(line)
    if cur_key and cur:
        blocks[cur_key] = cur
    return blocks


def extract_import_suggestions(patch_text: str) -> list[str]:
    lines = patch_text.splitlines()
    out: list[str] = []
    in_imp = False
    for line in lines:
        ls = line.strip()
        if ls.startswith("# --- REQUIRED IMPORT SUGGESTIONS"):
            in_imp = True
            continue
        if in_imp and ls.startswith("# --- DEF BLOCK START:"):
            break
        if in_imp:
            if line.strip():
                out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Filtere out_porting auf ausgewählte DEF-Blöcke.")
    ap.add_argument(
        "--from_out",
        required=True,
        help="Original out_porting Ordner")
    ap.add_argument(
        "--out",
        required=True,
        help="Zielordner für gefilterte Auswahl")
    ap.add_argument(
        "--include",
        action="append",
        help="Pattern (mehrfach erlaubt). Siehe Modul:Qualname oder nur Qualname")
    ap.add_argument(
        "--include-file",
        help="Datei mit Patterns (eine pro Zeile)")
    args = ap.parse_args()

    src = Path(args.from_out).resolve()
    dst = Path(args.out).resolve()
    dst.mkdir(parents=True, exist_ok=True)

    pats = load_patterns(args)

    # placement_instructions.csv filtern
    place_src = src / "placement_instructions.csv"
    if not place_src.exists():
        raise SystemExit(f"Fehlt: {place_src}")

    rows: list[dict[str, str]] = []
    with place_src.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if all(
                k in row for k in HDR) and any(
                match_row(
                    row,
                    p) for p in pats):
                rows.append(row)

    if not rows:
        raise SystemExit("Kein Eintrag passt zu den Include-Patterns.")

    # Schreibe gefilterte CSV
    place_dst = dst / "placement_instructions.csv"
    with place_dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HDR)
        w.writeheader()
        for rrow in rows:
            w.writerow(rrow)

    # Für jedes Modul: passende Patch-Blöcke extrahieren
    # Gruppe nach module_rel -> zugehörige qualnames/kinds
    need: dict[str, set[tuple[str, str]]] = {}
    for r in rows:
        need.setdefault(r["module_rel"], set()).add((r["kind"], r["qualname"]))

    for mod_rel, needed in need.items():
        patch_src = src / "patches" / (mod_rel + ".insert.py")
        if not patch_src.exists():
            print(f"[WARN] Patch fehlt: {patch_src}")
            continue
        text = patch_src.read_text(encoding="utf-8")
        blocks = parse_blocks(text)
        imps = extract_import_suggestions(text)

        # Baue reduzierte Patch-Datei
        out_patch = dst / "patches" / (mod_rel + ".insert.py")
        out_patch.parent.mkdir(parents=True, exist_ok=True)
        parts: list[str] = []
        parts.append("# === AUTO-GENERATED INSERT PATCH (filtered) ===")
        parts.append(f"# target_module: {mod_rel}")

        if imps:
            parts.append(
                "\n# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---")
            parts.extend(imps)

        for key in needed:
            if key not in blocks:
                print(f"[WARN] DEF-Block fehlt in Patch: {mod_rel} :: {key}")
                continue
            kind, qual = key
            parts.append(f"\n# --- DEF BLOCK START: {kind} {qual} ---")
            parts.extend(blocks[key])
            parts.append("# --- DEF BLOCK END ---\n")

        out_patch.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"[OK] Patch gebaut: {out_patch}")

    # (Optional) index_src/dst.csv + report.json einfach mitkopieren (nicht zwingend)
    for name in ("index_src.csv", "index_dst.csv", "report.json"):
        p = src / name
        if p.exists():
            shutil.copy2(p, dst / name)

    print(f"[OK] Auswahl vorbereitet: {dst}")


if __name__ == "__main__":
    main()
