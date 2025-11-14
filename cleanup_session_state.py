"""
Cleanup Script für Session State
Entfernt nicht-serialisierbare Objekte aus Session State
"""

import streamlit as st

def cleanup_non_serializable_objects():
    """Entfernt bekannte nicht-serialisierbare Objekte aus Session State"""
    
    # Liste der Keys, die entfernt werden sollen
    keys_to_remove = [
        'pdf_section_manager',  # PDFSectionManager - nicht serialisierbar
    ]
    
    removed_count = 0
    for key in keys_to_remove:
        if key in st.session_state:
            try:
                del st.session_state[key]
                removed_count += 1
                print(f"[OK] Entfernt: {key}")
            except Exception as e:
                print(f"[ERROR] Fehler beim Entfernen von {key}: {e}")
    
    if removed_count > 0:
        print(f"\n🎉 {removed_count} nicht-serialisierbare Objekte entfernt!")
    else:
        print("\n[OK] Keine problematischen Objekte in Session State gefunden.")
    
    return removed_count


if __name__ == "__main__":
    print("=" * 80)
    print("🧹 Session State Cleanup")
    print("=" * 80)
    print("\nHinweis: Dieses Script sollte VOR dem Start der Streamlit-App ausgeführt werden.")
    print("Es entfernt bekannte nicht-serialisierbare Objekte aus dem Session State.\n")
    
    # Hinweis: Dieses Script kann nur in einer laufenden Streamlit-App verwendet werden
    print("[WARNING]  Dieses Script muss innerhalb einer Streamlit-App laufen!")
    print("Fügen Sie am Anfang Ihrer gui.py folgende Zeile hinzu:")
    print("\nfrom cleanup_session_state import cleanup_non_serializable_objects")
    print("cleanup_non_serializable_objects()  # Am Anfang von main()")
