"""
TXT-zu-PDF Integration für das Hauptsystem
Ersetzt die komplexe PDF-Generierung durch die einfache TXT-basierte Lösung

Autor: GitHub Copilot
Datum: 28.07.2025
"""

import os
import re
import subprocess
import sys
import traceback
from typing import Any


def generate_pdf_from_txt_files(
    project_data: dict[str, Any] = None,
    analysis_results: dict[str, Any] = None,
    **kwargs
) -> bytes | None:
    """
    Generiert PDF aus TXT-Dateien im input-Ordner
    
    Args:
        project_data: Projektdaten (werden für künftige Erweiterungen verwendet)
        analysis_results: Analyseergebnisse (werden für künftige Erweiterungen verwendet)
        **kwargs: Weitere Parameter (für Kompatibilität)
    
    Returns:
        bytes: PDF-Bytes oder None bei Fehler
    """
    try:
        # Pfade definieren
        base_dir = os.getcwd()
        pdf_script = os.path.join(base_dir, "pdf_erstellen_komplett.py")
        output_pdf = os.path.join(base_dir, "recreated_full.pdf")

        # Prüfen ob das Script existiert
        if not os.path.exists(pdf_script):
            print(f"❌ PDF-Script nicht gefunden: {pdf_script}")
            return None

        # Prüfen ob input-Ordner existiert
        input_dir = os.path.join(base_dir, "input")
        if not os.path.exists(input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {input_dir}")
            return None

        # Dynamische Platzhalter in den TXT-Dateien ersetzen
        update_txt_files_from_project_data(project_data or {}, analysis_results or {})

        print("📄 Starte TXT-zu-PDF Generierung...")

        # PDF-Script ausführen
        result = subprocess.run(
            [sys.executable, pdf_script],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ PDF-Script Fehler: {result.stderr}")
            return None

        # Prüfen ob PDF erstellt wurde
        if not os.path.exists(output_pdf):
            print(f"❌ PDF-Datei nicht erstellt: {output_pdf}")
            return None

        # PDF-Bytes lesen
        with open(output_pdf, 'rb') as f:
            pdf_bytes = f.read()

        print("✅ PDF erfolgreich aus TXT-Dateien erstellt!")
        return pdf_bytes

    except subprocess.TimeoutExpired:
        print("❌ PDF-Generierung Timeout nach 30 Sekunden")
        return None
    except Exception as e:
        print(f"❌ Fehler bei TXT-zu-PDF Generierung: {e}")
        print(traceback.format_exc())
        return None

def update_txt_files_from_project_data(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any]
) -> bool:
    """
    Aktualisiert TXT-Dateien im input-Ordner basierend auf den Projektdaten
    
    Args:
        project_data: Aktuelle Projektdaten
        analysis_results: Aktuelle Analyseergebnisse
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        base_dir = os.getcwd()
        input_dir = os.path.join(base_dir, "input")
        if not os.path.exists(input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {input_dir}")
            return False

        def _get_value(key: str) -> str | None:
            """Interne Hilfsfunktion zur Auflösung von Platzhalter-Keys."""
            key_lower = key.strip().lower()

            # Direktes Mapping aus project_data
            if key_lower in (project_data or {}):
                return str(project_data[key_lower])

            # Direktes Mapping aus analysis_results
            if key_lower in (analysis_results or {}):
                return str(analysis_results[key_lower])

            # === KUNDENDATEN ===
            if key_lower == "customer_name":
                return (project_data or {}).get("customer_name") or (project_data or {}).get("name") or "Max Mustermann"
            if key_lower == "salutation":
                return (project_data or {}).get("salutation") or "Herr"
            if key_lower == "first_name":
                return (project_data or {}).get("first_name") or "Max"
            if key_lower == "last_name":
                return (project_data or {}).get("last_name") or "Mustermann"

            # === KUNDENADRESSE ===
            if key_lower == "customer_address_street":
                addr = (project_data or {}).get("customer_address") or (project_data or {}).get("address") or {}
                if isinstance(addr, dict):
                    street = addr.get("street", "")
                    number = addr.get("house_number") or addr.get("number") or ""
                    return f"{street} {number}".strip() or "Musterstraße 1"
                return str(addr) or "Musterstraße 1"
            if key_lower == "customer_address_city":
                addr = (project_data or {}).get("customer_address") or (project_data or {}).get("address") or {}
                if isinstance(addr, dict):
                    zip_code = addr.get("zip_code") or addr.get("postal_code") or ""
                    city = addr.get("city") or ""
                    return f"{zip_code} {city}".strip() or "12345 Musterstadt"
                return str(addr) or "12345 Musterstadt"
            if key_lower == "address":
                return _get_value("customer_address_street")
            if key_lower == "house_number":
                addr = (project_data or {}).get("customer_address") or (project_data or {}).get("address") or {}
                if isinstance(addr, dict):
                    return str(addr.get("house_number") or addr.get("number") or "1")
                return "1"
            if key_lower == "zip_code":
                addr = (project_data or {}).get("customer_address") or (project_data or {}).get("address") or {}
                if isinstance(addr, dict):
                    return str(addr.get("zip_code") or addr.get("postal_code") or "12345")
                return "12345"

            # === FIRMENDATEN ===
            if key_lower == "company_name":
                return (project_data or {}).get("company_name") or "TommaTech"
            if key_lower == "company_email":
                return (project_data or {}).get("company_email") or "mail@tommatech.de"
            if key_lower == "company_phone":
                return (project_data or {}).get("company_phone") or "089244186540"
            if key_lower == "company_website":
                return (project_data or {}).get("company_website") or "www.tommatech.de"
            if key_lower == "company_address_street":
                return (project_data or {}).get("company_address_street") or "Maximilianstraße 35"
            if key_lower == "company_address_city":
                return (project_data or {}).get("company_address_city") or "80539 München"
            if key_lower == "company_tax_id":
                return (project_data or {}).get("company_tax_id") or "DE354973606"

            # === TECHNISCHE DATEN ===
            if key_lower == "anlage_kwp":
                value = (analysis_results or {}).get("anlage_kwp") or (project_data or {}).get("anlage_kwp")
                if isinstance(value, (int, float)):
                    return f"{value:.1f}".replace(".", ",")
                return str(value) if value is not None else "8,4"
            if key_lower == "anlage_kwp_formatted":
                value = (analysis_results or {}).get("anlage_kwp") or (project_data or {}).get("anlage_kwp")
                if isinstance(value, (int, float)):
                    return f"{value:.1f}".replace(".", ",")
                return str(value) if value is not None else "8,4"
            if key_lower == "battery_capacity_kwh":
                value = (analysis_results or {}).get("battery_capacity_kwh") or (project_data or {}).get("battery_capacity_kwh")
                if isinstance(value, (int, float)):
                    return f"{value:.1f}".replace(".", ",")
                return str(value) if value is not None else "6,1"
            if key_lower == "module_quantity":
                return str((analysis_results or {}).get("module_quantity") or (project_data or {}).get("module_quantity") or "21")
            if key_lower == "roof_angle":
                return str((analysis_results or {}).get("roof_angle") or (project_data or {}).get("roof_angle") or "30")
            if key_lower == "annual_consumption_kwh":
                value = (analysis_results or {}).get("annual_consumption_kwh") or (project_data or {}).get("annual_consumption_kwh")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f}".replace(",", ".")
                return str(value) if value is not None else "6.000"
            if key_lower == "annual_pv_production_kwh":
                value = (analysis_results or {}).get("annual_pv_production_kwh") or (project_data or {}).get("annual_pv_production_kwh")
                if isinstance(value, (int, float)):
                    return f"{value:,.2f}".replace(",", ".")
                return str(value) if value is not None else "8.251,92"

            # === FINANZIELLE DATEN ===
            if key_lower == "final_cost":
                value = (analysis_results or {}).get("final_cost") or (project_data or {}).get("final_cost")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f}".replace(",", ".")
                return str(value) if value is not None else "45.000"
            if key_lower == "final_cost_formatted":
                value = (analysis_results or {}).get("final_cost") or (project_data or {}).get("final_cost")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f} EUR".replace(",", ".")
                return f"{value} EUR" if value is not None else "45.000 EUR"
            if key_lower == "total_savings_with_storage_eur":
                value = (analysis_results or {}).get("total_savings_with_storage_eur")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f}".replace(",", ".")
                return str(value) if value is not None else "36.958"
            if key_lower == "total_savings_with_storage_eur_formatted":
                value = (analysis_results or {}).get("total_savings_with_storage_eur")
                if isinstance(value, (int, float)):
                    return f"{value:,.2f} EUR".replace(",", ".")
                return f"{value} EUR" if value is not None else "36.958,00 EUR"
            if key_lower == "total_savings_without_storage_eur":
                value = (analysis_results or {}).get("total_savings_without_storage_eur")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f}".replace(",", ".")
                return str(value) if value is not None else "29.150"
            if key_lower == "total_savings_without_storage_eur_formatted":
                value = (analysis_results or {}).get("total_savings_without_storage_eur")
                if isinstance(value, (int, float)):
                    return f"{value:,.2f} EUR".replace(",", ".")
                return f"{value} EUR" if value is not None else "29.150,00 EUR"

            # === PROZENTUALE WERTE ===
            if key_lower == "independence_degree_percent":
                value = (analysis_results or {}).get("independence_degree_percent") or (analysis_results or {}).get("independence_degree")
                if isinstance(value, (int, float)):
                    return f"{value:.0f}%"
                return f"{value}%" if value is not None else "54%"
            if key_lower == "self_consumption_percent":
                value = (analysis_results or {}).get("self_consumption_percent") or (analysis_results or {}).get("self_consumption")
                if isinstance(value, (int, float)):
                    return f"{value:.0f}%"
                return f"{value}%" if value is not None else "42%"

            # === UMWELTDATEN ===
            if key_lower == "co2_savings_km_equivalent":
                value = (analysis_results or {}).get("co2_savings_km_equivalent")
                if isinstance(value, (int, float)):
                    return f"{value:,.0f}".replace(",", ".")
                return str(value) if value is not None else "15.266"

            # === DATUM UND PROJEKT ===
            if key_lower == "current_date":
                from datetime import datetime
                return datetime.now().strftime("%d.%m.%Y")
            if key_lower == "project_id":
                return (project_data or {}).get("project_id") or (project_data or {}).get("offer_number") or "AN2025-1454"
            if key_lower == "pdf_offer_number_label":
                return f"Angebot {_get_value('project_id')}"
            if key_lower == "pdf_offer_date_label":
                return "Datum:"
            if key_lower == "pdf_created_on":
                return _get_value("current_date")

            # === ZUSÄTZLICHE FINANZDATEN ===
            if key_lower == "total_investment":
                return str((analysis_results or {}).get("total_investment") or "45.000")
            if key_lower == "annual_savings":
                return str((analysis_results or {}).get("annual_savings") or "2.400")
            if key_lower == "payback_period":
                return str((analysis_results or {}).get("payback_period") or "12 Jahre")
            if key_lower == "total_roi_25_years":
                return str((analysis_results or {}).get("total_roi_25_years") or "25%")
            if key_lower == "net_present_value":
                return str((analysis_results or {}).get("net_present_value") or "18.500")
            if key_lower == "monthly_savings":
                return str((analysis_results or {}).get("monthly_savings") or "200")
            if key_lower == "cumulative_savings":
                return str((analysis_results or {}).get("cumulative_savings") or "60.000")
            if key_lower == "financing_costs":
                return str((analysis_results or {}).get("financing_costs") or "2.500")
            if key_lower == "loan_details":
                return str((analysis_results or {}).get("loan_details") or "15 Jahre, 3,5% Zinsen")

            # Fallback: Key nicht gefunden
            print(f"⚠️ Unbekannter Key: {key}")
            return f"{{{key}}}"  # Gib den Key unverändert zurück

        # alle TXT-Dateien bearbeiten
        for filename in os.listdir(input_dir):
            if filename.endswith(".txt"):
                path = os.path.join(input_dir, filename)
                try:
                    with open(path, encoding="utf-8") as f:
                        content = f.read()
                    def replace(match: re.Match) -> str:
                        key = match.group(1)
                        val = _get_value(key)
                        return str(val) if val is not None else match.group(0)
                    new_content = re.sub(r"\{([^{}]+)\}", replace, content)
                    if new_content != content:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"⚠️ Fehler beim Aktualisieren von {filename}: {e}")
        print("🔄 TXT-Dateien wurden mit dynamischen Werten aktualisiert")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren der TXT-Dateien: {e}")
        return False

def check_txt_system_requirements() -> dict[str, bool]:
    """
    Prüft ob alle Anforderungen für das TXT-System erfüllt sind
    
    Returns:
        Dict mit Status-Informationen
    """
    base_dir = os.getcwd()
    requirements = {
        'pdf_script_exists': os.path.exists(os.path.join(base_dir, "pdf_erstellen_komplett.py")),
        'input_dir_exists': os.path.exists(os.path.join(base_dir, "input")),
        'txt_files_found': False,
        'all_pages_available': False
    }

    # Prüfe TXT-Dateien
    input_dir = os.path.join(base_dir, "input")
    if requirements['input_dir_exists']:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        requirements['txt_files_found'] = len(txt_files) > 0

        # Prüfe ob alle 20 Seiten verfügbar sind
        page_files = [f for f in txt_files if f.startswith('seite_') and '_texte.txt' in f]
        if page_files:
            page_numbers = []
            for file in page_files:
                try:
                    num = int(file.split('_')[1])
                    page_numbers.append(num)
                except:
                    pass
            requirements['all_pages_available'] = len(page_numbers) >= 20

    return requirements

def get_system_status() -> str:
    """
    Gibt den aktuellen Status des TXT-Systems zurück
    
    Returns:
        str: Status-Nachricht
    """
    requirements = check_txt_system_requirements()

    status_parts = []

    if requirements['pdf_script_exists']:
        status_parts.append("✅ PDF-Script verfügbar")
    else:
        status_parts.append("❌ PDF-Script fehlt")

    if requirements['input_dir_exists']:
        status_parts.append("✅ Input-Ordner gefunden")
    else:
        status_parts.append("❌ Input-Ordner fehlt")

    if requirements['txt_files_found']:
        status_parts.append("✅ TXT-Dateien gefunden")
    else:
        status_parts.append("❌ Keine TXT-Dateien")

    if requirements['all_pages_available']:
        status_parts.append("✅ 20+ Seiten verfügbar")
    else:
        status_parts.append("⚠️ Weniger als 20 Seiten")

    return " | ".join(status_parts)

# Kompatibilitäts-Wrapper für bestehende Funktionen
def generate_offer_pdf(*args, **kwargs) -> bytes | None:
    """
    Wrapper-Funktion für Kompatibilität mit bestehendem System
    Leitet Anfragen an die TXT-basierte PDF-Generierung weiter
    """
    return generate_pdf_from_txt_files(*args, **kwargs)

if __name__ == "__main__":
    # Test der Integration
    print("🧪 Teste TXT-zu-PDF Integration...")
    print(f"Status: {get_system_status()}")

    # Test-PDF generieren
    pdf_bytes = generate_pdf_from_txt_files()
    if pdf_bytes:
        print(f"✅ Test erfolgreich! PDF-Größe: {len(pdf_bytes)} bytes")
    else:
        print("❌ Test fehlgeschlagen!")
