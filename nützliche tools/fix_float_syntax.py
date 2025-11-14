#!/usr/bin/env python3
"""
Finale Reparatur der Float-Syntax-Probleme in TXT-Dateien.
Korrigiert ungültige Float-Werte wie "3.21.5758972167969".
"""
import os
import re


def fix_invalid_floats():
    """
    Repariert ungültige Float-Werte in den TXT-Dateien.
    """

    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"[ERROR] Ordner '{input_dir}' nicht gefunden!")
        return None

    total_fixes = 0

    # Pattern für ungültige Floats (mehrere Punkte)
    invalid_float_pattern = r'(\d+)\.(\d+)\.(\d+)'

    # Alle TXT-Dateien durchgehen
    for i in range(1, 21):
        filename = f"seite_{i}_texte.txt"
        filepath = os.path.join(input_dir, filename)

        if not os.path.exists(filepath):
            continue

        # Datei einlesen
        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        original_content = content
        file_fixes = 0

        # Alle ungültigen Float-Werte finden und reparieren
        matches = re.findall(invalid_float_pattern, content)
        for match in matches:
            invalid_float = f"{match[0]}.{match[1]}.{match[2]}"
            # Repariere zu gültigem Float: nimm nur erste Dezimalstelle
            valid_float = f"{match[0]}.{match[1]}{match[2]}"

            if invalid_float in content:
                content = content.replace(invalid_float, valid_float)
                file_fixes += 1
                print(f"   [TOOL] {filename}: '{invalid_float}' → '{valid_float}'")

        # Weitere Muster reparieren (z.B. "2.21.72483825683594")
        # Spezielle Behandlung für doppelte Punkte
        content = re.sub(r'(\d+)\.21\.(\d+)', r'\1.21\2', content)
        content = re.sub(r'(\d+)\.30\.(\d+)', r'\1.30\2', content)

        # Zähle zusätzliche Fixes
        if content != original_content:
            additional_fixes = original_content.count(
                '.21.') + original_content.count('.30.')
            file_fixes += additional_fixes

        # Datei zurückschreiben wenn Änderungen gemacht wurden
        if file_fixes > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] {filename}: {file_fixes} Float-Korrekturen gespeichert")
            total_fixes += file_fixes
        else:
            print(f"[INFO]  {filename}: Keine Float-Korrekturen nötig")

    print(
        f"\n[TARGET] Float-Reparatur abgeschlossen: {total_fixes} Korrekturen insgesamt")
    return total_fixes > 0


if __name__ == "__main__":
    print("[TOOL] Starte Float-Syntax-Reparatur...")
    print("=" * 60)

    success = fix_invalid_floats()

    if success:
        print("\n[OK] Float-Syntax erfolgreich repariert!")
        print("[IDEA] Führe jetzt 'python debug_syntax_issues.py' zum Testen aus")
    else:
        print("\n[WARNING]  Keine Float-Probleme gefunden")
