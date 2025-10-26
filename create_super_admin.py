"""
create_super_admin.py
Erstellt den Super-Admin Account für TSchwarz
"""
from user_management import UserManagement


def create_super_admin_account():
    """Erstellt Super-Admin TSchwarz"""
    um = UserManagement()

    # Prüfe ob bereits ein Super-Admin existiert
    existing_super = um.get_super_admin()
    if existing_super:
        print(f"⚠ Super-Admin existiert bereits: {existing_super['username']}")
        return False

    # Erstelle Super-Admin
    user_id = um.create_super_admin(
        username="TSchwarz",
        password="Timur2014!",
        full_name="Timur Schwarz",
        email="",
        phone=""
    )

    if user_id:
        print("✅ Super-Admin 'TSchwarz' erfolgreich erstellt!")
        print(f"   User-ID: {user_id}")
        print("   Rang: Geschäftsführer")
        print("   Rolle: admin")
        print("   Super-Admin: JA")
        print("\n🔐 Rechte:")
        print("   - Volle Kontrolle über alle Funktionen")
        print("   - Kann alle Benutzer verwalten")
        print("   - Kann Super-Admin-Rechte übertragen")
        print("   - Niemand kann diese Rechte entziehen")
        return True
    print("❌ Fehler: Benutzername bereits vergeben")
    return False


if __name__ == "__main__":
    create_super_admin_account()
