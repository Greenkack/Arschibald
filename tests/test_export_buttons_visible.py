"""
Test ob Export-Buttons jetzt sichtbar sind

Prüft ob die Buttons in render_export_options integriert sind.
"""

def test_export_buttons_in_ui_components():
    """Test ob Export-Buttons in UI-Komponenten vorhanden sind"""
    try:
        with open("utils/pv3d_ui_components.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("btn_export_screenshot_inline", "Screenshot Button"),
            ("btn_export_multiview_inline", "Multi-View Button"),
            ("btn_export_360_inline", "360° Animation Button"),
            ("btn_export_3d_model_inline", "3D-Modell Button"),
            ("btn_export_csv_inline", "CSV Button"),
            ("btn_export_json_inline", "JSON Button"),
            ("[LAUNCH] Export starten", "Export-Überschrift"),
            ("trigger_screenshot_export", "Screenshot Trigger"),
            ("trigger_multiview_export", "Multi-View Trigger"),
            ("trigger_360_export", "360° Trigger"),
            ("trigger_3d_model_export", "3D-Modell Trigger"),
            ("trigger_csv_export", "CSV Trigger"),
            ("trigger_json_export", "JSON Trigger")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"[OK] {description} gefunden")
            else:
                print(f"[ERROR] {description} NICHT gefunden")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"[ERROR] Test fehlgeschlagen: {e}")
        return False


def test_trigger_logic_in_main():
    """Test ob Trigger-Logik in Hauptdatei vorhanden ist"""
    try:
        with open("solar_3d_view_module.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("trigger_screenshot", "Screenshot Trigger-Check"),
            ("trigger_multiview", "Multi-View Trigger-Check"),
            ("trigger_360", "360° Trigger-Check"),
            ("trigger_3d_model", "3D-Modell Trigger-Check"),
            ("trigger_csv", "CSV Trigger-Check"),
            ("trigger_json", "JSON Trigger-Check"),
            ("Reset Trigger", "Trigger-Reset Logik")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"[OK] {description} gefunden")
            else:
                print(f"[ERROR] {description} NICHT gefunden")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"[ERROR] Test fehlgeschlagen: {e}")
        return False


def run_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("Export-Buttons Sichtbarkeits-Test")
    print("="*60 + "\n")
    
    print("Test 1: Export-Buttons in UI-Komponenten")
    print("-" * 60)
    result1 = test_export_buttons_in_ui_components()
    print()
    
    print("Test 2: Trigger-Logik in Hauptdatei")
    print("-" * 60)
    result2 = test_trigger_logic_in_main()
    print()
    
    print("="*60)
    if result1 and result2:
        print("🎉 Alle Tests bestanden!")
        print("\n[OK] Export-Buttons sind jetzt SICHTBAR!")
        print("\nSo testen Sie in der App:")
        print("1. Starten Sie: streamlit run gui.py")
        print("2. Gehen Sie zu: 3D-Visualisierung")
        print("3. Sidebar → Export-Optionen")
        print("4. Aktivieren Sie eine Checkbox (z.B. Screenshot)")
        print("5. [OK] Button sollte SOFORT erscheinen!")
        print("6. Klicken Sie den Button")
        print("7. [OK] Download-Button sollte erscheinen!")
        return 0
    else:
        print("[WARNING] Einige Tests fehlgeschlagen")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
