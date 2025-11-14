"""
Bereinigt doppelte separators-Zeilen in heatpump_ui.py
"""

with open('heatpump_ui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

result_lines = []
prev_was_separator = False

for line in lines:
    # Prüfe ob aktuelle Zeile ein separator ist
    is_separator = 'separators=' in line
    
    # Wenn vorherige UND aktuelle Zeile separator sind, überspringe
    if prev_was_separator and is_separator:
        continue
    
    result_lines.append(line)
    prev_was_separator = is_separator

with open('heatpump_ui.py', 'w', encoding='utf-8') as f:
    f.writelines(result_lines)

print(f"[OK] Doppelte separators entfernt!")
print(f"   Vorher: {len(lines)} Zeilen")
print(f"   Nachher: {len(result_lines)} Zeilen")
print(f"   Entfernt: {len(lines) - len(result_lines)} doppelte Zeilen")
