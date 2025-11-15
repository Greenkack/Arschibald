"""
Automatisches Ersetzen aller hartcodierten Emojis mit e() Helper-Funktion.

Dieses Skript scannt alle Python-Dateien und ersetzt Emoji-Strings mit dem e() Wrapper.
"""

import re
import os
from pathlib import Path
from typing import List, Tuple

# Emoji Pattern (alle Unicode-Ranges)
EMOJI_PATTERN = re.compile(
    r'([\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
    r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF'
    r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+)'
)

# Dateien, die übersprungen werden sollen
SKIP_FILES = {
    'emoji_toggle.py',  # Enthält die e() Funktion selbst
    'replace_all_emojis.py',  # Dieses Skript
    'clean_unicode_emojis.py',  # Utility-Skript
    '__pycache__',
}

# Verzeichnisse, die übersprungen werden
SKIP_DIRS = {
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.venv',
    'node_modules',
}


def find_python_files(root_dir: str) -> List[Path]:
    """Findet alle Python-Dateien im Verzeichnis."""
    python_files = []
    root_path = Path(root_dir)
    
    for py_file in root_path.rglob('*.py'):
        # Prüfe, ob Datei oder Parent-Dir in Skip-Liste
        if py_file.name in SKIP_FILES:
            continue
        if any(skip_dir in py_file.parts for skip_dir in SKIP_DIRS):
            continue
        python_files.append(py_file)
    
    return python_files


def find_emojis_in_line(line: str) -> List[Tuple[str, int, int]]:
    """
    Findet alle Emojis in einer Zeile.
    
    Returns:
        Liste von (emoji, start_pos, end_pos) Tupeln
    """
    matches = []
    for match in EMOJI_PATTERN.finditer(line):
        emoji = match.group(0)
        start = match.start()
        end = match.end()
        matches.append((emoji, start, end))
    return matches


def replace_emoji_in_string(line: str) -> Tuple[str, int]:
    """
    Ersetzt Emojis in String-Literalen mit e() Wrapper.
    
    Returns:
        (neue_zeile, anzahl_ersetzungen)
    """
    replacements = 0
    new_line = line
    
    # Finde alle String-Literale (einfache und doppelte Anführungszeichen)
    # Pattern: "text more" oder 'text more' oder f"text {var} "
    string_patterns = [
        r'"([^"]*?")',  # Double quotes
        r"'([^']*?')",  # Single quotes
        r'f"([^"]*?")',  # f-strings double
        r"f'([^']*?')",  # f-strings single
    ]
    
    for pattern in string_patterns:
        matches = list(re.finditer(pattern, line))
        offset = 0
        
        for match in matches:
            string_content = match.group(0)
            emojis = find_emojis_in_line(string_content)
            
            if not emojis:
                continue
            
            # Ersetze jeden Emoji in diesem String
            modified_string = string_content
            emoji_offset = 0
            
            for emoji, start, end in emojis:
                # Berechne Position mit Offset
                actual_start = start + emoji_offset
                
                # Ersetze Emoji mit e("emoji")
                before = modified_string[:actual_start]
                after = modified_string[end + emoji_offset:]
                replacement = f'{{e("{emoji}")}}'
                
                # Wenn der String kein f-string ist, mache ihn zu einem
                if not modified_string.startswith('f"') and not modified_string.startswith("f'"):
                    # Konvertiere zu f-string
                    if modified_string[0] == '"':
                        modified_string = 'f"' + modified_string[1:]
                    else:
                        modified_string = "f'" + modified_string[1:]
                    emoji_offset += 1
                
                modified_string = before + replacement + after
                emoji_offset += len(replacement) - len(emoji)
                replacements += 1
            
            # Ersetze in original line
            start_pos = match.start() + offset
            end_pos = match.end() + offset
            new_line = new_line[:start_pos] + modified_string + new_line[end_pos:]
            offset += len(modified_string) - len(string_content)
    
    return new_line, replacements


def process_file(file_path: Path) -> Tuple[int, int]:
    """
    Verarbeitet eine einzelne Python-Datei.
    
    Returns:
        (anzahl_zeilen_geändert, anzahl_emojis_ersetzt)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Fehler beim Lesen von {file_path}: {e}")
        return 0, 0
    
    new_lines = []
    total_replacements = 0
    lines_changed = 0
    needs_import = False
    has_import = False
    
    # Prüfe, ob e() bereits importiert ist
    for line in lines:
        if 'from emoji_toggle import' in line and 'e' in line:
            has_import = True
            break
    
    # Verarbeite jede Zeile
    for line in lines:
        # Überspringe Kommentare und Docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            new_lines.append(line)
            continue
        
        # Ersetze Emojis
        new_line, replacements = replace_emoji_in_string(line)
        
        if replacements > 0:
            total_replacements += replacements
            lines_changed += 1
            needs_import = True
        
        new_lines.append(new_line)
    
    # Wenn Emojis ersetzt wurden und kein Import vorhanden, füge Import hinzu
    if needs_import and not has_import:
        # Finde passende Stelle für Import (nach anderen Imports)
        insert_pos = 0
        for i, line in enumerate(new_lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_pos = i + 1
        
        # Füge Import hinzu
        new_lines.insert(insert_pos, 'from emoji_toggle import e\n')
        lines_changed += 1
    
    # Schreibe Datei nur, wenn Änderungen vorgenommen wurden
    if lines_changed > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"{file_path.name}: {total_replacements} Emojis in {lines_changed} Zeilen ersetzt")
        except Exception as e:
            print(f"Fehler beim Schreiben von {file_path}: {e}")
            return 0, 0
    
    return lines_changed, total_replacements


def main():
    """Hauptfunktion - scannt und ersetzt alle Emojis."""
    print("Suche Python-Dateien...")
    root_dir = Path(__file__).parent
    python_files = find_python_files(root_dir)
    
    print(f"Gefunden: {len(python_files)} Python-Dateien\n")
    
    total_files = 0
    total_lines = 0
    total_emojis = 0
    
    for file_path in python_files:
        lines_changed, emojis_replaced = process_file(file_path)
        
        if lines_changed > 0:
            total_files += 1
            total_lines += lines_changed
            total_emojis += emojis_replaced
    
    print(f"\n{'='*60}")
    print(f"FERTIG!")
    print(f"{'='*60}")
    print(f"Dateien geändert: {total_files}")
    print(f"Zeilen geändert: {total_lines}")
    print(f"😀 Emojis ersetzt: {total_emojis}")
    print(f"{'='*60}\n")
    
    if total_emojis > 0:
        print("WICHTIG:")
        print("1. Überprüfe die Änderungen mit 'git diff'")
        print("2. Teste die App mit Emojis aktiviert")
        print("3. Teste die App mit Emojis deaktiviert")
        print("4. Committe nur, wenn alles funktioniert!")


if __name__ == "__main__":
    main()
