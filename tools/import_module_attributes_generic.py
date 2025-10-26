# tools/import_module_attributes_generic.py
# Generischer Importer: Modul-Attribute aus diversen Formaten
# (PDF/CSV/XLSX/JSON/YAML/TXT/MD/JPG/PNG)
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Reuse existing PDF importer helpers when possible
try:
    from tools.import_module_attributes_from_pdf import (
        _canonical_map as _pdf_canonical_map,  # type: ignore
    )
    from tools.import_module_attributes_from_pdf import (
        import_from_path as import_pdf_path,
    )
except Exception:
    import_pdf_path = None  # type: ignore

    def _pdf_canonical_map():
        return {}

# DB helpers
try:
    from product_db import (
        add_product,
        get_product_by_model_name,
        list_products,
        update_product,
    )
except Exception:
    get_product_by_model_name = None  # type: ignore
    add_product = None  # type: ignore
    update_product = None  # type: ignore
    list_products = None  # type: ignore

try:
    from product_attributes import upsert_attribute
except Exception:
    upsert_attribute = None  # type: ignore


def _canonical_map() -> dict[str, str]:
    base = _pdf_canonical_map() or {}
    if not base:
        base = {}
    # Fallback-Aliasse, wenn PDF-Map nicht geladen werden konnte
    base.setdefault("kategorie", "category")
    base.setdefault("kategorie:", "category")
    base.setdefault("category", "category")
    base.setdefault("modell | typ", "model_name")
    base.setdefault("modell | typ:", "model_name")
    base.setdefault("modell", "model_name")
    base.setdefault("modell/typ", "model_name")
    base.setdefault("modell-typ", "model_name")
    base.setdefault("typ", "model_name")
    base.setdefault("hersteller", "brand")
    base.setdefault("hersteller:", "brand")
    base.setdefault("modulleistung", "capacity_w")
    base.setdefault("leistung pro pv-modul", "capacity_w")
    base.setdefault("leistung pro pv modul", "capacity_w")
    base.setdefault("leistung kw", "power_kw")
    base.setdefault("leistung (kw)", "power_kw")
    base.setdefault("nennleistung", "power_kw")
    base.setdefault("wechselrichterleistung", "power_kw")
    base.setdefault("kapazität kwh", "storage_power_kw")
    base.setdefault("kapazitaet kwh", "storage_power_kw")
    base.setdefault("speicherkapazität", "storage_power_kw")
    base.setdefault("speicherkapazitaet", "storage_power_kw")
    base.setdefault("nutzbare kapazität", "storage_power_kw")
    base.setdefault("nutzbare kapazitaet", "storage_power_kw")
    base.setdefault("zyklen", "max_cycles")
    base.setdefault("max. ladezyklen", "max_cycles")
    base.setdefault("zellentechnologie", "cell_technology")
    base.setdefault("zellentechnologie:", "cell_technology")
    base.setdefault("pv zellentechnologie", "cell_technology")
    base.setdefault("pv-zellentechnologie", "cell_technology")
    base.setdefault("pv-zellentechnologie:", "cell_technology")
    base.setdefault("zellentechnologie", "cell_technology")
    base.setdefault("solarzellen", "cell_type")
    base.setdefault("solarzellen:", "cell_type")
    base.setdefault("version", "version")
    base.setdefault("version:", "version")
    # Wechselrichter-spezifisch
    base.setdefault("typ wechselrichter", "inverter_type")
    base.setdefault("typ wechselrichter:", "inverter_type")
    base.setdefault("schattenmanagement", "shade_management")
    base.setdefault("schattenmanagement:", "shade_management")
    base.setdefault("notstromfähig", "notstromfaehig")
    base.setdefault("notstromfähig:", "notstromfaehig")
    base.setdefault("notstromfaehig", "notstromfaehig")
    base.setdefault("smart home", "smart_home")
    base.setdefault("smart home:", "smart_home")
    # Weitere relevante Felder (werden als Attribute gespeichert)
    base.setdefault("erweiterungsmodul", "expansion_module")
    base.setdefault("erweiterungsmodul:", "expansion_module")
    base.setdefault("erweiterungs-modul", "expansion_module")
    base.setdefault("max. speichergröße", "max_storage_size")
    base.setdefault("max. speichergröße:", "max_storage_size")
    base.setdefault("max. speichergroesse", "max_storage_size")
    base.setdefault("max speichergröße", "max_storage_size")
    base.setdefault("max speichergroesse", "max_storage_size")
    base.setdefault("outdoorfähig", "outdoorfaehig")
    base.setdefault("outdoorfähig:", "outdoorfaehig")
    base.setdefault("outdoorfaehig", "outdoorfaehig")
    base.setdefault("speicherkapazität", "storage_power_kw")
    base.setdefault("speicherkapazität:", "storage_power_kw")
    base.setdefault("leistung pro pv-modul", "capacity_w")
    base.setdefault("leistung pro pv-modul:", "capacity_w")
    base.setdefault("pv-zellentechnologie:", "cell_technology")
    base.setdefault("modulaufbau", "module_structure")
    base.setdefault("modulaufbau:", "module_structure")
    base.setdefault("wechselrichterleistung:", "power_kw")
    # Datenblatt-Link/Datei
    base.setdefault("produktdatenblatt", "datasheet_link_db_path")
    base.setdefault("datenblatt", "datasheet_link_db_path")
    base.setdefault("datasheet", "datasheet_link_db_path")
    return base


def _to_number(val: Any) -> float | None:
    try:
        s = str(val)
    except Exception:
        return None
    s = s.strip()
    if not s:
        return None
    import re
    s = re.sub(r"[^0-9,\.\-]", "", s)
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


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
            parts.append(str(prod))
    if perf not in (None, ""):
        parts.append(str(perf))
    if not parts:
        return None
    return parts[0] if len(parts) == 1 else f"{parts[0]} | {parts[1]}"


def _ensure_product(category: str, model_name: str,
                    brand: str | None = None) -> tuple[int | None, bool]:
    if not get_product_by_model_name or not add_product or not update_product:
        return None, False
    rec = get_product_by_model_name(model_name)
    if rec:
        pid = int(rec.get("id"))
        to_upd: dict[str, Any] = {}
        if brand and not rec.get("brand"):
            to_upd["brand"] = brand
        if to_upd:
            update_product(pid, to_upd)
        return pid, True
    # Fuzzy Match: whitespace/punktuation entfernen

    def _norm_key(s: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]", "", s.lower())

    def _strip_power_suffix(s: str) -> str:
        import re
        # Entferne typische Leistungsendungen wie " 440w", " 460 wp", "-460 Wp"
        return re.sub(
            r"[\s\-]*\b\d{3,4}\s*(wp|w)\b\s*$",
            "",
            s,
            flags=re.IGNORECASE).strip()

    def _tokens(s: str) -> set:
        import re
        toks = re.findall(r"[a-z0-9]+", s.lower())
        stop = {"pv", "wp", "w"}
        return {t for t in toks if t not in stop and not t.isdigit()
                and len(t) >= 2}

    def _similar(a: str, b: str) -> bool:
        A = _tokens(_strip_power_suffix(a))
        B = _tokens(_strip_power_suffix(b))
        if not A or not B:
            return False
        inter = A & B
        if len(inter) >= 2 and (A <= B or B <= A):
            return True
        jacc = len(inter) / max(1, len(A | B))
        return jacc >= 0.7
    try:
        if list_products:
            existing = list_products(category)
        else:
            existing = []
    except Exception:
        existing = []
    key_target = _norm_key(model_name)
    key_target_base = _norm_key(_strip_power_suffix(model_name))
    candidates = {key_target, key_target_base}
    if brand:
        bm = f"{brand} {model_name}".strip()
        mb = f"{model_name} {brand}".strip()
        candidates.update({_norm_key(bm),
                           _norm_key(_strip_power_suffix(bm)),
                           _norm_key(mb),
                           _norm_key(_strip_power_suffix(mb))})
    for p in (existing or []):
        name = p.get("model_name") or ""
        nk = _norm_key(str(name))
        if nk in candidates or _norm_key(
            _strip_power_suffix(
                str(name))) in candidates:
            pid = int(p.get("id"))
            to_upd: dict[str, Any] = {}
            if brand and not p.get("brand"):
                to_upd["brand"] = brand
            if to_upd:
                update_product(pid, to_upd)
            return pid, True
        # Tokenbasierter Fallback: vergleiche (Brand + Model)
        bm_exist = f"{p.get('brand') or ''} {name}".strip()
        bm_target = f"{brand or ''} {model_name}".strip()
        if _similar(bm_exist, bm_target):
            pid = int(p.get("id"))
            to_upd: dict[str, Any] = {}
            if brand and not p.get("brand"):
                to_upd["brand"] = brand
            if to_upd:
                update_product(pid, to_upd)
            return pid, True
    # Neu anlegen, wenn nix passt
    new_id = add_product(
        {"category": category, "model_name": model_name, "brand": brand or ""})
    return new_id, False


def _normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
    cmap = _canonical_map()
    out: dict[str, Any] = {}
    orig_mapped: dict[str, Any] = {}
    for k, v in raw.items():
        if k is None:
            continue
        low = str(k).strip().lower()
        low = " ".join(low.split())
        # Entferne abschließende Doppelpunkte (z. B. "Kategorie:")
        try:
            import re as _re
            low = _re.sub(r"[:：]+$", "", low).strip()
        except Exception:
            pass
        if low in cmap:
            # trim Strings
            if isinstance(v, str):
                v = v.strip()
            target = cmap[low]
            orig_mapped[target] = v
            # Spezialfall: Garantie mit zwei Zahlen (z. B. "25 / 30")
            if target == "product_warranty_years" and isinstance(v, str):
                import re
                nums = re.findall(r"\d{1,3}", v)
                if nums:
                    out["product_warranty_years"] = int(nums[0])
                    if len(nums) >= 2:
                        out["performance_warranty_text"] = f"{
                            nums[1]} Jahre Leistungsgarantie"
                else:
                    out["product_warranty_years"] = v
            else:
                out[target] = v
        else:
            # keep original too (raw attr)
            out.setdefault("__raw__", {})[str(k)] = (
                v.strip() if isinstance(v, str) else v)
    # normalize numeric
    if out.get("capacity_w") is not None:
        num = _to_number(out["capacity_w"])
        if num is not None:
            out["capacity_w"] = num
    if out.get("product_warranty_years") is not None:
        num = _to_number(out["product_warranty_years"])
        if num is not None:
            out["product_warranty_years"] = int(num)
    # Version: führende/umgebende Anführungszeichen entfernen
    if isinstance(out.get("version"), str):
        vv = out.get("version")
        if vv and len(vv) >= 2 and (
            (vv.startswith('"') and vv.endswith('"')) or (
                vv.startswith("'") and vv.endswith("'"))):
            out["version"] = vv[1:-1].strip()
    mw = _build_module_warranty_text(out)
    if mw:
        out["module_warranty_text"] = mw
    return out


def _process_record(row: dict[str, Any], *, default_category: str = "Modul") -> dict[str, Any]:
    summary = {
        "ensured": 0,
        "ensured_existing": 0,
        "ensured_created": 0,
        "updated": 0,
        "upserted": 0,
        "skipped": 0,
        "reason": None,
        "pid": None,
        "model": None}
    norm = _normalize_record(row)
    model = norm.get("model_name")
    if not model:
        summary["skipped"] = 1
        summary["reason"] = "no_model_name"
        return summary
    brand = norm.get("brand")
    category = (norm.get("category") or default_category or "Modul").strip()
    pid, existed = _ensure_product(category, str(model), brand)
    if not pid:
        summary["skipped"] = 1
        summary["reason"] = "ensure_product_failed"
        return summary
    summary["ensured"] = 1
    if existed:
        summary["ensured_existing"] = 1
    else:
        summary["ensured_created"] = 1
    summary["pid"] = pid
    summary["model"] = str(model)
    # update product canonical fields
    to_upd: dict[str, Any] = {}

    def _is_blank(v: Any) -> bool:
        return v is None or (
            isinstance(
                v, str) and v.strip().lower() in (
                "", "-", "nan", "none"))
    for col in (
        "cell_technology",
        "module_structure",
        "cell_type",
        "version",
        "module_warranty_text",
        "capacity_w",
        "power_kw",
        "storage_power_kw",
            "max_cycles"):
        if col in norm and not _is_blank(norm[col]):
            to_upd[col] = norm[col]
    if not _is_blank(norm.get("product_warranty_years")):
        to_upd["warranty_years"] = norm["product_warranty_years"]
    if not _is_blank(norm.get("datasheet_link_db_path")):
        to_upd["datasheet_link_db_path"] = norm["datasheet_link_db_path"]
    if to_upd:
        update_product(pid, to_upd)
        summary["updated"] = 1
    # upsert canonical attributes
    if upsert_attribute:
        upserted_keys: set = set()
        # 1) bevorzugte bekannte Felder
        for ckey in (
            "cell_technology",
            "module_structure",
            "cell_type",
            "version",
            "module_warranty_text",
            "capacity_w",
            "power_kw",
            "storage_power_kw",
            "max_cycles",
            "expansion_module",
            "max_storage_size",
            "outdoorfaehig",
            "inverter_type",
            "shade_management",
            "notstromfaehig",
                "smart_home"):
            if not _is_blank(norm.get(ckey)):
                if upsert_attribute(pid, category, ckey, str(norm[ckey])):
                    summary["upserted"] += 1
                upserted_keys.add(ckey)
        # 2) alle weiteren normalisierten Felder (breites XLSX-Schema)
        for k, v in norm.items():
            if k in (
                "__raw__",
                "model_name",
                "brand",
                "category",
                    "product_warranty_years"):
                continue
            if k in upserted_keys:
                continue
            if not _is_blank(v):
                if upsert_attribute(pid, category, k, str(v)):
                    summary["upserted"] += 1
        # raw
        for rk, rv in (norm.get("__raw__") or {}).items():
            if not _is_blank(rv):
                # Skip typische Platzhalter (bereits im Helper)
                if upsert_attribute(pid, category, str(rk), str(rv)):
                    summary["upserted"] += 1
    return summary


def _import_csv_xlsx(path: str, *, default_category: str |
                     None = None) -> dict[str, Any]:
    try:
        import pandas as pd
    except Exception:
        return {"ok": False, "error": "pandas_missing", "path": path}
    total_rows = 0
    ensured = 0
    ensured_existing = 0
    ensured_created = 0
    updated = 0
    upserted = 0
    skipped = 0
    details: list[dict[str, Any]] = []
    mapping_report: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    try:
        sheets_info: list[dict[str, Any]] = []
        if path.lower().endswith(".xlsx"):
            dfs = pd.read_excel(path, sheet_name=None)
            file_format = "xlsx"
            if not dfs:
                return {"ok": False, "error": "empty", "path": path}
            for sheet_name, df in dfs.items():
                if df is None or df.empty:
                    continue
                orig_cols = list(df.columns)
                cmap = _canonical_map()
                mapping_report_sheet: list[dict[str, Any]] = []
                samples_sheet: list[dict[str, Any]] = []
                for h in orig_cols:
                    nh = str(h).strip().lower()
                    nh = " ".join(nh.split())
                    mapping_report_sheet.append(
                        {"header": str(h), "normalized": nh, "mapped_to": cmap.get(nh)})
                ensured_s = updated_s = upserted_s = skipped_s = total_s = 0
                for _, row in df.iterrows():
                    total_rows += 1
                    total_s += 1
                    rec = {k: (row[k] if k in row else None)
                           for k in orig_cols}
                    if len(samples_sheet) < 5:
                        norm = _normalize_record(rec)
                        samples_sheet.append(
                            {
                                k: norm.get(k) for k in [
                                    "model_name",
                                    "brand",
                                    "capacity_w",
                                    "cell_technology",
                                    "module_structure",
                                    "cell_type",
                                    "version",
                                    "product_warranty_years",
                                    "module_warranty_text"]})
                    s = _process_record(
                        rec, default_category=(
                            default_category or "Modul"))
                    ensured += s["ensured"]
                    ensured_existing += s.get("ensured_existing", 0)
                    ensured_created += s.get("ensured_created", 0)
                    updated += s["updated"]
                    upserted += s["upserted"]
                    skipped += s["skipped"]
                    ensured_s += s["ensured"]
                    updated_s += s["updated"]
                    upserted_s += s["upserted"]
                    skipped_s += s["skipped"]
                    if s.get("reason"):
                        details.append({"file": os.path.basename(
                            path), "sheet": sheet_name, "reason": s["reason"]})
                    else:
                        details.append({"file": os.path.basename(path), "sheet": sheet_name, "model": s.get(
                            "model"), "pid": s.get("pid"), "existed": bool(s.get("ensured_existing"))})
                sheets_info.append({
                    "name": sheet_name,
                    "headers": orig_cols,
                    "mapping": mapping_report_sheet,
                    "samples": samples_sheet,
                    "total_rows": total_s,
                    "ensured": ensured_s,
                    "updated": updated_s,
                    "upserted": upserted_s,
                    "skipped": skipped_s,
                })
        else:
            # CSV: versuchen Auto-Parsing
            try:
                df = pd.read_csv(path, sep=None, engine='python')
                file_format = "csv"
            except Exception:
                df = pd.read_csv(path, sep=';')
                file_format = "csv"
            if df is None or df.empty:
                return {"ok": False, "error": "empty", "path": path}
            orig_cols = list(df.columns)
            cmap = _canonical_map()
            for h in orig_cols:
                nh = str(h).strip().lower()
                nh = " ".join(nh.split())
                mapping_report.append(
                    {"header": str(h), "normalized": nh, "mapped_to": cmap.get(nh)})
            for _, row in df.iterrows():
                total_rows += 1
                rec = {k: (row[k] if k in row else None) for k in orig_cols}
                if len(samples) < 5:
                    norm = _normalize_record(rec)
                    samples.append(
                        {
                            k: norm.get(k) for k in [
                                "model_name",
                                "brand",
                                "capacity_w",
                                "cell_technology",
                                "module_structure",
                                "cell_type",
                                "version",
                                "product_warranty_years",
                                "module_warranty_text"]})
                s = _process_record(
                    rec, default_category=(
                        default_category or "Modul"))
                ensured += s["ensured"]
                ensured_existing += s.get("ensured_existing", 0)
                ensured_created += s.get("ensured_created", 0)
                updated += s["updated"]
                upserted += s["upserted"]
                skipped += s["skipped"]
                if s.get("reason"):
                    details.append(
                        {"file": os.path.basename(path), "reason": s["reason"]})
                else:
                    details.append({"file": os.path.basename(path), "model": s.get(
                        "model"), "pid": s.get("pid"), "existed": bool(s.get("ensured_existing"))})
        result = {
            "ok": True,
            "path": path,
            "format": file_format,
            "headers": orig_cols if 'orig_cols' in locals() else None,
            "mapping": mapping_report,
            "samples": samples,
            "sheets": sheets_info if file_format == "xlsx" else None,
            "total_rows": total_rows,
            "ensured": ensured,
            "ensured_existing": ensured_existing,
            "ensured_created": ensured_created,
            "updated": updated,
            "upserted": upserted,
            "skipped": skipped,
            "details": details}
        return result
    except Exception as e:
        return {"ok": False, "error": str(e), "path": path}


def _load_json(path: str) -> list[dict[str, Any]]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def _load_yaml(path: str) -> list[dict[str, Any]]:
    try:
        import yaml  # PyYAML
    except Exception:
        return []
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def _flatten(d: dict[str, Any], parent_key: str = '',
             sep: str = '.') -> dict[str, Any]:
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _import_json_yaml(path: str, *, default_category: str |
                      None = None) -> dict[str, Any]:
    try:
        records = _load_json(path) if path.lower().endswith(
            ('.json',)) else _load_yaml(path)
    except Exception as e:
        return {"ok": False, "error": str(e), "path": path}
    total_rows = 0
    ensured = 0
    updated = 0
    upserted = 0
    skipped = 0
    details: list[dict[str, Any]] = []
    for rec in records:
        total_rows += 1
        flat = _flatten(rec) if isinstance(rec, dict) else {}
        # samples: 1-3 Beispiele
        # hier minimal: kein mapping-report, da freie JSON Strukturen
        s = _process_record(
            flat, default_category=(
                default_category or "Modul"))
        ensured += s["ensured"]
        updated += s["updated"]
        upserted += s["upserted"]
        skipped += s["skipped"]
        if s.get("reason"):
            details.append(
                {"file": os.path.basename(path), "reason": s["reason"]})
    return {
        "ok": True,
        "path": path,
        "format": "json" if path.lower().endswith('.json') else "yaml",
        "total_rows": total_rows,
        "ensured": ensured,
        "updated": updated,
        "upserted": upserted,
        "skipped": skipped,
        "details": details}


def _parse_kv_lines(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            out[k.strip()] = v.strip()
    return out


def _import_txt_md(path: str, *, default_category: str |
                   None = None) -> dict[str, Any]:
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception as e:
        return {"ok": False, "error": str(e), "path": path}
    # Einfach: gesamte Datei als ein Record aus key:value-Zeilen interpretieren
    rec = _parse_kv_lines(text)
    if not rec:
        return {"ok": False, "error": "no_kv_pairs", "path": path}
    s = _process_record(rec, default_category=(default_category or "Modul"))
    return {"ok": True,
            "path": path,
            "format": "txt" if path.lower().endswith('.txt') else "md",
            "total_rows": 1,
            "ensured": s["ensured"],
            "updated": s["updated"],
            "upserted": s["upserted"],
            "skipped": s["skipped"],
            "details": [{"reason": s.get("reason")}] if s.get("reason") else []}


def _import_image(path: str) -> dict[str, Any]:
    # Ohne OCR: Versuche Produktbild zu setzen, wenn ein Produkt mit exakt
    # gleichem Modellnamen wie Dateiname (ohne Endung) existiert
    stem = Path(path).stem
    if not get_product_by_model_name or not update_product:
        return {"ok": False, "error": "db_funcs_missing", "path": path}
    rec = get_product_by_model_name(stem)
    if not rec:
        return {
            "ok": True,
            "path": path,
            "note": "no_matching_product",
            "updated": 0}
    try:
        with open(path, 'rb') as f:
            b = f.read()
        import base64
        b64 = base64.b64encode(b).decode('utf-8')
        if update_product(int(rec['id']), {"image_base64": b64}):
            return {"ok": True, "path": path, "format": "image", "updated": 1}
        return {"ok": False, "path": path, "format": "image", "updated": 0}
    except Exception as e:
        return {"ok": False, "error": str(e), "path": path}


def import_any_from_path(
        path: str, *, default_category: str | None = None) -> dict[str, Any]:
    p = Path(path)
    results: list[dict[str, Any]] = []
    if p.is_dir():
        files = sorted([str(x) for x in p.rglob('*') if x.is_file()])
    elif p.is_file():
        files = [str(p)]
    else:
        return {"ok": False, "error": "path_invalid", "path": path}

    # Optional: erst PDFs mit dem bestehenden Importer laufen lassen (der kann
    # tiefgreifend Tabellen erkennen)
    pdfs = [f for f in files if f.lower().endswith('.pdf')]
    non_pdfs = [f for f in files if not f.lower().endswith('.pdf')]

    if import_pdf_path and pdfs:
        try:
            # PDFs separat: falls deren Importer Kategorie unterstützt, wird
            # sie dort berücksichtigt
            try:
                results.append(import_pdf_path(str(p if p.is_dir() else Path(
                    p).parent), default_category=(default_category or "Modul")))
            except TypeError:
                # Fallback: ältere Signatur ohne Kategorie
                results.append(import_pdf_path(
                    str(p if p.is_dir() else Path(p).parent)))
            # Achtung: Der PDF-Importer aggregiert selbst; wir fügen keine Einzel-PDF Ergebnisse hier hinzu, um Doppelbearbeitung zu vermeiden.
            # Entferne PDFs aus weiterer Verarbeitung
            non_pdfs = [f for f in non_pdfs if not f.lower().endswith('.pdf')]
        except Exception as e:
            results.append(
                {"ok": False, "error": f"pdf_import_failed: {e}", "path": path})

    for f in non_pdfs:
        lower = f.lower()
        try:
            if lower.endswith(('.csv', '.xlsx')):
                results.append(
                    _import_csv_xlsx(
                        f, default_category=default_category))
            elif lower.endswith(('.json',)) or lower.endswith(('.yml', '.yaml')):
                results.append(
                    _import_json_yaml(
                        f, default_category=default_category))
            elif lower.endswith(('.txt', '.md')):
                results.append(
                    _import_txt_md(
                        f, default_category=default_category))
            elif lower.endswith(('.jpg', '.jpeg', '.png')):
                results.append(_import_image(f))
            else:
                results.append(
                    {"ok": False, "error": "unsupported_extension", "path": f})
        except Exception as e:
            results.append({"ok": False, "error": str(e), "path": f})

    # Aggregation
    agg = {
        "ok": any(r.get("ok") for r in results),
        "files": len(results),
        "total_rows": sum(r.get("total_rows", 0) for r in results),
        "ensured_products": sum(r.get("ensured", 0) for r in results),
        "updated_products": sum(r.get("updated", 0) for r in results),
        "upserted_attributes": sum(r.get("upserted", 0) for r in results),
        "skipped": sum(r.get("skipped", 0) for r in results),
        "details": results,
    }
    return agg


if __name__ == '__main__':
    import sys
    arg = sys.argv[1] if len(
        sys.argv) > 1 else os.path.join(
        os.getcwd(), 'data', 'imports')
    summary = import_any_from_path(arg)
    print('SUMMARY_ANY:', summary)
