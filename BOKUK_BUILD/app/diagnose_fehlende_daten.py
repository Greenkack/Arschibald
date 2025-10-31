"""
NOTFALL-DIAGNOSE: Warum fehlen Charts und Wechselrichter/Speicher?
"""

print("=" * 100)
print("🚨 KRITISCHE DIAGNOSE: Fehlende Inhalte")
print("=" * 100)

print("\n" + "=" * 100)
print("PROBLEM 1: Charts können nicht ausgewählt werden")
print("=" * 100)

print("\n❌ FEHLER: 'Keine Analyseergebnisse verfügbar'")
print("\nURSACHE:")
print("   st.session_state.analysis_results ist LEER oder NICHT VORHANDEN")

print("\n🔍 ROOT CAUSE:")
print("   1. Sie haben KEINE Berechnung im Solar Calculator durchgeführt")
print("   2. ODER: Sie haben die Berechnung durchgeführt, aber die Seite neu geladen")
print("   3. ODER: Es gab einen Fehler bei der Berechnung")

print("\n✅ LÖSUNG:")
print("   1. Gehen Sie zurück zum 'Solar Calculator' Tab")
print("   2. Führen Sie die Berechnung ERNEUT aus")
print("   3. Warten Sie bis 'Berechnung abgeschlossen' erscheint")
print("   4. Dann gehen Sie wieder zur PDF-UI")

print("\n" + "=" * 100)
print("PROBLEM 2: Nur PV-Module, keine Wechselrichter/Speicher")
print("=" * 100)

print("\n❌ SYMPTOM: Nur 2 Datenblätter (beide PV-Module)")
print("\nMÖGLICHE URSACHEN:")
print("   1. Im Solar Calculator wurden nur Module konfiguriert")
print("   2. Wechselrichter/Speicher sind NICHT ausgewählt")
print("   3. pv_details enthält keine Wechselrichter/Speicher IDs")

print("\n✅ LÖSUNG:")
print("   1. Gehen Sie zum 'Solar Calculator' Tab")
print("   2. Stellen Sie sicher dass folgendes konfiguriert ist:")
print("      ☑️  PV-Module")
print("      ☑️  Wechselrichter")
print("      ☑️  Speicher (falls gewünscht)")
print("      ☑️  Zubehör (Wallbox, EMS, etc.)")
print("   3. Führen Sie die Berechnung aus")
print("   4. Prüfen Sie ob 'project_data' alle IDs enthält")

print("\n" + "=" * 100)
print("KRITISCHER WORKFLOW")
print("=" * 100)

print("\n📋 RICHTIGE REIHENFOLGE:")
print("   1️⃣  Solar Calculator öffnen")
print("   2️⃣  Alle Komponenten konfigurieren:")
print("       • PV-Module auswählen")
print("       • Wechselrichter auswählen")
print("       • Speicher aktivieren + auswählen (optional)")
print("       • Wallbox/EMS/Zubehör auswählen (optional)")
print("   3️⃣  'Berechnung durchführen' klicken")
print("   4️⃣  Warten bis Ergebnisse angezeigt werden")
print("   5️⃣  Zur PDF-UI wechseln")
print("   6️⃣  'Zusätzliche Seiten anhängen' aktivieren")
print("   7️⃣  Charts auswählen (sollten jetzt verfügbar sein!)")
print("   8️⃣  PDF generieren")

print("\n" + "=" * 100)
print("SCHNELLTEST")
print("=" * 100)

print("\n🔍 Prüfen Sie in der Streamlit App:")
print("\n1. Sidebar → Welcher Tab ist aktiv?")
print("   ✅ Sollte 'Solar Calculator' oder 'Angebotsausgabe' sein")

print("\n2. Im Solar Calculator:")
print("   ✅ Sind ALLE Komponenten konfiguriert?")
print("   ✅ Wurde die Berechnung durchgeführt?")
print("   ✅ Werden Ergebnisse angezeigt (Kosten, Produktion, ROI)?")

print("\n3. In der PDF-UI:")
print("   ✅ Steht 'Keine Analyseergebnisse verfügbar'?")
print("   ✅ Wenn JA → Zurück zu Schritt 1!")

print("\n" + "=" * 100)
print("ERWARTETES VERHALTEN NACH FIX")
print("=" * 100)

print("\nWenn Sie die Berechnung korrekt durchgeführt haben:")
print("   ✅ Charts sind auswählbar (26 Diagramme in 6 Kategorien)")
print("   ✅ 3-5 Datenblätter (Module + Inverter + Speicher + Zubehör)")
print("   ✅ 6 Firmendokumente")
print("   ✅ PDF mit allen Inhalten")

print("\n" + "=" * 100)
print("WICHTIG")
print("=" * 100)

print("\n⚠️  STREAMLIT SESSION STATE IST FLÜCHTIG!")
print("   • Wenn Sie die Seite neu laden → Daten sind WEG")
print("   • Wenn Sie den Tab wechseln → Daten BLEIBEN (normalerweise)")
print("   • Wenn Sie einen Fehler bekommen → Daten können VERLOREN gehen")

print("\n✅ IMMER:")
print("   1. Solar Calculator Berechnung ZUERST")
print("   2. DANN zur PDF-UI wechseln")
print("   3. NICHT die Seite neu laden")

print("\n" + "=" * 100)
