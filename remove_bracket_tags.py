"""
Entfernt ALLE Tags in eckigen Klammern aus allen Python-Dateien
Beispiele: [OK], [ERROR], [WARNING], [TOOL], [DESIGN], usw.
"""

import re
from pathlib import Path

# Alle bekannten Tags in eckigen Klammern
BRACKET_TAGS = [
    'OK', 'ERROR', 'WARNING', 'TOOL', 'FALSE', 'DESIGN', 'PACKAGE', 
    'CHART', 'SEARCH', 'TARGET', 'DELETE', 'LAUNCH', 'MONEY', 'INFO',
    'FILE', 'BUILD', 'STATS', 'IDEA', 'NOTE', 'FOLDER', 'SKIP', 
    'TEMP', 'POWER', 'GREEN', 'WINNER', 'MERGE', 'FINALISIERUNG',
    'ZUSATZ-PDF', 'TEMPLATE', 'PDF', 'ZUSAMMENFASSUNG', 'TEST',
    'BEISPIEL', 'DEBUG', 'KRITISCH', 'WARNUNG', 'FEHLER', 'ERFOLG'
]

# Regex-Pattern für alle Tags in eckigen Klammern
# Matches: [TAG] oder [TAG ]  oder [ TAG] oder f"[TAG]" usw.
pattern = r'\[(' + '|'.join(BRACKET_TAGS) + r')\]\s*'

def remove_bracket_tags(content: str) -> tuple[str, int]:
    """Entfernt alle Tags in eckigen Klammern aus dem Inhalt"""
    
    # Zähle Ersetzungen
    count = len(re.findall(pattern, content, re.IGNORECASE))
    
    # Ersetze alle Vorkommen
    new_content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    return new_content, count

def process_file(file_path: Path) -> dict:
    """Verarbeitet eine einzelne Python-Datei"""
    try:
        content = file_path.read_text(encoding='utf-8')
        new_content, count = remove_bracket_tags(content)
        
        if count > 0:
            file_path.write_text(new_content, encoding='utf-8')
            return {
                'file': file_path.name,
                'replacements': count,
                'status': 'success'
            }
        else:
            return {
                'file': file_path.name,
                'replacements': 0,
                'status': 'skipped'
            }
    except Exception as e:
        return {
            'file': file_path.name,
            'replacements': 0,
            'status': 'error',
            'error': str(e)
        }

def main():
    root = Path(__file__).parent
    
    # Finde alle Python-Dateien
    python_files = list(root.rglob('*.py'))
    
    # Exkludiere dieses Script selbst
    python_files = [f for f in python_files if f.name != 'remove_bracket_tags.py']
    
    # Exkludiere virtuelle Umgebungen und Backups
    python_files = [f for f in python_files if not any(
        part in f.parts for part in ['venv', '.venv', 'env', '__pycache__', 
                                      '_backup', 'backup', '.git']
    )]
    
    print(f"\nGefunden: {len(python_files)} Python-Dateien\n")
    print("=" * 80)
    
    results = {
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'total_replacements': 0
    }
    
    # Verarbeite jede Datei
    for py_file in sorted(python_files):
        result = process_file(py_file)
        
        if result['status'] == 'success':
            results['processed'] += 1
            results['total_replacements'] += result['replacements']
            if result['replacements'] > 0:
                print(f"✓ {result['file']}: {result['replacements']} Tags entfernt")
        elif result['status'] == 'skipped':
            results['skipped'] += 1
        else:
            results['errors'] += 1
            print(f"✗ {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print(f"\nZUSAMMENFASSUNG:")
    print(f"  Verarbeitet: {results['processed']} Dateien")
    print(f"  Übersprungen: {results['skipped']} Dateien (keine Tags)")
    print(f"  Fehler: {results['errors']} Dateien")
    print(f"  GESAMT ENTFERNT: {results['total_replacements']} Tags")
    print()

if __name__ == '__main__':
    main()
