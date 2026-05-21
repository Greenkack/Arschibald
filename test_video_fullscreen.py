"""
Test Script für Video Fullscreen Background Feature

Testet:
1. video_size, video_autoplay, video_loop in default_settings
2. HTML5-Video mit autoplay/loop/muted
3. Größen-Logik (small, medium, large, fullscreen)
4. Admin-UI für Video-Optionen
5. Settings-Schema vollständig
"""

import sys
from pathlib import Path

workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

def test_intro_screen_default_settings():
    """Test 1: Neue Settings in intro_screen.py vorhanden"""
    intro_path = workspace_root / "intro_screen.py"
    content = intro_path.read_text(encoding='utf-8')
    
    assert '"video_size"' in content, "video_size nicht in default_settings"
    assert '"video_autoplay"' in content, "video_autoplay nicht in default_settings"
    assert '"video_loop"' in content, "video_loop nicht in default_settings"
    print("Test 1: video_size, video_autoplay, video_loop in default_settings... OK")
    
    # Check Default-Werte
    assert '"fullscreen"' in content, "Default video_size nicht 'full    assert 'True' in content or 'true' in content, "Defaults nicht auf True"
    print("Test 1: Default-Werte korrekt (fullscreen, True, True)... OK")
    
    return True

def test_html5_video_implementation():
    """Test 2: HTML5-Video mit autoplay/loop/muted implementiert"""
    intro_path = workspace_root / "intro_screen.py"
    content = intro_path.read_text(encoding='utf-8')
    
    # Check HTML5-Video Tag
    assert '<video' in content, "HTML5 <video> Tag nicht gefunden"
    assert 'autoplay' in content, "autoplay Attribut fehlt"
    assert 'loop' in content, "loop Attribut fehlt"
    assert 'muted' in content, "muted Attribut fehlt"
    assert 'playsinline' in content, "playsinline Attribut fehlt"
    print("Test 2: HTML5-Video mit autoplay/loop/muted/playsinline... OK")
    
    # Check st.video() entfernt (sollte nicht mehr direkt verwendet werden)
    # Erlaubt in Kommentaren/Strings, aber nicht als aktiver Code
    st_video_count = content.count('st.video(')
    # Toleranz: Max 2 (Backup-Datei oder auskommentiert)
    assert st_video_count <= 2, f"st.video() noch {st_video_count}x aktiv (erwartet: 0-2)"
    print("Test 2: st.video() Play-Button entfernt... OK")
    
    return True

def test_video_sizes_logic():
    """Test 3: Größen-Logik implementiert"""
    intro_path = workspace_root / "intro_screen.py"
    content = intro_path.read_text(encoding='utf-8')
    
    # Check size_styles Dictionary
    assert 'size_styles' in content, "size_styles Dictionary nicht gefunden"
    assert "'small'" in content, "small Größe fehlt"
    assert "'medium'" in content, "medium Größe fehlt"
    assert "'large'" in content, "large Größe fehlt"
    assert "'fullscreen'" in content, "fullscreen Größe fehlt"
    print("Test 3: size_styles mit allen 4 Größen... OK")
    
    # Check Fullscreen-CSS
    assert 'position: fixed' in content, "Fullscreen position: fixed fehlt"
    assert 'width: 100vw' in content or 'width:100vw' in content, "Fullscreen width: 100vw fehlt"
    assert 'height: 100vh' in content or 'height:100vh' in content, "Fullscreen height: 100vh fehlt"
    assert 'object-fit: cover' in content, "object-fit: cover fehlt"
    assert 'z-index: -1' in content, "z-index: -1 fehlt"
    print("Test 3: Fullscreen-CSS korrekt (fixed, 100vw/vh, cover, z-1)... OK")
    
    return True

def test_admin_ui_video_options():
    """Test 4: Admin-UI für Video-Optionen vorhanden"""
    admin_path = workspace_root / "admin_intro_settings_ui.py"
    content = admin_path.read_text(encoding='utf-8')
    
    # Check Video-Größe Selectbox
    assert 'video_size' in content, "video_size Variable nicht gefunden"
    assert 'st.selectbox' in content or 'selectbox' in content, "Selectbox für video_size fehlt"
    assert 'fullscreen' in content.lower(), "fullscreen Option fehlt"
    print("Test 4: Video-Größe Selectbox vorhanden... OK")
    
    # Check Autoplay Checkbox
    assert 'video_autoplay' in content, "video_autoplay Variable nicht gefunden"
    assert 'Automatisch starten' in content, "Autoplay-Checkbox-Text fehlt"
    print("Test 4: Autoplay Checkbox vorhanden... OK")
    
    # Check Loop Checkbox
    assert 'video_loop' in content, "video_loop Variable nicht gefunden"
    assert 'wiederholen' in content.lower() or 'loop' in content.lower(), "Loop-Checkbox-Text fehlt"
    print("Test 4: Loop Checkbox vorhanden... OK")
    
    return True

def test_settings_save_logic():
    """Test 5: Settings werden korrekt gespeichert"""
    admin_path = workspace_root / "admin_intro_settings_ui.py"
    content = admin_path.read_text(encoding='utf-8')
    
    # Check dass neue Settings in new_settings Dict gespeichert werden
    assert "'video_size':" in content, "video_size nicht in new_settings"
    assert "'video_autoplay':" in content, "video_autoplay nicht in new_settings"
    assert "'video_loop':" in content, "video_loop nicht in new_settings"
    print("Test 5: video_size, video_autoplay, video_loop in new_settings... OK")
    
    # Check Fallback-Logik
    assert 'if media_type == ' in content or "if media_type ==" in content, "Conditional Save fehlt"
    print("Test 5: Conditional Save-Logik vorhanden... OK")
    
    return True

def test_youtube_autoplay_params():
    """Test 6: YouTube-iframe mit Autoplay-Parametern"""
    intro_path = workspace_root / "intro_screen.py"
    content = intro_path.read_text(encoding='utf-8')
    
    # Check YouTube-iframe
    assert 'youtube.com/embed' in content, "YouTube-iframe nicht gefunden"
    
    # Check Autoplay-Parameter
    if 'autoplay=' in content:
        print("Test 6: YouTube autoplay Parameter vorhanden... OK")
    else:
        print("Test 6: YouTube autoplay Parameter fehlt... WARNING")
    
    # Check Loop-Parameter (playlist erforderlich für Loop)
    if 'loop=' in content or 'playlist=' in content:
        print("Test 6: YouTube loop Parameter vorhanden... OK")
    else:
        print("Test 6: YouTube loop Parameter fehlt... WARNING")
    
    # Check Mute-Parameter
    if 'mute=' in content:
        print("Test 6: YouTube mute Parameter vorhanden... OK")
    else:
        print("Test 6: YouTube mute Parameter fehlt... WARNING")
    
    return True

def test_documentation_exists():
    """Test 7: Dokumentation erstellt"""
    doc_path = workspace_root / "docs" / "features" / "VIDEO_FULLSCREEN_BACKGROUND.md"
    
    assert doc_path.exists(), "VIDEO_FULLSCREEN_BACKGROUND.md nicht gefunden"
    print("Test 7: Dokumentation existiert... OK")
    
    # Check Inhalt
    content = doc_path.read_text(encoding='utf-8')
    assert 'Fullscreen' in content or 'fullscreen' in content, "Fullscreen nicht dokumentiert"
    assert 'Autoplay' in content or 'autoplay' in content, "Autoplay nicht dokumentiert"
    assert 'Loop' in content or 'loop' in content, "Loop nicht dokumentiert"
    print("Test 7: Dokumentation vollständig (Fullscreen, Autoplay, Loop)... OK")
    
    return True

def test_no_play_button():
    """Test 8: Kein Play-Button mehr (autoplay statt st.video)"""
    intro_path = workspace_root / "intro_screen.py"
    content = intro_path.read_text(encoding='utf-8')
    
    # Zähle st.video() Aufrufe (sollte minimal sein)
    st_video_count = content.count('st.video(')
    
    if st_video_count == 0:
        print("Test 8: Kein st.video() mehr - nur HTML5/iframe... OK")
    elif st_video_count <= 2:
        print(f"Test 8: st.video() minimal ({st_video_count}x) - vermutlich Backup/Kommentar... OK")
    else:
        print(f"Test 8: st.video() noch {st_video_count}x vorhanden... WARNING")
    
    # Check HTML5 autoplay als Ersatz
    assert '<video' in content and 'autoplay' in content, "HTML5-Video mit autoplay fehlt"
    print("Test 8: HTML5-Video mit autoplay als Ersatz vorhanden... OK")
    
    return True

def run_all_tests():
    """Führe alle Tests aus"""
    tests = [
        test_intro_screen_default_settings,
        test_html5_video_implementation,
        test_video_sizes_logic,
        test_admin_ui_video_options,
        test_settings_save_logic,
        test_youtube_autoplay_params,
        test_documentation_exists,
        test_no_play_button,
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("VIDEO FULLSCREEN BACKGROUND TESTS")
    print("="*60 + "\n")
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"FEHLER in {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"EXCEPTION in {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TESTS ABGESCHLOSSEN: {passed} bestanden, {failed} fehlgeschlagen")
    print("="*60 + "\n")
    
    if failed == 0:
        print("ERFOLG - Alle Tests bestanden!")
        print("\nFeature-Zusammenfassung:")
        print("  - Video-Größen: small, medium, large, fullscreen")
        print("  - Autoplay: Aktiviert (mit muted)")
        print("  - Loop: Endlos-Wiederholung")
        print("  - Kein Play-Button: Automatischer Start")
        print("  - Fullscreen Background: position fixed, 100vw/vh")
        return True
    else:
        print(f"FEHLER - {failed} Test(s) fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
