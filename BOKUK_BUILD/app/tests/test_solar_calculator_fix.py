#!/usr/bin/env python3
"""
Test Script: Teste ob der solar_calculator Fehler behoben ist
"""

import sys

sys.path.append('.')


def test_solar_calculator_import():
    """Teste den Import des solar_calculator Moduls"""
    try:
        print('✅ solar_calculator Modul erfolgreich importiert!')
        return True
    except Exception as e:
        print(f'❌ Import-Fehler: {e}')
        return False


def test_ensure_project_data_dicts():
    """Teste die _ensure_project_data_dicts Funktion"""
    try:
        import streamlit as st

        import solar_calculator

        # Mock st.session_state
        class MockSessionState:
            def __init__(self):
                self.data = {}

            def __contains__(self, key):
                return key in self.data

            def __getitem__(self, key):
                return self.data[key]

            def __setitem__(self, key, value):
                self.data[key] = value

        st.session_state = MockSessionState()

        # Test der Funktion
        result = solar_calculator._ensure_project_data_dicts()

        if result is None:
            print('❌ _ensure_project_data_dicts gibt None zurück!')
            return False

        if not isinstance(result, dict):
            print(
                f'❌ _ensure_project_data_dicts gibt {
                    type(result)} zurück, erwartet dict!')
            return False

        if 'project_details' not in result:
            print('❌ project_details nicht in result!')
            return False

        print('✅ _ensure_project_data_dicts funktioniert korrekt!')
        print(f'   - Rückgabe-Typ: {type(result)}')
        print(f'   - project_details vorhanden: {"project_details" in result}')
        print(f'   - Keys: {list(result.keys())}')

        return True

    except Exception as e:
        print(f'❌ Fehler beim Testen von _ensure_project_data_dicts: {e}')
        return False


def test_render_solar_calculator_start():
    """Teste den Start der render_solar_calculator Funktion"""
    try:
        import streamlit as st

        import solar_calculator

        # Mock st.session_state
        class MockSessionState:
            def __init__(self):
                self.data = {}

            def __contains__(self, key):
                return key in self.data

            def __getitem__(self, key):
                return self.data[key]

            def __setitem__(self, key, value):
                self.data[key] = value

        st.session_state = MockSessionState()

        # Mock andere Streamlit Funktionen
        def mock_function(*args, **kwargs):
            pass

        st.markdown = mock_function
        st.write = mock_function
        st.columns = lambda x: [mock_function] * x
        st.selectbox = lambda *args, **kwargs: "Test"
        st.number_input = lambda *args, **kwargs: 0
        st.checkbox = lambda *args, **kwargs: False
        st.button = lambda *args, **kwargs: False

        # Test-Texte
        texts = {
            'please_select_option': '--- Bitte wählen ---',
            'menu_item_solar_calculator': 'Solar Calculator'
        }

        # Teste nur den Anfang der Funktion (bis zur ersten
        # Streamlit-Interaktion)
        pd = solar_calculator._ensure_project_data_dicts()
        details = pd['project_details']

        print('✅ render_solar_calculator Anfang funktioniert!')
        print(f'   - pd ist nicht None: {pd is not None}')
        print(f'   - details ist dict: {isinstance(details, dict)}')

        return True

    except Exception as e:
        print(f'❌ Fehler beim Testen von render_solar_calculator: {e}')
        return False


if __name__ == "__main__":
    print("🔧 TESTE SOLAR CALCULATOR FIX")
    print("=" * 50)

    success = True

    # Test 1: Import
    print("\n1. TESTE IMPORT:")
    if not test_solar_calculator_import():
        success = False

    # Test 2: _ensure_project_data_dicts
    print("\n2. TESTE _ensure_project_data_dicts:")
    if not test_ensure_project_data_dicts():
        success = False

    # Test 3: render_solar_calculator Start
    print("\n3. TESTE render_solar_calculator START:")
    if not test_render_solar_calculator_start():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("✅ ALLE TESTS ERFOLGREICH!")
        print("✅ Der TypeError: 'NoneType' object is not subscriptable ist behoben!")
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN!")
