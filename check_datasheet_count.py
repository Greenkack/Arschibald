"""
Quick Check: Warum zeigt die UI nur 2 Datenblätter?
"""

# Mögliche Gründe:
print("=" * 80)
print("DIAGNOSE: 2 Datenblätter in der Übersicht")
print("=" * 80)

print("\nMögliche Szenarien:")
print("\n1. ✅ NORMAL: Benutzer hat nur Modul + Inverter konfiguriert")
print("   → Kein Speicher ausgewählt im Solar Calculator")
print("   → Kein Zubehör ausgewählt")
print("   → Erwartung: 2 Datenblätter ist KORREKT")

print("\n2. ⚠️  MÖGLICH: Manuelle Auswahl statt Auto-Auswahl")
print("   → Benutzer hat manuell 2 Produkte ausgewählt")
print("   → Check: Scrollen Sie zu 'Produktdatenblätter' im Formular")
print("   → Dort sollten Checkboxen sichtbar sein")

print("\n3. ❌ PROBLEM: Speicher ist konfiguriert aber wird nicht erkannt")
print("   → project_data['pv_details']['include_storage'] = False")
print("   → Lösung: Im Solar Calculator Speicher aktivieren")

print("\n" + "=" * 80)
print("EMPFEHLUNG")
print("=" * 80)
print("\n✅ Wenn Sie NUR Modul + Inverter haben:")
print("   → 2 Datenblätter ist KORREKT!")
print("   → Wählen Sie jetzt Diagramme aus und generieren Sie die PDF")

print("\n⚠️  Wenn Sie auch Speicher/Zubehör erwarten:")
print("   1. Gehen Sie zurück zum Solar Calculator")
print("   2. Aktivieren Sie Speicher / Zubehör")
print("   3. Führen Sie die Berechnung erneut aus")
print("   4. Dann sollten mehr Datenblätter erscheinen")

print("\n" + "=" * 80)
