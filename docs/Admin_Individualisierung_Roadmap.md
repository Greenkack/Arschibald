# Admin-Bereich: Individualisierung

## ✅ Aktuell verfügbare Funktionen

### 📊 Datenbank-Spalten konfigurieren

**Status: ✅ Vollständig implementiert**

- **Spalten für alle Produktkategorien anpassen**
  - PV-Module: 16 vordefinierte Spalten
  - Batteriespeicher: 21 vordefinierte Spalten  
  - Wechselrichter: 21 vordefinierte Spalten
  - Zubehör: 15 vordefinierte Spalten

- **Flexible Upload-Validierung**
  - Automatische Akzeptanz von "x", "0", "o" und leeren Zellen
  - Intelligente Zahlenkonvertierung (1,5 → 1.5)
  - Automatische Spaltenerkennung und -mapping

- **Schema-Verwaltung**
  - Spalten hinzufügen, bearbeiten und löschen
  - Schema exportieren als JSON-Backup
  - Zurücksetzen auf Standardwerte
  - Verschiedene Datentypen (Text, Zahl, Boolean, Datum)

## 🚧 Geplante Erweiterungen

### 🎨 Erscheinungsbild

**Status: 🔄 In Planung**

- **Theme-Editor**
  - Custom CSS-Variablen definieren
  - Farb-Paletten anpassen
  - Dark/Light Mode Konfiguration

- **Logo & Branding**
  - Firmenlogo hochladen und positionieren
  - Header/Footer Anpassungen
  - Corporate Design Integration

- **Farben & Fonts**
  - Primärfarben definieren
  - Schriftarten anpassen
  - Button-Styles konfigurieren

### 📋 Formular-Anpassungen

**Status: 🔄 In Planung**

- **Kundenformular anpassen**
  - Zusätzliche Felder definieren
  - Feldvalidierung konfigurieren
  - Sektionen ein/ausblenden

- **Berechnungsparameter**
  - Standard-Werte für Berechnungen
  - Regionale Anpassungen (Strompreise, etc.)
  - Formeln und Faktoren konfigurieren

- **Standard-Werte definieren**
  - Dropdown-Optionen anpassen
  - Vorausgefüllte Felder
  - Regionale Einstellungen

### 📄 PDF-Templates

**Status: 🔄 In Planung**

- **Angebot-Template bearbeiten**
  - Seitenlayout anpassen
  - Inhalte ein/ausblenden
  - Formatierung konfigurieren

- **Firmen-Header anpassen**
  - Kopfzeile mit Logo und Adresse
  - Kontaktdaten positionieren
  - Rechtliche Hinweise

- **Berechnungs-Layout**
  - Tabellen-Design anpassen
  - Diagramm-Styles definieren
  - Zusammenfassungen konfigurieren

### 🔧 System-Verhalten

**Status: 🔄 In Planung**

- **Auto-Berechnungen**
  - Automatische Neuberechnung bei Änderungen
  - Intelligente Vorschläge
  - Plausibilitätsprüfungen

- **Validierungs-Regeln**
  - Custom Validierung für Eingaben
  - Warnungen und Hinweise
  - Datenqualitäts-Checks

- **Import-Automatisierung**
  - Überwachte Ordner für Auto-Import
  - Benachrichtigungen bei neuen Dateien
  - Batch-Verarbeitung

## 🎯 Roadmap

### Phase 1: Basis-Individualisierung (Q4 2025)

- ✅ Spalten-Editor (Fertig)
- 🔄 Theme-Editor
- 🔄 Logo-Upload

### Phase 2: Erweiterte Anpassungen (Q1 2026)

- 🔄 Formular-Anpassungen
- 🔄 PDF-Template Editor
- 🔄 Standard-Werte Konfiguration

### Phase 3: Automatisierung (Q2 2026)

- 🔄 Auto-Berechnungen
- 🔄 Validierungs-System
- 🔄 Import-Automatisierung

## 💡 Entwickler-Hinweise

### Struktur für neue Individualisierungs-Features

1. **Frontend-Komponente** in `/renderer/components/`
2. **IPC-Handler** in `/main/ipc-handlers.ts`
3. **Konfiguration** in `/data/` als JSON
4. **Integration** in AdminArea → Individualisierung Tab

### Konventionen

- Alle Einstellungen werden in `/data/customization/` gespeichert
- JSON-Format für Konfigurationsdateien
- Backup-Funktionalität für alle Anpassungen
- Validierung vor Anwendung von Änderungen

### Beispiel-Implementation

```typescript
// Neue Individualisierungs-Komponente
export default function ThemeEditor() {
  // Theme-spezifische Logik
}

// IPC-Handler
ipcMain.handle('admin:theme:save', async (event, themeConfig) => {
  // Theme speichern
});
```
