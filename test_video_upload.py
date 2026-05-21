"""
Test-Skript für Video-Upload-Funktionalität
Prüft ob alle notwendigen Komponenten vorhanden sind
"""

import sys
from pathlib import Path

def test_video_upload_implementation():
    """Testet die Video-Upload-Implementierung"""
    
    print("=" * 60)
    print("VIDEO-UPLOAD IMPLEMENTIERUNG TEST")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Verzeichnis existiert
    print("Test 1: Verzeichnis data/intro_videos/ existiert...")
    video_dir = Path("data/intro_videos")
    if video_dir.exists() and video_dir.is_dir():
        print("  OK - Verzeichnis existiert")
        tests_passed += 1
    else:
        print("  FEHLER - Verzeichnis fehlt")
        tests_failed += 1
    print()
    
    # Test 2: intro_screen.py Änderungen
    print("Test 2: intro_screen.py enthält video_file_path...")
    intro_screen_file = Path("intro_screen.py")
    if intro_screen_file.exists():
        content = intro_screen_file.read_text(encoding='utf-8')
        if 'video_file_path' in content:
            print("  OK - video_file_path gefunden")
            tests_passed += 1
            
            # Check für Prioritätslogik
            if 'video_file_path and Path(video_file_path).exists()' in content:
                print("  OK - Prioritätslogik implementiert")
                tests_passed += 1
            else:
                print("  WARNUNG - Prioritätslogik möglicherweise fehlt")
                tests_failed += 1
        else:
            print("  FEHLER - video_file_path nicht gefunden")
            tests_failed += 1
    else:
        print("  FEHLER - intro_screen.py nicht gefunden")
        tests_failed += 1
    print()
    
    # Test 3: admin_intro_settings_ui.py Änderungen
    print("Test 3: admin_intro_settings_ui.py enthält File Uploader...")
    admin_file = Path("admin_intro_settings_ui.py")
    if admin_file.exists():
        content = admin_file.read_text(encoding='utf-8')
        if 'st.file_uploader' in content:
            print("  OK - File Uploader gefunden")
            tests_passed += 1
            
            # Check für Video-Formate
            if '"mp4", "avi", "mov"' in content:
                print("  OK - Video-Formate definiert")
                tests_passed += 1
            else:
                print("  WARNUNG - Video-Formate möglicherweise fehlen")
                tests_failed += 1
                
            # Check für video_file_path Speicherung
            if "'video_file_path'" in content:
                print("  OK - video_file_path wird gespeichert")
                tests_passed += 1
            else:
                print("  FEHLER - video_file_path Speicherung fehlt")
                tests_failed += 1
        else:
            print("  FEHLER - File Uploader nicht gefunden")
            tests_failed += 1
    else:
        print("  FEHLER - admin_intro_settings_ui.py nicht gefunden")
        tests_failed += 1
    print()
    
    # Test 4: intro_settings.json Default-Werte
    print("Test 4: intro_settings.json Default-Werte...")
    settings_file = Path("data/intro_settings.json")
    if settings_file.exists():
        import json
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            if 'video_file_path' in settings:
                print(f"  OK - video_file_path in Settings: '{settings['video_file_path']}'")
                tests_passed += 1
            else:
                print("  INFO - video_file_path noch nicht in Settings (wird beim Speichern hinzugefügt)")
                tests_passed += 1
        except Exception as e:
            print(f"  WARNUNG - Fehler beim Lesen: {e}")
            tests_failed += 1
    else:
        print("  INFO - intro_settings.json existiert noch nicht (wird beim ersten Speichern erstellt)")
        tests_passed += 1
    print()
    
    # Test 5: Dokumentation
    print("Test 5: Dokumentation vorhanden...")
    doc_file = Path("docs/features/VIDEO_UPLOAD_INTRO.md")
    if doc_file.exists():
        print("  OK - Dokumentation erstellt")
        tests_passed += 1
        
        content = doc_file.read_text(encoding='utf-8')
        if 'MP4' in content and 'AVI' in content and 'MOV' in content:
            print("  OK - Unterstützte Formate dokumentiert")
            tests_passed += 1
        else:
            print("  WARNUNG - Formate möglicherweise unvollständig dokumentiert")
            tests_failed += 1
    else:
        print("  WARNUNG - Dokumentation fehlt")
        tests_failed += 1
    print()
    
    # Zusammenfassung
    print("=" * 60)
    print(f"TESTS ABGESCHLOSSEN: {tests_passed} bestanden, {tests_failed} fehlgeschlagen")
    print("=" * 60)
    print()
    
    if tests_failed == 0:
        print("ERFOLG - Alle Tests bestanden!")
        print()
        print("Nächste Schritte:")
        print("1. Admin-Panel öffnen (streamlit run admin_panel.py)")
        print("2. Zu 'Intro-Einstellungen' navigieren")
        print("3. Media-Typ 'Video' auswählen")
        print("4. Video hochladen oder URL eingeben")
        print("5. Speichern und Intro-Screen testen")
        return True
    else:
        print("FEHLER - Einige Tests fehlgeschlagen")
        print("Bitte überprüfe die Implementierung")
        return False

if __name__ == "__main__":
    success = test_video_upload_implementation()
    sys.exit(0 if success else 1)
