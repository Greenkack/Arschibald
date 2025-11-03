# Admin-Passwortschutz-System - Implementierungsdokumentation

## Übersicht

Das neue Admin-Passwortschutz-System ermöglicht es, einzelne Admin-Bereiche mit Passwörtern zu schützen. Nur Administratoren mit gültigem Passwort können auf geschützte Bereiche zugreifen.

## Neue Features

### 1. **Build Infos Tab** (📋)
- **Zweck**: Zeigt Hauptdokumentation und detaillierte Docs
- **Schutz**: Standardmäßig passwortgeschützt
- **Inhalt**:
  - Build-Statistiken (Anzahl Python-Module, Dokumentationen, Gesamtgröße)
  - Hauptdokumentation (README, QUICKSTART, INSTALLATION, etc.)
  - Detaillierte Docs (alle anderen .md Dateien)
  - Suchfunktion für schnelle Navigation
  - Download-Funktion für einzelne Dokumente

### 2. **Sicherheitseinstellungen Tab** (🔐)
- **Zweck**: Konfiguration des Passwortschutzes
- **Funktionen**:
  - Ein/Ausschalten des Schutzes pro Bereich
  - Übersicht aktiver Authentifizierungen
  - Abmelden von einzelnen Bereichen

### 3. **Passwortschutz-System**
- **Authentifizierung**: Admin-Benutzername + Passwort
- **Passwort-Hashing**: SHA-256 für sichere Speicherung
- **Session-basiert**: Authentifizierung bleibt während der Session aktiv
- **Flexibel**: Jeder Bereich kann einzeln geschützt werden

## Dateien

### Neue Dateien
1. **admin_security.py** - Kern des Sicherheitssystems
   - `verify_admin_password()` - Passwort-Verifizierung
   - `require_admin_auth()` - Schutz-Enforcement
   - `get_admin_protected_areas()` - Lädt Schutz-Konfiguration
   - `save_admin_protected_areas()` - Speichert Schutz-Konfiguration
   - `render_admin_security_settings()` - UI für Einstellungen

2. **admin_build_infos_ui.py** - Build Infos Tab
   - `render_build_infos_tab()` - Hauptfunktion
   - `collect_documentation_files()` - Sammelt .md Dateien
   - `render_documentation_tab()` - Zeigt Docs mit Suche
   - `render_build_info_statistics()` - Build-Statistiken

### Geänderte Dateien
1. **admin_panel.py**
   - Neue Tabs hinzugefügt: `admin_tab_build_infos`, `admin_tab_security_settings`
   - Icons und Labels ergänzt
   - Render-Funktionen integriert

## Verwendung

### Als Administrator

1. **Passwortschutz aktivieren**:
   - Gehe zu Admin → 🔐 Sicherheitseinstellungen
   - Aktiviere Checkboxen für zu schützende Bereiche
   - Klicke "💾 Änderungen speichern"

2. **Auf geschützte Bereiche zugreifen**:
   - Navigiere zum geschützten Bereich
   - Gebe Admin-Benutzername ein
   - Gebe Admin-Passwort ein
   - Klicke "🔓 Entsperren"

3. **Von Bereich abmelden**:
   - Gehe zu 🔐 Sicherheitseinstellungen
   - Finde aktive Sitzung
   - Klicke "🚪 Abmelden"

### Als Entwickler

**Neuen Bereich schützen**:
```python
from admin_security import require_admin_auth

def render_my_protected_area():
    # Prüfe Authentifizierung
    if not require_admin_auth('my_area_id', 'Mein Bereich'):
        return  # Zugriff verweigert
    
    # Bereich-Code hier
    st.write("Geschützter Inhalt")
```

**Geschützte Bereiche in Datenbank**:
```python
# In admin_security.py → get_admin_protected_areas()
default_areas = {
    'my_area_id': True,  # True = geschützt, False = offen
}
```

## Geschützte Bereiche

Standardmäßig konfigurierbare Bereiche:

| Bereich ID | Name | Standard-Schutz |
|------------|------|----------------|
| `build_infos` | Build Infos & Dokumentation | ✅ Ja |
| `user_management` | Benutzerverwaltung | ❌ Nein |
| `company_management` | Firmenverwaltung | ❌ Nein |
| `product_database` | Produktdatenbank | ❌ Nein |
| `economic_settings` | Wirtschaftlichkeitseinstellungen | ❌ Nein |
| `ui_customization` | UI-Anpassungen | ❌ Nein |
| `logo_management` | Logo-Verwaltung | ❌ Nein |
| `intro_settings` | Intro-Einstellungen | ❌ Nein |
| `payment_terms` | Zahlungsbedingungen | ❌ Nein |
| `services_management` | Dienstleistungsverwaltung | ❌ Nein |
| `pdf_settings` | PDF-Einstellungen | ❌ Nein |

## Sicherheitsaspekte

### Passwort-Hashing
- SHA-256 Hash für Passwörter
- Legacy-Support für Klartext-Passwörter (wird automatisch konvertiert)

### Session-Management
- Authentifizierung wird in `st.session_state` gespeichert
- Format: `admin_auth_{area_id}` = True/False
- User: `admin_auth_{area_id}_user` = Username

### Datenbank
- Geschützte Bereiche in `admin_settings` Tabelle
- Key: `protected_admin_areas`
- Value: JSON mit Bereich-IDs

## Nächste Schritte

1. **Weitere Bereiche schützen** (nach Bedarf):
   - Benutzerverwaltung
   - Firmenverwaltung
   - Produktdatenbank
   - Etc.

2. **Erweiterte Features** (optional):
   - Zeitbasierte Session-Timeouts
   - Multi-Faktor-Authentifizierung
   - Audit-Logging für Zugriffe
   - Rolle-basierte Berechtigungen (nicht nur Admin)

## Fehlerbehebung

### "Module nicht gefunden"
```bash
# Prüfe ob Dateien existieren
ls admin_security.py
ls admin_build_infos_ui.py
```

### "Passwort falsch" obwohl korrekt
- Prüfe ob User in Datenbank als Admin markiert ist
- Prüfe password_hash Spalte in users Tabelle

### Authentifizierung bleibt nicht
- Session State wurde gelöscht → Neu authentifizieren

## Changelog

**2025-10-31**: Erste Implementierung
- Admin-Passwortschutz-System erstellt
- Build Infos Tab mit Dokumentation
- Sicherheitseinstellungen Tab
- Integration in admin_panel.py
