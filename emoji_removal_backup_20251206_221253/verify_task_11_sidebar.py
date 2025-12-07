"""
Verifikations-Skript für Task 11: Sidebar-Styling

Prüft ob alle Features korrekt implementiert sind.
"""

import sys
from pathlib import Path


def verify_files_exist():
    """Prüft ob alle erforderlichen Dateien existieren"""
    print("🔍 Prüfe Dateien...")
    
    required_files = [
        "utils/shadcn_sidebar.py",
        "utils/SHADCN_SIDEBAR_REFERENCE.md",
        "docs/SHADCN_SIDEBAR_QUICK_REFERENCE.md",
        "demo_shadcn_sidebar.py",
        "tests/test_shadcn_sidebar.py",
        "TASK_11_SIDEBAR_STYLING_COMPLETE.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def verify_imports():
    """Prüft ob alle Importe funktionieren"""
    print("\n🔍 Prüfe Importe...")
    
    try:
        from utils.shadcn_sidebar import (
            MenuItem,
            MenuGroup,
            ShadcnSidebar,
            create_sidebar_menu,
            get_default_menu,
            get_solar_calculator_menu
        )
        print("  ✅ Alle Importe erfolgreich")
        return True
    except ImportError as e:
        print(f"  ❌ Import-Fehler: {e}")
        return False


def verify_classes():
    """Prüft ob alle Klassen korrekt definiert sind"""
    print("\n🔍 Prüfe Klassen...")
    
    from utils.shadcn_sidebar import MenuItem, MenuGroup, ShadcnSidebar
    
    # MenuItem
    item = MenuItem(label="Test", icon="🔘", key="test")
    assert item.label == "Test"
    assert item.icon == "🔘"
    assert item.key == "test"
    print("  ✅ MenuItem funktioniert")
    
    # MenuGroup
    group = MenuGroup(
        title="Test Group",
        items=[item],
        collapsible=True
    )
    assert group.title == "Test Group"
    assert len(group.items) == 1
    assert group.collapsible is True
    print("  ✅ MenuGroup funktioniert")
    
    # ShadcnSidebar
    sidebar = ShadcnSidebar()
    assert sidebar is not None
    print("  ✅ ShadcnSidebar funktioniert")
    
    return True


def verify_methods():
    """Prüft ob alle Methoden vorhanden sind"""
    print("\n🔍 Prüfe Methoden...")
    
    from utils.shadcn_sidebar import ShadcnSidebar
    
    sidebar = ShadcnSidebar()
    
    methods = [
        'get_token',
        'inject_sidebar_css',
        'render_menu_item',
        'render_menu_group',
        'render'
    ]
    
    all_present = True
    for method in methods:
        has_method = hasattr(sidebar, method)
        status = "✅" if has_method else "❌"
        print(f"  {status} {method}()")
        if not has_method:
            all_present = False
    
    return all_present


def verify_predefined_menus():
    """Prüft vordefinierte Menüs"""
    print("\n🔍 Prüfe vordefinierte Menüs...")
    
    from utils.shadcn_sidebar import (
        get_default_menu,
        get_solar_calculator_menu
    )
    
    # Default-Menü
    default_menu = get_default_menu()
    assert isinstance(default_menu, list)
    assert len(default_menu) > 0
    print(f"  ✅ Default-Menü ({len(default_menu)} Gruppen)")
    
    # Solar-Menü
    solar_menu = get_solar_calculator_menu()
    assert isinstance(solar_menu, list)
    assert len(solar_menu) > 0
    print(f"  ✅ Solar-Menü ({len(solar_menu)} Gruppen)")
    
    return True


def verify_documentation():
    """Prüft Dokumentation"""
    print("\n🔍 Prüfe Dokumentation...")
    
    # Technische Referenz
    ref_path = Path("utils/SHADCN_SIDEBAR_REFERENCE.md")
    if ref_path.exists():
        content = ref_path.read_text(encoding='utf-8')
        assert "MenuItem" in content
        assert "MenuGroup" in content
        assert "ShadcnSidebar" in content
        print("  ✅ Technische Referenz vollständig")
    else:
        print("  ❌ Technische Referenz fehlt")
        return False
    
    # Quick Reference
    quick_path = Path("docs/SHADCN_SIDEBAR_QUICK_REFERENCE.md")
    if quick_path.exists():
        content = quick_path.read_text(encoding='utf-8')
        assert "Schnellstart" in content
        assert "Beispiele" in content
        print("  ✅ Quick Reference vollständig")
    else:
        print("  ❌ Quick Reference fehlt")
        return False
    
    return True


def verify_tests():
    """Prüft Tests"""
    print("\n🔍 Prüfe Tests...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_shadcn_sidebar.py", "-v"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Zähle bestandene Tests
            passed = result.stdout.count(" passed")
            print(f"  ✅ Alle Tests bestanden ({passed} Tests)")
            return True
        else:
            print(f"  ❌ Tests fehlgeschlagen")
            print(result.stdout[-500:])  # Letzte 500 Zeichen
            return False
    except Exception as e:
        print(f"  ⚠️  Tests konnten nicht ausgeführt werden: {e}")
        return False


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("Task 11: Sidebar-Styling - Verifikation")
    print("=" * 60)
    
    results = {
        "Dateien": verify_files_exist(),
        "Importe": verify_imports(),
        "Klassen": verify_classes(),
        "Methoden": verify_methods(),
        "Vordefinierte Menüs": verify_predefined_menus(),
        "Dokumentation": verify_documentation(),
        "Tests": verify_tests()
    }
    
    print("\n" + "=" * 60)
    print("Zusammenfassung")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALLE PRÜFUNGEN BESTANDEN!")
        print("Task 11 ist vollständig implementiert.")
    else:
        print("❌ EINIGE PRÜFUNGEN FEHLGESCHLAGEN")
        print("Bitte behebe die Fehler.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
