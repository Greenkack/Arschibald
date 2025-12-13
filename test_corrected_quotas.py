"""
Test script to verify corrected quota calculations
"""
import sqlite3
from pathlib import Path

# Database connection
DB_PATH = Path(__file__).parent / "data" / "app_data.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "="*80)
print("TEST: Korrigierte Quotenberechnungen")
print("="*80)

# Get Kamuran's ID
cursor.execute("""
    SELECT id, first_name, last_name 
    FROM controlling_employees 
    WHERE first_name LIKE '%Kamuran%'
""")
kamuran = cursor.fetchone()
if not kamuran:
    print("❌ Kamuran nicht gefunden!")
    exit(1)

kamuran_id, first_name, last_name = kamuran
print(f"\n✅ Mitarbeiter: {first_name} {last_name} (ID: {kamuran_id})")

# Get latest data for Kamuran (2025-12-07)
cursor.execute("""
    SELECT c.name, pd.value
    FROM controlling_performance_data pd
    JOIN controlling_criteria c ON pd.criterion_id = c.id
    WHERE pd.employee_id = ? AND pd.date = '2025-12-07'
""", (kamuran_id,))

data = {}
for row in cursor.fetchall():
    criterion_name, value = row
    data[criterion_name] = float(value)

print(f"\n📅 Datum: 2025-12-07")
print(f"\n📊 ROHDATEN:")
print(f"  Verkauf: {data.get('Verkauf', 0)}")
print(f"  Kunden terminiert: {data.get('Kunden terminiert', 0)}")
print(f"  Getätigte Anrufe gesamt: {data.get('Getätigte Anrufe gesamt', 0)}")
print(f"  Angefahrene Termine: {data.get('Angefahrene Termine', 0)}")
print(f"  Storniert / kein Interesse: {data.get('Storniert / kein Interesse', 0)}")
print(f"  Technisch nicht machbar: {data.get('Technisch nicht machbar', 0)}")
print(f"  Nicht erreicht / neu terminieren: {data.get('Nicht erreicht / neu terminieren', 0)}")
print(f"  Folgetermin gemacht: {data.get('Folgetermin gemacht', 0)}")
print(f"  Angebot erhalten: {data.get('Angebot erhalten', 0)}")
print(f"  Zu teuer gewesen: {data.get('Zu teuer gewesen', 0)}")
print(f"  QC bestanden: {data.get('QC bestanden', 0)}")

# Calculate quotas with CORRECTED formulas
verkauf = data.get('Verkauf', 0)
kunden_terminiert = data.get('Kunden terminiert', 0)
getaetigte_anrufe = data.get('Getätigte Anrufe gesamt', 0)
angefahrene_termine = data.get('Angefahrene Termine', 0)
storniert = data.get('Storniert / kein Interesse', 0)
technisch_nicht_machbar = data.get('Technisch nicht machbar', 0)
nicht_erreicht = data.get('Nicht erreicht / neu terminieren', 0)
folgetermin = data.get('Folgetermin gemacht', 0)
angebot = data.get('Angebot erhalten', 0)
zu_teuer = data.get('Zu teuer gewesen', 0)
qc_bestanden = data.get('QC bestanden', 0)

print(f"\n📈 BERECHNUNGEN (KORRIGIERTE FORMELN):")
print(f"\n0. Abschlussquote:")
if kunden_terminiert > 0:
    abschluss = (verkauf / kunden_terminiert) * 100
    print(f"   ({verkauf} / {kunden_terminiert}) × 100 = {abschluss:.2f}%")
    print(f"   ✅ Jeder {(kunden_terminiert/verkauf if verkauf > 0 else 0):.1f}. terminierte Kunde kauft")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n1. Terminvereinbarungsquote:")
if getaetigte_anrufe > 0:
    termin_quote = (kunden_terminiert / getaetigte_anrufe) * 100
    print(f"   ({kunden_terminiert} / {getaetigte_anrufe}) × 100 = {termin_quote:.2f}%")
    print(f"   ✅ Jeder {(getaetigte_anrufe/kunden_terminiert if kunden_terminiert > 0 else 0):.1f}. Anruf führt zu einem Termin")
else:
    print(f"   0.00% (keine Anrufe)")

print(f"\n2. Termine-Anfahrquote:")
if kunden_terminiert > 0:
    anfahr_quote = (angefahrene_termine / kunden_terminiert) * 100
    print(f"   ({angefahrene_termine} / {kunden_terminiert}) × 100 = {anfahr_quote:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n3. nicht interessierte Kunden Quote:")
if kunden_terminiert > 0:
    nicht_int = (storniert / kunden_terminiert) * 100
    print(f"   ({storniert} / {kunden_terminiert}) × 100 = {nicht_int:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n4. technisch nicht machbar Quote:")
if kunden_terminiert > 0:
    tech_nicht = (technisch_nicht_machbar / kunden_terminiert) * 100
    print(f"   ({technisch_nicht_machbar} / {kunden_terminiert}) × 100 = {tech_nicht:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n5. Quote der nicht erreichten Kunden:")
if getaetigte_anrufe > 0:
    nicht_err = (nicht_erreicht / getaetigte_anrufe) * 100
    print(f"   ({nicht_erreicht} / {getaetigte_anrufe}) × 100 = {nicht_err:.2f}%")
    print(f"   ✅ Jeder {(getaetigte_anrufe/nicht_erreicht if nicht_erreicht > 0 else 0):.1f}. Anruf erreicht den Kunden nicht")
else:
    print(f"   0.00% (keine Anrufe)")

print(f"\n6. Quote für Folgetermine-Vereinbarungen:")
if kunden_terminiert > 0:
    folge_quote = (folgetermin / kunden_terminiert) * 100
    print(f"   ({folgetermin} / {kunden_terminiert}) × 100 = {folge_quote:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n7. Quote für Angebote:")
if kunden_terminiert > 0:
    angebot_quote = (angebot / kunden_terminiert) * 100
    print(f"   ({angebot} / {kunden_terminiert}) × 100 = {angebot_quote:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n8. Quote für zu teuer:")
if kunden_terminiert > 0:
    teuer_quote = (zu_teuer / kunden_terminiert) * 100
    print(f"   ({zu_teuer} / {kunden_terminiert}) × 100 = {teuer_quote:.2f}%")
else:
    print(f"   0.00% (keine terminierten Kunden)")

print(f"\n9. Quote für QC bestanden:")
if verkauf > 0:
    qc_quote = (qc_bestanden / verkauf) * 100
    print(f"   ({qc_bestanden} / {verkauf}) × 100 = {qc_quote:.2f}%")
    if qc_bestanden > verkauf:
        print(f"   ⚠️ WARNUNG: QC bestanden ({qc_bestanden}) > Verkauf ({verkauf})")
else:
    print(f"   0.00% (keine Verkäufe)")

print("\n" + "="*80)
print("✅ NEUE FORMELN VERWENDEN 'Kunden terminiert' ALS NENNER!")
print("="*80 + "\n")

conn.close()
