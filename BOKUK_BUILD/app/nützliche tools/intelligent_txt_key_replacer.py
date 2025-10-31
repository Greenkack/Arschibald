#!/usr/bin/env python3
"""
Intelligenter TXT-Dateien Analyzer und Key-Replacer
Analysiert die TXT-Dateien im input-Ordner und ersetzt statische Werte durch dynamische Keys.

Autor: GitHub Copilot
Datum: 28.07.2025
"""

import json
import os
import re


class TXTKeyReplacer:
    """Intelligenter Ersatz von statischen Werten durch dynamische Keys in TXT-Dateien."""

    def __init__(self):
        self.input_dir = os.path.join(os.getcwd(), "input")

        # Mapping von statischen Werten zu Keys basierend auf typischen Daten
        self.static_to_key_mappings = {
            # KUNDENDATEN
            "Max Mustermann": "{customer_name}",
            "Mustermann": "{last_name}",
            "Max": "{first_name}",
            "Herr": "{salutation}",
            "Frau": "{salutation}",
            "Dr.": "{salutation}",
            "Prof.": "{salutation}",

            # FIRMENDATEN
            "TommaTech": "{company_name}",
            "BTPV Deutschland Gmbh": "{company_name}",
            "SuperSolar GmbH": "{company_name}",
            "mail@tommatech.de": "{company_email}",
            "info@btpv-deutschland.de": "{company_email}",
            "089244186540": "{company_phone}",
            "+49 89 1250 36 860": "{company_phone}",
            "www.tommatech.de": "{company_website}",
            "www.btpv-deutschland.de": "{company_website}",
            "Maximilianstraße 35": "{company_address_street}",
            "Augsburger Str. 3a": "{company_address_street}",
            "80539 München": "{company_address_city}",
            "82178 Puchheim": "{company_address_city}",
            "DE354973606": "{company_tax_id}",

            # KUNDENADRESSE
            "Brunnenäcker 46": "{customer_address_street}",
            "79793 Wutöschingen": "{customer_address_city}",

            # TECHNISCHE DATEN
            "8,4 kWp": "{anlage_kwp_formatted} kWp",
            "8,4": "{anlage_kwp}",
            "10,5": "{anlage_kwp}",
            "6,1 kWh": "{battery_capacity_kwh} kWh",
            "8,5 kWh": "{battery_capacity_kwh} kWh",
            "6,1": "{battery_capacity_kwh}",
            "8,5": "{battery_capacity_kwh}",
            "21": "{module_quantity}",
            "25": "{module_quantity}",
            "30°": "{roof_angle}°",
            "30": "{roof_angle}",
            "6.000 kWh/Jahr": "{annual_consumption_kwh} kWh/Jahr",
            "6000": "{annual_consumption_kwh}",
            "8.251,92 kWh/Jahr": "{annual_pv_production_kwh} kWh/Jahr",
            "8251,92": "{annual_pv_production_kwh}",

            # FINANZIELLE WERTE
            "36.958,00 EUR": "{total_savings_with_storage_eur_formatted}",
            "36958": "{total_savings_with_storage_eur}",
            "29.150,00 EUR": "{total_savings_without_storage_eur_formatted}",
            "29150": "{total_savings_without_storage_eur}",
            "45.000": "{final_cost}",
            "45.000 EUR": "{final_cost_formatted}",

            # PROZENTE UND GRADE
            "54%": "{independence_degree_percent}",
            "42%": "{self_consumption_percent}",

            # DATUM
            "26.07.2025": "{current_date}",
            "29.11.2024": "{current_date}",
            "28.07.2025": "{current_date}",

            # PROJEKT-IDs
            "AN2025-1454": "{project_id}",
            "tom-90": "{project_id}",
            "TOM-90": "{project_id}",
        }

        # Pattern für intelligente Erkennung
        self.smart_patterns = [
            # E-Mail Pattern
            (
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
                '{company_email}'),
            # Telefonnummer Pattern (verschiedene Formate)
            (
                r'\b(?:\+49\s?)?(?:\(0\))?(?:0)?[1-9]\d{1,4}[\s\-]?\d{3,}\b',
                '{company_phone}'),
            # Website Pattern
            (r'\bwww\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '{company_website}'),
            # Datum Pattern (DD.MM.YYYY)
            (r'\b\d{1,2}\.\d{1,2}\.\d{4}\b', '{current_date}'),
            # Währung Pattern (Betrag EUR)
            (r'\b\d{1,3}(?:\.\d{3})*,\d{2}\s?EUR\b', '{final_cost_formatted}'),
            # kWp Pattern
            (r'\b\d+,\d\s?kWp\b', '{anlage_kwp_formatted} kWp'),
            # kWh Pattern
            (r'\b\d+,\d\s?kWh\b', '{battery_capacity_kwh} kWh'),
            # Prozent Pattern
            (r'\b\d{1,2}%\b', '{percentage_value}'),
            # PLZ + Ort Pattern (Deutschland)
            (r'\b\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*\b',
             '{customer_address_city}'),
        ]

    def analyze_txt_files(self) -> dict[str, list[tuple[str, str]]]:
        """
        Analysiert alle TXT-Dateien und findet Kandidaten für Key-Ersetzung.

        Returns:
            Dict mit Dateiname als Key und Liste von (original_text, suggested_key) Tupeln
        """
        candidates = {}

        if not os.path.exists(self.input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {self.input_dir}")
            return candidates

        for filename in os.listdir(self.input_dir):
            if filename.endswith('_texte.txt'):
                file_path = os.path.join(self.input_dir, filename)
                file_candidates = []

                try:
                    with open(file_path, encoding='utf-8') as f:
                        content = f.read()

                    # Analysiere Text-Blöcke
                    blocks = content.split('-' * 40)
                    for block in blocks:
                        lines = [
                            line.strip() for line in block.strip().split('\n') if line.strip()]

                        for line in lines:
                            if line.startswith('Text: '):
                                # Entferne "Text: "
                                text_content = line[6:].strip()

                                # Prüfe auf bereits vorhandene Keys
                                if '{' in text_content and '}' in text_content:
                                    continue  # Bereits dynamisch

                                # Prüfe exakte Mappings
                                for static_val, key in self.static_to_key_mappings.items():
                                    if static_val in text_content:
                                        suggested_replacement = text_content.replace(
                                            static_val, key)
                                        file_candidates.append(
                                            (text_content, suggested_replacement))
                                        break
                                else:
                                    # Prüfe Smart Patterns
                                    for pattern, key in self.smart_patterns:
                                        if re.search(pattern, text_content):
                                            suggested_replacement = re.sub(
                                                pattern, key, text_content)
                                            file_candidates.append(
                                                (text_content, suggested_replacement))
                                            break

                except Exception as e:
                    print(f"⚠️ Fehler beim Analysieren von {filename}: {e}")

                if file_candidates:
                    candidates[filename] = file_candidates

        return candidates

    def apply_replacements(
            self, candidates: dict[str, list[tuple[str, str]]], auto_apply: bool = False) -> int:
        """
        Wendet die gefundenen Ersetzungen auf die TXT-Dateien an.

        Args:
            candidates: Dictionary mit Ersetzungskandidaten
            auto_apply: Wenn True, werden alle Ersetzungen automatisch angewendet

        Returns:
            Anzahl der durchgeführten Ersetzungen
        """
        total_replacements = 0

        for filename, file_candidates in candidates.items():
            file_path = os.path.join(self.input_dir, filename)

            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                file_replacements = 0

                for original_text, suggested_replacement in file_candidates:
                    if not auto_apply:
                        # Interaktive Bestätigung
                        print(f"\n📄 {filename}")
                        print(f"Original: {original_text}")
                        print(f"Vorschlag: {suggested_replacement}")

                        choice = input("Anwenden? (j/n/a für alle): ").lower()
                        if choice == 'a':
                            auto_apply = True
                        elif choice != 'j' and choice != 'a':
                            continue

                    # Führe Ersetzung durch
                    if original_text in content:
                        content = content.replace(
                            f"Text: {original_text}", f"Text: {suggested_replacement}")
                        file_replacements += 1
                        print(
                            f"✅ Ersetzt: {original_text} → {suggested_replacement}")

                # Schreibe Datei zurück wenn Änderungen gemacht wurden
                if file_replacements > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(
                        f"💾 {filename}: {file_replacements} Ersetzungen gespeichert")
                    total_replacements += file_replacements

            except Exception as e:
                print(f"❌ Fehler beim Bearbeiten von {filename}: {e}")

        return total_replacements

    def create_backup(self) -> str:
        """
        Erstellt ein Backup des input-Ordners.

        Returns:
            Pfad zum Backup-Ordner
        """
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"input_backup_{timestamp}"

        try:
            shutil.copytree(self.input_dir, backup_dir)
            print(f"✅ Backup erstellt: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Backups: {e}")
            return ""

    def generate_key_reference(self) -> None:
        """Erstellt eine Referenz-Datei mit allen verfügbaren Keys."""
        reference = {
            "kundendaten": {
                "customer_name": "Vollständiger Kundenname",
                "salutation": "Anrede (Herr, Frau, Dr., etc.)",
                "first_name": "Vorname",
                "last_name": "Nachname",
                "customer_address_street": "Straße und Hausnummer",
                "customer_address_city": "PLZ und Ort"
            },
            "firmendaten": {
                "company_name": "Firmenname",
                "company_email": "E-Mail-Adresse",
                "company_phone": "Telefonnummer",
                "company_website": "Website",
                "company_address_street": "Firmenadresse Straße",
                "company_address_city": "Firmenadresse PLZ/Ort",
                "company_tax_id": "Steuernummer/USt-ID"
            },
            "technische_daten": {
                "anlage_kwp": "Anlagenleistung in kWp (Zahl)",
                "anlage_kwp_formatted": "Anlagenleistung formatiert (z.B. 8,40)",
                "battery_capacity_kwh": "Batteriekapazität in kWh",
                "module_quantity": "Anzahl Module",
                "roof_angle": "Dachneigung in Grad",
                "annual_consumption_kwh": "Jährlicher Verbrauch in kWh",
                "annual_pv_production_kwh": "Jährliche PV-Produktion in kWh"
            },
            "finanzielle_daten": {
                "final_cost": "Endpreis (Zahl)",
                "final_cost_formatted": "Endpreis formatiert (z.B. 45.000 EUR)",
                "total_savings_with_storage_eur": "Ersparnis mit Speicher",
                "total_savings_without_storage_eur": "Ersparnis ohne Speicher",
                "total_investment": "Gesamtinvestition",
                "annual_savings": "Jährliche Ersparnis",
                "payback_period": "Amortisationszeit",
                "monthly_savings": "Monatliche Ersparnis"
            },
            "sonstige": {
                "current_date": "Aktuelles Datum",
                "project_id": "Projekt-/Angebotsnummer",
                "independence_degree_percent": "Unabhängigkeitsgrad in %",
                "self_consumption_percent": "Eigenverbrauch in %"
            }
        }

        with open('key_reference.json', 'w', encoding='utf-8') as f:
            json.dump(reference, f, indent=2, ensure_ascii=False)

        print("✅ Key-Referenz erstellt: key_reference.json")


def main():
    """Hauptfunktion für interaktive Nutzung."""
    replacer = TXTKeyReplacer()

    print("🔍 TXT-Dateien Key-Replacer")
    print("=" * 40)

    # Backup erstellen
    print("1. Erstelle Backup...")
    backup_path = replacer.create_backup()
    if not backup_path:
        print("⚠️ Warnung: Kein Backup erstellt!")

    # Analysiere Dateien
    print("\n2. Analysiere TXT-Dateien...")
    candidates = replacer.analyze_txt_files()

    if not candidates:
        print("✅ Keine statischen Werte gefunden - alle Dateien bereits dynamisch!")
        return

    total_candidates = sum(len(cands) for cands in candidates.values())
    print(
        f"📊 {total_candidates} Ersetzungskandidaten in {
            len(candidates)} Dateien gefunden")

    # Zeige Zusammenfassung
    for filename, file_candidates in candidates.items():
        print(f"  📄 {filename}: {len(file_candidates)} Kandidaten")

    # Frage nach automatischer Anwendung
    print("\n3. Ersetzungen anwenden...")
    choice = input("Alle automatisch anwenden? (j/n): ").lower()
    auto_apply = choice == 'j'

    # Führe Ersetzungen durch
    total_replacements = replacer.apply_replacements(candidates, auto_apply)

    print(f"\n🎯 Fertig! {total_replacements} Ersetzungen durchgeführt")

    # Erstelle Key-Referenz
    print("\n4. Erstelle Key-Referenz...")
    replacer.generate_key_reference()

    print("\n✅ Alle TXT-Dateien wurden aktualisiert!")
    print("💡 Tipp: Prüfen Sie die Dateien und verwenden Sie 'python txt_to_pdf_integration.py' zum Testen")


if __name__ == "__main__":
    main()
