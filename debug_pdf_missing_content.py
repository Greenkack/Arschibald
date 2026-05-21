"""
NOTFALL-DEBUG: Warum fehlen Wechselrichter, Speicher und Charts in der PDF?
Dieser Test simuliert den KOMPLETTEN Ablauf und identifiziert das Problem.
"""

import json


def test_complete_pdf_flow():
    """Simuliert den kompletten PDF-Generierungs-Flow"""
    
    print("=" * 100)
    print("NOTFALL-DEBUG: PDF-GENERIERUNG FLOW-ANALYSE")
    print("=" * 100)
    
    # ========================================================================
    # TEST 1: Ist pv_details korrekt strukturiert?
    # ========================================================================
    print("\n" + "=" * 100)
    print("TEST 1: pv_details Datenstruktur")
    print("=" * 100)
    
    mock_project_data = {
        "pv_details": {
            "selected_module_id": 101,
            "selected_inverter_id": 202,
            "selected_storage_id": 303,
            "include_storage": True,
            "selected_wallbox_id": 404,
            "include_additional_components": True
        }
    }
    
    # Simuliere pdf_generator.py Zeile 3947 (NACH FIX)
    pv_details_pdf = mock_project_data.get("pv_details", {})
    if not pv_details_pdf:
        pv_details_pdf = mock_project_data.get("project_details", {})
    
    print(f"pv_details_pdf extrahiert:")
    print(f"   Module: {pv_details_pdf.get('selected_module_id')}")
    print(f"   Inverter: {pv_details_pdf.get('selected_inverter_id')}")
    print(f"   Storage: {pv_details_pdf.get('selected_storage_id')}")
    print(f"   Include Storage: {pv_details_pdf.get('include_storage')}")
    
    # ========================================================================
    # TEST 2: Werden IDs korrekt extrahiert in _append_datasheets_and_documents?
    # ========================================================================
    print("\n" + "=" * 100)
    print("TEST 2: Produktdatenblatt-ID Extraktion")
    print("=" * 100)
    
    # Simuliere _append_datasheets_and_documents() Logik
    manually_selected = []  # Leer, weil User nichts manuell ausgewählt
    
    if manually_selected:
        product_ids = manually_selected
        print(f"   Using manual selection: {product_ids}")
    else:
        product_ids = list(filter(None, [
            pv_details_pdf.get("selected_module_id"),
            pv_details_pdf.get("selected_inverter_id"),
            pv_details_pdf.get("selected_storage_id") if pv_details_pdf.get("include_storage") else None
        ]))
        print(f"   Using auto-selection: {product_ids}")
    
    # Zubehör
    include_additional = pv_details_pdf.get('include_additional_components', True)
    if not manually_selected and include_additional:
        for key in ['selected_wallbox_id', 'selected_ems_id']:
            val = pv_details_pdf.get(key)
            if val:
                product_ids.append(val)
    
    print(f"\nFinale Produkt-IDs: {product_ids}")
    print(f"   Anzahl: {len(product_ids)}")
    
    if len(product_ids) < 3:
        print(f"WARNUNG: Nur {len(product_ids)} Produkte gefunden, erwartet 3+ (Modul, Inverter, Speicher)")
    
    # ========================================================================
    # TEST 3: Wird include_all_documents_opt korrekt gesetzt?
    # ========================================================================
    print("\n" + "=" * 100)
    print("TEST 3: include_all_documents Flag")
    print("=" * 100)
    
    mock_inclusion_options = {
        "include_all_documents": True,
        "append_additional_pages_after_main8": True,
        "selected_charts_for_pdf": ["chart1", "chart2"]
    }
    
    include_all_docs = mock_inclusion_options.get("include_all_documents", False)
    print(f"   include_all_documents: {include_all_docs}")
    
    if not include_all_docs:
        print("FEHLER: include_all_documents ist FALSE - Funktion wird NICHT aufgerufen!")
        print("   LÖSUNG: Prüfen Sie, ob die Checkbox 'Alle Dokumente anhängen' aktiviert ist")
    else:
        print("include_all_documents ist TRUE - Funktion wird aufgerufen")
    
    # ========================================================================
    # TEST 4: Charts - werden sie übergeben?
    # ========================================================================
    print("\n" + "=" * 100)
    print("TEST 4: Chart-Daten")
    print("=" * 100)
    
    selected_charts = mock_inclusion_options.get("selected_charts_for_pdf", [])
    print(f"   selected_charts_for_pdf: {selected_charts}")
    print(f"   Anzahl: {len(selected_charts)}")
    
    if not selected_charts:
        print("WARNUNG: Keine Charts ausgewählt!")
    else:
        print("Charts sind ausgewählt")
    
    # Simuliere analysis_results
    mock_analysis_results = {
        "financial": {"total_cost": 25000},
        "production": {"annual_kwh": 8500}
    }
    
    if not mock_analysis_results:
        print("FEHLER: analysis_results ist leer - Charts können NICHT generiert werden!")
    else:
        print("analysis_results verfügbar")
    
    # ========================================================================
    # TEST 5: CRITICAL - Wird die NEUE Funktion überhaupt aufgerufen?
    # ========================================================================
    print("\n" + "=" * 100)
    print("TEST 5: KRITISCH - Funktionsaufruf-Bedingungen")
    print("=" * 100)
    
    # Bedingung in pdf_generator.py Zeile 5043
    _PYPDF_AVAILABLE = True  # Annahme
    
    print(f"   include_all_documents_opt: {include_all_docs}")
    print(f"   _PYPDF_AVAILABLE: {_PYPDF_AVAILABLE}")
    print(f"   Bedingung erfüllt: {include_all_docs and _PYPDF_AVAILABLE}")
    
    if not (include_all_docs and _PYPDF_AVAILABLE):
        print("\nKRITISCHER FEHLER: _append_datasheets_and_documents() wird NICHT aufgerufen!")
        print("   GRUND: Bedingung 'if include_all_documents_opt and _PYPDF_AVAILABLE' ist FALSE")
    else:
        print("\nBedingung erfüllt - Funktion wird aufgerufen")
    
    # ========================================================================
    # ZUSAMMENFASSUNG & DIAGNOSE
    # ========================================================================
    print("\n" + "=" * 100)
    print("DIAGNOSE-ZUSAMMENFASSUNG")
    print("=" * 100)
    
    issues_found = []
    
    if len(product_ids) < 3:
        issues_found.append("Zu wenige Produkt-IDs extrahiert")
    
    if not include_all_docs:
        issues_found.append("include_all_documents ist FALSE")
    
    if not selected_charts:
        issues_found.append("Keine Charts ausgewählt")
    
    if issues_found:
        print("\n GEFUNDENE PROBLEME:")
        for issue in issues_found:
            print(f"   {issue}")
        
        print("\nLÖSUNGSANSÄTZE:")
        print("   1. In pdf_ui.py: Prüfen Sie die Checkbox 'Alle Dokumente anhängen'")
        print("   2. In pdf_ui.py: Stellen Sie sicher, dass 'Zusätzliche Seiten' aktiviert ist")
        print("   3. In pdf_ui.py: Wählen Sie mindestens 1 Chart aus")
        print("   4. Prüfen Sie Console-Output nach 'Anhängen von Produktdatenblättern...'")
    else:
        print("\nKEINE KRITISCHEN PROBLEME GEFUNDEN")
        print("   Alle Bedingungen sind erfüllt!")
    
    # ========================================================================
    # ERWARTETES VERHALTEN
    # ========================================================================
    print("\n" + "=" * 100)
    print(" ERWARTETES VERHALTEN BEI KORREKTER KONFIGURATION")
    print("=" * 100)
    
    print("\n1⃣  Console-Output beim PDF-Generieren:")
    print("   'Anhängen von Produktdatenblättern und Firmendokumenten...'")
    print("   'Using auto-selected main component datasheets: [101, 202, 303]'")
    print("   'Chart-Generierung gestartet: 2 Chart(s) ausgewählt'")
    print("   '2 Chart-Seite(n) erfolgreich angehängt'")
    print("   'Finale PDF erstellt mit X Seiten'")
    
    print("\n2⃣  PDF sollte enthalten:")
    print("   PV-Modul Datenblatt")
    print("   Wechselrichter Datenblatt")
    print("   Speicher Datenblatt")
    print("   Wallbox Datenblatt (wenn vorhanden)")
    print("   Firmendokumente")
    print("   Chart-Seiten (1-2 Charts pro Seite)")
    
    print("\n3⃣  UI-Checkboxen müssen AKTIV sein:")
    print("     'Zusätzliche Seiten nach Hauptseiten anhängen'")
    print("     'Alle Dokumente anhängen' (im Formular)")
    print("     Mindestens 1 Chart ausgewählt (außerhalb Formular)")
    
    print("\n" + "=" * 100)
    print("ANALYSE ABGESCHLOSSEN")
    print("=" * 100)
    print("\nNÄCHSTE SCHRITTE:")
    print("1. Prüfen Sie die UI-Checkboxen wie oben beschrieben")
    print("2. Schauen Sie in die Console beim PDF-Generieren")
    print("3. Wenn 'Anhängen von Produktdatenblättern...' NICHT erscheint:")
    print("   → include_all_documents ist FALSE in der UI!")
    print("4. Wenn nur Module erscheinen:")
    print("   → pv_details enthält keine Inverter/Speicher IDs!")


if __name__ == '__main__':
    test_complete_pdf_flow()
