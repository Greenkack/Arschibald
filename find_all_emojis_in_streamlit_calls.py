"""
Findet ALLE Emojis in Streamlit-Aufrufen und gibt einen Report aus.

Scannt alle Python-Dateien und listet Emojis in st.write(), st.error(), etc. auf.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict

# Emoji Pattern
EMOJI_PATTERN = re.compile(
    r'([\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
    r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF'
    r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+)'
)

# Streamlit-Methoden die Text enthalten können
ST_METHODS = [
    'write', 'markdown', 'title', 'header', 'subheader', 'text', 'caption', 'code',
    'success', 'info', 'warning', 'error', 'exception',
    'button', 'download_button', 'link_button',
    'checkbox', 'radio', 'selectbox', 'multiselect',
    'metric', 'columns'
]

# Pattern für st.method("text 📊") oder st.method(f"text {var} 📊")
ST_CALL_PATTERN = re.compile(
    r'st\.(' + '|'.join(ST_METHODS) + r')\s*\([^)]*?([\'"][^\'"]*?[📊🔧💰📈⚡🏠🌍📋✅❌⚠️💡🔍📄🖼️🎨📱💻🔐📞📧🗓️👤👥🏢💳🔔🎁📌📎🔗🔄♻️📥📤💾🗂️🔎🔝⬆️⬇️➡️⬅️✔️✖️➕➖🆕🆓🆙🔴🟢🟡🔵⚪⚫🟣🟤🟠🌡️☀️🎞️🎯💻🏗️🔌📊💰📈🎛️🎬🔮🌤️💎🎪🎢🎡📶📡🔬🔭🎓🎖️🏆🏅🎗️🎟️🎫🎬🎭🎪🎨🎬🎤🎧🎼🎹🎷🎺🎸🎻🎬🎭🎪🎨🎬🎤🎧🎼🎹🎷🎺🎸🎻🎬🎭🎪🎨🎬🎤🎧🎼🎹🎷🎺🎸🎻][^\'"]*?[\'"])',
    re.DOTALL
)

SKIP_FILES = {
    'emoji_toggle.py',
    'replace_all_emojis.py',
    'find_all_emojis_in_streamlit_calls.py',
    'clean_unicode_emojis.py',
    '__pycache__',
}

SKIP_DIRS = {
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.venv',
    'node_modules',
}


def find_python_files(root_dir: Path) -> List[Path]:
    """Findet alle Python-Dateien."""
    python_files = []
    for py_file in root_dir.rglob('*.py'):
        if py_file.name in SKIP_FILES:
            continue
        if any(skip_dir in py_file.parts for skip_dir in SKIP_DIRS):
            continue
        python_files.append(py_file)
    return python_files


def find_emojis_in_file(file_path: Path) -> List[Tuple[int, str, List[str]]]:
    """
    Findet alle Streamlit-Calls mit Emojis in einer Datei.
    
    Returns:
        Liste von (line_number, line_text, emojis_list)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {file_path}: {e}")
        return []
    
    results = []
    for i, line in enumerate(lines, start=1):
        # Überspringe Kommentare
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        
        # Finde Emojis in der Zeile
        emojis = EMOJI_PATTERN.findall(line)
        if not emojis:
            continue
        
        # Prüfe, ob es ein Streamlit-Call ist
        for method in ST_METHODS:
            if f'st.{method}' in line:
                results.append((i, line.rstrip(), emojis))
                break
    
    return results


def main():
    """Hauptfunktion - scannt und listet alle Emojis auf."""
    print("=" * 80)
    print("🔍 EMOJI SCANNER - Findet alle Emojis in Streamlit-Aufrufen")
    print("=" * 80)
    print()
    
    root_dir = Path(__file__).parent
    python_files = find_python_files(root_dir)
    
    print(f"📁 Scanne {len(python_files)} Python-Dateien...\n")
    
    all_findings: Dict[str, List[Tuple[int, str, List[str]]]] = {}
    total_emojis = 0
    
    for file_path in python_files:
        findings = find_emojis_in_file(file_path)
        if findings:
            all_findings[str(file_path.name)] = findings
            total_emojis += sum(len(emojis) for _, _, emojis in findings)
    
    # Ausgabe der Ergebnisse
    print("=" * 80)
    print(f"📊 ERGEBNISSE: {len(all_findings)} Dateien mit Emojis")
    print("=" * 80)
    print()
    
    for filename, findings in sorted(all_findings.items()):
        print(f"\n📄 {filename}")
        print("-" * 80)
        for line_num, line_text, emojis in findings:
            emoji_str = ', '.join(emojis)
            print(f"  Zeile {line_num:4d}: {emoji_str}")
            print(f"              {line_text[:100]}")
        print(f"  → {len(findings)} Zeilen mit Emojis")
    
    print()
    print("=" * 80)
    print(f"✅ GESAMT: {total_emojis} Emojis in {sum(len(f) for f in all_findings.values())} Zeilen")
    print("=" * 80)
    print()
    print("💡 NÄCHSTE SCHRITTE:")
    print("1. Nutze 'from emoji_toggle import e' in jeder Datei")
    print("2. Ersetze 'st.write(\"📊 Text\")' mit 'st.write(f\"{e('📊')} Text\")'")
    print("3. Teste mit Emojis aktiviert/deaktiviert")
    print()


if __name__ == "__main__":
    main()
