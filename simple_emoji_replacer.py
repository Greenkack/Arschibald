"""
SIMPLER AUTO-REPLACER: Verarbeitet die wichtigsten Dateien mit Emojis.

Macht automatisch Backups vor jeder Änderung!
"""

import re
from pathlib import Path
import shutil

# Emoji Pattern
EMOJI_PATTERN = re.compile(
    r'[\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
    r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF'
    r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+'
)

# Die wichtigsten Dateien (nach Scan-Ergebnis)
TARGET_FILES = [
    "solar_3d_view_module.py",  # 231 Zeilen mit Emojis
    "admin_panel.py",            # 196 Zeilen
    "gui.py",                    # 186 Zeilen
    "admin_heatpump_settings_ui.py",  # 78 Zeilen
]


def process_file(file_path: Path) -> tuple:
    """Verarbeitet eine Datei und ersetzt alle Emojis."""
    
    # Backup erstellen
    backup_path = file_path.with_suffix('.py.bak')
    shutil.copy2(file_path, backup_path)
    print(f"📦 Backup erstellt: {backup_path.name}")
    
    # Datei lesen
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe ob emoji_toggle import vorhanden
    has_import = 'from emoji_toggle import' in content and ' e' in content
    
    # Zähler
    replacements = 0
    
    # Ersetze alle Emojis in Strings
    def replace_emoji(match):
        nonlocal replacements
        emoji = match.group(0)
        replacements += 1
        return f'{{e("{emoji}")}}'
    
    # Finde und ersetze alle String-Literale mit Emojis
    # Pattern: st.xxx("text emoji") oder st.xxx(f"text emoji")
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Überspringe Kommentare
        if line.strip().startswith('#'):
            new_lines.append(line)
            continue
        
        # Suche nach st.method("...emoji...") oder st.method('...emoji...')
        if 'st.' in line and EMOJI_PATTERN.search(line):
            # Ersetze "text emoji" mit f"{e('emoji')} text"
            new_line = line
            
            # Finde alle Strings in der Zeile
            for quote in ['"', "'"]:
                # Pattern für "text" oder f"text"
                string_pattern = re.compile(rf'(f?{quote}[^{quote}]*?{quote})')
                
                for string_match in string_pattern.finditer(line):
                    original_string = string_match.group(0)
                    
                    # Prüfe ob Emoji enthalten
                    if not EMOJI_PATTERN.search(original_string):
                        continue
                    
                    # Ersetze Emojis in diesem String
                    is_fstring = original_string.startswith('f')
                    if is_fstring:
                        # Bereits f-string
                        inner = original_string[2:-1]  # Entferne f" und "
                        new_inner = EMOJI_PATTERN.sub(replace_emoji, inner)
                        new_string = f'f{quote}{new_inner}{quote}'
                    else:
                        # Konvertiere zu f-string
                        inner = original_string[1:-1]  # Entferne " und "
                        new_inner = EMOJI_PATTERN.sub(replace_emoji, inner)
                        new_string = f'f{quote}{new_inner}{quote}'
                    
                    # Ersetze in Zeile
                    new_line = new_line.replace(original_string, new_string, 1)
            
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    # Füge Import hinzu wenn nötig und nicht vorhanden
    if replacements > 0 and not has_import:
        # Finde Zeile nach imports
        import_insert_line = 0
        for i, line in enumerate(new_lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_insert_line = i + 1
        
        new_lines.insert(import_insert_line, 'from emoji_toggle import e')
    
    # Schreibe neue Datei
    new_content = '\n'.join(new_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return replacements, backup_path


def main():
    """Hauptfunktion."""
    print("=" * 80)
    print("🚀 SIMPLE EMOJI AUTO-REPLACER")
    print("=" * 80)
    print()
    
    root = Path(__file__).parent
    total_replacements = 0
    
    for filename in TARGET_FILES:
        file_path = root / filename
        
        if not file_path.exists():
            print(f"⚠️ Überspringe: {filename} (nicht gefunden)")
            continue
        
        print(f"\n📝 Verarbeite: {filename}")
        print("-" * 80)
        
        try:
            replacements, backup = process_file(file_path)
            print(f"✅ {replacements} Emojis ersetzt")
            total_replacements += replacements
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ GESAMT: {total_replacements} Emojis in {len(TARGET_FILES)} Dateien ersetzt")
    print("=" * 80)
    print("\n💡 WICHTIG:")
    print("1. Backup-Dateien (.bak) wurden erstellt")
    print("2. Teste die App mit 'streamlit run gui.py'")
    print("3. Prüfe Emojis aktiviert/deaktiviert in Optionen")
    print("4. Bei Problemen: Backup wiederherstellen mit 'copy *.bak *.py'")


if __name__ == "__main__":
    main()
