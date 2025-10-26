# === AUTO-GENERATED INSERT PATCH ===
# target_module: pdf_atomizer.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from pathlib import Path
from datetime import datetime
import json
import sys
import tempfile
import shutil
import hashlib
import fitz                         # PyMuPDF
import pikepdf                      # low‑level Objekt‑Zugriff
from pdfminer.high_level import extract_text_to_fp
from pdfminer.pdfparser import PDFSyntaxError

# --- DEF BLOCK START: method PDFAatomizer._snapshot ---
 def _snapshot(self, obj, _depth=0, _max_depth=10):
      """
        Konvertiert pikepdf-Objekte in reine Python-Typen (dict/list/str/...),
        damit self.atoms JSON-serialisierbar bleibt – auch nach Schließen der PDF.
        Streams werden nicht als Bytes gezogen; nur schlanke Metadaten.
        """
       if _depth > _max_depth:
            return "<max_depth>"

        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj

        # Dictionary-artige PikePDF-Objekte
        try:
            if hasattr(obj, "items"):
                out = {}
                for k, v in obj.items():
                    ks = str(k)
                    out[ks] = self._snapshot(v, _depth + 1, _max_depth)
                # Stream? -> nur Metadaten anhängen
                if hasattr(obj, "read_bytes"):
                    try:
                        length = None
                        try:
                            length = int(obj.get("/Length", 0))
                        except Exception:
                            length = None
                        out["__stream__"] = True
                        out["Length"] = length
                        if "/Filter" in obj:
                            out["Filter"] = str(obj["/Filter"])
                        if "/Subtype" in obj:
                            out["Subtype"] = str(obj["/Subtype"])
                    except Exception as e:
                        out["__stream__"] = f"<error {e}>"
                return out
        except Exception:
            pass

        # Listen-/Array-artige PikePDF-Objekte
        try:
            if hasattr(
                obj, "__iter__") and not isinstance(
                obj, (str, bytes, bytearray, dict)):
                return [self._snapshot(x, _depth + 1, _max_depth) for x in obj]
        except Exception:
            pass

        # Namen/IndirectRefs/etc. -> String
        try:
            return str(obj)
        except Exception:
            return f"<unserializable {type(obj).__name__}>"
# --- DEF BLOCK END ---
