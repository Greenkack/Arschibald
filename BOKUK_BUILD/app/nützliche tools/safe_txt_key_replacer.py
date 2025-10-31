#!/usr/bin/env python3
"""
SICHERER TXT-Dateien Key-Replacer
=================================

Ersetzt nur SPEZIFISCHE statische Werte durch Keys,
ohne das Layout oder die Struktur zu zerstören.

VORSICHTIG: Nur bekannte, sichere Ersetzungen!
"""

import glob
import os


def get_safe_replacements() -> dict[str, str]:
    """
    Nur 100% SICHERE Ersetzungen, die das Layout NICHT zerstören!

    Diese Werte wurden manuell identifiziert und sind sicher zu ersetzen.
    """
    return {
        # === FIRMENADRESSE - SPEZIFISCH IDENTIFIZIERT ===
        "82178 Puchheim": "{company_address_city}",  # Seite 2, Zeile 3

        # === TECHNISCHE WERTE - NUR WENN EINDEUTIG ===
        # Diese werden NUR ersetzt wenn sie alleine stehen (ohne Kontext)
        # NICHT ersetzen wenn sie Teil einer größeren Zeichenkette sind!

        # === DATUM - NUR SPEZIFISCHE FORMATE ===
        # Diese nur wenn sie als vollständige "Text:" Einträge stehen

        # === KUNDENDATEN - NUR WENN SICHER ===
        # Diese nur wenn eindeutig als separate Textblöcke

        # === WEITERE SICHERE ERSETZUNGEN NACH ANALYSE ===
        # Werden nach manueller Prüfung hinzugefügt
    }


def analyze_txt_files() -> dict[str, list[str]]:
    """
    Analysiert TXT-Dateien und zeigt potentielle statische Werte.
    MACHT KEINE ÄNDERUNGEN - nur Analyse!
    """
    input_dir = os.path.join(os.getcwd(), "input")
    txt_files = glob.glob(os.path.join(input_dir, "seite_*_texte.txt"))

    findings = {}

    # Bekannte Keys zum Ausschließen
    known_keys = [
        '{customer_name}',
        '{salutation}',
        '{last_name}',
        '{first_name}',
        '{company_name}',
        '{company_email}',
        '{company_phone}',
        '{company_website}',
        '{company_address_street}',
        '{company_address_city}',
        '{company_tax_id}',
        '{customer_address_street}',
        '{customer_address_city}',
        '{anlage_kwp}',
        '{battery_capacity_kwh}',
        '{annual_consumption_kwh}',
        '{annual_pv_production_kwh}',
        '{roof_angle}',
        '{current_date}',
        '{project_id}',
        '{total_savings_with_storage_eur_formatted}',
        '{total_savings_without_storage_eur_formatted}',
        '{module_quantity}',
        '{pdf_offer_number_label}',
        '{pdf_offer_date_label}',
        '{pdf_created_on}',
        '{zip_code}',
        '{address}',
        '{house_number}']

    for txt_file in sorted(txt_files):
        filename = os.path.basename(txt_file)
        static_values = []

        try:
            with open(txt_file, encoding='utf-8') as f:
                content = f.read()

            # Suche nach Text-Einträgen
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('Text: '):
                    text_content = line[6:].strip()  # Entferne "Text: "

                    # Prüfe ob bereits ein Key ist
                    if any(key in text_content for key in known_keys):
                        continue  # Ist bereits dynamisch

                    # Prüfe ob es aussieht wie statischer Inhalt
                    if (len(text_content) > 2 and
                        not text_content.startswith('*') and
                        not text_content.startswith(' ') and
                            'Position:' not in text_content):

                        # Weitere Filter für bekannte dynamische Inhalte
                        if (text_content not in ['*', 'xxxxxxxxxx', 'yyyyyyyyyyyyy'] and
                            not text_content.startswith('inkl.') and
                            not text_content.startswith('vielen Dank') and
                                not text_content.startswith('Mit freundlichen')):
                            static_values.append(
                                f"Zeile {i + 1}: {text_content}")

        except Exception as e:
            static_values.append(f"FEHLER beim Lesen: {e}")

        if static_values:
            findings[filename] = static_values

    return findings


def apply_safe_replacements() -> int:
    """
    Wendet nur die SICHEREN Ersetzungen an.
    """
    replacements = get_safe_replacements()

    if not replacements:
        print("⚠️ Keine sicheren Ersetzungen definiert!")
        return 0

    input_dir = os.path.join(os.getcwd(), "input")
    txt_files = glob.glob(os.path.join(input_dir, "seite_*_texte.txt"))

    total_replacements = 0

    print("🔄 Führe SICHERE Ersetzungen durch...")

    for txt_file in sorted(txt_files):
        filename = os.path.basename(txt_file)
        file_replacements = 0

        try:
            # Datei lesen
            with open(txt_file, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Nur sichere Ersetzungen durchführen
            for old_value, new_key in replacements.items():
                if f"Text: {old_value}" in content:
                    content = content.replace(
                        f"Text: {old_value}", f"Text: {new_key}")
                    file_replacements += 1
                    print(f"✅ {filename}: '{old_value}' → '{new_key}'")

            # Datei zurückschreiben wenn geändert
            if content != original_content:
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(
                    f"💾 {filename}: {file_replacements} sichere Ersetzungen gespeichert")
                total_replacements += file_replacements

        except Exception as e:
            print(f"❌ Fehler bei {filename}: {e}")

    return total_replacements


def main():
    """Hauptfunktion mit sicherer Vorgehensweise."""
    print("🔍 SICHERER TXT-Dateien Key-Replacer")
    print("=" * 50)

    # 1. ANALYSE - KEINE ÄNDERUNGEN
    print("\n1. 📊 ANALYSIERE statische Werte (keine Änderungen)...")
    findings = analyze_txt_files()

    if not findings:
        print("✅ Alle TXT-Dateien sind bereits vollständig dynamisch!")
        return

    print(
        f"\n📋 Gefundene potentielle statische Werte in {
            len(findings)} Dateien:")
    for filename, static_values in findings.items():
        print(f"\n📄 {filename}:")
        for value in static_values[:5]:  # Zeige max. 5 pro Datei
            print(f"  • {value}")
        if len(static_values) > 5:
            print(f"  ... und {len(static_values) - 5} weitere")

    # 2. SICHERE ERSETZUNGEN
    print("\n2. 🛡️ SICHERE Ersetzungen...")
    safe_replacements = get_safe_replacements()

    if safe_replacements:
        print("Folgende sichere Ersetzungen werden durchgeführt:")
        for old, new in safe_replacements.items():
            print(f"  • '{old}' → '{new}'")

        confirm = input(
            f"\n💡 {
                len(safe_replacements)} sichere Ersetzungen anwenden? (j/n): ")
        if confirm.lower() == 'j':
            total = apply_safe_replacements()
            print(f"\n🎯 {total} sichere Ersetzungen durchgeführt!")
        else:
            print("❌ Abgebrochen - keine Änderungen gemacht")
    else:
        print("ℹ️ Keine sicheren Ersetzungen definiert.")
        print("💡 Definieren Sie sichere Ersetzungen in get_safe_replacements()")

    # 3. EMPFEHLUNGEN
    print("\n3. 💡 EMPFEHLUNGEN für weitere Optimierung:")
    print("• Prüfen Sie die gefundenen statischen Werte manuell")
    print("• Fügen Sie nur eindeutige Werte zu get_safe_replacements() hinzu")
    print("• Testen Sie jede Änderung einzeln")
    print("• Nutzen Sie Git für Backups vor größeren Änderungen")


if __name__ == "__main__":
    main()
