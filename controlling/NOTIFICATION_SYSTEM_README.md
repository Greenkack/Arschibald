# Notification System - Employee Controlling

## Übersicht

Das Notification System ermöglicht die automatische Generierung von Benachrichtigungen basierend auf konfigurierbaren Schwellenwerten für Quoten. Es unterstützt verschiedene Benachrichtigungstypen (Erfolg, Warnung, Information, Fehler) und kann sowohl für einzelne Mitarbeiter als auch für Vergleichsberichte verwendet werden.

## Komponenten

### NotificationManager

Der `NotificationManager` ist die zentrale Klasse für die Verwaltung von Benachrichtigungsschwellenwerten und die Generierung von Benachrichtigungen.

**Hauptfunktionen:**
- Verwaltung von Benachrichtigungsschwellenwerten
- Überprüfung von Quoten gegen Schwellenwerte
- Generierung von Benachrichtigungen
- Formatierung für Streamlit-Anzeige

### NotificationThreshold

Definiert einen Schwellenwert für eine bestimmte Quote.

**Attribute:**
- `quota_name`: Name der Quote (z.B. "Abschlussquote")
- `threshold_value`: Schwellenwert in Prozent (0-100)
- `threshold_type`: Typ (ABOVE oder BELOW)
- `notification_type`: Art der Benachrichtigung (SUCCESS, INFO, WARNING, ERROR)
- `message_template`: Nachrichtenvorlage mit Platzhaltern

### Notification

Repräsentiert eine generierte Benachrichtigung.

**Attribute:**
- `notification_type`: Art der Benachrichtigung
- `title`: Titel der Benachrichtigung
- `message`: Nachrichtentext
- `quota_name`: Name der Quote
- `quota_value`: Aktueller Quotenwert
- `threshold_value`: Schwellenwert
- `employee_name`: Optional - Name des Mitarbeiters

## Verwendung

### Initialisierung

```python
from controlling.notifications import NotificationManager

# Manager mit Standard-Schwellenwerten initialisieren
manager = NotificationManager()
```

### Schwellenwerte hinzufügen

```python
from controlling.notifications import (
    NotificationType,
    ThresholdType
)

# Erfolgs-Benachrichtigung für hohe Abschlussquote
manager.add_threshold(
    quota_name="Abschlussquote",
    threshold_value=30.0,
    threshold_type=ThresholdType.ABOVE,
    notification_type=NotificationType.SUCCESS,
    message_template=(
        "Hervorragende Leistung! Die Abschlussquote von "
        "{quota_value:.1f}% liegt über dem Ziel von "
        "{threshold_value:.1f}%."
    )
)

# Warnungs-Benachrichtigung für niedrige Abschlussquote
manager.add_threshold(
    quota_name="Abschlussquote",
    threshold_value=15.0,
    threshold_type=ThresholdType.BELOW,
    notification_type=NotificationType.WARNING,
    message_template=(
        "Achtung: Die Abschlussquote von {quota_value:.1f}% "
        "liegt unter dem Mindestziel von {threshold_value:.1f}%."
    )
)
```

### Quoten überprüfen

```python
# Quoten-Dictionary
quotas = {
    "Abschlussquote": 35.0,
    "Terminvereinbarungsquote": 22.0,
    "Termine-Anfahrquote": 85.0
}

# Benachrichtigungen generieren
notifications = manager.check_quotas(
    quotas,
    employee_name="Max Mustermann"
)

# Benachrichtigungen anzeigen
for notification in notifications:
    print(f"{notification.title}: {notification.message}")
```

### Streamlit-Integration

```python
import streamlit as st

# Benachrichtigungen für Streamlit formatieren
for notification in notifications:
    streamlit_type, title, message = (
        manager.format_notification_for_streamlit(notification)
    )
    
    if streamlit_type == "success":
        st.success(f"**{title}**\n\n{message}")
    elif streamlit_type == "warning":
        st.warning(f"**{title}**\n\n{message}")
    elif streamlit_type == "info":
        st.info(f"**{title}**\n\n{message}")
    elif streamlit_type == "error":
        st.error(f"**{title}**\n\n{message}")
```

## Standard-Schwellenwerte

Das System wird mit folgenden Standard-Schwellenwerten initialisiert:

### Erfolgs-Benachrichtigungen (ABOVE)
- **Abschlussquote**: > 30%
- **Terminvereinbarungsquote**: > 20%
- **QC bestanden Quote**: > 90%

### Warnungs-Benachrichtigungen (BELOW)
- **Abschlussquote**: < 15%
- **Terminvereinbarungsquote**: < 10%
- **Termine-Anfahrquote**: < 70%

### Info-Benachrichtigungen (ABOVE)
- **Nicht interessierte Kunden Quote**: > 30%
- **Zu teuer Quote**: > 25%

## Admin-Konfiguration

Administratoren können Schwellenwerte über die Admin-UI konfigurieren:

1. Navigieren Sie zu **Admin-Panel** → **Controlling Einstellungen**
2. Wählen Sie den Tab **🔔 Benachrichtigungen**
3. Fügen Sie neue Schwellenwerte hinzu oder entfernen Sie bestehende

**Konfigurationsoptionen:**
- Quote auswählen (aus Standard-Quoten)
- Schwellenwert in Prozent (0-100)
- Schwellenwert-Typ (Über/Unter)
- Benachrichtigungs-Typ (Erfolg/Info/Warnung/Fehler)
- Nachrichtenvorlage mit Platzhaltern

## Controlling-UI Integration

Benachrichtigungen werden automatisch nach der Berichtserstellung angezeigt:

1. Erstellen Sie einen Bericht im Tab **📈 Berichte erstellen**
2. Nach erfolgreicher Erstellung werden relevante Benachrichtigungen angezeigt
3. Benachrichtigungen werden nach Typ farblich gekennzeichnet

**Hinweis:** Benachrichtigungen werden nur für Einzelmitarbeiter-Berichte generiert, nicht für Vergleichsberichte.

## API-Referenz

### NotificationManager

#### `__init__()`
Initialisiert den Manager mit Standard-Schwellenwerten.

#### `add_threshold(quota_name, threshold_value, threshold_type, notification_type, message_template)`
Fügt einen neuen Schwellenwert hinzu.

**Parameter:**
- `quota_name` (str): Name der Quote
- `threshold_value` (float): Schwellenwert (0-100)
- `threshold_type` (ThresholdType): ABOVE oder BELOW
- `notification_type` (NotificationType): Art der Benachrichtigung
- `message_template` (str): Nachrichtenvorlage

**Returns:** NotificationThreshold

#### `remove_threshold(quota_name, threshold_value, threshold_type)`
Entfernt einen Schwellenwert.

**Returns:** bool (True wenn erfolgreich)

#### `get_thresholds(quota_name=None)`
Gibt alle Schwellenwerte zurück, optional gefiltert nach Quote.

**Returns:** List[NotificationThreshold]

#### `check_quotas(quotas, employee_name=None)`
Überprüft Quoten gegen Schwellenwerte und generiert Benachrichtigungen.

**Parameter:**
- `quotas` (Dict[str, float]): Dictionary mit Quoten-Namen und Werten
- `employee_name` (str, optional): Name des Mitarbeiters

**Returns:** List[Notification]

#### `format_notification_for_streamlit(notification)`
Formatiert eine Benachrichtigung für Streamlit.

**Returns:** Tuple[str, str, str] (type, title, message)

#### `get_notification_summary(notifications)`
Gibt eine Zusammenfassung der Benachrichtigungen nach Typ zurück.

**Returns:** Dict[str, int]

## Tests

### Unit Tests
- 15 Unit Tests in `tests/test_notifications.py`
- Decken alle Funktionen des NotificationManagers ab
- Testen Schwellenwert-Verwaltung, Benachrichtigungsgenerierung und Formatierung

### Property-Based Tests
- 2 Property Tests in `tests/test_controlling_properties.py`
- **Property 53**: Quota Threshold Notification (100 Beispiele)
- **Property 54**: Quota Threshold Warning (100 Beispiele)

**Alle Tests bestehen:** ✅ 17/17

## Requirements

Implementiert folgende Requirements:
- **21.1**: Benachrichtigung bei Überschreitung von Schwellenwerten
- **21.2**: Warnung bei Unterschreitung von Schwellenwerten
- **21.4**: Konfigurierbare Schwellenwerte in Admin-Einstellungen

## Beispiel-Workflow

```python
# 1. Manager initialisieren
manager = NotificationManager()

# 2. Bericht erstellen (aus ReportGenerator)
report_data = report_gen.generate_report(
    employee_id=1,
    report_type=ReportType.MONTHLY,
    end_date=date.today()
)

# 3. Benachrichtigungen generieren
if "quotas" in report_data:
    notifications = manager.check_quotas(
        report_data["quotas"],
        employee_name=report_data.get("employee_name")
    )
    
    # 4. Benachrichtigungen anzeigen
    for notification in notifications:
        streamlit_type, title, message = (
            manager.format_notification_for_streamlit(notification)
        )
        
        if streamlit_type == "success":
            st.success(f"**{title}**\n\n{message}")
        elif streamlit_type == "warning":
            st.warning(f"**{title}**\n\n{message}")
```

## Erweiterungsmöglichkeiten

Das Notification System kann erweitert werden durch:

1. **E-Mail-Benachrichtigungen**: Integration mit E-Mail-Service
2. **Push-Benachrichtigungen**: Browser-Benachrichtigungen
3. **Benachrichtigungs-Historie**: Speicherung in Datenbank
4. **Benachrichtigungs-Präferenzen**: Benutzer-spezifische Einstellungen
5. **Eskalations-Regeln**: Automatische Eskalation bei kritischen Werten
6. **Benachrichtigungs-Aggregation**: Zusammenfassung mehrerer Benachrichtigungen

## Lizenz

Teil des Employee Controlling Systems.
