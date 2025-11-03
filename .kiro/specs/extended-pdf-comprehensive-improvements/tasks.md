# Implementation Plan

- [x] 1. Transparente Diagramm-Hintergründe implementieren

  - Alle Matplotlib-Diagramme mit transparenten Hintergründen versehen
  - Alle Plotly-Diagramme mit transparenten Hintergründen versehen
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12_

- [x] 1.1 Transparente Hintergründe in calculations.py implementieren

  - `fig.patch.set_alpha(0)` und `ax.patch.set_alpha(0)` zu allen Chart-Funktionen hinzufügen
  - `plt.savefig()` mit `facecolor='none', edgecolor='none', transparent=True` aktualisieren
  - Legenden-Hintergründe transparent machen
  - Gitternetz-Transparenz auf 0.3 setzen
  - Betroffene Funktionen: generate_monthly_production_consumption_chart, generate_cost_projection_chart, generate_cumulative_cashflow_chart, generate_roi_chart, generate_energy_balance_chart, generate_monthly_savings_chart, generate_yearly_comparison_chart, generate_amortization_chart, generate_co2_savings_chart, generate_financing_comparison_chart
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.10, 1.11, 1.12_

- [x] 1.2 Transparente Hintergründe in calculations_extended.py implementieren

  - `fig.patch.set_alpha(0)` und `ax.patch.set_alpha(0)` zu allen Chart-Funktionen hinzufügen
  - `plt.savefig()` mit `facecolor='none', edgecolor='none', transparent=True` aktualisieren
  - Betroffene Funktionen: generate_scenario_comparison_chart, generate_tariff_comparison_chart, generate_income_projection_chart, generate_battery_usage_chart, generate_grid_interaction_chart
  - _Requirements: 1.1, 1.2, 1.4, 1.6_

- [x] 1.3 Transparente Hintergründe in analysis.py implementieren

  - Plotly `fig.update_layout()` mit `paper_bgcolor='rgba(0,0,0,0)'` und `plot_bgcolor='rgba(0,0,0,0)'` aktualisieren
  - Legenden und Gitternetz transparent machen
  - Betroffene Funktionen: generate_advanced_analysis_chart, generate_sensitivity_analysis_chart, generate_optimization_chart
  - _Requirements: 1.3, 1.4, 1.7_

- [x] 1.4 Transparente Hintergründe in doc_output.py implementieren

  - `fig.patch.set_alpha(0)` und `ax.patch.set_alpha(0)` zu allen Chart-Funktionen hinzufügen
  - `plt.savefig()` mit transparenten Parametern aktualisieren
  - Betroffene Funktionen: generate_summary_chart, generate_comparison_chart
  - _Requirements: 1.1, 1.2, 1.4, 1.8_

- [x] 1.5 Unit Tests für transparente Hintergründe schreiben

  - Test für Matplotlib-Diagramme: PNG-Bytes auf Alpha-Kanal prüfen
  - Test für Plotly-Diagramme: Layout-Konfiguration prüfen
  - Test für alle Chart-Funktionen in calculations.py, calculations_extended.py, analysis.py, doc_output.py
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.9_

- [x] 2. 3D zu 2D Konvertierung durchführen

  - Alle 3D-Diagramme identifizieren und in 2D konvertieren
  - Dritte Dimension durch Farb-Kodierung oder Gruppierung darstellen
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13_

- [x] 2.1 3D zu 2D Konvertierung in calculations_extended.py

  - `from mpl_toolkits.mplot3d import Axes3D` Imports entfernen
  - `projection='3d'` aus allen add_subplot() entfernen
  - generate_scenario_comparison_chart: 3D Bar Chart → 2D Grouped Bar Chart
  - generate_tariff_comparison_chart: 3D Bar Chart → 2D Grouped Bar Chart
  - generate_income_projection_chart: 3D Line Plot → 2D Multi-Line Chart
  - Werte über Balken mit ax.text() anzeigen
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 2.10, 2.11_

- [x] 2.2 3D zu 2D Konvertierung in analysis.py

  - generate_sensitivity_analysis_chart: 3D Surface Plot → 2D Heatmap mit Contour-Linien
  - generate_optimization_chart: 3D Scatter Plot → 2D Scatter Plot mit Farb-Kodierung
  - `ax.plot_surface()` durch `ax.imshow()` oder `ax.contourf()` ersetzen
  - `ax.scatter3D()` durch `ax.scatter()` mit Farb-Kodierung ersetzen
  - Colorbar für dritte Dimension hinzufügen
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6, 2.8, 2.10, 2.11_

- [x] 2.3 Verifizierung der 2D Konvertierung

  - Sicherstellen dass keine `mpl_toolkits.mplot3d` Imports mehr existieren
  - Alle konvertierten Diagramme mit transparenten Hintergründen versehen
  - Datenintegrität nach Konvertierung prüfen
  - _Requirements: 2.9, 2.10, 2.12, 2.13_

- [x] 2.4 Unit Tests für 2D Konvertierung schreiben

  - Test dass keine 3D-Imports mehr existieren
  - Test dass alle Diagramme 2D sind
  - Visuelle Vergleichstests zwischen 3D und 2D Versionen
  - _Requirements: 2.12, 2.13_

- [x] 3. Diagrammauswahl in PDF UI implementieren

  - Vollständiges Mapping aller verfügbaren Diagramme erstellen
  - Kategorisierung der Diagramme implementieren
  - Session State Management für Auswahl
  - Dynamische Verfügbarkeits-Prüfung
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, 3.15, 3.16, 3.17, 3.18, 3.19, 3.20_

- [x] 3.1 Chart-Konfiguration in pdf_ui.py erstellen

  - CHART_KEY_TO_FRIENDLY_NAME_MAP Dictionary mit allen Diagrammen erstellen
  - CHART_CATEGORIES Dictionary für Kategorisierung erstellen
  - Kategorien: Finanzierung, Energie, Vergleiche, Umwelt, Analyse, Zusammenfassung
  - Alle Diagramme aus calculations.py, calculations_extended.py, analysis.py, doc_output.py einbeziehen
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.17_

- [x] 3.2 Verfügbarkeits-Prüfung implementieren

  - check_chart_availability() Funktion erstellen
  - Basis-Diagramme sind immer verfügbar
  - Finanzierungs-Diagramme benötigen include_financing Flag
  - Batterie-Diagramme benötigen selected_storage_id
  - Szenario-Diagramme benötigen mehrere Szenarien
  - Analyse-Diagramme benötigen include_advanced_analysis Flag
  - _Requirements: 3.8, 3.12_

- [x] 3.3 Diagrammauswahl-UI rendern

  - render_chart_selection_ui() Funktion erstellen
  - st.multiselect Widget mit kategorisierten Diagrammen
  - Statistiken anzeigen: Verfügbare, Nicht verfügbare, Ausgewählte
  - "Alle auswählen" und "Keine auswählen" Buttons
  - Nicht verfügbare Diagramme als deaktiviert markieren
  - _Requirements: 3.6, 3.7, 3.9, 3.12, 3.18, 3.19_

- [x] 3.4 Session State Management implementieren

  - Auswahl in st.session_state['selected_charts_for_pdf'] speichern
  - Auswahl für zukünftige Sessions persistieren
  - Warnung anzeigen wenn keine Diagramme ausgewählt
  - Geschätzte PDF-Größe basierend auf Auswahl berechnen und anzeigen
  - _Requirements: 3.7, 3.8, 3.9, 3.15, 3.20_

- [x] 3.5 Diagramm-Generierung mit Auswahl verknüpfen

  - Nur ausgewählte Diagramme generieren
  - Dynamische Werte aus project_data und pv_details verwenden
  - Generierte PDF-Bytes aus Session State verwenden
  - Fehlerbehandlung für nicht verfügbare Diagramme
  - _Requirements: 3.9, 3.10, 3.11, 3.13_

- [x] 3.6 Vorschau-Funktionalität implementieren

  - Thumbnail-Generierung für jedes Diagramm
  - Vorschau in UI anzeigen
  - _Requirements: 3.14_

- [x] 3.7 Unit Tests für Diagrammauswahl schreiben

  - Test für check_chart_availability()
  - Test für Session State Management
  - Test dass nur ausgewählte Diagramme generiert werden
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.16_
-

- [x] 4. Diagramm-Darstellung verbessern

  - Dickere Balken und Donuts
  - Größere Schriftarten
  - Beschreibungen unter jedem Diagramm
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 4.15, 4.16, 4.17, 4.18, 4.19, 4.20_

- [x] 4.1 Diagramm-Styling in allen Modulen verbessern

  - Balkendiagramme: width=0.6 oder größer
  - Donut-Diagramme: wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}
  - Liniendiagramme: linewidth=2.5 oder größer
  - Scatter-Plots: s=100 oder größer für Marker
  - Achsenbeschriftungen: fontsize=12 oder größer
  - Titel: fontsize=14 oder größer, fontweight='bold'
  - Legende: fontsize=10 oder größer
  - Tick-Labels: fontsize=10 oder größer
  - Alle Module: calculations.py, calculations_extended.py, analysis.py, doc_output.py
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

- [x] 4.2 Farben und Gitternetz optimieren

  - Kontrastreiche, professionelle Farben verwenden
  - Gitternetz mit alpha=0.3 für subtile Linien
  - Daten-Labels mit fontsize=9 oder größer
  - Balkendiagramme: Werte über Balken mit ha='center', va='bottom'
  - Pie-Charts: autopct='%1.1f%%' mit fontsize=10
  - _Requirements: 4.14, 4.15, 4.16, 4.17, 4.18_

- [x] 4.3 Hohe Auflösung und optimale Dimensionen
  - dpi=300 für alle Diagramme
  - Optimale Dimensionen: 14cm x 10cm
  - _Requirements: 4.19, 4.20_

- [x] 4.4 Beschreibungen für Diagramme generieren

  - Funktion generate_chart_description() erstellen
  - Beschreibung enthält: Diagrammtyp, Zweck, Haupterkenntnisse
  - Gleiche numerische Werte wie im Diagramm verwenden
  - Formatierung mit styles['BodyText']
  - Strukturierte Darstellung bei mehreren Werten
  - Beschreibung als Paragraph unter Diagramm in PDF einfügen
  - _Requirements: 4.9, 4.10, 4.11, 4.12, 4.13_

- [x] 4.5 Unit Tests für Diagramm-Darstellung schreiben

  - Test für Balkenbreite, Liniendicke, Schriftgrößen
  - Test für Beschreibungs-Generierung
  - Test für dpi und Dimensionen
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.19, 4.20_

- [x] 5. Produktdatenblätter in PDF einbinden

  - Datenblätter aus Produktdatenbank laden und anhängen
  - Fehlerbehandlung für fehlende oder ungültige Datenblätter
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 5.17, 5.18, 5.19, 5.20, 5.21, 5.22, 5.23, 5.24, 5.25_

- [x] 5.1 _append_datasheets_and_documents() Funktion erstellen

  - Funktion in pdf_generator.py implementieren
  - PdfWriter und PdfReader aus pypdf verwenden
  - Basis-Pfad PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN verwenden
  - Logik aus repair_pdf/pdf_generator.py Zeilen 4930-4970 übernehmen
  - _Requirements: 5.15, 5.16, 5.17, 5.25_

- [x] 5.2 Produktdatenblätter für alle Komponenten laden

  - PV-Module: get_product_by_id_func für selected_module_id aufrufen
  - Wechselrichter: get_product_by_id_func für selected_inverter_id aufrufen
  - Speicher: get_product_by_id_func für selected_storage_id aufrufen
  - Wallbox: get_product_by_id_func für selected_wallbox_id aufrufen
  - EMS: get_product_by_id_func für selected_ems_id aufrufen
  - Optimizer: get_product_by_id_func für selected_optimizer_id aufrufen
  - Carport: get_product_by_id_func für selected_carport_id aufrufen
  - Notstrom: get_product_by_id_func für selected_emergency_power_id aufrufen
  - Tierabwehr: get_product_by_id_func für selected_animal_defense_id aufrufen
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.21_

- [x] 5.3 Zubehör-Datenblätter laden

  - Wenn include_additional_components True: Alle Zubehör-Datenblätter einschließen
  - Wenn include_additional_components False: Nur Hauptkomponenten
  - _Requirements: 5.10, 5.11_

- [x] 5.4 Datenblätter anhängen mit Fehlerbehandlung

  - Für jedes Produkt: Datenblatt-Pfad aus Produktdaten extrahieren
  - Relativen Pfad mit Basis-Pfad kombinieren
  - Prüfen ob Pfad existiert und lesbar ist
  - PDF-Datenblätter direkt anhängen
  - Andere Formate konvertieren oder überspringen
  - Fehler loggen und fortfahren bei Problemen
  - Mehrere Datenblätter pro Produkt unterstützen
  - Reihenfolge beibehalten: Module, Wechselrichter, Speicher, Zubehör
  - _Requirements: 5.12, 5.13, 5.14, 5.18, 5.19, 5.22, 5.23, 5.24_

- [x] 5.5 Finale PDF mit Datenblättern zurückgeben

  - Alle Seiten in PdfWriter zusammenführen
  - Als Bytes zurückgeben
  - _Requirements: 5.20_

- [ ]* 5.6 Unit Tests für Produktdatenblätter schreiben
  - Test für _append_datasheets_and_documents()
  - Test für alle Produkttypen
  - Test für Fehlerbehandlung bei fehlenden Datenblättern
  - Test für include_additional_components Flag
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.10, 5.11, 5.12, 5.13, 5.14_
- [x] 6. Firmendokumente in PDF einbinden

  - Firmenspezifische Dokumente aus Firmendatenbank laden und anhängen
  - Fehlerbehandlung für fehlende oder ungültige Dokumente
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13, 6.14, 6.15, 6.16, 6.17, 6.18, 6.19, 6.20_

- [x] 6.1 Firmendokumente laden

  - active_company_id aus project_data extrahieren
  - db_list_company_documents_func(active_company_id, None) aufrufen
  - company_document_ids_to_include aus inclusion_options verwenden
  - Nur Dokumente mit IDs in company_document_ids_to_include filtern
  - Wenn company_document_ids_to_include leer: Keine Firmendokumente anhängen
  - Wenn keine active_company_id: Keine Firmendokumente anhängen
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.14_

- [x] 6.2 Firmendokumente anhängen

  - Relativen Pfad mit COMPANY_DOCS_BASE_DIR_PDF_GEN kombinieren
  - Prüfen ob Pfad existiert
  - PDF-Dokumente direkt anhängen mit PdfWriter und PdfReader
  - Andere Formate konvertieren oder überspringen
  - Mehrere Seiten pro Dokument unterstützen
  - Alle Dokumente in Reihenfolge der IDs anhängen
  - Verschlüsselte Dokumente entschlüsseln oder überspringen
  - Fehler loggen und fortfahren
  - _Requirements: 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.16, 6.19, 6.20_

- [x] 6.3 Reihenfolge und Integration

  - Produktdatenblätter zuerst anhängen
  - Dann Firmendokumente anhängen
  - Finale PDF als Bytes zurückgeben
  - Logik aus repair_pdf/pdf_generator.py Zeilen 4980-5000 verwenden
  - _Requirements: 6.13, 6.15, 6.17, 6.18_

- [ ]* 6.4 Unit Tests für Firmendokumente schreiben
  - Test für Laden von Firmendokumenten
  - Test für Filterung nach IDs
  - Test für Fehlerbehandlung
  - Test für Reihenfolge
  --_Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8,
 6.9_

- [x] 7. Seitenschutz für erweiterte Seiten implementieren

  - KeepTogether für Diagramme und Beschreibungen
  - Automatische PageBreaks bei Platzmangel
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15, 7.16, 7.17, 7.18, 7.19, 7.20_

- [x] 7.1 KeepTogether für Diagramme implementieren

  - Diagramm, Überschrift und Beschreibung mit KeepTogether gruppieren
  - Tabellen mit Überschrift mit KeepTogether gruppieren
  - Finanzierungspläne (Überschrift, Tabelle, Beschreibung) mit KeepTogether gruppieren
  - Diagramme mit Legenden zusammenhalten
  - Diagramme mit Fußnoten zusammenhalten
  - KeepTogether aus reportlab.platypus verwenden
  - _Requirements: 7.1, 7.6, 7.7, 7.10, 7.18, 7.20_

- [x] 7.2 Automatische PageBreaks bei Platzmangel

  - Verfügbare Höhe mit doc.height berechnen
  - Wenn nicht genug Platz für Gruppe: PageBreak einfügen
  - Mindestens 3cm Platz am Seitenende reservieren
  - Überschriften am Seitenende auf nächste Seite verschieben
  - Absätze nach Diagrammen auf Platz prüfen
  - _Requirements: 7.2, 7.5, 7.11, 7.12, 7.13, 7.14, 7.19_

- [x] 7.3 Seitenschutz nur für Seiten 9+ anwenden

  - Seiten 1-8 (Standard-PDF): Kein Seitenschutz
  - Seiten ab 9 (erweiterte PDF): Seitenschutz für alle Diagramme und Tabellen
  - Besonders strikt für Finanzierungsinformationen
  - _Requirements: 7.3, 7.4, 7.16_

- [x] 7.4 Spezialfälle behandeln

  - Wenn KeepTogether-Element zu groß für eine Seite: Auf mehrere Seiten aufteilen
  - Mehrere Diagramme nacheinander: Angemessenen Abstand lassen
  - Alle Verschiebungen im Log dokumentieren
  - _Requirements: 7.8, 7.9, 7.15, 7.17_

- [ ]* 7.5 Unit Tests für Seitenschutz schreiben
  - Test dass Diagramme und Beschreibungen zusammenbleiben
  - Test für automatische PageBreaks
  - Test dass Seitenschutz nur ab Seite 9 gilt
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8. Kopf- und Fußzeilen für erweiterte Seiten implementieren

  - Dreieck rechts oben, Logo links oben
  - Blauer Balken in Fußzeile
  - Kundenname, Angebotsdatum, Seitenzahlen
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11, 8.12, 8.13, 8.14, 8.15, 8.16, 8.17, 8.18, 8.19, 8.20, 8.21, 8.22, 8.23, 8.24, 8.25, 8.26, 8.27, 8.28, 8.29, 8.30_

- [-] 8.1 page_layout_handler() Funktion erstellen

  - Funktion in pdf_generator.py implementieren
  - canvas_obj.saveState() und canvas_obj.restoreState() verwenden
  - Alle Parameter aus layout_callback_kwargs_build verwenden
  - Logik aus repair_pdf/pdf_generator.py Zeilen 103-428 übernehmen
  - _Requirements: 8.22, 8.23, 8.24, 8.26_

- [ ] 8.2 Kopfzeile für Seiten 9+ implementieren
  - Dreieck rechts oben: Größe 20x20 Punkte, Farbe RGB(0, 0.33, 0.64)
  - Position: Rechtes oberes Eck
  - Firmenlogo links oben: Breite 40, Höhe 20 Punkte
  - company_logo_base64_ref dekodieren und als ImageReader verwenden
  - Wenn Logo nicht verfügbar: Schritt überspringen
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ] 8.3 Fußzeile für Seiten 9+ implementieren
  - Blauer Balken: Höhe 5 Punkte, Farbe RGB(0, 0.33, 0.64), über gesamte Dokumentbreite
  - Kundenname links unten: customer_name_ref, Schriftart "Helvetica", Größe 8
  - "Angebot [Datum]" mittig unten: Format "dd.mm.yyyy", datetime.now().strftime("%d.%m.%Y")
  - "Seite X von XX" rechts unten: canvas_obj.getPageNumber() für aktuelle Seite, Gesamtseitenzahl dynamisch berechnen
  - Schriftart "Helvetica", Größe 8 für alle Texte
  - Wenn Kundenname nicht verfügbar: Schritt überspringen
  - _Requirements: 8.8, 8.9, 8.10, 8.11, 8.12, 8.13, 8.14, 8.15, 8.16, 8.17, 8.18, 8.19, 8.20, 8.21_

- [ ] 8.4 PageNumCanvas und Integration
  - PageNumCanvas mit onPage_callback=page_layout_handler verwenden
  - callback_kwargs=layout_callback_kwargs_build übergeben
  - Ränder respektieren: margin_left_ref, margin_right_ref, margin_top_ref, margin_bottom_ref
  - Keine Überlappung mit Hauptinhalt
  - Seiten 1-8: Standard-Kopf-/Fußzeilen verwenden
  - _Requirements: 8.25, 8.27, 8.28, 8.29, 8.30_

- [ ]* 8.5 Unit Tests für Kopf-/Fußzeilen schreiben
  - Test für Dreieck-Position und -Farbe
  - Test für Logo-Position und -Größe
  - Test für Fußzeilen-Elemente
  - Test für Seitenzahlen
  - Test dass nur Seiten 9+ betroffen sind
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.8, 8.9, 8.18, 8.19, 8.20, 8.25_

- [x] 9. Finanzierungsinformationen priorisieren

  - Vollständige Finanzierungsinformationen ab Seite 9
  - Kredit, Leasing, Amortisationspläne mit dynamischen Berechnungen
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10, 9.11, 9.12, 9.13, 9.14, 9.15, 9.16, 9.17, 9.18, 9.19, 9.20, 9.21, 9.22, 9.23, 9.24, 9.25, 9.26, 9.27, 9.28, 9.29, 9.30_

- [x] 9.1 Finanzierungsabschnitt ab Seite 9 einfügen

  - Nach Seite 8: PageBreak einfügen
  - Überschrift "Finanzierungsinformationen" als erstes auf Seite 9
  - final_end_preis aus project_data['pv_details'] verwenden
  - Wenn final_end_preis nicht verfügbar: Fehler loggen und 0 verwenden
  - Wenn inclusion_options['include_financing_details'] False: Abschnitt überspringen
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.28_

- [x] 9.2 Kreditfinanzierung berechnen und darstellen

  - calculate_annuity() aus financial_tools verwenden
  - Parameter: principal=final_end_preis, interest_rate aus global_constants, years aus global_constants oder Benutzerauswahl
  - Tabelle erstellen mit: Kreditbetrag, Zinssatz, Laufzeit, monatliche Rate, Gesamtkosten
  - Table mit colWidths=[8*cm, 6*cm] verwenden
  - Blauer Header mit weißem Text
  - Gitternetzlinien mit colors.grey
  - Alle Werte mit 2 Dezimalstellen und Tausendertrennzeichen formatieren
  - _Requirements: 9.5, 9.6, 9.7, 9.8, 9.9, 9.10, 9.11, 9.12, 9.29_

- [x] 9.3 Leasingfinanzierung berechnen und darstellen

  - calculate_leasing_costs() aus financial_tools verwenden
  - Parameter: asset_value=final_end_preis, residual_value_percent aus global_constants
  - Tabelle erstellen mit: Leasingbetrag, Zinssatz, Laufzeit, monatliche Rate, Restwert
  - Gleiches Styling wie Kredittabelle
  - _Requirements: 9.13, 9.14, 9.15, 9.16, 9.17_

- [x] 9.4 Amortisationsplan erstellen

  - Jährliche Werte für 20-25 Jahre berechnen
  - Spalten: Jahr, Einsparungen, Kosten, Netto-Cashflow, kumulierter Cashflow
  - Amortisationszeit hervorheben
  - Table mit angemessenen Spaltenbreiten verwenden
  - _Requirements: 9.18, 9.19, 9.20, 9.21_

- [x] 9.5 Finanzierungsvergleich erstellen

  - Barkauf, Kredit und Leasing vergleichen
  - Gesamtkosten, monatliche Belastung und ROI vergleichen
  - Empfehlung basierend auf Daten geben
  - _Requirements: 9.22, 9.23, 9.24_

- [x] 9.6 Finanzierungsdiagramme einfügen

  - Nach Tabellen: Finanzierungsdiagramme einfügen (falls ausgewählt)
  - Mehrere Seiten für Finanzierungsinformationen erlauben
  - Spacer vor nächstem Abschnitt einfügen
  - _Requirements: 9.25, 9.26, 9.27_

- [ ]* 9.7 Unit Tests für Finanzierungsinformationen schreiben
  - Test für Kreditberechnung
  - Test für Leasingberechnung
  - Test für Amortisationsplan
  - Test für Finanzierungsvergleich
  - Test dass Finanzierungen ab Seite 9 erscheinen
  - Test für Fehlerbehandlung
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.28, 9.29, 9.30_
- [x] 10. Logik aus repair_pdf extrahieren und integrieren

- [ ] 10. Logik aus repair_pdf extrahieren und integrieren

  - Systematische Extraktion aller funktionierenden Logiken
  - Vollständige Integration in aktuellen Code
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 10.12, 10.13, 10.14, 10.15, 10.16, 10.17, 10.18, 10.19, 10.20, 10.21, 10.22, 10.23, 10.24, 10.25, 10.26, 10.27, 10.28, 10.29, 10.30, 10.31_

- [x] 10.1 repair_pdf Dateien analysieren

  - repair_pdf/pdf_generator.py analysieren und relevante Funktionen identifizieren
  - repair_pdf/pdf_ui.py analysieren
  - repair_pdf/pdf_styles.py analysieren
  - repair_pdf/calculations.py analysieren
  - repair_pdf/calculations_extended.py analysieren
  - repair_pdf/analysis.py analysieren
  - repair_pdf/doc_output.py analysieren
  - Integrations-Checkliste erstellen
  - _Requirements: 10.1, 10.11, 10.14, 10.18, 10.19_

- [x] 10.2 page_layout_handler() aus repair_pdf extrahieren

  - Zeilen 103-428 aus repair_pdf/pdf_generator.py extrahieren
  - In aktuellen pdf_generator.py integrieren
  - Alle Imports aktualisieren
  - Funktionsaufrufe aktualisieren
  - Variablennamen konsistent halten
  - _Requirements: 10.2, 10.20, 10.21, 10.22, 10.23, 10.24_

- [x] 10.3 _append_datasheets_and_documents() aus repair_pdf extrahieren

  - Zeilen 4930-5050 aus repair_pdf/pdf_generator.py extrahieren
  - In aktuellen pdf_generator.py integrieren
  - Alle Imports aktualisieren
  - _Requirements: 10.3, 10.20, 10.21, 10.22, 10.23, 10.24_

- [x] 10.4 PageNumCanvas und _header_footer() aus repair_pdf extrahieren

  - Zeilen 2660-2663 aus repair_pdf/pdf_generator.py extrahieren
  - _header_footer() Funktion extrahieren
  - In aktuellen pdf_generator.py integrieren
  - _Requirements: 10.4, 10.5_

- [x] 10.5 UI-Komponenten aus repair_pdf extrahieren

  - chart_key_to_friendly_name_map aus repair_pdf/pdf_ui.py Zeilen 262-265 extrahieren
  - Diagrammauswahl-UI extrahieren
  - Session State Management extrahieren
  - In aktuellen pdf_ui.py integrieren
  - _Requirements: 10.6, 10.7, 10.8_

- [x] 10.6 Style-Definitionen aus repair_pdf extrahieren

  - Transparente Hintergrund-Logik aus repair_pdf/pdf_styles.py Zeilen 373-376 extrahieren
  - Style-Definitionen extrahieren
  - In aktuellen pdf_styles.py integrieren
  - _Requirements: 10.9, 10.10_

- [x] 10.7 Chart-Funktionen aus repair_pdf extrahieren

  - Transparente Hintergründe aus repair_pdf/calculations.py extrahieren und integrieren
  - 2D-Diagramme aus repair_pdf/calculations.py extrahieren und integrieren
  - Erweiterte Berechnungen aus repair_pdf/calculations_extended.py extrahieren und integrieren
  - Plotly-Diagramme mit transparenten Hintergründen aus repair_pdf/analysis.py Zeilen 2006-2010 extrahieren
  - Dokumenten-Ausgabe-Funktionen aus repair_pdf/doc_output.py extrahieren
  - _Requirements: 10.11, 10.12, 10.13, 10.14, 10.15, 10.16, 10.17, 10.18_

- [x] 10.8 Konflikte identifizieren und auflösen

  - Bestehenden Code nicht überschreiben sondern erweitern
  - Konflikte zwischen repair_pdf und aktuellem Code identifizieren
  - Konflikte auflösen durch Merge oder Refactoring
  - _Requirements: 10.20, 10.21_

- [x] 10.9 Integration validieren

  - Alle Imports prüfen und aktualisieren
  - Alle Funktionsaufrufe prüfen und aktualisieren
  - Alle Variablennamen konsistent halten
  - Dokumentation der Änderungen erstellen
  - _Requirements: 10.22, 10.23, 10.24, 10.29_

- [ ]* 10.10 Unit Tests für integrierte Logiken schreiben
  - Unit Tests für jede integrierte Funktion
  - Integration Tests für Gesamtsystem
  - Alle Anforderungen 1-9 in Tests abdecken
  - Detaillierte Fehlermeldungen bei Test-Fehlschlägen

  - _Requirements: 10.25, 10.26, 10.27, 10.28_

- [x] 10.11 Vollständige Validierung durchführen

  - Vollständige PDF mit allen Features generieren
  - Alle Punkte 1-10 vollständig und funktionsfähig validieren
  - Alle Requirements erfüllt prüfen
  - _Requirements: 10.30, 10.31_

- [ ] 11. Integration Tests und Validierung
  - End-to-End Tests für vollständige PDF-Generierung
  - Validierung aller 10 Verbesserungsbereiche
  - _Requirements: Alle Requirements 1.1-10.31_

- [ ]* 11.1 Integration Test: Vollständige PDF-Generierung
  - Test mit allen Features aktiviert
  - Test mit minimalen Features
  - Test mit verschiedenen Kombinationen von Optionen
  - Verifizieren dass PDF korrekt generiert wird

- [ ]* 11.2 Integration Test: Diagramme
  - Verifizieren dass alle Diagramme transparente Hintergründe haben
  - Verifizieren dass keine 3D-Diagramme existieren
  - Verifizieren dass nur ausgewählte Diagramme in PDF erscheinen
  - Verifizieren dass Diagramme mit Beschreibungen zusammenbleiben

- [ ]* 11.3 Integration Test: Dokumente
  - Verifizieren dass alle Produktdatenblätter angehängt werden
  - Verifizieren dass alle Firmendokumente angehängt werden
  - Verifizieren dass Reihenfolge korrekt ist

- [ ]* 11.4 Integration Test: Layout
  - Verifizieren dass Kopf-/Fußzeilen auf Seiten 9+ korrekt sind
  - Verifizieren dass Seitenschutz funktioniert
  - Verifizieren dass Finanzierungsinformationen ab Seite 9 erscheinen

- [ ]* 11.5 Manuelle Validierung
  - PDF öffnen und visuell inspizieren
  - Alle Diagramme auf transparente Hintergründe prüfen
  - Alle Seitenzahlen prüfen
  - Alle Logos und Kopf-/Fußzeilen prüfen
  - Alle Finanzierungsdaten prüfen
  - Alle Produktdatenblätter und Firmendokumente prüfen

- [ ] 12. Dokumentation und Abschluss
  - Vollständige Dokumentation aller Änderungen
  - README aktualisieren
  - Changelog erstellen

- [ ] 12.1 Code-Dokumentation vervollständigen
  - Docstrings für alle neuen Funktionen
  - Inline-Kommentare für komplexe Logik
  - Type Hints für alle Funktionen

- [ ] 12.2 Benutzer-Dokumentation erstellen
  - README mit Beispielen aktualisieren
  - Troubleshooting-Guide erstellen
  - FAQ erstellen

- [ ] 12.3 Changelog und Release Notes
  - Changelog mit allen Änderungen erstellen
  - Release Notes für Version erstellen
  - Migration Guide für bestehende Benutzer
