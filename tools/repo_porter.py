#!/usr/bin/env python3
"""
repo_porter.py
==============
Vergleicht ein erweitertes Quell-Repo (SRC, z.B. A..X) mit einem Basis-Repo (DST, z.B. A..T),
identifiziert fehlende Funktionen/Klassen/Methoden, extrahiert deren DEF-Blöcke *formatgetreu*
und erzeugt:
  - patches/<module>.insert.py       (DEF-Blöcke zum Einfügen)
  - placement_instructions.csv       (exakte Einbauanweisungen mit Zeilen & Anker-Kontext)
  - index_src.csv / index_dst.csv    (Symbol-Inventare)
  - report.json                      (Zusammenfassung)

Optional kann 'apply' sichere Fälle automatisch einspielen:
  - Imports (oben, nach Modul-Docstring)
  - Top-Level Funktionen/Klassen
  - (optional) Methoden in existierenden Klassen (nur mit --apply-methods)

WICHTIG:
- Keine bestehenden Funktionen in DST werden überschrieben (Default: Skip).
- Format des Zielcodes bleibt unangetastet; neue Blöcke werden nur eingefügt.
- Python >= 3.8 (für end_lineno in AST).

Beispiele (Windows):
    py tools/repo_porter.py scan ^
        --src "C:\\path\\Repo2" ^
        --dst "C:\\path\\Repo1" ^
        --out "C:\\path\\out_porting"

    py tools/repo_porter.py apply ^
        --dst "C:\\path\\Repo1" ^
        --from_out "C:\\path\\out_porting" ^
        --apply-methods
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".env",
    "env",
    "venv",
    "build",
    "dist",
    ".idea",
    ".vscode",
    ".ipynb_checkpoints"}
PY_EXT = {".py"}

# ---------- Datenstrukturen ----------


@dataclass(frozen=True)
class SymbolKey:
    module_rel: str   # z.B. "pkg/modul.py"
    qualname: str     # z.B. "funktion" oder "Klasse" oder "Klasse.methode"


@dataclass
class DefInfo:
    kind: str                  # "func" | "class" | "method"
    name: str                  # Kurzname (funktion | Klasse | methode)
    qualname: str              # Voll, z.B. "Klasse.methode" oder "funktion"
    module_rel: str            # relativer Modulpfad
    lineno: int                # 1-basiert (Quelle)
    end_lineno: int            # inkl. Dekoratoren/Block
    # Zeilennummern der Dekoratoren (falls vorhanden)
    decorators: list[int]
    signature_hint: str        # grobe Signatur-Repräsentation
    parent_class: str | None = None  # für Methoden
    depends_on_local: set[str] = field(
        default_factory=set)  # einfache lokale Namensrefs
    # lineno von Importzeilen im Modul
    import_lines: list[int] = field(default_factory=list)


@dataclass
class ModuleIndex:
    module_rel: str
    file_path: Path
    src_lines: list[str]
    top_funcs: dict[str, DefInfo]       # name -> DefInfo
    classes: dict[str, DefInfo]         # class_name -> DefInfo
    methods: dict[tuple[str, str], DefInfo]  # (class, method) -> DefInfo
    imports_line_nos: list[int]         # lineno der import-Zeilen

# ---------- Utilities ----------


def is_code_dir(p: Path) -> bool:
    return p.is_dir() and p.name not in EXCLUDE_DIRS


def iter_py_files(root: Path) -> Iterable[Path]:
    for dp, dn, fn in os.walk(root):
        d = Path(dp)
        dn[:] = [x for x in dn if x not in EXCLUDE_DIRS]
        for f in fn:
            pf = d / f
            if pf.suffix in PY_EXT:
                yield pf


def relpath(p: Path, base: Path) -> str:
    return str(p.relative_to(base)).replace("\\", "/")


def read_lines(p: Path) -> list[str]:
    return p.read_text(
        encoding="utf-8",
        errors="ignore").splitlines(
        keepends=False)


def segment(lines: list[str], start: int, end: int) -> list[str]:
    # start/end sind 1-basiert inklusiv
    s = max(1, start) - 1
    e = min(len(lines), end)
    return lines[s:e]


def get_module_docstring_node(tree: ast.AST) -> ast.Expr | None:
    if tree.body and isinstance(
            tree.body[0],
            ast.Expr) and isinstance(
            getattr(
                tree.body[0],
                "value",
                None),
            ast.Constant):
        return tree.body[0]
    return None


def node_signature(n: ast.AST) -> str:
    # grobe Signatur (Namen), nicht reformatieren
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        names = []
        a = n.args
        for x in a.posonlyargs + a.args:
            names.append(x.arg)
        if a.vararg:
            names.append("*" + a.vararg.arg)
        if a.kwonlyargs:
            names.extend([k.arg for k in a.kwonlyargs])
        if a.kwarg:
            names.append("**" + a.kwarg.arg)
        return f"({', '.join(names)})"
    if isinstance(n, ast.ClassDef):
        bases = [
            getattr(
                b,
                "id",
                getattr(
                    getattr(
                        b,
                        "attr",
                        None),
                    "__str__",
                    lambda: "")()) for b in n.bases]
        return f"({', '.join([b for b in bases if b])})"
    return ""


def collect_name_reads(n: ast.AST) -> set[str]:
    out: set[str] = set()
    for x in ast.walk(n):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            out.add(x.id)
    return out


def collect_import_line_numbers(tree: ast.AST) -> list[int]:
    lines = []
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            lines.append(n.lineno)
    return lines


def collect_decorator_lines(n: ast.AST) -> list[int]:
    decos = getattr(n, "decorator_list", [])
    return [d.lineno for d in decos] if decos else []

# ---------- Indexierung ----------


def index_repo(root: Path) -> dict[str, ModuleIndex]:
    root = root.resolve()
    modules: dict[str, ModuleIndex] = {}
    for f in iter_py_files(root):
        try:
            lines = read_lines(f)
            text = "\n".join(lines) + ("\n" if lines else "")
            tree = ast.parse(text)
        except Exception:
            continue
        mod_rel = relpath(f, root)
        imports = collect_import_line_numbers(tree)
        top_funcs: dict[str, DefInfo] = {}
        classes: dict[str, DefInfo] = {}
        methods: dict[tuple[str, str], DefInfo] = {}

        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                di = DefInfo(
                    kind="func",
                    name=n.name,
                    qualname=n.name,
                    module_rel=mod_rel,
                    lineno=n.lineno if hasattr(
                        n,
                        "lineno") else 1,
                    end_lineno=n.end_lineno if hasattr(
                        n,
                        "end_lineno") else n.lineno,
                    decorators=collect_decorator_lines(n),
                    signature_hint=node_signature(n),
                    parent_class=None,
                    depends_on_local=collect_name_reads(n),
                    import_lines=imports)
                top_funcs[n.name] = di
            elif isinstance(n, ast.ClassDef):
                cinfo = DefInfo(
                    kind="class",
                    name=n.name,
                    qualname=n.name,
                    module_rel=mod_rel,
                    lineno=n.lineno,
                    end_lineno=n.end_lineno if hasattr(
                        n, "end_lineno") else n.lineno,
                    decorators=collect_decorator_lines(n),
                    signature_hint=node_signature(n),
                    parent_class=None,
                    depends_on_local=set(),  # Klassen-Header hat selten Reads
                    import_lines=imports
                )
                classes[n.name] = cinfo
                # Methoden
                for b in n.body:
                    if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        mi = DefInfo(
                            kind="method",
                            name=b.name,
                            qualname=f"{
                                n.name}.{
                                b.name}",
                            module_rel=mod_rel,
                            lineno=b.lineno,
                            end_lineno=b.end_lineno if hasattr(
                                b,
                                "end_lineno") else b.lineno,
                            decorators=collect_decorator_lines(b),
                            signature_hint=node_signature(b),
                            parent_class=n.name,
                            depends_on_local=collect_name_reads(b),
                            import_lines=imports)
                        methods[(n.name, b.name)] = mi

        modules[mod_rel] = ModuleIndex(
            module_rel=mod_rel,
            file_path=f,
            src_lines=lines,
            top_funcs=top_funcs,
            classes=classes,
            methods=methods,
            imports_line_nos=imports
        )
    return modules

# ---------- Vergleich ----------


@dataclass
class MissingItem:
    module_rel: str
    kind: str              # func | class | method
    qualname: str
    parent_class: str | None
    src_def: DefInfo
    dst_anchor_line: int   # Vorschlag im Ziel
    insert_type: str       # "imports"|"toplevel"|"method"
    anchor_context_before: str
    anchor_context_after: str


def compute_missing(src: dict[str,
                              ModuleIndex],
                    dst: dict[str,
                              ModuleIndex]) -> tuple[list[MissingItem],
                                                     dict]:
    missing: list[MissingItem] = []
    report = {
        "modules_compared": 0,
        "missing_counts": {
            "func": 0,
            "class": 0,
            "method": 0}}

    for mod_rel, src_mod in src.items():
        dst_mod = dst.get(mod_rel)
        if not dst_mod:
            # Ganzes Modul fehlt -> sämtl. Top-Level + Klassen als "toplevel" markieren
            # Anchor = Ende (neue Datei bei apply)
            anchor_line = 0
            ctx_b = ""
            ctx_a = ""
            for fn, di in src_mod.top_funcs.items():
                missing.append(
                    MissingItem(
                        mod_rel,
                        "func",
                        di.qualname,
                        None,
                        di,
                        anchor_line,
                        "toplevel",
                        ctx_b,
                        ctx_a))
                report["missing_counts"]["func"] += 1
            for cn, di in src_mod.classes.items():
                missing.append(
                    MissingItem(
                        mod_rel,
                        "class",
                        di.qualname,
                        None,
                        di,
                        anchor_line,
                        "toplevel",
                        ctx_b,
                        ctx_a))
                report["missing_counts"]["class"] += 1
            for (cn, mn), di in src_mod.methods.items():
                missing.append(
                    MissingItem(
                        mod_rel,
                        "method",
                        di.qualname,
                        cn,
                        di,
                        anchor_line,
                        "method",
                        ctx_b,
                        ctx_a))
                report["missing_counts"]["method"] += 1
            report["modules_compared"] += 1
            continue

        # Top-Level Funktionen
        for fn, di in src_mod.top_funcs.items():
            if fn not in dst_mod.top_funcs:
                # Anchor = nach letztem Top-Level-Block in DST
                anchor = _anchor_after_last_toplevel(dst_mod)
                ctx_b, ctx_a = _anchor_context(dst_mod.src_lines, anchor)
                missing.append(
                    MissingItem(
                        mod_rel,
                        "func",
                        di.qualname,
                        None,
                        di,
                        anchor,
                        "toplevel",
                        ctx_b,
                        ctx_a))
                report["missing_counts"]["func"] += 1

        # Klassen
        for cn, di in src_mod.classes.items():
            if cn not in dst_mod.classes:
                anchor = _anchor_after_last_toplevel(dst_mod)
                ctx_b, ctx_a = _anchor_context(dst_mod.src_lines, anchor)
                missing.append(
                    MissingItem(
                        mod_rel,
                        "class",
                        di.qualname,
                        None,
                        di,
                        anchor,
                        "toplevel",
                        ctx_b,
                        ctx_a))
                report["missing_counts"]["class"] += 1
            else:
                # Methoden vergleichen
                for (cc, mn), mdi in src_mod.methods.items():
                    if cc != cn:
                        continue
                    if (cc, mn) not in dst_mod.methods:
                        # Anchor = nach letzter Methode in dieser Klasse
                        cls = dst_mod.classes[cn]
                        anchor = _anchor_after_class_body(dst_mod, cls)
                        ctx_b, ctx_a = _anchor_context(
                            dst_mod.src_lines, anchor)
                        missing.append(
                            MissingItem(
                                mod_rel,
                                "method",
                                mdi.qualname,
                                cn,
                                mdi,
                                anchor,
                                "method",
                                ctx_b,
                                ctx_a))
                        report["missing_counts"]["method"] += 1

        report["modules_compared"] += 1

    return missing, report


def _anchor_after_last_toplevel(dst_mod: ModuleIndex) -> int:
    last = 0
    for di in list(dst_mod.top_funcs.values()) + \
            list(dst_mod.classes.values()):
        if di.end_lineno > last:
            last = di.end_lineno
    if last == 0:
        # evtl. nur Docstring/Imports – dann nach letzter Zeile
        return len(dst_mod.src_lines)
    return last


def _anchor_after_class_body(dst_mod: ModuleIndex, cls: DefInfo) -> int:
    # Nach letzter vorhandener Methode, sonst direkt nach Klassenkopf
    last = cls.lineno
    for (c, m), di in dst_mod.methods.items():
        if c == cls.name and di.end_lineno > last:
            last = di.end_lineno
    return last


def _anchor_context(lines: list[str], anchor_line: int,
                    radius: int = 2) -> tuple[str, str]:
    # liefert 2 Zeilen davor/danach als Kontext
    before_idx = max(0, anchor_line - 1 - radius)
    after_idx = min(len(lines), anchor_line + radius)
    ctx_before = "\n".join(lines[before_idx:anchor_line])
    ctx_after = "\n".join(lines[anchor_line:after_idx])
    return ctx_before, ctx_after

# ---------- Extraktion ----------


def extract_block(lines: list[str], di: DefInfo) -> list[str]:
    # Enthält auch Dekoratoren, falls vorhanden
    start = min(di.decorators) if di.decorators else di.lineno
    end = di.end_lineno
    return segment(lines, start, end)


def extract_imports(lines: list[str], import_line_nos: list[int]) -> list[str]:
    out: list[str] = []
    seen: set[int] = set()
    for ln in import_line_nos:
        if ln in seen:
            continue
        if 1 <= ln <= len(lines):
            out.append(lines[ln - 1])
            seen.add(ln)
    return out

# ---------- Ausgaben ----------


def write_csv(path: Path, rows: list[list[str]], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

# ---------- SCAN ----------


def cmd_scan(args: argparse.Namespace) -> None:
    src_root = Path(args.src).resolve()
    dst_root = Path(args.dst).resolve()
    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    idx_src = index_repo(src_root)
    idx_dst = index_repo(dst_root)

    # Inventare
    rows_src = []
    for m in sorted(idx_src.keys()):
        mi = idx_src[m]
        for n in sorted(mi.top_funcs.keys()):
            di = mi.top_funcs[n]
            rows_src.append(
                [m, "func", di.qualname, str(di.lineno), str(di.end_lineno)])
        for n in sorted(mi.classes.keys()):
            di = mi.classes[n]
            rows_src.append(
                [m, "class", di.qualname, str(di.lineno), str(di.end_lineno)])
        for (c, n), di in sorted(mi.methods.items()):
            rows_src.append([m, "method", di.qualname,
                            str(di.lineno), str(di.end_lineno)])

    rows_dst = []
    for m in sorted(idx_dst.keys()):
        mi = idx_dst[m]
        for n in sorted(mi.top_funcs.keys()):
            di = mi.top_funcs[n]
            rows_dst.append(
                [m, "func", di.qualname, str(di.lineno), str(di.end_lineno)])
        for n in sorted(mi.classes.keys()):
            di = mi.classes[n]
            rows_dst.append(
                [m, "class", di.qualname, str(di.lineno), str(di.end_lineno)])
        for (c, n), di in sorted(mi.methods.items()):
            rows_dst.append([m, "method", di.qualname,
                            str(di.lineno), str(di.end_lineno)])

    write_csv(out_root / "index_src.csv", rows_src,
              ["module_rel", "kind", "qualname", "lineno", "end_lineno"])
    write_csv(out_root / "index_dst.csv", rows_dst,
              ["module_rel", "kind", "qualname", "lineno", "end_lineno"])

    # Vergleich
    missing, report = compute_missing(idx_src, idx_dst)

    # Patches + Placement-CSV
    place_rows: list[list[str]] = []
    for mi in missing:
        src_mod = idx_src[mi.module_rel]
        block_lines = extract_block(src_mod.src_lines, mi.src_def)

        # Imports, reduziert: nur die Import-Zeilen des Moduls (Dedup bei
        # Apply)
        imp_lines = extract_imports(
            src_mod.src_lines, src_mod.imports_line_nos)

        patch_rel = Path("patches") / (mi.module_rel + ".insert.py")
        patch_path = out_root / patch_rel
        # Append (ein Modul kann mehrere Items haben)
        header = []
        if not patch_path.exists():
            header.append("# === AUTO-GENERATED INSERT PATCH ===")
            header.append(f"# target_module: {mi.module_rel}")
            header.append("# insert_blocks follow; keep formatting unchanged")
        body = []
        if imp_lines:
            body.append(
                "\n# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---")
            for l in imp_lines:
                body.append(l)
        body.append(f"\n# --- DEF BLOCK START: {mi.kind} {mi.qualname} ---")
        body.extend(block_lines)
        body.append("# --- DEF BLOCK END ---\n")

        content = ""
        if header:
            content = "\n".join(header) + "\n"
        content += "\n".join(body) + "\n"

        # Append sicher
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        with patch_path.open("a", encoding="utf-8") as f:
            f.write(content)

        # Placement-Zeile
        place_rows.append([
            mi.module_rel,
            mi.kind,
            mi.qualname,
            str(mi.dst_anchor_line),
            mi.insert_type,
            mi.parent_class or "",
            mi.anchor_context_before.replace("\n", " \\n "),
            mi.anchor_context_after.replace("\n", " \\n ")
        ])

    write_csv(out_root / "placement_instructions.csv",
              place_rows,
              ["module_rel",
               "kind",
               "qualname",
               "dst_anchor_line",
               "insert_type",
               "parent_class",
               "ctx_before",
               "ctx_after"])

    # Report
    write_text(
        out_root /
        "report.json",
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False))

    print(f"[OK] Scan fertig. Output: {out_root}")

# ---------- APPLY ----------


def insert_at_line(
        original: list[str],
        insert_block: list[str],
        after_line: int) -> list[str]:
    # after_line: 0 = vor Zeile 1, sonst nach dieser Zeile einfügen
    idx = max(0, min(len(original), after_line))
    return original[:idx] + insert_block + original[idx:]


def find_import_insertion_line(lines: list[str]) -> int:
    # Nach Modul-Docstring, sonst Zeile 0
    try:
        text = "\n".join(lines) + ("\n" if lines else "")
        tree = ast.parse(text)
        ds = get_module_docstring_node(tree)
        if ds:
            return getattr(ds, "end_lineno", ds.lineno)
    except Exception:
        pass
    return 0


def cmd_apply(args: argparse.Namespace) -> None:
    dst_root = Path(args.dst).resolve()
    out_root = Path(args.from_out).resolve()
    apply_methods: bool = bool(args.apply_methods)

    # Laden placement + patches
    place_csv = out_root / "placement_instructions.csv"
    if not place_csv.exists():
        raise SystemExit(f"Fehlt: {place_csv}")

    # Gruppieren nach Modul
    per_mod: dict[str, list[dict[str, str]]] = {}
    with place_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            per_mod.setdefault(row["module_rel"], []).append(row)

    # Patches lesen
    for mod_rel, rows in per_mod.items():
        dst_file = dst_root / mod_rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        if dst_file.exists():
            dst_lines = read_lines(dst_file)
        else:
            dst_lines = []

        # Patchdatei
        patch_file = out_root / "patches" / (mod_rel + ".insert.py")
        if not patch_file.exists():
            print(f"[SKIP] Keine Patchdatei für {mod_rel}")
            continue
        patch_text = patch_file.read_text(encoding="utf-8")
        # Split in Blöcke
        blocks = []
        cur: list[str] = []
        for line in patch_text.splitlines():
            if line.strip().startswith("# --- DEF BLOCK START:"):
                if cur:
                    blocks.append(cur)
                    cur = []
                cur = [line]
            else:
                if cur:
                    cur.append(line)
        if cur:
            blocks.append(cur)

        # Imports (einmal dedup)
        if "# --- REQUIRED IMPORT SUGGESTIONS" in patch_text and dst_lines is not None:
            import_suggestions = []
            in_imp = False
            for line in patch_text.splitlines():
                if line.strip().startswith("# --- REQUIRED IMPORT SUGGESTIONS"):
                    in_imp = True
                    continue
                if in_imp and line.strip().startswith("# --- DEF BLOCK START"):
                    break
                if in_imp:
                    if line.strip():
                        import_suggestions.append(line)

            # Dedup: Nur Zeilen übernehmen, die noch nicht exakt vorhanden sind
            to_add = [l for l in import_suggestions if l not in dst_lines]
            if to_add:
                insert_line = find_import_insertion_line(dst_lines)
                dst_lines = insert_at_line(
                    dst_lines, [*to_add, ""], insert_line)

        # DEF-Blöcke einfügen
        for row in rows:
            kind = row["kind"]
            anchor_line = int(row["dst_anchor_line"])
            parent_class = row["parent_class"].strip()
            # passenden Block ziehen
            # (einfachste Strategie: erster Block mit passendem qualname-Start in der Start-Zeile)
            qual = row["qualname"]

            chosen: list[str] | None = None
            for b in blocks:
                header = b[0]
                if f"{kind} {qual}" in header:
                    chosen = b[1:]  # ohne Headerzeile
                    break
            if not chosen:
                print(
                    f"[WARN] Kein DEF-Block gefunden für {mod_rel} :: {qual}")
                continue

            if kind in ("func", "class"):
                # Top-Level: direkt nach Anchor
                dst_lines = insert_at_line(
                    dst_lines, chosen + [""], anchor_line)
            elif kind == "method":
                if not apply_methods:
                    print(
                        f"[INFO] Methode ausgelassen (manuell einfügen): {mod_rel} :: {qual}")
                    continue
                # Grob: Einfügen *innerhalb* der Klasse (Anchor ist Ende letzter Methodenkörper)
                # Heuristik: Block ggf. korrekt einrücken
                indent = _detect_class_indent(dst_lines, parent_class)
                adjusted = _indent_block(chosen, indent + " " * 4)
                dst_lines = insert_at_line(
                    dst_lines, adjusted + [""], anchor_line)

        # Schreiben
        dst_file.write_text("\n".join(dst_lines) +
                            ("\n" if dst_lines else ""), encoding="utf-8")
        print(f"[OK] Eingespielt: {mod_rel}")


def _detect_class_indent(lines: list[str], class_name: str) -> str:
    # findet führende Spaces der class-Zeile
    for ln in lines:
        s = ln.lstrip()
        if s.startswith("class ") and s.split(
                "(")[0].strip() == f"class {class_name}":
            return ln[:len(ln) - len(s)]
    return ""


def _indent_block(block: list[str], base_indent: str) -> list[str]:
    # Wenn Block top-level beginnt (def ...), rücke um base_indent ein
    if not block:
        return block
    first = block[0]
    lead = len(first) - len(first.lstrip(" "))
    # Nur „flache“ Blöcke einrücken
    if first.lstrip().startswith(("def ", "async def ")):
        return [(base_indent + line) if line.strip()
                else line for line in block]
    return block

# ---------- CLI ----------


def main():
    ap = argparse.ArgumentParser(
        description="Port fehlende Funktionen/Klassen/Methoden von SRC → DST (formatgetreu).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    aps = sub.add_parser("scan", help="Analysieren & Patches/CSV erzeugen")
    aps.add_argument(
        "--src",
        required=True,
        help="Pfad zum erweiterten Repo (Repo 2, A..X)")
    aps.add_argument(
        "--dst",
        required=True,
        help="Pfad zum Basis-Repo (Repo 1, A..T)")
    aps.add_argument(
        "--out",
        required=True,
        help="Ausgabeordner für Patches/CSV/Report")

    apa = sub.add_parser(
        "apply",
        help="Patches in DST einspielen (sichere Fälle)")
    apa.add_argument("--dst", required=True, help="Pfad zum Basis-Repo (Ziel)")
    apa.add_argument("--from_out", required=True, help="Ordner aus 'scan'")
    apa.add_argument(
        "--apply-methods",
        action="store_true",
        help="Auch Klassen-Methoden automatisch einfügen (vorsichtig)")

    args = ap.parse_args()

    if args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "apply":
        cmd_apply(args)


if __name__ == "__main__":
    main()
