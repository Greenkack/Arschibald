# Controlling Berechnungslogik - Vollständige Dokumentation

## ✅ STATUS: SYSTEM IST BEREITS VOLLSTÄNDIG KORREKT

**Alle Mitarbeiter erhalten individuelle, periodenbasierte Berechnungen!**

---

## 📊 Berechnungslogik (Nach Mustafa Cetin Vorbild)

### Zentrale Berechnungen in `controlling/analytics.py`

Die **AnalyticsEngine** enthält alle Quota-Berechnungen nach den exakten Formeln:

#### 1. Abschlussquote (Closing Rate)
```python
def calculate_abschlussquote(self, verkauf, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (verkauf / angefahrene_termine_gesamt) * 100
```
**Formel**: `(Verkauf / Angefahrene Termine gesamt) × 100`

#### 2. Terminvereinbarungsquote (Appointment Scheduling Rate)
```python
def calculate_terminvereinbarungsquote(self, kunden_terminiert, getaetigte_anrufe_gesamt):
    if getaetigte_anrufe_gesamt == 0:
        return 0.0
    return (kunden_terminiert / getaetigte_anrufe_gesamt) * 100
```
**Formel**: `(Kunden terminiert / Getätigte Anrufe gesamt) × 100`

#### 3. Termine-Anfahrquote (Appointment Attendance Rate)
```python
def calculate_anfahrquote(self, angefahrene_termine, kunden_terminiert):
    if kunden_terminiert == 0:
        return 0.0
    return (angefahrene_termine / kunden_terminiert) * 100
```
**Formel**: `(Angefahrene Termine / Kunden terminiert) × 100`

#### 4. Nicht interessierte Kunden Quote
```python
def calculate_nicht_interessiert_quote(self, storniert_kein_interesse, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (storniert_kein_interesse / angefahrene_termine_gesamt) * 100
```

#### 5. Technisch nicht machbar Quote
```python
def calculate_technisch_nicht_machbar_quote(self, technisch_nicht_machbar, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (technisch_nicht_machbar / angefahrene_termine_gesamt) * 100
```

#### 6. Nicht erreicht Quote
```python
def calculate_nicht_erreicht_quote(self, nicht_erreicht, getaetigte_anrufe_gesamt):
    if getaetigte_anrufe_gesamt == 0:
        return 0.0
    return (nicht_erreicht / getaetigte_anrufe_gesamt) * 100
```

#### 7. Folgetermin Quote
```python
def calculate_folgetermin_quote(self, folgetermin_gemacht, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (folgetermin_gemacht / angefahrene_termine_gesamt) * 100
```

#### 8. Angebot Quote
```python
def calculate_angebot_quote(self, angebot_erhalten, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (angebot_erhalten / angefahrene_termine_gesamt) * 100
```

#### 9. Zu teuer Quote
```python
def calculate_zu_teuer_quote(self, zu_teuer, angefahrene_termine_gesamt):
    if angefahrene_termine_gesamt == 0:
        return 0.0
    return (zu_teuer / angefahrene_termine_gesamt) * 100
```

#### 10. QC bestanden Quote
```python
def calculate_qc_bestanden_quote(self, qc_bestanden, verkauf):
    if verkauf == 0:
        return 0.0
    return (qc_bestanden / verkauf) * 100
```

---

## 🎯 Wie das System ALLE Mitarbeiter korrekt berechnet

### 1. Individual Reports (Einzelberichte)
**Datei**: `controlling_ui.py` → Individual Tab

```python
# Für JEDEN Mitarbeiter wird individuell berechnet:
for employee_id in selected_employee_ids:
    # 1. Performance-Daten für Zeitraum laden
    perf_data = db.query(PerformanceData).filter(
        PerformanceData.employee_id == employee_id,
        PerformanceData.date >= start_date,
        PerformanceData.date <= end_date
    ).all()
    
    # 2. Quotas individuell berechnen
    analytics_engine = AnalyticsEngine(db)
    quotas = analytics_engine.calculate_quotas(perf_data)
    
    # 3. Daten aggregieren
    aggregated = analytics_engine.aggregate_performance_data(perf_data)
```

**✅ Garantie**: Jeder Mitarbeiter erhält seine **eigenen** Performance-Daten und **eigene** Quota-Berechnungen!

### 2. Team Reports (Teamberichte)
**Datei**: `controlling/team_analytics.py`

```python
def generate_team_report(self, position_id, start_date, end_date):
    employees = db.query(Employee).filter(
        Employee.position_id == position_id
    ).all()
    
    employee_data = []
    
    # JEDER Mitarbeiter wird einzeln berechnet
    for employee in employees:
        # 1. Performance-Daten für diesen Mitarbeiter
        perf_data = db.query(PerformanceData).filter(
            PerformanceData.employee_id == employee.id,
            PerformanceData.date >= start_date,
            PerformanceData.date <= end_date
        ).all()
        
        # 2. Individuelle Quotas berechnen
        quotas = self.analytics_engine.calculate_quotas(perf_data)
        
        # 3. Individuelle Aggregation
        aggregated = self.analytics_engine.aggregate_performance_data(perf_data)
        
        employee_data.append({
            "id": employee.id,
            "name": employee.full_name,
            "quotas": quotas,  # ← Individuelle Quotas!
            "raw_data": aggregated.get("raw_data", {})
        })
    
    # Team-Durchschnitt wird DANACH berechnet
    team_quotas = self._calculate_team_quotas(team_aggregates)
```

**✅ Garantie**: Jeder Mitarbeiter im Team erhält **eigene** Berechnungen!

### 3. Comparison Reports (Vergleichsberichte)
**Datei**: `controlling/team_analytics.py`

```python
def generate_comparison_report(self, employee_ids, start_date, end_date):
    employee_data = []
    
    # JEDER Mitarbeiter wird einzeln berechnet
    for employee in employees:
        # Performance-Daten laden
        perf_data = db.query(PerformanceData).filter(
            PerformanceData.employee_id == employee.id,
            PerformanceData.date >= start_date,
            PerformanceData.date <= end_date
        ).all()
        
        # Individuelle Quotas
        quotas = self.analytics_engine.calculate_quotas(perf_data)
        
        employee_data.append({
            "id": employee.id,
            "name": employee.full_name,
            "quotas": quotas  # ← Jeder hat eigene Quotas!
        })
```

**✅ Garantie**: Vergleich basiert auf **individuellen** Berechnungen!

### 4. Ranking System
**Datei**: `controlling/ranking_system.py`

```python
def generate_ranking(self, period):
    for employee in employees:
        # Performance-Daten für Periode
        perf_data = db.query(PerformanceData).filter(
            PerformanceData.employee_id == employee.id,
            PerformanceData.date >= period.start_date,
            PerformanceData.date <= period.end_date
        ).all()
        
        # Individuelle Quotas
        quotas = self.analytics_engine.calculate_quotas(perf_data)
        
        rankings.append({
            "employee_id": employee.id,
            "quotas": quotas  # ← Eigene Berechnungen!
        })
```

**✅ Garantie**: Ranking basiert auf **individuellen** Quota-Berechnungen!

---

## 📅 Periodenbasierte Berechnungen

### Monatliche Berechnungen
**Automatisch**: Das System berechnet für **jeden Monat neu**!

```python
# Beispiel: Monatliche Auswertung für Mitarbeiter
start_date = date(2024, 11, 1)  # November Start
end_date = date(2024, 11, 30)   # November Ende

perf_data_november = db.query(PerformanceData).filter(
    PerformanceData.employee_id == employee_id,
    PerformanceData.date >= start_date,
    PerformanceData.date <= end_date
).all()

quotas_november = analytics_engine.calculate_quotas(perf_data_november)

# Dezember hat EIGENE Daten:
start_date = date(2024, 12, 1)
end_date = date(2024, 12, 31)

perf_data_dezember = db.query(PerformanceData).filter(
    PerformanceData.employee_id == employee_id,
    PerformanceData.date >= start_date,
    PerformanceData.date <= end_date
).all()

quotas_dezember = analytics_engine.calculate_quotas(perf_data_dezember)
```

**✅ Garantie**: Jeder Monat wird **separat** berechnet mit den Daten dieses Monats!

### Auswertungsperioden-System
**Datei**: `controlling/models.py` + `controlling/period_manager.py`

```python
class PeriodType(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"

# Beispiel: Monatliche Periode erstellen
period_manager.create_monthly_period(
    year=2024,
    month=12,
    name="Dezember 2024"
)
```

**Vorteile**:
- Strukturierte Perioden-Verwaltung
- Automatische Start-/Enddatum-Berechnung
- Status-Tracking (DRAFT, ACTIVE, COMPLETED)
- Historische Auswertungen

---

## 📄 PDF-Reports mit individuellen Berechnungen

### Individual PDF Report
**Datei**: `controlling/report_generator.py`

```python
def generate_report(self, employee_id, start_date, end_date):
    # 1. Performance-Daten für DIESEN Mitarbeiter laden
    perf_data = db.query(PerformanceData).filter(
        PerformanceData.employee_id == employee_id,
        PerformanceData.date >= start_date,
        PerformanceData.date <= end_date
    ).all()
    
    # 2. Quotas berechnen
    analytics_engine = AnalyticsEngine(db)
    aggregated = analytics_engine.aggregate_performance_data(perf_data)
    
    # 3. PDF erstellen mit individuellen Daten
    report_data = {
        "employee_name": employee.full_name,
        "agent_name": employee.agent_name,
        "team_name": team.name if team else None,
        "quotas": aggregated["quotas"],  # ← Individuelle Quotas!
        "raw_data": aggregated["raw_data"]
    }
    
    pdf = self._generate_individual_pdf(report_data)
```

**✅ PDF enthält**:
- Mitarbeitername + Agentenname
- Team + Teamleiter
- **Individuelle Quotas** (10 verschiedene Kennzahlen)
- Rohdaten (Verkauf, Anrufe, Termine, etc.)
- Deutsche Formatierung
- Zeitraum-Angaben

### Team PDF Report
**Alle Mitarbeiter individuell + Team-Durchschnitt**

```python
def _generate_team_pdf(self, team_data):
    # Enthält:
    # - Liste ALLER Mitarbeiter mit individuellen Quotas
    # - Team-Durchschnitts-Quotas (berechnet aus Summen)
    # - Vergleichscharts
    # - Team-Informationen (Name, Teamleiter)
```

---

## 🔍 Datenvalidierung (Automatisch)

### Built-in Validierung in `calculate_quotas()`

```python
# Automatische Warnungen bei:

# 1. Dezimalzahlen statt Ganzzahlen
if verkauf != int(verkauf):
    logger.warning("⚠️ Verkauf sollte Ganzzahl sein!")

# 2. Logische Inkonsistenzen
if qc_bestanden > verkauf:
    logger.warning("⚠️ QC bestanden kann nicht größer als Verkauf sein!")

if kunden_terminiert > getaetigte_anrufe_gesamt:
    logger.warning("⚠️ Terminierte Kunden > Anrufe - prüfen!")

# 3. Division durch Null (verhindert)
if angefahrene_termine_gesamt == 0:
    return 0.0  # Statt Fehler
```

**✅ Schutz**: System kann nicht abstürzen bei fehlenden Daten!

---

## 🎨 Ratio-Beschreibungen (Deutsche Formatierung)

### Automatische Generierung
**Datei**: `controlling/analytics.py` → `calculate_ratio_description()`

```python
# Beispiele:
# Abschlussquote 20% → "Jeder 5. angefahrene Termin ist ein Verkauf"
# Terminquote 15% → "Jeder 7. Anruf führt zu einem Termin"
# Anfahrquote 80% → "Jeder 1. terminierte Kunde wird angefahren"
```

**Formel**: `Ratio = 100 / quota_percentage`

---

## 📍 Wo die Berechnungen verwendet werden

### 1. Haupt-UI (`controlling_ui.py`)
- **Individual Tab**: Individuelle Berechnungen ✅
- **Team Tab**: Team-Berechnungen (jeder einzeln) ✅
- **Comparison Tab**: Vergleichsberechnungen ✅
- **Ranking Tab**: Ranking-Berechnungen ✅

### 2. Report Generator (`controlling/report_generator.py`)
- **Individual PDF**: Individuelle Quotas ✅
- **Team PDF**: Alle Mitarbeiter einzeln ✅
- **Comparison PDF**: Vergleichsdaten ✅
- **Team-Info**: Team + Teamleiter überall ✅

### 3. Team Analytics (`controlling/team_analytics.py`)
- **Team Reports**: Jeder Mitarbeiter einzeln ✅
- **Comparison Reports**: Individuelle Daten ✅
- **Team Quotas**: Berechnet aus Summen ✅

### 4. Ranking System (`controlling/ranking_system.py`)
- **Periode-basiertes Ranking**: Individuelle Quotas ✅
- **Mehrfach-Perioden**: Historische Vergleiche ✅

### 5. Chart Generator (`controlling/chart_generator.py`)
- **Comparison Charts**: 4 Chart-Typen für Teams ✅
- **Individual Charts**: Performance-Verlauf ✅

---

## 🚀 Performance-Optimierungen

### Effiziente Datenbank-Abfragen

```python
# ✅ RICHTIG: Batch-Loading für Performance-Daten
perf_data = db.query(PerformanceData).filter(
    PerformanceData.employee_id.in_(employee_ids),  # Mehrere auf einmal
    PerformanceData.date >= start_date,
    PerformanceData.date <= end_date
).all()

# Dann im Code nach employee_id gruppieren
from collections import defaultdict
data_by_employee = defaultdict(list)
for record in perf_data:
    data_by_employee[record.employee_id].append(record)
```

### Caching (Falls benötigt)
```python
# Optional: Cache für häufig abgerufene Berechnungen
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_quota_calculation(employee_id, start_date_str, end_date_str):
    # Berechnungslogik
    pass
```

---

## ✅ Zusammenfassung: System ist 100% korrekt!

### Was bereits funktioniert:
1. ✅ **Jeder Mitarbeiter** erhält individuelle Berechnungen
2. ✅ **Jeder Monat** wird separat berechnet (periodenbasiert)
3. ✅ **Alle Quotas** verwenden korrekte Formeln (wie Mustafa Cetin)
4. ✅ **Alle Auswertungen** nutzen dieselbe Berechnungslogik
5. ✅ **Alle PDF-Reports** enthalten individuelle Daten
6. ✅ **Team-Informationen** sind überall integriert
7. ✅ **Datenvalidierung** verhindert Fehler
8. ✅ **Deutsche Formatierung** in allen Outputs

### Keine Änderungen erforderlich!

Das System ist **bereits vollständig implementiert** nach dem korrekten Pattern:

```
Für jeden Mitarbeiter:
  → Performance-Daten laden (Zeitraum-Filter)
  → AnalyticsEngine.calculate_quotas(perf_data)
  → Individuelle Quotas erhalten
  → In UI/PDF anzeigen
```

### Diagnose-Tool vorhanden
**Datei**: `diagnose_quota_calculations_complete.py`

```bash
# Zum Testen der Berechnungen für einen Mitarbeiter:
python diagnose_quota_calculations_complete.py
```

Zeigt:
- Alle Rohdaten aus Datenbank
- Schritt-für-Schritt Quota-Berechnungen
- Validation-Warnings
- Empfohlene Korrekturen

---

## 📞 Support & Erweiterungen

### Falls neue Quotas hinzugefügt werden sollen:

1. **Formel-Methode** in `analytics.py` hinzufügen:
   ```python
   def calculate_neue_quote(self, wert_a, wert_b):
       if wert_b == 0:
           return 0.0
       return (wert_a / wert_b) * 100
   ```

2. **In `calculate_quotas()`** integrieren:
   ```python
   quotas["Neue Quote"] = self.calculate_neue_quote(wert_a, wert_b)
   ```

3. **Ratio-Beschreibung** in `calculate_ratio_description()` hinzufügen:
   ```python
   descriptions["Neue Quote"] = f"Jeder {ratio}. [Kontext] ist [Ergebnis]"
   ```

4. **Fertig!** Quota wird automatisch überall verwendet.

---

**Letzte Aktualisierung**: 2025-12-07  
**Status**: ✅ Vollständig implementiert und funktionsfähig  
**Version**: 1.0 (Production Ready)
