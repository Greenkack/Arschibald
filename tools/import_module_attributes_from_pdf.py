# tools/import_module_attributes_from_pdf.py
# Importer: PV-Modul-Eigenschaften aus modul.pdf in product_attributes +
# products
from __future__ import annotations
from product_db import add_product, get_product_by_model_name, update_product
from product_attributes import upsert_attribute

import os
import re
import sys
import traceback
from pathlib import Path
from typing import Any

# Ensure project root on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def ensure_product(
        category: str,
        model_name: str,
        brand: str | None = None) -> int | None:
    rec = get_product_by_model_name(model_name)
    if rec:
        pid = int(rec.get("id"))
        # ergänze ggf. Marke
        to_upd: dict[str, Any] = {}
        if brand and not rec.get("brand"):
            to_upd["brand"] = brand
        if to_upd:
            update_product(pid, to_upd)
        return pid
    return add_product(
        {"category": category, "model_name": model_name, "brand": brand or ""})


def _clean_header(h: Any) -> str:
    s = "" if h is None else str(h)
    s = s.replace("\n", " ").replace("\r", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _to_number(val: Any) -> float | None:
    if val is None:
        return None
    try:
        s = str(val)
        s = re.sub(r"[^0-9,\.\-]", "", s)
        s = s.replace(",", ".")
        if s in ("", "-", "."):
            return None
        return float(s)
    except Exception:
        return None


def _canonical_map() -> dict[str, str]:
    # Header -> kanonischer Key (DB-Spalten/Attribute)
    base = {
        # Identität
        "modell": "model_name",
        "modell | typ": "model_name",
        "modell/typ": "model_name",
        "modell-typ": "model_name",
        "model": "model_name",
        "modul": "model_name",
        "bezeichnung": "model_name",
        "typ": "model_name",
        "hersteller": "brand",
        "marke": "brand",
        # Seite-4 Pflichtfelder
        "zellentechnologie": "cell_technology",
        "pv-zellentechnologie": "cell_technology",
        "pv zellentechnologie": "cell_technology",
        "zelltechnologie": "cell_technology",
        "modulaufbau": "module_structure",
        "solarzellen": "cell_type",
        "solar-zellen": "cell_type",
        "solarzellentyp": "cell_type",
        "version": "version",
        # Leistung/Warranty
        "leistung": "capacity_w",  # Wp
        "leistung (wp)": "capacity_w",
        "wp": "capacity_w",
        "modulleistung": "capacity_w",
        "leistung pro pv-modul": "capacity_w",
        "leistung pro pv modul": "capacity_w",
        "garantie": "product_warranty_years",
        "produktgarantie": "product_warranty_years",
        "leistungsgarantie": "performance_warranty_text",
        # Kategorien und Speicher/WR-Felder
        "kategorie": "category",
        "speicherkapazität": "storage_power_kw",
        "speicherkapazitaet": "storage_power_kw",
        "kapazität kwh": "storage_power_kw",
        "kapazitaet kwh": "storage_power_kw",
        "leistung kw": "power_kw",
        "nennleistung": "power_kw",
        "wechselrichterleistung": "power_kw",
        # Weitere Felder
        "erweiterungsmodul": "expansion_module",
        "erweiterungs-modul": "expansion_module",
        "max. speichergröße": "max_storage_size",
        "max. speichergroesse": "max_storage_size",
        "max speichergröße": "max_storage_size",
        "max speichergroesse": "max_storage_size",
        "outdoorfähig": "outdoorfaehig",
        "outdoorfaehig": "outdoorfaehig",
        "pv-zellentechnologie": "cell_technology",
        # WR-spezifisch
        "typ wechselrichter": "inverter_type",
        "schattenmanagement": "shade_management",
        "notstromfähig": "notstromfaehig",
        "notstromfaehig": "notstromfaehig",
        "smart home": "smart_home",
        # Varianten für Modell/Bezeichnung
        "artikel": "model_name",
        "artikelname": "model_name",
        "produkt": "model_name",
        "produktname": "model_name",
        "modellbezeichnung": "model_name",
    }
    # Optional: konfigurierbare Alias-Mappings aus admin_settings laden und
    # mergen
    try:
        from database import load_admin_setting  # type: ignore
        cfg = load_admin_setting("module_pdf_alias_map", {}) or {}
        # Normiere Keys wie im Parser (klein + Whitespaces -> 1 Space)
        norm_cfg: dict[str, str] = {}
        for k, v in cfg.items():
            if not k or not v:
                continue
            nk = re.sub(r"\s+", " ", str(k).strip().lower())
            norm_cfg[nk] = str(v).strip()
        base.update(norm_cfg)
    except Exception:
        pass
    return base


def _build_module_warranty_text(row: dict[str, Any]) -> str | None:
    prod = row.get("product_warranty_years")
    perf = row.get("performance_warranty_text")
    parts: list[str] = []
    if prod not in (None, ""):
        try:
            f = _to_number(prod)
            parts.append(
                f"{int(f) if f is not None else prod} Jahre Produktgarantie")
        except Exception:
            parts.append(f"{prod}")
    if perf not in (None, ""):
        # übernehme Text roh (kann Jahre/Prozent enthalten)
        # gängiges Format: "30 Jahre / 87%"
        parts.append(f"{perf}" if isinstance(perf, str) else str(perf))
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} | {parts[1]}"


def parse_pdf_tables(pdf_path: str) -> list[dict[str, Any]]:
    import pdfplumber
    rows: list[dict[str, Any]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for t in tables or []:
                if not t or len(t) < 2:
                    continue
                # finde Header-Zeile: erste Reihe mit >=3 nichtleeren Zellen
                header = None
                data_rows = []
                for ridx, row in enumerate(t):
                    non_empty = [c for c in row if c not in (None, "", " ")]
                    if header is None and len(non_empty) >= 3:
                        header = [_clean_header(h) for h in row]
                        continue
                    if header is not None:
                        data_rows.append(row)
                if not header or not data_rows:
                    continue
                # baue dicts
                for r in data_rows:
                    d: dict[str, Any] = {}
                    for i, h in enumerate(header):
                        key = h.strip()
                        val = r[i] if i < len(r) else None
                        if key:
                            d[key] = None if val is None else str(val).strip()
                    if d:
                        rows.append(d)
    return rows


def normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    cmap = _canonical_map()
    out: dict[str, Any] = {}
    # 1) Kanonische Felder mappen
    for k, v in raw.items():
        low = k.strip().lower()
        low = re.sub(r"\s+", " ", low)
        if low in cmap:
            out[cmap[low]] = v
    # 2) Numerik vereinheitlichen
    if out.get("capacity_w"):
        num = _to_number(out["capacity_w"])
        if num is not None:
            out["capacity_w"] = num
    if out.get("product_warranty_years"):
        num = _to_number(out["product_warranty_years"])
        if num is not None:
            out["product_warranty_years"] = int(num)
    # 3) Garantietext kombinieren
    mw = _build_module_warranty_text(out)
    if mw:
        out["module_warranty_text"] = mw
    return out


def import_from_pdf(pdf_path: str, default_category: str |
                    None = None) -> dict[str, Any]:
    if not os.path.exists(pdf_path):
        print(f"PDF nicht gefunden: {pdf_path}")
        return {"ok": False, "error": "not_found", "pdf": pdf_path}
    try:
        raw_rows = parse_pdf_tables(pdf_path)
        if not raw_rows:
            print("Keine Tabellen erkannt. Bitte Import-Mapping anpassen.")
            return {"ok": False, "error": "no_tables", "pdf": pdf_path}
        print(f"Gefundene Zeilen: {len(raw_rows)}")
        total_rows = 0
        ensured_products = 0
        updated_products = 0
        upserted_attributes = 0
        skipped_no_model = 0
        skipped_rows: list[dict[str, Any]] = []

        for raw in raw_rows:
            total_rows += 1
            norm = normalize_row(raw)
            # Modellname ermitteln
            model = norm.get("model_name")
            if not model:
                # ohne explizites Mapping für model_name überspringen
                print(
                    "SKIP: Keine Modellspalte gemappt (füge Alias für 'model_name' im Admin-UI hinzu). Raw-Header:",
                    list(
                        raw.keys())[
                        :6],
                    '...')
                skipped_no_model += 1
                skipped_rows.append(
                    {"reason": "no_model_name", "raw_headers": list(raw.keys())})
                continue
            brand = norm.get("brand")
            category = (norm.get("category")
                        or default_category or "Modul").strip()
            pid = ensure_product(category, str(model), brand)
            if not pid:
                skipped_rows.append(
                    {"reason": "ensure_product_failed", "model": model})
                continue
            ensured_products += 1
            # Produkte DB-Spalten updaten (nur wenn vorhanden)
            to_upd: dict[str, Any] = {}
            for col in (
                "cell_technology",
                "module_structure",
                "cell_type",
                "version",
                "module_warranty_text",
                    "capacity_w"):
                if col in norm and norm[col] not in (None, ""):
                    to_upd[col] = norm[col]
            # Produktgarantie in warranty_years, falls vorhanden
            if norm.get("product_warranty_years") not in (None, ""):
                to_upd["warranty_years"] = norm["product_warranty_years"]
            if to_upd:
                update_product(pid, to_upd)
                updated_products += 1
            # Zusätzlich: kanonische Keys auch als Attribute hinterlegen
            for ckey in (
                "cell_technology",
                "module_structure",
                "cell_type",
                "version",
                "module_warranty_text",
                    "capacity_w"):
                if norm.get(ckey) not in (None, ""):
                    if upsert_attribute(pid, category, ckey, str(norm[ckey])):
                        upserted_attributes += 1
            # Alle Roh-Attribute zusätzlich flexibel speichern
            # Key: original Header, Value: Zelleninhalt
            for k, v in raw.items():
                if k and v not in (None, ""):
                    if upsert_attribute(pid, category, k, str(v)):
                        upserted_attributes += 1
        print("Import abgeschlossen.")
        return {
            "ok": True,
            "pdf": pdf_path,
            "total_rows": total_rows,
            "ensured_products": ensured_products,
            "updated_products": updated_products,
            "upserted_attributes": upserted_attributes,
            "skipped_no_model": skipped_no_model,
            "skipped_rows": skipped_rows,
        }
    except Exception as e:
        print(f"Fehler beim Import: {e}")
        traceback.print_exc()
        return {"ok": False, "error": str(e), "pdf": pdf_path}


def import_from_path(path: str, default_category: str |
                     None = None) -> dict[str, Any]:
    """Importiert aus Datei oder allen PDFs in einem Verzeichnis. Liefert Gesamtsummary."""
    p = Path(path)
    results: list[dict[str, Any]] = []
    if p.is_dir():
        pdfs = sorted([str(x) for x in p.glob("**/*.pdf")])
        for pdf in pdfs:
            results.append(
                import_from_pdf(
                    pdf, default_category=default_category))
    elif p.is_file() and p.suffix.lower() == ".pdf":
        results.append(
            import_from_pdf(
                str(p),
                default_category=default_category))
    else:
        return {"ok": False, "error": "path_not_pdf_or_dir", "path": path}

    # Aggregation
    agg = {
        "ok": any(r.get("ok") for r in results),
        "files": len(results),
        "total_rows": sum(r.get("total_rows", 0) for r in results),
        "ensured_products": sum(r.get("ensured_products", 0) for r in results),
        "updated_products": sum(r.get("updated_products", 0) for r in results),
        "upserted_attributes": sum(r.get("upserted_attributes", 0) for r in results),
        "skipped_no_model": sum(r.get("skipped_no_model", 0) for r in results),
        "details": results,
    }
    return agg


if __name__ == "__main__":
    arg = sys.argv[1] if len(
        sys.argv) > 1 else os.path.join(
        os.path.expanduser("~"),
        "Desktop",
        "modul.pdf")
    summary = import_from_path(arg)
    print("SUMMARY:", summary)
