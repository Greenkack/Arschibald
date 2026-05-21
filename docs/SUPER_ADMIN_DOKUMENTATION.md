# 🔒 Super-Admin System - Dokumentation

## Übersicht

Das Super-Admin-System bietet höchste Sicherheitsstufe für den Hauptverantwortlichen der Anwendung.

## Super-Admin: TSchwarz

**Login-Daten:**

- Benutzername: `TSchwarz`
- Passwort: `Timur2014!`
- User-ID: 2
- Rang: Geschäftsführer
- Status: SUPER-ADMIN ⭐

## Besondere Rechte

### Was der Super-Admin kann

1. **Vollständige Kontrolle**
   - Zugriff auf alle Funktionen der Anwendung
   - Kann alle Benutzer verwalten (erstellen, bearbeiten, löschen)
   - Kann Admin-Rechte vergeben
   - Kann Firmen verwalten
   - Kann alle Einstellungen ändern

2. **Geschützte Position**
   - Niemand kann Super-Admin-Rechte entziehen
   - Kann nicht gelöscht werden
   - Kann nicht gekündigt werden
   - Passwort kann nur selbst geändert werden
   - Alle anderen Benutzer sind hierarchisch untergeordnet

3. **Rechteübertragung** (Einzige Ausnahme)
   - Super-Admin kann Rechte freiwillig übertragen
   - Erfordert mehrfache Sicherheitsbestätigung:
     - Aktuelles Passwort
     - Eingabe von "RECHTE ÜBERTRAGEN"
     - Empfänger muss Transfer-Code mit eigenem Passwort bestätigen
   - Transfer-Code ist 16-stellig und einmalig verwendbar
   - Gültigkeit bis Ende des Tages

## Sicherheitsmerkmale

### 3-Faktor-Authentifizierung für Rechteübertragung

1. **Passwort-Verifizierung**
   - Super-Admin muss aktuelles Passwort eingeben
   - PBKDF2-HMAC-SHA256 Hashing mit 100.000 Iterationen

2. **Explizite Bestätigung**
   - Muss "RECHTE ÜBERTRAGEN" exakt eintippen
   - Verhindert versehentliche Übertragung

3. **Transfer-Code**
   - Empfänger erhält 16-stelligen Code
   - Muss eigenes neues Passwort setzen
   - Code läuft nach 24 Stunden ab

### Datenbank-Schutz

```sql
-- Super-Admin Flag
is_super_admin INTEGER DEFAULT 0

-- Transfer-Tracking
CREATE TABLE super_admin_transfers (
    id INTEGER PRIMARY KEY,
    from_user_id INTEGER NOT NULL,
    to_user_id INTEGER NOT NULL,
    transfer_code TEXT NOT NULL,
    authorized_by TEXT NOT NULL,
    authorized_at TEXT,
    expires_at TEXT,
    status TEXT DEFAULT 'pending',
    completed_at TEXT
)
```

## Verwendung

### Als Super-Admin einloggen

1. Öffnen Sie die Anwendung
2. Intro-Bildschirm → Tab "Anmelden"
3. Benutzername: `TSchwarz`
4. Passwort: `Timur2014!`
5. Sie sehen Ihr Profil mit ⭐ SUPER-ADMIN Kennzeichnung

### Rechte übertragen (falls gewünscht)

1. Navigieren Sie zu: Admin-Panel (F) → Benutzerverwaltung
2. Öffnen Sie Ihr Profil (TSchwarz)
3. Klicken Sie auf "Rechte übertragen"
4. Wählen Sie Empfänger aus
5. Geben Sie Ihr Passwort ein
6. Tippen Sie "RECHTE ÜBERTRAGEN"
7. Sie erhalten einen 16-stelligen Transfer-Code
8. Geben Sie den Code dem Empfänger
9. Empfänger muss sich anmelden und Code eingeben

### Benutzer verwalten

- **Erstellen:** Tab "Benutzer erstellen"
- **Bearbeiten:** Benutzer öffnen → "Bearbeiten"
- **Befördern:** Rang erhöhen
- **Löschen:** Nur bei Nicht-Admins möglich

## Hierarchie

```
⭐ SUPER-ADMIN (TSchwarz)
├─ Administrator (admin)
├─ Geschäftsführer
├─ Abteilungsleiter
├─ Team Lead
├─ Senior Mitarbeiter
├─ Mitarbeiter
├─ Junior Mitarbeiter
└─ Praktikant
```

**Wichtig:** Alle Benutzer sind hierarchisch unter dem Super-Admin.

## API-Funktionen

### Python (user_management.py)

```python
um = UserManagement()

# Prüfen ob Super-Admin
is_super = um.is_super_admin(user_id)

# Super-Admin holen
super_admin = um.get_super_admin()

# Rechte übertragen initiieren
transfer_code = um.initiate_super_admin_transfer(
    from_user_id=2,
    to_user_id=5,
    current_password="Timur2014!"
)

# Rechte übertragen abschließen (vom Empfänger)
success = um.complete_super_admin_transfer(
    to_user_id=5,
    transfer_code="ABC123...",
    new_password="NewSecurePass123!"
)
```

## Troubleshooting

### Problem: Kann mich nicht als Super-Admin anmelden

**Lösung:**

```bash
python create_super_admin.py
```

### Problem: Datenbank-Fehler "no such column: is_super_admin"

**Lösung:**

```bash
python migrate_super_admin.py
```

### Problem: Passwort vergessen

**Lösung:**
Löschen Sie `data/users.db` und führen Sie aus:

```bash
python create_super_admin.py
```

## Sicherheitsempfehlungen

1. **Passwort niemals teilen**
2. **Rechteübertragung nur in Notfällen**
3. **Transfer-Code sofort nach Generierung verwenden**
4. **Regelmäßig Passwort ändern** (mindestens alle 90 Tage)
5. **Zwei-Faktor-Authentifizierung aktivieren** (geplantes Feature)

---

**Erstellt:** 19. Oktober 2025  
**Version:** 1.0  
**Super-Admin:** TSchwarz (User-ID: 2)
