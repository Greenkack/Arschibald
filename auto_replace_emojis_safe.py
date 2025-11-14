"""
Automatisches Ersetzen von Emojis in Streamlit-Calls mit e() Helper.

SICHER: Macht Backup vor Änderungen und zeigt Preview.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
import shutil

# Emoji Pattern
EMOJI_PATTERN = re.compile(
    r'([\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
    r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF'
    r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+)'
)

SKIP_FILES = {
    'emoji_toggle.py',
    'replace_all_emojis.py',
    'find_all_emojis_in_streamlit_calls.py',
    'auto_replace_emojis_safe.py',
    'clean_unicode_emojis.py',
}


def replace_emoji_in_string(text: str) -> Tuple[str, int]:
    """
    Ersetzt Emojis in einem String mit e() Wrapper.
    
    Beispiele:
        "[CHART] Dashboard" -> f"{e('[CHART]')} Dashboard"
        f"[OK] Saved {count}" -> f"{e('[OK]')} Saved {count}"
        '[ERROR] Error' -> f"{e('[ERROR]')} Error"
    
    Returns:
        (neuer_text, anzahl_ersetzungen)
    """
    emojis = EMOJI_PATTERN.findall(text)
    if not emojis:
        return text, 0
    
    # Entferne Anführungszeichen am Anfang/Ende
    quote_char = None
    is_fstring = False
    
    if text.startswith('f"') or text.startswith("f'"):
        is_fstring = True
        quote_char = text[1]
        text_content = text[2:-1]  # Entferne f" und "
    elif text.startswith('"'):
        quote_char = '"'
        text_content = text[1:-1]
    elif text.startswith("'"):
        quote_char = "'"
        text_content = text[1:-1]
    else:
        return text, 0
    
    # Ersetze jeden Emoji
    new_content = text_content
    replacements = 0
    
    for emoji in emojis:
        # Ersetze Emoji mit {e("emoji")}
        new_content = new_content.replace(emoji, f'{{e("{emoji}")}}')
        replacements += 1
    
    # Baue neuen String
    result = f'f{quote_char}{new_content}{quote_char}'
    return result, replacements


def process_line(line: str) -> Tuple[str, int]:
    """
    Verarbeitet eine Zeile und ersetzt Emojis in Strings.
    
    Returns:
        (neue_zeile, anzahl_ersetzungen)
    """
    # Finde String-Literale
    # Pattern matcht: "text", 'text', f"text", f'text'
    string_pattern = re.compile(r'(f?["\'][^"\']*?["\'])')
    
    total_replacements = 0
    offset = 0
    new_line = line
    
    for match in string_pattern.finditer(line):
        string_literal = match.group(0)
        
        # Prüfe ob Emoji enthalten
        if not EMOJI_PATTERN.search(string_literal):
            continue
        
        # Ersetze Emojis
        new_string, replacements = replace_emoji_in_string(string_literal)
        
        if replacements > 0:
            start_pos = match.start() + offset
            end_pos = match.end() + offset
            
            new_line = new_line[:start_pos] + new_string + new_line[end_pos:]
            offset += len(new_string) - len(string_literal)
            total_replacements += replacements
    
    return new_line, total_replacements


def process_file(file_path: Path, dry_run: bool = True) -> Tuple[int, int]:
    """
    Verarbeitet eine Python-Datei und ersetzt alle Emojis.
    
    Args:
        file_path: Pfad zur Datei
        dry_run: Wenn True, werden keine Änderungen geschrieben
    
    Returns:
        (zeilen_geändert, emojis_ersetzt)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Fehler beim Lesen: {e}")
        return 0, 0
    
    new_lines = []
    total_replacements = 0
    lines_changed = 0
    needs_import = False
    has_import = False
    
    # Prüfe ob e() bereits importiert
    for line in lines:
        if ('from emoji_toggle import' in line and ' e' in line) or \
           ('from emoji_toggle import' in line and line.strip().endswith('e')):
            has_import = True
            break
    
    # Verarbeite Zeilen
    for i, line in enumerate(lines):
        # Überspringe Docstrings und Kommentare
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            new_lines.append(line)
            continue
        
        # Ersetze Emojis
        new_line, replacements = process_line(line)
        
        if replacements > 0:
            total_replacements += replacements
            lines_changed += 1
            needs_import = True
            
            if not dry_run and replacements > 0:
                print(f"  Zeile {i+1:4d}: {replacements} Emojis ersetzt")
        
        new_lines.append(new_line)
    
    # Füge Import hinzu wenn nötig
    if needs_import and not has_import:
        # Finde Stelle für Import (nach anderen Imports)
        insert_pos = 0
        for i, line in enumerate(new_lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_pos = i + 1
        
        new_lines.insert(insert_pos, 'from emoji_toggle import e\n')
        lines_changed += 1
    
    # Schreibe Datei
    if not dry_run and lines_changed > 0:
        try:
            # Backup erstellen
            backup_path = file_path.with_suffix('.py.backup')
            shutil.copy2(file_path, backup_path)
            
            # Neue Datei schreiben
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"[OK] {file_path.name}: {total_replacements} Emojis ersetzt, Backup: {backup_path.name}")
        except Exception as e:
            print(f"[ERROR] Fehler beim Schreiben: {e}")
            return 0, 0
    
    return lines_changed, total_replacements


def main():
    """Hauptfunktion."""
    print("=" * 80)
    print("[TOOL] AUTOMATISCHES EMOJI-REPLACEMENT (SICHER)")
    print("=" * 80)
    print()
    
    # Teste zuerst mit einzelner Datei
    test_file = Path(__file__).parent / "test_css_templates.py"
    
    if test_file.exists():
        print(f"🧪 TEST-MODUS: Verarbeite {test_file.name}")
        print("=" * 80)
        
        # Dry-Run
        print("\n📋 DRY-RUN (keine Änderungen):")
        lines_changed, emojis_replaced = process_file(test_file, dry_run=True)
        print(f"\n→ Würde ändern: {lines_changed} Zeilen, {emojis_replaced} Emojis")
        
        # Frage Benutzer
        print("\n" + "=" * 80)
        response = input("\n[OK] Test-Datei WIRKLICH ändern? (ja/nein): ").strip().lower()
        
        if response == 'ja':
            print("\n🔄 SCHREIBE ÄNDERUNGEN...")
            lines_changed, emojis_replaced = process_file(test_file, dry_run=False)
            print(f"\n[OK] FERTIG: {lines_changed} Zeilen geändert, {emojis_replaced} Emojis ersetzt")
        else:
            print("\n[ERROR] ABGEBROCHEN - Keine Änderungen vorgenommen")
    else:
        print(f"[ERROR] Test-Datei nicht gefunden: {test_file}")
    
    print("\n" + "=" * 80)
    print("[IDEA] HINWEIS:")
    print("Wenn der Test erfolgreich war, können Sie das Skript für alle Dateien ausführen.")
    print("=" * 80)


if __name__ == "__main__":
    main()
