# Admin Panel Reorganisation - Dokumentation

## Datum: 2025-12-16

## Übersicht
Das Admin Panel wurde vollständig reorganisiert und in **4 Hauptkategorien** strukturiert, um eine übersichtliche und intuitive Bedienung zu gewährleisten.

---

## Neue Struktur

### 1. 💼 Business & Management
**Beschreibung:** Unternehmens-, Personal- und Produktverwaltung

**Enthaltene Bereiche:**
- ✅ **Firmenverwaltung** - Stammdaten, Dokumente & Standardwerte
- ✅ **Benutzerverwaltung** - Benutzerrollen, Teams und Rechte
- ✅ **Produktverwaltung** - Produkte, Varianten und Preise verwalten
- ✅ **Logo-Verwaltung** - Logos, Brand-Assets und Platzierungen
- ✅ **Produktdatenbank** - Produktdatenbank synchronisieren und pflegen
- ✅ **PV-Unterkonstruktionen** - PV-Unterkonstruktions-Komponenten verwalten
- ✅ **Dienstleistungen Management** - Dienstleistungen strukturieren und bündeln
- ✅ **Preis Matrix** - Excel-ähnliche Preismatrizen erstellen und verwalten
- ✅ **Controlling Einstellungen** - Mitarbeiter, Positionen, Kriterien & Benachrichtigungen
- ✅ **Einspeisung Tarifverwaltung** - Einspeisevergütungen & Tarife konfigurieren
- ✅ **Wärmepumpen-Einstellungen** - Wärmepumpen-Preise, Heizkosten & Konfiguration
- ✅ **Wärmepumpen-Produkte** - Wärmepumpen-Produkte verwalten und konfigurieren
- ✅ **Zahlungsbedingungen** - Zahlungsbedingungen & Varianten steuern

**Passwortschutz:** ✅ Alle Bereiche können mit Passwort geschützt werden

---

### 2. 🎨 Visuelle Einstellungen
**Beschreibung:** Design, Layouts und visuelle Anpassungen

**Enthaltene Bereiche:**
- ✅ **Anzeigeeinstellungen** - Themes, UI-Effekte, Charts & Farben
- ✅ **PDF-Design Einstellungen** - PDF-Looks, Cover und Layouts definieren
- ✅ **Intro-Einstellungen** - Intro-Inhalte und Onboarding-Story anpassen
- ✅ **Dokument-Vorlagen** - Dokument-Vorlagen mit Platzhaltern erstellen

**Passwortschutz:** ✅ Alle Bereiche können mit Passwort geschützt werden

---

### 3. 🔧 App & Diagnose
**Beschreibung:** System-Tools, Monitoring und Performance

**Enthaltene Bereiche:**
- ✅ **Tag-Verwaltung** - Tags für Kundensegmentierung erstellen
- ✅ **Jobmanager & Background Tasks** - Background-Tasks und Job-Queue verwalten
- ✅ **Cache-Erweiterungen** - Cache-Invalidierung, Monitoring & Warming
- ✅ **Datenbank-Performance** - DB Performance Monitoring & Query Tracking
- ✅ **Dependency Injection** - Dependency Injection Container & Lifetimes
- ✅ **Build-Infos** - Build-Informationen & Dokumentation

**Passwortschutz:** ✅ Alle Bereiche können mit Passwort geschützt werden

---

### 4. ⚙️ Sonstiges
**Beschreibung:** Allgemeine und erweiterte Konfiguration

**Enthaltene Bereiche:**
- ✅ **Erweiterte Einstellungen** - Erweiterte Tools, Debugging & Integrationen
- ✅ **Allgemeine Einstellungen** - Globale Parameter, Einheiten und Defaults
- ✅ **Sicherheitseinstellungen** - Sicherheit & Passwortschutz konfigurieren

**Passwortschutz:** ✅ Erweiterte & Allgemeine Einstellungen geschützt, Sicherheitseinstellungen selbst NICHT geschützt (damit Zugang zum Passwort-Management gewährleistet ist)

---

## Technische Änderungen

### Dateien geändert:
1. **admin_panel.py**
   - Neue Tab-Struktur mit 4 Hauptkategorien
   - Sub-Tabs für jede Kategorie implementiert
   - `render_business_management_subtabs()`
   - `render_visual_settings_subtabs()`
   - `render_app_diagnostics_subtabs()`
   - `render_misc_settings_subtabs()`

2. **admin_security.py**
   - Erweiterte Bereichs-IDs für alle neuen Bereiche
   - Passwortschutz-Konfiguration aktualisiert

### Neue Konstanten:
- `ADMIN_BUSINESS_SUBTABS` - Liste der Business-Bereiche
- `ADMIN_VISUAL_SUBTABS` - Liste der visuellen Einstellungen
- `ADMIN_APP_DIAGNOSTICS_SUBTABS` - Liste der Diagnose-Tools
- `ADMIN_MISC_SUBTABS` - Liste der sonstigen Bereiche

---

## Benutzer-Login

### Standard-Besitzer-Zugang (Bypass für alle Sperren):
- **Benutzername:** `TSchwarz`
- **Passwort:** `Timur2014`

### Admin-Benutzer:
Können über die Benutzerverwaltung angelegt werden. Admin-Benutzer können auf passwortgeschützte Bereiche zugreifen.

---

## Passwortschutz-Konfiguration

Jeder Bereich kann in den **Sicherheitseinstellungen** individuell geschützt oder freigegeben werden:

1. Navigation: `Administration & Konfiguration` → `⚙️ Sonstiges` → `Sicherheitseinstellungen`
2. Bereiche aktivieren/deaktivieren
3. Änderungen speichern

**Standard:** Alle Bereiche sind standardmäßig **geschützt**, außer:
- Sicherheitseinstellungen selbst (damit Zugang gewährleistet ist)

---

## Vorteile der neuen Struktur

✅ **Übersichtlichkeit:** Logische Gruppierung verwandter Funktionen  
✅ **Intuitive Navigation:** 4 klare Hauptkategorien statt 25+ einzelner Tabs  
✅ **Skalierbarkeit:** Einfaches Hinzufügen neuer Sub-Bereiche  
✅ **Sicherheit:** Konsistenter Passwortschutz für alle Bereiche  
✅ **Performance:** Reduzierte UI-Komplexität durch verschachtelte Tabs  
✅ **Wartbarkeit:** Klare Code-Struktur mit dedizierten Render-Funktionen  

---

## Migration

**Keine Datenverluste!** Alle bestehenden Funktionen wurden erhalten und sind weiterhin verfügbar. Die Reorganisation betrifft **nur die UI-Struktur**, nicht die Datenhaltung.

**Bestehende Daten:**
- ✅ Firmen
- ✅ Benutzer
- ✅ Produkte
- ✅ Logos
- ✅ Einstellungen
- ✅ Preismatrizen
- ✅ Controlling-Daten
- ✅ Alle weiteren Daten

**Alle Daten bleiben erhalten und sind sofort verfügbar!**

---

## Fehlerbehandlung

Sollte ein Bereich nicht laden:
1. Fehlermeldung wird angezeigt
2. Stack Trace für Debugging verfügbar
3. Andere Bereiche bleiben funktionsfähig

---

## Support

Bei Fragen oder Problemen:
- Prüfen Sie die Konsole auf Fehlermeldungen
- Verifizieren Sie die Passwort-Konfiguration in den Sicherheitseinstellungen
- Kontaktieren Sie den Administrator

---

**Stand:** 2025-12-16  
**Version:** 2.0 (Reorganised Admin Panel)  
**Status:** ✅ Produktionsbereit
