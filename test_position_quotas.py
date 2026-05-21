"""
Test für positions-spezifische Quoten-Berechnungen
"""

from controlling.position_criteria import (
    calculate_quotas_for_position,
    calculate_ratio_description,
    get_position_criteria,
    get_position_quotas,
    CALL_AGENT_CRITERIA,
    VERKAUFER_CRITERIA
)


def test_call_agent_quotas():
    """Test Call Agent Quoten"""
    print("\n=== CALL AGENT QUOTEN TEST ===\n")
    
    # Testdaten für Call Agent
    raw_data = {
        "Kunden terminiert": 70,
        "QC bestanden": 56,
        "Storniert / kein Interesse": 10,
        "Nicht erreicht / neu terminieren": 30,
        "Getätigte Anrufe gesamt": 200,
        "Verkauf": 20,
        "Folgetermin gemacht": 15,
        "Zu teuer gewesen": 5,
        "Angebot erhalten": 40,
        "Technisch nicht machbar": 8
    }
    
    quotas = calculate_quotas_for_position("Call Agent", raw_data)
    
    print("Berechnete Quoten:")
    for quota_name, quota_value in quotas.items():
        ratio = calculate_ratio_description(quota_value, quota_name, "Call Agent")
        print(f"  {quota_name}: {quota_value:.2f}% → {ratio}")
    
    # Erwartete Werte prüfen
    expected = {
        "QC bestanden Quote": 80.0,  # 56/70 * 100
        "Terminvereinbarungsquote": 35.0,  # 70/200 * 100
        "Verkaufsquote": 28.57,  # 20/70 * 100 (ca.)
    }
    
    print("\nValidierung:")
    for key, expected_val in expected.items():
        actual_val = quotas.get(key, 0.0)
        diff = abs(actual_val - expected_val)
        status = "✅ OK" if diff < 0.1 else f"❌ FEHLER (Differenz: {diff:.2f})"
        print(f"  {key}: {actual_val:.2f}% (erwartet {expected_val:.2f}%) {status}")


def test_verkaufer_quotas():
    """Test Verkäufer Quoten"""
    print("\n\n=== VERKÄUFER QUOTEN TEST ===\n")
    
    # Testdaten für Verkäufer
    raw_data = {
        "Angefahrene Termine": 50,
        "Nicht angefahrene Termine": 10,
        "Verkauf": 15,
        "QC bestanden": 12,
        "Storniert / kein Interesse": 5,
        "Technisch nicht machbar": 3,
        "Folgetermin gemacht": 8,
        "Zu teuer gewesen": 4,
        "Angebot erhalten": 30
    }
    
    quotas = calculate_quotas_for_position("Verkäufer", raw_data)
    
    print("Berechnete Quoten:")
    for quota_name, quota_value in quotas.items():
        ratio = calculate_ratio_description(quota_value, quota_name, "Verkäufer")
        print(f"  {quota_name}: {quota_value:.2f}% → {ratio}")
    
    # Erwartete Werte prüfen
    expected = {
        "Abschlussquote": 30.0,  # 15/50 * 100
        "QC bestanden Quote": 80.0,  # 12/15 * 100
        "Anfahrquote": 83.33,  # 50/60 * 100
    }
    
    print("\nValidierung:")
    for key, expected_val in expected.items():
        actual_val = quotas.get(key, 0.0)
        diff = abs(actual_val - expected_val)
        status = "✅ OK" if diff < 0.1 else f"❌ FEHLER (Differenz: {diff:.2f})"
        print(f"  {key}: {actual_val:.2f}% (erwartet {expected_val:.2f}%) {status}")


def test_position_criteria():
    """Test Kriterien-Listen"""
    print("\n\n=== POSITIONS-KRITERIEN TEST ===\n")
    
    print("Call Agent Kriterien:")
    ca_criteria = get_position_criteria("Call Agent")
    for i, criterion in enumerate(ca_criteria, 1):
        print(f"  {i}. {criterion}")
    
    print(f"\nAnzahl: {len(ca_criteria)}")
    
    print("\n\nVerkäufer Kriterien:")
    vk_criteria = get_position_criteria("Verkäufer")
    for i, criterion in enumerate(vk_criteria, 1):
        print(f"  {i}. {criterion}")
    
    print(f"\nAnzahl: {len(vk_criteria)}")
    
    # Prüfe dass keine irrelevanten Kriterien dabei sind
    print("\n\nValidierung:")
    if "Angefahrene Termine" not in ca_criteria:
        print("  ✅ Call Agent: 'Angefahrene Termine' korrekt NICHT enthalten")
    else:
        print("  ❌ Call Agent: 'Angefahrene Termine' sollte NICHT enthalten sein!")
    
    if "Getätigte Anrufe gesamt" not in vk_criteria:
        print("  ✅ Verkäufer: 'Getätigte Anrufe gesamt' korrekt NICHT enthalten")
    else:
        print("  ❌ Verkäufer: 'Getätigte Anrufe gesamt' sollte NICHT enthalten sein!")


def test_quota_definitions():
    """Test Quota-Definitionen"""
    print("\n\n=== QUOTA-DEFINITIONEN TEST ===\n")
    
    ca_quotas = get_position_quotas("Call Agent")
    print(f"Call Agent Quoten: {len(ca_quotas)}")
    for quota_def in ca_quotas:
        print(f"  - {quota_def.name}")
    
    vk_quotas = get_position_quotas("Verkäufer")
    print(f"\nVerkäufer Quoten: {len(vk_quotas)}")
    for quota_def in vk_quotas:
        print(f"  - {quota_def.name}")
    
    # Prüfe dass irrelevante Quoten NICHT dabei sind
    print("\n\nValidierung:")
    ca_quota_names = [q.name for q in ca_quotas]
    if "Termine-Anfahrquote" not in ca_quota_names:
        print("  ✅ Call Agent: 'Termine-Anfahrquote' korrekt NICHT enthalten")
    else:
        print("  ❌ Call Agent: 'Termine-Anfahrquote' sollte NICHT enthalten sein!")


if __name__ == "__main__":
    print("=" * 60)
    print("POSITIONS-SPEZIFISCHE QUOTEN - VALIDIERUNGSTEST")
    print("=" * 60)
    
    try:
        test_position_criteria()
        test_quota_definitions()
        test_call_agent_quotas()
        test_verkaufer_quotas()
        
        print("\n" + "=" * 60)
        print("✅ ALLE TESTS ABGESCHLOSSEN")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
