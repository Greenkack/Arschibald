import streamlit as st
import traceback

def main():
    st.set_page_config(page_title="Test App", layout="wide")
    st.title("[LAUNCH] Minimale Test-App")
    st.success("[OK] Die App läuft erfolgreich!")
    
    st.write("### Test-Bereiche:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("[CHART] Daten-Eingabe")
        if st.button("Test Button 1"):
            st.balloons()
    
    with col2:
        st.info("[STATS] Analyse")
        if st.button("Test Button 2"):
            st.snow()
    
    st.write("---")
    st.write("**Status:** App läuft ohne moderne CSS-Templates")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Fehler: {e}")
        st.code(traceback.format_exc())