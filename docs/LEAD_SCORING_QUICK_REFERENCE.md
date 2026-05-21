# Lead Scoring - Quick Reference

## Übersicht

Das Lead Scoring System bewertet Leads automatisch basierend auf konfigurierbaren Regeln und hilft dem Vertriebsteam, sich auf die vielversprechendsten Opportunities zu konzentrieren.

## Features

### ✅ Automatische Score-Berechnung
- Scores werden automatisch bei Lead-Erstellung berechnet
- Automatische Aktualisierung bei Änderungen (Stage, Wert, etc.)
- Score-Range: 0-100 Punkte

### 🎯 Scoring-Faktoren

**Projektgröße:**
- Großes Projekt (>50k): +30 Punkte
- Mittleres Projekt (25k-50k): +20 Punkte
- Kleines Projekt (10k-25k): +10 Punkte

**Lead-Quelle:**
- Empfehlung: +25 Punkte
- Website: +15 Punkte
- Social Media: +10 Punkte

**Engagement:**
- Hohe Wahrscheinlichkeit (>70%): +20 Punkte
- Mittlere Wahrscheinlichkeit (40-70%): +10 Punkte

**Pipeline-Stufe:**
- In Verhandlung: +35 Punkte
- Angebot erstellt: +25 Punkte
- Qualifiziert: +15 Punkte

### 📊 Score-Kategorien

- **🔥 Hot (80-100)**: Höchste Priorität
- **⚡ Warm (60-79)**: Hohe Priorität
- **📊 Medium (40-59)**: Mittlere Priorität
- **❄️ Cold (0-39)**: Niedrige Priorität

## Verwendung

### In der Pipeline

Scores werden automatisch in der Pipeline-Ansicht angezeigt:
- Score-Badge in jeder Lead-Karte
- Farbcodierung nach Kategorie
- Sortierung nach Score möglich

### Im Admin-Panel

**Navigation:** Admin-Panel → 🎯 Lead Scoring

**Tabs:**
1. **📊 Übersicht**
   - Score-Verteilung
   - Top-Leads (Score ≥ 70)
   - Neue High-Score Leads (letzte 24h)

2. **⚙️ Regeln verwalten**
   - Bestehende Regeln anzeigen/bearbeiten
   - Neue Regeln hinzufügen
   - Regeln aktivieren/deaktivieren

3. **🔄 Scores aktualisieren**
   - Alle Scores neu berechnen
   - Score-Statistiken anzeigen

### Benachrichtigungen

Das System benachrichtigt automatisch bei:
- Leads die einen Score ≥ 80 erreichen
- Signifikante Score-Erhöhungen
- Anzeige in der Übersicht (letzte 24h)

## API-Funktionen

### Lead Score berechnen
```python
from crm.features.lead_scoring import calculate_lead_score

score = calculate_lead_score(conn, lead_id)
```

### Lead Score aktualisieren
```python
from crm.features.lead_scoring import update_lead_score

success = update_lead_score(conn, lead_id, "Reason for update")
```

### High-Score Leads abrufen
```python
from crm.features.lead_scoring import get_high_score_leads

high_score_leads = get_high_score_leads(conn, min_score=70)
```

### Scoring-Regeln verwalten
```python
from crm.features.lead_scoring import (
    get_scoring_rules,
    add_scoring_rule,
    update_scoring_rule,
    delete_scoring_rule
)

# Regeln abrufen
rules = get_scoring_rules(conn, active_only=True)

# Neue Regel hinzufügen
rule_id = add_scoring_rule(
    conn,
    rule_name="Custom Rule",
    rule_type="custom",
    condition_field="estimated_value",
    condition_operator=">",
    condition_value="75000",
    points=40
)

# Regel aktualisieren
update_scoring_rule(conn, rule_id, points=50, is_active=True)

# Regel löschen
delete_scoring_rule(conn, rule_id)
```

## Regel-Operatoren

- `>`: Größer als
- `<`: Kleiner als
- `>=`: Größer oder gleich
- `<=`: Kleiner oder gleich
- `==`: Gleich
- `between`: Zwischen zwei Werten (Format: "min,max")
- `age_hours`: Alter in Stunden (für Zeitfelder)
- `age_days`: Alter in Tagen (für Zeitfelder)

## Beispiel: Benutzerdefinierte Regel

```python
# Regel für sehr große Projekte
add_scoring_rule(
    conn,
    rule_name="Sehr großes Projekt (>100k)",
    rule_type="project_size",
    condition_field="estimated_value",
    condition_operator=">",
    condition_value="100000",
    points=50
)

# Regel für schnelle Reaktion
add_scoring_rule(
    conn,
    rule_name="Sehr schnelle Reaktion (<12h)",
    rule_type="response_time",
    condition_field="created_at",
    condition_operator="age_hours",
    condition_value="12",
    points=20
)
```

## Score-Historie

Jede Score-Änderung wird protokolliert:
```python
from crm.features.lead_scoring import get_lead_score_history

history = get_lead_score_history(conn, lead_id)
# Gibt Liste mit: old_score, new_score, score_change, reason, calculated_at
```

## Best Practices

1. **Regelmäßige Überprüfung**: Überprüfen Sie die Scoring-Regeln regelmäßig und passen Sie sie an Ihre Erfahrungen an

2. **Nicht zu viele Regeln**: Halten Sie die Anzahl der Regeln überschaubar (10-15 Regeln sind optimal)

3. **Punkteverteilung**: Achten Sie darauf, dass die wichtigsten Faktoren die meisten Punkte geben

4. **Testen**: Testen Sie neue Regeln zunächst mit wenigen Punkten und passen Sie sie dann an

5. **Monitoring**: Überwachen Sie die Score-Verteilung und passen Sie Schwellenwerte bei Bedarf an

## Troubleshooting

**Problem:** Scores werden nicht aktualisiert
- **Lösung:** Führen Sie "Alle Scores neu berechnen" im Admin-Panel aus

**Problem:** Alle Leads haben niedrige Scores
- **Lösung:** Überprüfen Sie die Scoring-Regeln und passen Sie die Punktevergabe an

**Problem:** Score-Berechnung dauert lange
- **Lösung:** Deaktivieren Sie nicht benötigte Regeln

## Integration

Das Lead Scoring System ist automatisch integriert in:
- ✅ Pipeline-Übersicht (crm_pipeline_ui.py)
- ✅ Lead-Erstellung (automatische Score-Berechnung)
- ✅ Lead-Updates (automatische Score-Aktualisierung)
- ✅ Admin-Panel (Konfiguration)

## Datenbank-Tabellen

**crm_leads** (erweitert):
- `score` INTEGER - Aktueller Lead-Score (0-100)

**lead_scoring_rules**:
- Konfigurierbare Scoring-Regeln

**lead_scoring_history**:
- Historie aller Score-Änderungen

## Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die Logs auf Fehlermeldungen
2. Testen Sie die Score-Berechnung mit einem einzelnen Lead
3. Überprüfen Sie die Regel-Konfiguration im Admin-Panel
