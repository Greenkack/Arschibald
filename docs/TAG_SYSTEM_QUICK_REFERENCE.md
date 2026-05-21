# Tag-System Quick Reference

## Übersicht

Das Tag-System ermöglicht die flexible Kategorisierung und Segmentierung von Kunden im CRM. Tags können für verschiedene Zwecke verwendet werden: Kundentypen, Status, Branchen, Prioritäten, etc.

## Hauptfunktionen

### 1. Tag-Verwaltung (Admin-Panel)

**Zugriff:** Admin-Panel → 🏷️ Tag-Verwaltung

**Funktionen:**
- ➕ Neue Tags erstellen
- ✏️ Tags bearbeiten (Name, Farbe, Kategorie, Beschreibung)
- ✅/❌ Tags aktivieren/deaktivieren
- 🗑️ Tags löschen
- 📊 Tag-Statistiken anzeigen

**Tag-Eigenschaften:**
- **Name:** Eindeutiger Name des Tags
- **Farbe:** Hex-Farbe für visuelle Darstellung
- **Kategorie:** Gruppierung von Tags (z.B. "Kundentyp", "Status", "Branche")
- **Beschreibung:** Optionale Beschreibung des Tags
- **Status:** Aktiv/Inaktiv

### 2. Tags zu Kunden zuweisen

**Zugriff:** CRM → Kunde öffnen → 🏷️ Tags-Bereich

**Funktionen:**
- Tags aus Liste auswählen
- Mehrere Tags gleichzeitig zuweisen
- Tags entfernen
- Aktuelle Tags anzeigen

### 3. Kunden nach Tags filtern

**Zugriff:** CRM → Kundenliste → 🏷️ Tags filtern

**Funktionen:**
- Nach einem oder mehreren Tags filtern
- Kombiniert mit anderen Filtern (Stadt, Suche)
- Echtzeit-Filterung

### 4. Massen-Tagging

**Funktionen:**
- Mehrere Kunden auswählen
- Tags gleichzeitig hinzufügen oder entfernen
- Bulk-Operationen für effiziente Verwaltung

### 5. Tag-Statistiken

**Zugriff:** Admin-Panel → Tag-Verwaltung → 📊 Statistiken

**Anzeige:**
- Anzahl Kunden pro Tag
- Meistgenutzte Tags
- Tag-Kategorien
- Visuelle Darstellung

## Verwendungsbeispiele

### Beispiel 1: Kundentypen kategorisieren

```
Tags erstellen:
- "VIP-Kunde" (Gold) - Kategorie: Kundentyp
- "Privatkunde" (Blau) - Kategorie: Kundentyp
- "Gewerbekunde" (Grün) - Kategorie: Kundentyp
- "Landwirtschaft" (Braun) - Kategorie: Kundentyp
```

### Beispiel 2: Verkaufsstatus verfolgen

```
Tags erstellen:
- "Interessent" (Gelb) - Kategorie: Status
- "Angebot versendet" (Orange) - Kategorie: Status
- "Verhandlung" (Lila) - Kategorie: Status
- "Kunde" (Grün) - Kategorie: Status
- "Inaktiv" (Grau) - Kategorie: Status
```

### Beispiel 3: Branchen segmentieren

```
Tags erstellen:
- "Einzelhandel" (Rot) - Kategorie: Branche
- "Gastronomie" (Orange) - Kategorie: Branche
- "Produktion" (Blau) - Kategorie: Branche
- "Dienstleistung" (Grün) - Kategorie: Branche
```

## Technische Details

### Datenbankstruktur

**Tabelle: crm_tags**
- `id`: Primärschlüssel
- `name`: Tag-Name (eindeutig)
- `color`: Hex-Farbe
- `category`: Kategorie
- `description`: Beschreibung
- `created_at`: Erstellungsdatum
- `created_by`: Ersteller
- `is_active`: Aktiv-Status

**Tabelle: customer_tags**
- `id`: Primärschlüssel
- `customer_id`: Kunden-ID (Foreign Key)
- `tag_id`: Tag-ID (Foreign Key)
- `assigned_at`: Zuweisungsdatum
- `assigned_by`: Zuweiser
- Unique Constraint: (customer_id, tag_id)

### API-Funktionen

**Tag CRUD:**
```python
from crm.features.tag_manager import (
    create_tag,
    get_tag_by_id,
    get_all_tags,
    update_tag,
    delete_tag
)

# Tag erstellen
tag_id = create_tag(conn, name="VIP", color="#FFD700", category="Status")

# Alle Tags laden
tags = get_all_tags(conn, category="Status", active_only=True)

# Tag aktualisieren
update_tag(conn, tag_id, name="VIP-Kunde", description="Wichtige Kunden")

# Tag löschen
delete_tag(conn, tag_id)
```

**Tag-Zuweisungen:**
```python
from crm.features.tag_manager import (
    assign_tag_to_customer,
    remove_tag_from_customer,
    get_customer_tags,
    get_customers_by_tag
)

# Tag zuweisen
assign_tag_to_customer(conn, customer_id=1, tag_id=5)

# Tags eines Kunden laden
tags = get_customer_tags(conn, customer_id=1)

# Kunden mit bestimmtem Tag finden
customer_ids = get_customers_by_tag(conn, tag_id=5)
```

**Bulk-Operationen:**
```python
from crm.features.tag_manager import (
    assign_tags_to_customers,
    remove_tags_from_customers
)

# Mehrere Tags zu mehreren Kunden
stats = assign_tags_to_customers(
    conn,
    customer_ids=[1, 2, 3],
    tag_ids=[5, 6]
)
# Gibt zurück: {'success': 6, 'skipped': 0, 'errors': 0}

# Tags von mehreren Kunden entfernen
removed = remove_tags_from_customers(
    conn,
    customer_ids=[1, 2],
    tag_ids=[5]
)
```

**Statistiken:**
```python
from crm.features.tag_manager import (
    get_tag_statistics,
    get_tag_categories
)

# Tag-Statistiken
stats = get_tag_statistics(conn)
# Gibt zurück: [{'id': 1, 'name': 'VIP', 'customer_count': 15}, ...]

# Kategorien
categories = get_tag_categories(conn)
# Gibt zurück: ['Kundentyp', 'Status', 'Branche']
```

## Best Practices

### 1. Tag-Namenskonventionen
- Verwenden Sie klare, beschreibende Namen
- Vermeiden Sie Abkürzungen
- Seien Sie konsistent in der Schreibweise

### 2. Farb-Coding
- Verwenden Sie konsistente Farben für ähnliche Kategorien
- Rot/Orange: Dringend, Wichtig
- Grün: Positiv, Aktiv
- Blau: Neutral, Standard
- Grau: Inaktiv, Archiviert

### 3. Kategorien nutzen
- Gruppieren Sie Tags logisch in Kategorien
- Erleichtert die Verwaltung und Filterung
- Beispiele: "Kundentyp", "Status", "Branche", "Priorität"

### 4. Regelmäßige Wartung
- Überprüfen Sie regelmäßig ungenutzte Tags
- Konsolidieren Sie ähnliche Tags
- Deaktivieren Sie veraltete Tags statt sie zu löschen

### 5. Massen-Operationen
- Nutzen Sie Bulk-Tagging für effiziente Verwaltung
- Planen Sie Tag-Strukturen vor großen Importen
- Verwenden Sie Filter für gezielte Massen-Aktionen

## Fehlerbehebung

### Problem: Tag kann nicht erstellt werden
**Lösung:** Prüfen Sie, ob der Name bereits existiert. Tag-Namen müssen eindeutig sein.

### Problem: Tag wird nicht in der Liste angezeigt
**Lösung:** Prüfen Sie, ob der Tag aktiv ist. Inaktive Tags werden standardmäßig ausgeblendet.

### Problem: Kunde hat zu viele Tags
**Lösung:** Überprüfen Sie Ihre Tag-Struktur. Eventuell sollten Tags konsolidiert werden.

### Problem: Filterung nach Tags funktioniert nicht
**Lösung:** Stellen Sie sicher, dass die Tags den Kunden korrekt zugewiesen sind.

## Integration

### CRM-Kundenliste
- Tags werden als farbige Badges angezeigt
- Filterung nach Tags möglich
- Kombinierbar mit anderen Filtern

### CRM-Dashboard
- Tag-Statistiken im Statistik-Tab
- Top 5 meistgenutzte Tags
- Visuelle Darstellung

### Admin-Panel
- Vollständige Tag-Verwaltung
- Statistiken und Analysen
- Bulk-Operationen

## Weitere Informationen

- **Modul:** `crm/features/tag_manager.py`
- **UI:** `crm/features/tag_ui.py`
- **Tests:** `crm/features/test_tag_manager.py`
- **Datenbank:** Tabellen `crm_tags` und `customer_tags`

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie diese Dokumentation
2. Überprüfen Sie die Test-Datei für Beispiele
3. Kontaktieren Sie den System-Administrator
