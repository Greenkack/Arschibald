#!/usr/bin/env python3
"""
repo_to_json.py
Erstellt aus einem Ordner (z. B. Repo) eine einzige JSON-Datei mit:
- Liste aller Dateien (relativer Pfad)
- Größe, mtime, SHA-256
- Textinhalte (mit Encoding-Erkennung) ODER Base64 für Binärdateien
- Optional: Python-Symbolindex (Funktionen/Klassen/Methoden mit Zeilen)

Streaming-Writer (geringer RAM), optional GZip.
Python >= 3.8

Beispiele (Windows PowerShell):
    # Repo1 dumpen (inkl. Python-Index), gezippt:
    py tools/repo_to_json.py dump `
        --root "C:\\Pfad\\zu\\Repo1" `
        --out  "C:\\Pfad\repo1_dump.json.gz" `
        --gzip --python-index

    # Repo2 dumpen, nur Texttypen + max 2 MB pro Datei:
    py tools\repo_to_json.py dump `
        --root "C:\\Pfad\\zu\\Repo2" `
        --out  "C:\\Pfad\repo2_dump.json" `
        --max-bytes-per-file 2000000

Hinweise:
- Standardmäßig werden typische Build-/Cache-Ordner ignoriert.
- Große Dateien werden inhaltlich gekürzt (Konfig via --max-bytes-per-file),
  Hash & Metadaten werden vollständig erfasst.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import sys
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
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
    ".ipynb_checkpoints",
    ".tox",
    ".ruff_cache"}

# Dateitypen, die als Text versucht werden (ansonsten heuristisch)
DEFAULT_TEXT_EXT = {
    ".py", ".txt", ".md", ".rst", ".json", ".yml", ".yaml",
    ".ini", ".cfg", ".toml", ".csv", ".tsv",
    ".html", ".htm", ".css", ".js", ".ts", ".tsx",
    ".xml", ".bat", ".ps1", ".sh", ".pyi"
}


@dataclass
class FileMeta:
    relpath: str
    size: int
    mtime_iso: str
    sha256: str
    is_text: bool
    encoding: str | None
    stored_bytes: int
    truncated: bool


def human(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).isoformat()


def guess_is_binary(head: bytes) -> bool:
    # Null-Bytes → sehr wahrscheinlich binär
    if b"\x00" in head:
        return True
    # Wenn sehr „komisch“ → binär; grobe Heuristik
    text_like = sum(c >= 0x20 or c in (0x09, 0x0A, 0x0D) for c in head)
    return (len(head) > 0) and (text_like / max(1, len(head)) < 0.85)


def try_decode_text(data: bytes, prefer_ext: bool,
                    ext: str) -> tuple[bool, str | None, str | None]:
    """
    Gibt (is_text, decoded_text, encoding) zurück.
    Versucht utf-8, utf-8-sig, latin-1.
    """
    if prefer_ext and ext.lower() in DEFAULT_TEXT_EXT:
        prefer = True
    else:
        prefer = False

    # Heuristic: Wenn Header sehr binär wirkt und keine Text-Erweiterung →
    # binär
    if not prefer and guess_is_binary(data[:4096]):
        return False, None, None

    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return True, data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    # Fallback: trotzdem als Text mit 'replace'
    try:
        return True, data.decode("utf-8", errors="replace"), "utf-8?replace"
    except Exception:
        return False, None, None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path) -> Generator[Path, None, None]:
    for dp, dn, fn in os.walk(root):
        d = Path(dp)
        dn[:] = [x for x in dn if x not in EXCLUDE_DIRS]
        for name in fn:
            yield d / name


def index_python_symbols(text: str) -> dict:
    """
    Sehr schneller Python-Index (lineno/end_lineno/qualname).
    Keine Formatänderung; nur Koordinaten & Namen.
    """
    import ast
    out = {"functions": [], "classes": [], "methods": []}
    try:
        tree = ast.parse(text)
    except Exception:
        return out

    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out["functions"].append({
                "name": n.name,
                "lineno": getattr(n, "lineno", None),
                "end_lineno": getattr(n, "end_lineno", None)
            })
        elif isinstance(n, ast.ClassDef):
            out["classes"].append({
                "name": n.name,
                "lineno": getattr(n, "lineno", None),
                "end_lineno": getattr(n, "end_lineno", None)
            })
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out["methods"].append({
                        "class": n.name,
                        "name": m.name,
                        "qualname": f"{n.name}.{m.name}",
                        "lineno": getattr(m, "lineno", None),
                        "end_lineno": getattr(m, "end_lineno", None)
                    })
    return out


def file_record(path: Path, root: Path, max_bytes: int,
                add_py_index: bool) -> tuple[FileMeta, dict]:
    rel = str(path.relative_to(root)).replace("\\", "/")
    size = path.stat().st_size
    mtime = path.stat().st_mtime

    # Inhalt laden (bei großen Dateien nur den Kopf, aber Hash vollständig)
    data: bytes
    truncated = False
    read_bytes = size
    if size > max_bytes:
        # nur soweit laden, wie wir speichern wollen
        with path.open("rb") as f:
            data = f.read(max_bytes)
        truncated = True
        read_bytes = len(data)
    else:
        with path.open("rb") as f:
            data = f.read()

    ext = path.suffix.lower()
    # Text versuchen
    is_text, decoded, enc = try_decode_text(data, prefer_ext=True, ext=ext)

    # Metadaten (Hash immer vollständig, unabhängig vom cut)
    sha = sha256_file(path)

    meta = FileMeta(
        relpath=rel,
        size=size,
        mtime_iso=human(mtime),
        sha256=sha,
        is_text=is_text,
        encoding=enc if is_text else None,
        stored_bytes=read_bytes,
        truncated=truncated
    )

    rec: dict = {
        "path": meta.relpath,
        "size": meta.size,
        "mtime_iso": meta.mtime_iso,
        "sha256": meta.sha256,
        "is_text": meta.is_text,
        "stored_bytes": meta.stored_bytes,
        "truncated": meta.truncated
    }

    if is_text and decoded is not None:
        rec["encoding"] = meta.encoding
        rec["content"] = decoded
        if add_py_index and ext == ".py":
            rec["python_index"] = index_python_symbols(decoded)
    else:
        # Binär → Base64 der gespeicherten Portion
        rec["content_b64"] = base64.b64encode(data).decode("ascii")
        rec["encoding"] = None

    return meta, rec


def write_streaming_json(
    out_path: Path,
    items: Iterable[dict],
    gzip_enabled: bool,
    meta_header: dict
) -> None:
    """
    Schreibt eine einzige JSON-Datei streamend:
    {
      "meta": {...},
      "files": [ {...}, {...}, ... ]
    }
    """
    raw_io: io.BufferedWriter
    if gzip_enabled:
        f = gzip.open(out_path, "wb")
        raw_io = f  # type: ignore[assignment]
    else:
        f = open(out_path, "wb")
        raw_io = f  # type: ignore[assignment]

    try:
        def w(s: str) -> None:
            raw_io.write(s.encode("utf-8"))

        w("{\n")
        w('"meta": ')
        w(json.dumps(meta_header, ensure_ascii=False))
        w(",\n")
        w('"files": [\n')

        first = True
        for rec in items:
            if not first:
                w(",\n")
            else:
                first = False
            w(json.dumps(rec, ensure_ascii=False))
        w("\n]\n}\n")
    finally:
        raw_io.close()


def cmd_dump(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    file_count = 0
    total_bytes = 0
    kept_bytes = 0

    def generate_records() -> Generator[dict, None, None]:
        nonlocal file_count, total_bytes, kept_bytes
        for p in iter_files(root):
            try:
                # Skip sehr große Einzeldateien hart?
                # (lassen wir via max-bytes-per-file steuern)
                meta, rec = file_record(
                    p, root, args.max_bytes_per_file, args.python_index)
            except Exception as e:
                # Fehlerhafte Datei überspringen – robust bleiben
                rec = {
                    "path": str(p.relative_to(root)).replace("\\", "/"),
                    "error": f"{type(e).__name__}: {e}"
                }
                yield rec
                continue

            file_count += 1
            total_bytes += meta.size
            kept_bytes += meta.stored_bytes
            # Text-only vs Binär-Policy
            if not args.include_binary and not rec.get("is_text", False):
                # Binär komplett überspringen
                continue
            yield rec

    meta_header = {
        "root": str(root),
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "max_bytes_per_file": int(args.max_bytes_per_file),
        "include_binary": bool(args.include_binary),
        "python_index": bool(args.python_index),
        "exclude_dirs": sorted(EXCLUDE_DIRS),
    }

    write_streaming_json(out, generate_records(), args.gzip, meta_header)

    print(f"[OK] JSON geschrieben: {out}")
    print(f"[STAT] Dateien gescannt: {file_count}")
    print(f"[STAT] Gesamt-Bytes (original): {total_bytes:,}")
    print(
        f"[STAT] Gespeicherte Bytes (Summen der Ausschnitte): {
            kept_bytes:,    }")
    if args.gzip:
        print("[INFO] GZip aktiv – Upload ist kleiner.")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Wandle einen Ordner in eine JSON/JSON.GZ mit Datei-Inhalten um.")
    sp = ap.add_subparsers(dest="cmd", required=True)

    d = sp.add_parser("dump", help="Dump erzeugen")
    d.add_argument("--root", required=True, help="Quell-Ordner (Repo-Root)")
    d.add_argument(
        "--out",
        required=True,
        help="Zieldatei (.json oder .json.gz)")
    d.add_argument(
        "--gzip",
        action="store_true",
        help="Ausgabe gzip-komprimieren (.json.gz)")
    d.add_argument(
        "--python-index",
        action="store_true",
        help="Python-Funktionen/Klassen/Methoden indexieren")
    d.add_argument(
        "--include-binary",
        action="store_true",
        help="Binärdateien (Base64) mit aufnehmen (Standard: weglassen)")
    d.add_argument(
        "--max-bytes-per-file",
        type=int,
        default=2_000_000,
        help="Max Bytes pro Datei (Inhalt). Hash/Metadaten immer voll.")
    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()
    if args.cmd == "dump":
        cmd_dump(args)


if __name__ == "__main__":
    main()
