# -*- coding: utf-8 -*-
"""
Delete everything except files listed in data/keep/keepfiles.txt.
Defaults to dry-run; pass --force to actually delete.

Usage (PowerShell):
  python .\tools\delete_except_keep.py          # dry-run
  python .\tools\delete_except_keep.py --force  # really delete (careful!)
"""
import argparse
from pathlib import Path

ALWAYS_SKIP_DIRS = {".git", ".venv", ".env", ".idea", ".vscode"}
ALWAYS_KEEP_REL = {
    "tools/trace_pdf_dependencies.py",
    "tools/delete_except_keep.py",
    "data/keep",
}


def load_keeplist(keepfile: Path):
    keep = set()
    for line in keepfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            keep.add(str(Path(line).resolve()))
        except Exception:
            pass
    return keep


def should_keep(path: Path, keep_abs: set):
    p = str(path.resolve())
    if p in keep_abs:
        return True
    # keep any file under a keep directory
    for k in keep_abs:
        if p.startswith(k + "\\") or p.startswith(k + "/"):
            return True
    return False


def run():
    ap = argparse.ArgumentParser(description="Delete everything except files listed in keepfiles.txt (safe dry-run by default).")
    ap.add_argument("--root", default=".", help="Workspace root (default: current dir).")
    ap.add_argument("--keep", default="data/keep/keepfiles.txt", help="Path to keepfiles.txt.")
    ap.add_argument("--force", action="store_true", help="Actually delete (dangerous). Default is dry-run.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    keepfile = (root / args.keep).resolve()
    if not keepfile.exists():
        print(f"[clean] keep file not found: {keepfile}")
        return

    keep_abs = load_keeplist(keepfile)
    # Always keep helper files/dirs
    for rel in ALWAYS_KEEP_REL:
        keep_abs.add(str((root / rel).resolve()))

    to_delete = []
    for p in root.rglob("*"):
        if p.is_dir():
            # skip typical meta dirs
            if any(part in ALWAYS_SKIP_DIRS for part in p.parts):
                continue
            # we delete dirs only after files are removed; skip here
            continue
        # skip meta paths and our keep/trace outputs themselves
        if any(part in ALWAYS_SKIP_DIRS for part in p.parts):
            continue
        if should_keep(p, keep_abs):
            continue
        to_delete.append(p)

    print(f"[clean] Dateien, die gelöscht würden: {len(to_delete)}")
    for fp in to_delete[:50]:
        print(f"  - {fp}")
    if len(to_delete) > 50:
        print(f"  ... und {len(to_delete)-50} weitere")

    if args.force:
        count = 0
        for fp in to_delete:
            try:
                fp.unlink(missing_ok=True)
                count += 1
            except Exception as ex:
                print(f"[clean] Fehler beim Löschen {fp}: {ex}")
        print(f"[clean] Gelöscht: {count} Dateien")
    else:
        print("[clean] Dry-Run. Nichts gelöscht. Mit --force wirklich löschen.")


if __name__ == "__main__":
    run()
