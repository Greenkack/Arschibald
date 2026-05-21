#!/usr/bin/env python3
"""
Wiederherstellung der korruptierten TXT-Dateien mit intelligenter Reparatur.
Stellt nur Koordinaten und Farbwerte wieder her, behält aber valide Key-Ersetzungen.
"""
import os
import re


def restore_numeric_corruptions():
    """
    Repariert korrupte Koordinaten und Farbwerte in den TXT-Dateien.
    """

    # Bekannte Korruptionen und ihre Korrekturen
    corruption_fixes = {
        # Koordinaten-Reparaturen (spezifische Korruptionen)
        "5{module_quantity}0557": "5210557",  # Farbe korrigieren
        "99{module_quantity}": "9921",       # Position korrigieren
        "1{module_quantity}": "121",         # Position korrigieren
        "5{module_quantity}": "521",         # Position korrigieren
        "{module_quantity}0": "210",         # Position korrigieren
        "{module_quantity}1": "211",         # Position korrigieren
        "{module_quantity}5": "215",         # Position korrigieren
        "{module_quantity}8": "218",         # Position korrigieren

        # Dachneigung-Korruptionen
        "1{roof_angle}": "130",              # Position korrigieren
        "2{roof_angle}": "230",              # Position korrigieren
        "3{roof_angle}": "330",              # Position korrigieren
        "4{roof_angle}": "430",              # Position korrigieren
        "5{roof_angle}": "530",              # Position korrigieren
        "6{roof_angle}": "630",              # Position korrigieren
        "7{roof_angle}": "730",              # Position korrigieren
        "8{roof_angle}": "830",              # Position korrigieren
        "9{roof_angle}": "930",              # Position korrigieren
        "{roof_angle}0": "300",              # Position korrigieren
        "{roof_angle}1": "301",              # Position korrigieren
        "{roof_angle}5": "305",              # Position korrigieren
        "{roof_angle}6": "306",              # Position korrigieren
        "{roof_angle}8": "308",              # Position korrigieren
        "{roof_angle}9": "309",              # Position korrigieren

        # Weitere mögliche Korruptionen basierend on Muster
        "65{module_quantity}0000": "65210000",   # Farbe
        "00{module_quantity}255": "00021255",    # Farbe RGB
        "255{module_quantity}55": "25521055",    # Farbe RGB
    }

    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"Ordner '{input_dir}' nicht gefunden!")
        return None

    total_fixes = 0

    # Alle TXT-Dateien durchgehen
    for i in range(1, 21):
        filename = f"seite_{i}_texte.txt"
        filepath = os.path.join(input_dir, filename)

        if not os.path.exists(filepath):
            print(f"Datei {filename} nicht gefunden, überspringe...")
            continue

        # Datei einlesen
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Fehler beim Lesen von {filename}: {e}")
            continue

        original_content = content
        file_fixes = 0

        # Alle bekannten Korruptionen reparieren
        for corrupted, fixed in corruption_fixes.items():
            if corrupted in content:
                content = content.replace(corrupted, fixed)
                count = original_content.count(corrupted)
                file_fixes += count
                print(f"   {filename}: '{corrupted}' → '{fixed}' ({count}x)")

        # Weitere allgemeine Muster-Reparaturen
        # RGB-Farben mit Key-Korruption reparieren
        rgb_pattern = r'(\d+){module_quantity}(\d+)'
        matches = re.findall(rgb_pattern, content)
        for match in matches:
            corrupted_rgb = f"{match[0]}{{module_quantity}}{match[1]}"
            fixed_rgb = f"{match[0]}21{match[1]}"
            content = content.replace(corrupted_rgb, fixed_rgb)
            file_fixes += 1
            print(f"   {filename}: RGB '{corrupted_rgb}' → '{fixed_rgb}'")

        roof_angle_pattern = r'(\d+){roof_angle}(\d+)'
        matches = re.findall(roof_angle_pattern, content)
        for match in matches:
            corrupted_angle = f"{match[0]}{{roof_angle}}{match[1]}"
            fixed_angle = f"{match[0]}30{match[1]}"
            content = content.replace(corrupted_angle, fixed_angle)
            file_fixes += 1
            print(
                f"   {filename}: Winkel '{corrupted_angle}' → '{fixed_angle}'")

        # Datei zurückschreiben wenn Änderungen gemacht wurden
        if file_fixes > 0:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"{filename}: {file_fixes} Korrekturen gespeichert")
                total_fixes += file_fixes
            except Exception as e:
                print(f"Fehler beim Schreiben von {filename}: {e}")
        else:
            print(f"{filename}: Keine Korrekturen nötig")

    print(
        f"\nWiederherstellung abgeschlossen: {total_fixes} Korrekturen insgesamt")

    return total_fixes > 0


if __name__ == "__main__":
    print(" Starte Wiederherstellung der korruptierten TXT-Dateien...")
    print("=" * 60)

    success = restore_numeric_corruptions()

    if success:
        print("\nWiederherstellung erfolgreich!")
        print("Tipp: Führe jetzt 'python test_dynamic_keys.py' aus zum Testen")
    else:
        print("\nKeine Korruptionen gefunden oder repariert")
