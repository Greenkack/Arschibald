# PDF-Archivierung - Quick Reference

## Übersicht

Die automatische PDF-Archivierung speichert generierte PDFs automatisch in der Kundenakte mit Metadaten und Versionierung.

## Automatische Archivierung

PDFs werden **automatisch** nach der Generierung archiviert, wenn:
- Ein Kunde im Session State zugeordnet ist
- Die PDF-Generierung erfolgreich war

**Keine manuelle Aktion erforderlich!**

## PDF-Typen und Farben

| Typ | Label | Farbe | Verwendung |
|-----|-------|-------|------------|
| `offer_pdf` | Angebot | 🔵 Blau | Angebots-PDFs |
| `invoice_pdf` | Rechnung | 🟢 Grün | Rechnungs-PDFs |
| `contract_pdf` | Vertrag | 🟠 Orange | Vertrags-PDFs |
| `report_pdf` | Bericht | 🟣 Violett | Berichts-PDFs |
| `other_pdf` | Sonstiges | ⚫ Grau | Andere PDFs |

## Versionierung

PDFs werden automatisch versioniert:
- Erste Version: `angebot_v1_2025-01-13.pdf`
- Zweite Version: `angebot_v2_2025-01-14.pdf`
- Dritte Version: `angebot_v3_2025-01-15.pdf`

## Kundenakte-Anzeige

In der Kundenakte werden PDFs angezeigt mit:
- 🏷️ **Badge** mit Typ und Version
- 📅 **Datum** (formatiert: DD.MM.YYYY HH:MM)
- 📊 **Dateigröße** (KB/MB)
- 📥 **Download-Button**
- 🗑️ **Löschen-Button**

## Manuelle Verwendung

Falls Sie ein PDF manuell archivieren möchten:

```python
from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents

doc_id = auto_save_pdf_to_customer_documents(
    pdf_path="pfad/zur/datei.pdf",
    customer_id=123,
    project_id=456,  # Optional
    offer_data=offer_data  # Optional
)
```

## Session State Keys

Die automatische Erkennung sucht nach folgenden Keys:
- `current_customer_id`
- `selected_customer_id`
- `customer_id`
- `crm_current_customer_id`
- `current_customer['id']`

## Fehlerbehandlung

Bei Fehlern:
- ✅ PDF-Generierung wird **nicht** unterbrochen
- ✅ Fehler werden geloggt
- ✅ Benutzer wird informiert (falls UI verfügbar)

## Tipps

1. **Kunde zuordnen:** Stellen Sie sicher, dass ein Kunde im Session State ist
2. **Versionierung:** Alte Versionen bleiben erhalten
3. **Sortierung:** Neueste PDFs werden zuerst angezeigt
4. **Suche:** Nutzen Sie die Dateinamen-Suche in der Kundenakte

## Häufige Fragen

**Q: Warum wird mein PDF nicht archiviert?**  
A: Prüfen Sie, ob ein Kunde im Session State zugeordnet ist.

**Q: Kann ich die Versionsnummer manuell setzen?**  
A: Nein, die Versionierung erfolgt automatisch basierend auf vorhandenen Dokumenten.

**Q: Werden alte Versionen überschrieben?**  
A: Nein, alle Versionen bleiben erhalten.

**Q: Kann ich den PDF-Typ ändern?**  
A: Der Typ wird automatisch aus dem Dateinamen erkannt. Sie können ihn in der Datenbank manuell ändern.

## Support

Bei Problemen:
1. Prüfen Sie die Logs in der Konsole
2. Führen Sie Tests aus: `python crm/integration/test_pdf_bridge.py`
3. Lesen Sie die vollständige Dokumentation: `crm/integration/README.md`
