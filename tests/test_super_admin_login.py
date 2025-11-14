"""
test_super_admin_login.py
Testet den Super-Admin Login
"""
from user_management import UserManagement


def test_login():
    """Testet Super-Admin Login"""
    um = UserManagement()

    print("🔐 Teste Super-Admin Login...")
    print()

    # Login versuchen
    user = um.authenticate("TSchwarz", "Timur2014!")

    if user:
        print("[OK] Login erfolgreich!")
        print()
        print("📋 Benutzer-Details:")
        print(f"   ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Name: {user['full_name']}")
        print(f"   Rang: {user['rank']}")
        print(f"   Rolle: {user['role']}")
        print(
            f"   Super-Admin: {'JA ⭐' if user.get('is_super_admin', 0) == 1 else 'NEIN'}")
        print(f"   Status: {user['status']}")
        print()
        print("🔐 Berechtigungen:")
        for perm, value in user['permissions'].items():
            print(f"   - {perm}: {value}")

        # Prüfe Super-Admin Status
        is_super = um.is_super_admin(user['id'])
        print()
        print(
            f"[OK] Super-Admin-Verifizierung: {'BESTÄTIGT ⭐' if is_super else 'FEHLGESCHLAGEN'}")

        return True
    print("[ERROR] Login fehlgeschlagen!")
    print("   Benutzername oder Passwort falsch")
    return False


if __name__ == "__main__":
    test_login()
