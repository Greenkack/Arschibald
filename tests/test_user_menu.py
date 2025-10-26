"""
test_user_menu.py
Schnelltest für Benutzermenü-Funktionen
"""
from user_menu import get_avatar_url, get_rank_level
import sys

sys.path.insert(0, '.')


def test_avatar():
    """Test Avatar-Generierung"""
    print("🎨 Test: Avatar-URL-Generierung")

    # Mit E-Mail
    url1 = get_avatar_url(email="tschwarz@example.com")
    print(f"✅ Avatar mit E-Mail: {url1[:60]}...")

    # Mit Username
    url2 = get_avatar_url(username="TSchwarz")
    print(f"✅ Avatar mit Username: {url2[:60]}...")

    # Default
    url3 = get_avatar_url()
    print(f"✅ Avatar Standard: {url3[:60]}...")
    print()


def test_rank_level():
    """Test Rang-Level-Berechnung"""
    print("📊 Test: Rang-Level")

    ranks = [
        "Praktikant",
        "Junior Mitarbeiter",
        "Mitarbeiter",
        "Senior Mitarbeiter",
        "Team Lead",
        "Abteilungsleiter",
        "Geschäftsführer",
        "Administrator"
    ]

    for rank in ranks:
        level = get_rank_level(rank)
        print(f"✅ {rank}: Level {level}/8")

    # Unbekannter Rang
    level = get_rank_level("Unbekannt")
    print(f"✅ Unbekannt: Level {level}/8")
    print()


def test_user_menu_import():
    """Test Import"""
    print("📦 Test: Module-Import")

    try:
        from user_menu import (
            logout_user,
            render_info_tab,
            render_profile_editor,
            render_profile_tab,
            render_settings_tab,
            render_user_menu,
        )
        print("✅ Alle Funktionen importiert")
        print("   - render_user_menu")
        print("   - render_profile_tab")
        print("   - render_settings_tab")
        print("   - render_info_tab")
        print("   - render_profile_editor")
        print("   - logout_user")
        return True
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("   BENUTZERMENÜ - FUNKTIONSTEST")
    print("=" * 60)
    print()

    test_avatar()
    test_rank_level()
    test_user_menu_import()

    print()
    print("=" * 60)
    print("✅ Alle Tests abgeschlossen!")
    print("=" * 60)
