"""
Bulk Widget Migration Script
=============================

Migriert verbleibende Streamlit-Widgets zu session_widgets in data_input.py
"""

import re
from pathlib import Path

# Files to migrate
FILES_TO_MIGRATE = [
    'data_input.py',
    'options.py',
]

# Widget mapping
WIDGET_PATTERNS = [
    # st.text_input(...) -> session_text_input(...)
    (
        r"st\.text_input\(",
        "session_text_input("
    ),
    # st.number_input(...) -> session_number_input(...)
    (
        r"st\.number_input\(",
        "session_number_input("
    ),
    # st.selectbox(...) -> session_selectbox(...)
    (
        r"st\.selectbox\(",
        "session_selectbox("
    ),
    # st.checkbox(...) -> session_checkbox(...)
    (
        r"st\.checkbox\(",
        "session_checkbox("
    ),
    # st.slider(...) -> session_slider(...)
    (
        r"st\.slider\(",
        "session_slider("
    ),
]

def migrate_file(file_path: Path, dry_run=True):
    """Migriere Widgets in einer Datei"""
    
    if not file_path.exists():
        print(f"❌ Datei nicht gefunden: {file_path}")
        return
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Count replacements
    replacements = {}
    
    # Apply patterns
    for pattern, replacement in WIDGET_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            replacements[pattern] = len(matches)
            content = re.sub(pattern, replacement, content)
    
    # Summary
    total_replacements = sum(replacements.values())
    
    if total_replacements == 0:
        print(f"✅ {file_path.name}: Keine Widgets zum Migrieren gefunden")
        return
    
    print(f"\n📝 {file_path.name}:")
    for pattern, count in replacements.items():
        widget_type = pattern.replace(r"st\.", "").replace(r"\(", "")
        print(f"   - {widget_type}: {count} Ersetzungen")
    
    print(f"   📊 Gesamt: {total_replacements} Widgets migriert")
    
    if not dry_run:
        # Write back
        file_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Datei gespeichert")
    else:
        print(f"   ℹ️ DRY RUN - Keine Änderungen geschrieben")
    
    return total_replacements


def main():
    """Main migration function"""
    
    print("=" * 60)
    print("🔄 Bulk Widget Migration")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    
    # Check if session_widgets.py exists
    session_widgets_path = base_path / 'session_widgets.py'
    if not session_widgets_path.exists():
        print("❌ session_widgets.py nicht gefunden!")
        print("   Bitte erst Phase 3 implementieren.")
        return
    
    print("✅ session_widgets.py gefunden\n")
    
    # Dry run first
    print("🔍 DRY RUN - Analysiere Dateien...\n")
    
    total_all = 0
    for file_name in FILES_TO_MIGRATE:
        file_path = base_path / file_name
        count = migrate_file(file_path, dry_run=True)
        if count:
            total_all += count
    
    print(f"\n{'=' * 60}")
    print(f"📊 GESAMT: {total_all} Widgets würden migriert")
    print(f"{'=' * 60}")
    
    # Ask for confirmation
    print("\n⚠️ HINWEIS: Dies migriert nur die Widget-Funktionen.")
    print("   Parameter wie 'form_id' müssen manuell hinzugefügt werden.")
    print("\n❓ Migration durchführen? (j/n): ", end="")
    
    response = input().strip().lower()
    
    if response in ['j', 'ja', 'y', 'yes']:
        print("\n🚀 Starte Migration...\n")
        
        for file_name in FILES_TO_MIGRATE:
            file_path = base_path / file_name
            migrate_file(file_path, dry_run=False)
        
        print(f"\n{'=' * 60}")
        print("✅ Migration abgeschlossen!")
        print(f"{'=' * 60}")
        print("\n📝 NÄCHSTE SCHRITTE:")
        print("1. Code-Review durchführen")
        print("2. form_id Parameter zu wichtigen Widgets hinzufügen")
        print("3. App testen: streamlit run gui.py")
        print("4. Bei Problemen: Git diff prüfen")
    else:
        print("\n❌ Migration abgebrochen.")


if __name__ == '__main__':
    main()
