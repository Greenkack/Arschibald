# -*- coding: utf-8 -*-
"""
waermepumpen_parser.py
--------------------------------
CLI-Parser für lokal gespeicherte HTML/ZIP-Inhalte (Spiegel von heizungsdiscount24.de).
Extrahiert ausschließlich Produkte der Marken FISMAN, PODEROS, PHYLAND und nur die Typen MONOBLOC/HYBRID.
Erzeugt CSV/JSON zur Verwendung in der App.
"""
import os, re, json, argparse, zipfile

ALLOWED_BRANDS = ["FISMAN", "PODEROS", "PHYLAND"]
ALLOWED_TYPES = ["MONOBLOC", "HYBRID"]

# Mapping für Markenerkennung im HTML (anpassbar)
BRAND_MAP = {
    "FISMAN":  ["fisman", "viessmann", "viesmann", "vissmann", "vießmann"],
    "PODEROS": ["poderos", "buderus", "boderus"],
    "PHYLAND": ["phyland", "vaillant", "vailant", "valliant"]
}
TYPE_KEYS = ["monobloc", "monoblock", "mono block", "mono-bloc", "hybrid", "hybridsystem", "hybrid-"]

def is_html(path): return path.lower().endswith((".html",".htm",".xhtml"))

def guess_brand(raw_lower):
    for mapped, variants in BRAND_MAP.items():
        if any(v in raw_lower for v in variants):
            return mapped
    return None

def guess_type(raw_lower):
    for k in TYPE_KEYS:
        if k in raw_lower:
            return "HYBRID" if "hybrid" in k else "MONOBLOC"
    return None

def extract_jsonld_blocks(raw):
    return re.findall(r'<script[^>]+type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>',
                      raw, flags=re.IGNORECASE|re.DOTALL)

def parse_json_safe(txt):
    try: return json.loads(txt)
    except Exception:
        try: return json.loads(txt.strip().strip(';'))
        except Exception: return None

def walk_json(d, collector):
    if isinstance(d, dict):
        if not collector["name"] and isinstance(d.get("name"), str):
            collector["name"] = d["name"].strip()
        if collector["sku"] is None and d.get("sku") is not None:
            collector["sku"] = str(d["sku"]).strip()
        if "price" in d:
            try:
                p = float(str(d["price"]).replace(",", "."))
                if 200 <= p <= 200000: collector["prices"].append(p)
            except: pass
        for v in d.values(): walk_json(v, collector)
    elif isinstance(d, list):
        for it in d: walk_json(it, collector)

def strip_tags(html): return re.sub(r'<[^>]+>', ' ', html)

def extract_title_h1(raw):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', raw, flags=re.IGNORECASE|re.DOTALL)
    if m: return strip_tags(m.group(1)).strip()
    mt = re.search(r'<title[^>]*>(.*?)</title>', raw, flags=re.IGNORECASE|re.DOTALL)
    return strip_tags(mt.group(1)).strip()[:120] if mt else None

def find_prices(text):
    ps = []
    for m in re.finditer(r'(?:€\s*|EUR\s*)(\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})?|\d{1,6}(?:,\d{2})?)', text):
        raw = m.group(1).replace(" ", "").replace("\u00A0","")
        norm = raw.replace(".", "").replace(",", ".")
        try:
            val = float(norm)
            if 200 <= val <= 200000: ps.append(val)
        except: pass
    return min(ps) if ps else None

def find_kw(text):
    out = set()
    for m in re.finditer(r'(\d{1,3}(?:[.,]\d{1,2})?)\s*kW', text, flags=re.IGNORECASE):
        try:
            v = float(m.group(1).replace(",", "."))
            if 0.5 <= v <= 200: out.add(round(v, 2))
        except: pass
    return sorted(out)

def find_scop(text):
    m = re.search(r'\bSCOP\b[^0-9]*([0-9]+(?:[.,][0-9]+)?)', text, flags=re.IGNORECASE)
    return float(m.group(1).replace(",", ".")) if m else None

def find_max_flow(text):
    m = re.search(r'(?:max(?:\.|imale)?\s*(?:Vorlauftemperatur|Vorlauf)|Vorlauf\s*max)[^0-9]{0,20}([0-9]{2,3})\s*[°º]?\s*C',
                  text, flags=re.IGNORECASE)
    if m:
        try:
            val = int(m.group(1))
            if 30 <= val <= 95: return val
        except: pass
    return None

def find_list_after_heading(raw, keywords):
    out, lower = [], raw.lower()
    idx = next((lower.find(k) for k in keywords if lower.find(k) != -1), -1)
    if idx == -1: return out
    segment = raw[idx: idx+8000]
    for m in re.finditer(r'<li[^>]*>(.*?)</li>', segment, flags=re.IGNORECASE|re.DOTALL):
        t = strip_tags(m.group(1)).strip()
        if t: out.append(t[:200])
    return out

def find_install_costs(text):
    costs = []
    for m in re.finditer(r'(montage|installation|einbau)[^€]{0,80}(€\s*\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})?|\d{1,6}(?:,\d{2})?\s*€)', text, flags=re.IGNORECASE):
        raw = m.group(2).replace("€","").replace(" ", "").replace("\u00A0","")
        norm = raw.replace(".", "").replace(",", ".")
        try:
            val = float(norm)
            if 50 <= val <= 50000: costs.append(val)
        except: pass
    return min(costs) if costs else None

def iter_paths(dir_root):
    for root, _, files in os.walk(dir_root):
        for fn in files:
            if is_html(fn): yield os.path.join(root, fn)

def parse_root(dir_root):
    rows, candidates = [], 0
    for fpath in iter_paths(dir_root):
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read(1500000)
        except Exception:
            try:
                with open(fpath, "r", encoding="latin-1", errors="ignore") as f:
                    raw = f.read(1500000)
            except Exception:
                continue
        low = raw.lower()
        if not ("wärmepumpe" in low or "waermepumpe" in low or "heat pump" in low): continue
        brand = guess_brand(low)
        if not brand or brand not in ALLOWED_BRANDS: continue
        typ = guess_type(low)
        if typ not in ALLOWED_TYPES: continue
        candidates += 1

        name, sku, prices_ld = None, None, []
        for block in extract_jsonld_blocks(raw):
            data = parse_json_safe(block)
            if data is None: continue
            col = {"name": None, "sku": None, "prices": []}
            walk_json(data, col)
            name = name or col["name"]
            sku = sku or col["sku"]
            prices_ld.extend(col["prices"])

        title = extract_title_h1(raw)
        product_name = name or title
        text = strip_tags(raw)
        price_plain = find_prices(text)
        price_final = min(prices_ld+[price_plain]) if (prices_ld or price_plain) else None

        row = {
            "brand": brand,
            "type": typ,
            "product_name": product_name,
            "sku": sku,
            "sizes_kw": find_kw(text),
            "scop": find_scop(text),
            "max_flow_temp_c": find_max_flow(text),
            "price_eur": price_final,
            "install_cost_eur": find_install_costs(text),
            "lieferumfang": find_list_after_heading(raw, ["lieferumfang","umfang","im set enthalten","lieferinhalt"]),
            "zubehoer": find_list_after_heading(raw, ["zubehör","zubehoer","optional zubehör","optional"]),
            "reviews_count": (int(re.search(r'bewertungen?\s*\(?(\d+)\)?', text.lower()).group(1))
                              if re.search(r'bewertungen?\s*\(?(\d+)\)?', text.lower()) else None),
            "source_file": os.path.relpath(fpath, dir_root)
        }
        rows.append(row)
    return rows, candidates

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", dest="zip_path", help="Pfad zu einer ZIP mit HTML-Dateien")
    ap.add_argument("--dir", dest="dir_path", help="Pfad zu einem Ordner mit HTML-Dateien")
    ap.add_argument("--out", dest="out_path", required=True, help="Ausgabedatei (.json oder .csv)")
    args = ap.parse_args()

    work_dir, temp_dir = None, None
    if args.zip_path:
        if not os.path.exists(args.zip_path):
            raise SystemExit("ZIP nicht gefunden: %s" % args.zip_path)
        temp_dir = os.path.join(os.path.dirname(args.out_path), "_extract_tmp")
        os.makedirs(temp_dir, exist_ok=True)
        with zipfile.ZipFile(args.zip_path, 'r') as zf:
            zf.extractall(temp_dir)
        work_dir = temp_dir
    elif args.dir_path:
        work_dir = args.dir_path
        if not os.path.isdir(work_dir):
            raise SystemExit("Verzeichnis nicht gefunden: %s" % work_dir)
    else:
        raise SystemExit("Bitte --zip oder --dir angeben.")

    rows, candidates = parse_root(work_dir)
    if not rows:
        print("Keine passenden Produkte gefunden. Kandidaten-Dateien:", candidates)

    out = args.out_path
    if out.lower().endswith(".json"):
        grouped = {}
        for r in rows:
            grouped.setdefault(r["brand"], {}).setdefault(r["type"], []).append(r)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(grouped, f, ensure_ascii=False, indent=2)
        print("JSON gespeichert:", out)
    elif out.lower().endswith(".csv"):
        import pandas as pd
        import numpy as np
        df = pd.DataFrame(rows)
        df.to_csv(out, index=False)
        print("CSV gespeichert:", out)
    else:
        raise SystemExit("Dateiendung nicht erkannt. Bitte .json oder .csv verwenden.")

if __name__ == "__main__":
    main()
