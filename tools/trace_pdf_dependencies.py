# -*- coding: utf-8 -*-
"""
Trace dependencies touched while generating the normal single (8-page) PDF.
Writes:
- data/keep/trace_used_paths.json: all accessed files under WORKSPACE_ROOT
- data/keep/keepfiles.txt: normalized, unique file list to keep
- data/keep/pack.zip: optional ZIP containing the keep files

Usage (PowerShell):
  python .\tools\trace_pdf_dependencies.py --cmd "python .\pdf_generator.py --mode normal --input .\data\beispiel.json --output .\out\single.pdf"

Notes:
- Ensure you run from your repo root (e.g., "Bokuk2 - Kopie").
- Replace the --cmd string with your real single-PDF command.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

SITECUSTOMIZE_CODE = r"""
# -*- coding: utf-8 -*-
import atexit, builtins, inspect, json, os, sys, io, importlib
from pathlib import Path

def _norm(p):
    try:
        return os.path.realpath(os.path.abspath(p))
    except Exception:
        return p

WORKSPACE_ROOT = _norm(os.environ.get("WORKSPACE_ROOT", ""))
TRACE_LOG = os.environ.get("TRACE_LOG", "")
_accessed = set()

def _under_root(p):
    if not p:
        return False
    p = _norm(p)
    return bool(WORKSPACE_ROOT) and p.startswith(WORKSPACE_ROOT)

def _log(p):
    try:
        if _under_root(p) and os.path.exists(p):
            _accessed.add(_norm(p))
    except Exception:
        pass

# hook builtins.open and io.open
_orig_open = builtins.open

def _open_wrapper(file, *args, **kwargs):
    try:
        _log(file)
    except Exception:
        pass
    return _orig_open(file, *args, **kwargs)

builtins.open = _open_wrapper
io.open = _open_wrapper

# hook pathlib.Path.open/read_text/read_bytes
from pathlib import Path as _P

_orig_p_open = _P.open

def _p_open(self, *a, **kw):
    try:
        _log(str(self))
    except Exception:
        pass
    return _orig_p_open(self, *a, **kw)

_P.open = _p_open

_orig_read_text = _P.read_text

def _read_text(self, *a, **kw):
    try:
        _log(str(self))
    except Exception:
        pass
    return _orig_read_text(self, *a, **kw)

_P.read_text = _read_text

_orig_read_bytes = _P.read_bytes

def _read_bytes(self, *a, **kw):
    try:
        _log(str(self))
    except Exception:
        pass
    return _orig_read_bytes(self, *a, **kw)

_P.read_bytes = _read_bytes

# hook importlib.resources
try:
    import importlib.resources as _res

    _orig_open_text = getattr(_res, "open_text", None)
    if _orig_open_text:
        def _r_open_text(package, resource, *a, **kw):
            try:
                pkg = package if isinstance(package, str) else package.__name__
                loc = importlib.import_module(pkg).__file__
                if loc:
                    base = os.path.dirname(loc)
                    _log(os.path.join(base, resource))
            except Exception:
                pass
            return _orig_open_text(package, resource, *a, **kw)
        _res.open_text = _r_open_text

    _orig_open_binary = getattr(_res, "open_binary", None)
    if _orig_open_binary:
        def _r_open_binary(package, resource, *a, **kw):
            try:
                pkg = package if isinstance(package, str) else package.__name__
                loc = importlib.import_module(pkg).__file__
                if loc:
                    base = os.path.dirname(loc)
                    _log(os.path.join(base, resource))
            except Exception:
                pass
            return _orig_open_binary(package, resource, *a, **kw)
        _res.open_binary = _r_open_binary

    _orig_files = getattr(_res, "files", None)
    if _orig_files:
        def _r_files(package):
            try:
                pkg = package if isinstance(package, str) else package.__name__
                loc = importlib.import_module(pkg).__file__
                if loc:
                    _log(os.path.dirname(loc))
            except Exception:
                pass
            return _orig_files(package)
        _res.files = _r_files
except Exception:
    pass

# hook Jinja2 loader (templates)
try:
    import jinja2.loaders as _jinja_loaders

    _orig_get_source = _jinja_loaders.BaseLoader.get_source

    def _get_source(self, environment, template):
        contents, filename, uptodate = _orig_get_source(self, environment, template)
        try:
            _log(filename)
        except Exception:
            pass
        return contents, filename, uptodate

    _jinja_loaders.BaseLoader.get_source = _get_source
except Exception:
    pass

@atexit.register
def _dump_trace():
    # include imported module files
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f:
            _log(f)
    if TRACE_LOG:
        try:
            os.makedirs(os.path.dirname(TRACE_LOG), exist_ok=True)
            with open(TRACE_LOG, "w", encoding="utf-8") as fh:
                json.dump(sorted(_accessed), fh, ensure_ascii=False, indent=2)
        except Exception:
            pass
"""

def run():
    ap = argparse.ArgumentParser(description="Trace dependencies for normal 8-page PDF generation.")
    ap.add_argument("--cmd", required=True, help="Befehl, der die normale Einzel-PDF erzeugt (in Anführungszeichen).")
    ap.add_argument("--root", default=".", help="Workspace-Root (Standard: aktuelles Verzeichnis).")
    ap.add_argument("--out-dir", default="data/keep", help="Ausgabeverzeichnis für Logs und Artefakte.")
    ap.add_argument("--zip", dest="do_zip", action="store_true", help="Erzeugt ein ZIP mit allen benötigten Dateien.")
    ap.add_argument("--no-zip", dest="do_zip", action="store_false", help="Kein ZIP erzeugen.")
    ap.set_defaults(do_zip=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    trace_json = out_dir / "trace_used_paths.json"
    keep_txt = out_dir / "keepfiles.txt"
    keep_zip = out_dir / "pack.zip"

    tmpdir = Path(tempfile.mkdtemp(prefix="tracepdf_"))
    try:
        sc_path = tmpdir / "sitecustomize.py"
        sc_path.write_text(SITECUSTOMIZE_CODE, encoding="utf-8")

        env = os.environ.copy()
        # Ensure UTF-8 for safety
        env.setdefault("PYTHONIOENCODING", "utf-8")
        # Prepend our tmpdir to PYTHONPATH so sitecustomize is auto-imported
        env["PYTHONPATH"] = str(tmpdir) + os.pathsep + env.get("PYTHONPATH", "")
        env["WORKSPACE_ROOT"] = str(root)
        env["TRACE_LOG"] = str(trace_json)

        print(f"[trace] Running command: {args.cmd}")
        print(f"[trace] Workspace root: {root}")
        print(f"[trace] Trace log: {trace_json}")

        proc = subprocess.run(args.cmd, shell=True, cwd=str(root), env=env)
        if proc.returncode != 0:
            print(f"[trace] Warnung: Der Befehl beendete sich mit Code {proc.returncode}. Wir versuchen dennoch, das Trace zu verarbeiten.")

        if not trace_json.exists():
            print("[trace] Fehler: Keine Trace-Datei gefunden. Wurde der PDF-Lauf ausgeführt?")
            sys.exit(2)

        used_paths = json.loads(trace_json.read_text(encoding="utf-8"))
        # Normalize, filter to existing files inside root
        norm_used = []
        for p in used_paths:
            pp = Path(p)
            try:
                rp = pp.resolve()
            except Exception:
                continue
            if rp.is_file() and str(rp).startswith(str(root)):
                norm_used.append(str(rp))

        norm_used_sorted = sorted(set(norm_used))
        keep_txt.write_text("\n".join(norm_used_sorted) + "\n", encoding="utf-8")
        print(f"[trace] Keep-Liste geschrieben: {keep_txt} ({len(norm_used_sorted)} Dateien)")

        if args.do_zip:
            with ZipFile(keep_zip, "w", ZIP_DEFLATED) as zf:
                for fp in norm_used_sorted:
                    arcname = str(Path(fp).relative_to(root))
                    zf.write(fp, arcname)
            print(f"[trace] ZIP erzeugt: {keep_zip}")

        print("[trace] Fertig. Bitte prüfe keepfiles.txt vor dem Aufräumen.")
    finally:
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    run()
