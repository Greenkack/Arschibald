"""
Skript zum Einrücken des Status-Blocks in solar_3d_view_module.py
"""

def fix_status_indentation():
    file_path = r"c:\Users\win10\Desktop\Bokuk2 - Kopie\solar_3d_view_module.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Finde Start und Ende des Status-Blocks
    # Start: Zeile mit "# Berechne platzierte Module" (ca. Zeile 2107)
    # Ende: Zeile vor "# EXPORT-BEREICH" (ca. Zeile 2441)
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if "# Berechne platzierte Module aus aktuellen Scene-Daten" in line:
            start_idx = i
        if "# EXPORT-BEREICH" in line and start_idx is not None:
            end_idx = i
            break
    
    if start_idx is None or end_idx is None:
        print(f"❌ Konnte Grenzen nicht finden: start={start_idx}, end={end_idx}")
        return
    
    print(f"✓ Gefunden: Zeilen {start_idx+1} bis {end_idx}")
    
    # Rücke alle Zeilen zwischen start und end um 4 Spaces ein
    fixed_lines = []
    for i, line in enumerate(lines):
        if start_idx <= i < end_idx:
            # Nur einrücken wenn die Zeile nicht leer ist
            if line.strip():
                fixed_lines.append("    " + line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Schreibe zurück
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✓ Datei aktualisiert: {len(fixed_lines)} Zeilen")
    print(f"✓ Eingerückt: Zeilen {start_idx+1} bis {end_idx}")

if __name__ == "__main__":
    fix_indentation_status()
