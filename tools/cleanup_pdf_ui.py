#!/usr/bin/env python3
"""
Targeted cleaner: removes ONLY PDF-/UI-bezogene Alt-Dateien und lässt den Rest der App unberührt.

Strategie:
- Kandidaten sind Dateien/Ordner mit PDF-/UI-Bezug: Namen enthalten "pdf" oder explizite Liste
  (z. B. pdf_ui.py, central_pdf_system.py, repair_pdf/, archive/*pdf*, tom90*, mega*).
- Ausnahmen (niemals löschen):
  - pdf_generator.py (Kern, benötigt für normales Einzel-PDF)
  - pdf_templates.py (Fallback-Vorlagen)
  - theming/pdf_styles.py (Theme)
  - tools/run_normal_pdf.py, tools/trace_pdf_dependencies.py (Hilfstools)

Nutzung (PowerShell):
  # Dry‑Run (empfohlen)
  python .\tools\cleanup_pdf_ui.py --root .

  # Wirklich löschen
  python .\tools\cleanup_pdf_ui.py --root . --force
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PDF_UI_NAME_HINTS = [
    "pdf",
    "tom90",
    "mega_tom90",
    "business_sections",
]

EXPLICIT_CANDIDATES = {
    # Top‑Level
    "central_pdf_system.py",
    "pdf_ui.py",
    "pdf_preview.py",
    "multi_offer_generator.py",
    "extended_pdf_generator.py",
    "pdf_generation_bridge.py",
    "pdf_pricing_integration.py",
    "pdf_pricing_templates.py",
    "pdf_helpers.py",
    "pdf_styles.py",  # Achtung: in theming/ behalten! Nur Top‑Level löschen.
    "pdf_page_protection.py",
    "pdf_payment_integration.py",
    "pdf_payment_summary.py",
    "pdf_chart_renderer.py",
    "pdf_integration_helper.py",
    "pdf_atomizer.py",
    "pdf_migration.py",
    "pdf_generator_cli.py",
    "pdf_generator_patch.py",
    "pdf_with_payment.py",
    "pdf_erstellen_komplett.py",
    "verify_pdf_charts.py",
    # Verzeichnisse
    "repair_pdf",
    os.path.join("archive", "sokuk_legacy"),
}

NEVER_DELETE = {
    os.path.join("theming", "pdf_styles.py"),
    "pdf_generator.py",
    "pdf_templates.py",
    os.path.join("tools", "run_normal_pdf.py"),
    os.path.join("tools", "trace_pdf_dependencies.py"),
}

CODE_EXTS = {".py", ".pyi", ".pyc"}


def is_pdf_ui_candidate(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")

    # Harte Ausnahmen zuerst
    for nd in NEVER_DELETE:
        if rel_str == nd.replace("\\", "/"):
            return False

    # Explizite Kandidaten (Datei oder Ordner)
    for ex in EXPLICIT_CANDIDATES:
        ex_norm = ex.replace("\\", "/").rstrip("/")
        if rel_str == ex_norm or rel_str.startswith(ex_norm + "/"):
            if path.is_file():
                return path.suffix.lower() in CODE_EXTS
            return True

    # Generische Heuristik: Name enthält "pdf" (case‑insensitive)
    name_lower = path.name.lower()
    if any(hint in name_lower for hint in PDF_UI_NAME_HINTS):
        if rel_str.startswith("tools/"):
            return False
        if rel_str.startswith("data/") or rel_str.startswith("assets/") or rel_str.startswith("images/"):
            return False
        if path.is_file():
            return path.suffix.lower() in CODE_EXTS
        return True

    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Entfernt nur PDF-/UI-bezogene Alt-Dateien gezielt.")
    ap.add_argument("--root", default=".", help="Workspace-Root")
    ap.add_argument("--force", action="store_true", help="Wirklich löschen (ohne nur Dry-Run)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[cleanup] Root nicht gefunden: {root}")
        sys.exit(2)

    to_delete: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            if is_pdf_ui_candidate(p, root):
                to_delete.append(p)
            continue
        if p.is_file() and is_pdf_ui_candidate(p, root):
            to_delete.append(p)

    files = [x for x in to_delete if x.is_file()]
    dirs = [x for x in to_delete if x.is_dir()]
    files_sorted = sorted(files, key=lambda x: str(x).lower())
    dirs_sorted = sorted(dirs, key=lambda x: str(x).lower(), reverse=True)

    print(f"[cleanup] Geplante Löschungen: {len(files_sorted)} Dateien, {len(dirs_sorted)} Ordner")
    preview = files_sorted[:40] + dirs_sorted[:10]
    for x in preview:
        print(f"  - {x}")
    if len(files_sorted) + len(dirs_sorted) > len(preview):
        print(f"  ... und {len(files_sorted)+len(dirs_sorted)-len(preview)} weitere")

    if not args.force:
        print("[cleanup] Dry-Run. Nichts gelöscht. Starte mit --force zum Ausführen.")
        return

    errors = 0
    for f in files_sorted:
        try:
            f.unlink(missing_ok=True)
        except Exception as e:
            print(f"[cleanup] FEHLER Datei: {f} -> {e}")
            errors += 1
    for d in dirs_sorted:
        try:
            if any(d.iterdir()):
                for sub in sorted(d.rglob("*"), reverse=True):
                    try:
                        if sub.is_file():
                            sub.unlink(missing_ok=True)
                        else:
                            sub.rmdir()
                    except Exception:
                        pass
            d.rmdir()
        except Exception as e:
            print(f"[cleanup] FEHLER Ordner: {d} -> {e}")
            errors += 1

    if errors:
        print(f"[cleanup] Fertig mit {errors} Fehler(n).")
    else:
        print("[cleanup] Fertig. PDF-/UI-Altbestand entfernt.")


if __name__ == "__main__":
    main()
