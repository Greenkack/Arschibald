"""
Fügt separators=',.' zu allen Plotly fig.update_layout() hinzu
"""

import re

with open('heatpump_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle fig.update_layout Blöcke und füge separators hinzu
# Pattern: fig.update_layout( ... ) oder fig_XXX.update_layout( ... )

def add_separators_to_layout(match):
    layout_content = match.group(1)
    
    # Prüfe ob separators bereits vorhanden ist
    if 'separators=' in layout_content:
        return match.group(0)  # Bereits vorhanden, nichts tun
    
    # Füge separators vor der schließenden Klammer hinzu
    # Entferne die letzte Klammer, füge separators hinzu, füge Klammer wieder ein
    layout_content = layout_content.rstrip()
    
    if layout_content.endswith(','):
        new_content = f"{layout_content}\n                separators=',.'  # Deutsche Trennzeichen"
    else:
        new_content = f"{layout_content},\n                separators=',.'  # Deutsche Trennzeichen"
    
    return f"fig{match.group(0).split('fig')[1].split('.')[0]}.update_layout({new_content}\n            )"

# Pattern für .update_layout(...)
pattern = r'(fig[_\w]*\.update_layout\()([^)]+\))'

# Komplexerer Ansatz: Zeile für Zeile
lines = content.split('\n')
result_lines = []
in_update_layout = False
layout_lines = []
indent = ''

for i, line in enumerate(lines):
    if '.update_layout(' in line and 'separators=' not in line:
        in_update_layout = True
        layout_lines = [line]
        indent = line[:len(line) - len(line.lstrip())]
    elif in_update_layout:
        layout_lines.append(line)
        # Prüfe ob wir am Ende sind (schließende Klammer)
        if line.strip().startswith(')'):
            # Füge separators vor der letzten Zeile ein
            last_line = layout_lines[-1]
            layout_lines = layout_lines[:-1]
            
            # Prüfe letzte Zeile vor der Klammer
            if layout_lines and not layout_lines[-1].strip().endswith(','):
                layout_lines[-1] = layout_lines[-1] + ','
            
            # Füge separators hinzu
            layout_lines.append(f"{indent}    separators=',.'  # Deutsche Trennzeichen")
            layout_lines.append(last_line)
            
            result_lines.extend(layout_lines)
            in_update_layout = False
            layout_lines = []
        continue
    
    if not in_update_layout:
        result_lines.append(line)

# Schreibe zurück
with open('heatpump_ui.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result_lines))

print("✅ Separators zu allen Plotly-Charts hinzugefügt!")
print(f"   Verarbeitete Zeilen: {len(result_lines)}")
