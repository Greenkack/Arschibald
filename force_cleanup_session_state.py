"""
FORCE CLEANUP - Entfernt ALLE nicht-serialisierbaren Objekte aus session_state
Dieses Script wird beim App-Start automatisch ausgeführt
"""

import streamlit as st
import pickle

def force_cleanup_all_non_serializable():
    """
    Aggressives Cleanup: Testet JEDES Objekt in session_state auf Serialisierbarkeit
    und löscht nicht-serialisierbare Objekte automatisch
    """
    keys_to_delete = []
    
    for key in list(st.session_state.keys()):
        try:
            # Versuche das Objekt zu picklen
            obj = st.session_state[key]
            pickle.dumps(obj)
        except (TypeError, AttributeError, pickle.PicklingError) as e:
            # Objekt kann nicht serialisiert werden -> zur Löschliste
            keys_to_delete.append(key)
            print(f"Nicht-serialisierbares Objekt gefunden: {key} (Typ: {type(obj).__name__})")
    
    # Lösche alle nicht-serialisierbaren Objekte
    for key in keys_to_delete:
        try:
            del st.session_state[key]
            print(f"Gelöscht: {key}")
        except Exception as e:
            print(f"Fehler beim Löschen von {key}: {e}")
    
    if keys_to_delete:
        print(f"\n Cleanup abgeschlossen: {len(keys_to_delete)} nicht-serialisierbare Objekte entfernt")
    
    return len(keys_to_delete)

if __name__ == "__main__":
    print("Starte FORCE CLEANUP...")
    removed_count = force_cleanup_all_non_serializable()
    print(f"\nFertig! {removed_count} Objekte entfernt.")
