# Requirements Document

## Introduction

Das erweiterte PDF-Ausgabesystem benötigt umfassende Verbesserungen in 10 kritischen Bereichen mit höchster Priorität auf Robustheit, Vollständigkeit und Fehlerfreiheit. Diese Spezifikation definiert detaillierte Anforderungen für:

1. **Visuelle Diagramm-Optimierung**: Transparente Hintergründe, 2D-Konvertierung, verbesserte Darstellung
2. **UI-Integration**: Vollständige Diagrammauswahl mit dynamischen Werten und PDF-Bytes-Verknüpfung
3. **Dokumenten-Integration**: Produktdatenblätter aus Produktdatenbank, firmenspe zifische Dokumente
4. **Layout-Optimierung**: Intelligenter Seitenschutz, professionelle Kopf-/Fußzeilen
5. **Finanzierungs-Priorisierung**: Vollständige Finanzierungsinformationen ab Seite 9
6. **Code-Integration**: 100% Übernahme und Verbesserung der repair_pdf Logik

Alle Implementierungen müssen:

- 100% funktionsfähig und getestet sein
- Fehlerbehandlung für alle Edge Cases enthalten
- Rückwärtskompatibel sein
- Performance-optimiert sein
- Vollständig dokumentiert sein

## Requirements

### Requirement 1: Diagramm-Hintergründe transparent machen

**User Story:** Als Benutzer möchte ich, dass alle Diagramme in der erweiterten PDF transparente Hintergründe haben statt schwarze, damit sie professionell auf den weißen PDF-Seiten aussehen und keine visuellen Brüche entstehen.

#### Acceptance Criteria

1. WHEN ein Matplotlib-Diagramm generiert wird THEN SHALL das System `fig.patch.set_alpha(0)` und `ax.patch.set_alpha(0)` setzen
2. WHEN ein Matplotlib-Diagramm gespeichert wird THEN SHALL das System `facecolor='none'` und `edgecolor='none'` in `plt.savefig()` verwenden
3. WHEN ein Plotly-Diagramm generiert wird THEN SHALL das System `fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')` verwenden
4. WHEN ein Diagramm in die PDF eingefügt wird THEN SHALL der Hintergrund vollständig transparent sein ohne schwarze oder graue Artefakte
5. WHEN Diagramme in calculations.py generiert werden THEN SHALL jede Chart-Funktion transparente Hintergründe implementieren
6. WHEN Diagramme in calculations_extended.py generiert werden THEN SHALL jede Chart-Funktion transparente Hintergründe implementieren
7. WHEN Diagramme in analysis.py generiert werden THEN SHALL jede Chart-Funktion transparente Hintergründe implementieren
8. WHEN Diagramme in doc_output.py generiert werden THEN SHALL jede Chart-Funktion transparente Hintergründe implementieren
9. WHEN ein Diagramm einen Fehler beim Rendern hat THEN SHALL das System einen Fallback mit transparentem Hintergrund verwenden
10. WHEN Diagramme mit Legenden generiert werden THEN SHALL auch die Legende einen transparenten Hintergrund haben
11. WHEN Diagramme mit Gitternetzlinien generiert werden THEN SHALL das Gitternetz auf transparentem Hintergrund gezeichnet werden
12. WHEN mehrere Subplots in einem Diagramm existieren THEN SHALL jeder Subplot einen transparenten Hintergrund haben

### Requirement 2: Alle 3D-Diagramme in 2D umwandeln

**User Story:** Als Benutzer möchte ich, dass alle Diagramme in 2D dargestellt werden statt in 3D, damit sie klarer, professioneller und besser lesbar aussehen, insbesondere in gedruckten PDFs.

#### Acceptance Criteria

1. WHEN ein 3D-Pie-Chart existiert THEN SHALL das System es in ein 2D-Pie-Chart mit `ax = fig.add_subplot(111)` umwandeln
2. WHEN ein 3D-Bar-Chart existiert THEN SHALL das System es in ein 2D-Bar-Chart mit `ax.bar()` umwandeln
3. WHEN ein 3D-Surface-Plot existiert THEN SHALL das System es in ein 2D-Contour-Plot oder Heatmap umwandeln
4. WHEN `projection='3d'` in einem Subplot verwendet wird THEN SHALL das System dies entfernen
5. WHEN `ax.bar3d()` verwendet wird THEN SHALL das System es durch `ax.bar()` ersetzen
6. WHEN `ax.plot3D()` verwendet wird THEN SHALL das System es durch `ax.plot()` ersetzen
7. WHEN Diagramme in calculations.py existieren THEN SHALL das System alle 3D-Diagramme identifizieren und in 2D umwandeln
8. WHEN Diagramme in calculations_extended.py existieren THEN SHALL das System alle 3D-Diagramme identifizieren und in 2D umwandeln
9. WHEN Diagramme in analysis.py existieren THEN SHALL das System alle 3D-Diagramme identifizieren und in 2D umwandeln
10. WHEN ein 3D-Diagramm umgewandelt wird THEN SHALL das System die Datenintegrität bewahren
11. WHEN ein 3D-Diagramm umgewandelt wird THEN SHALL das System alternative Visualisierungen verwenden (z.B. Farb-Kodierung für die dritte Dimension)
12. WHEN alle Umwandlungen abgeschlossen sind THEN SHALL das System keine `mpl_toolkits.mplot3d` Imports mehr enthalten
13. WHEN ein Diagramm nach der Umwandlung getestet wird THEN SHALL es alle ursprünglichen Daten korrekt darstellen

### Requirement 3: Diagrammauswahl in PDF UI implementieren

**User Story:** Als Benutzer möchte ich in der PDF UI präzise auswählen können, welche Diagramme in die PDF eingefügt werden sollen, damit ich nur relevante Visualisierungen erhalte und die PDF-Größe kontrollieren kann.

#### Acceptance Criteria

1. WHEN die PDF UI geladen wird THEN SHALL das System alle verfügbaren Diagramme aus allen Modulen scannen und auflisten
2. WHEN Diagramme in calculations.py definiert sind THEN SHALL das System diese mit benutzerfreundlichen Namen in der UI anzeigen
3. WHEN Diagramme in calculations_extended.py definiert sind THEN SHALL das System diese mit benutzerfreundlichen Namen in der UI anzeigen
4. WHEN Diagramme in analysis.py definiert sind THEN SHALL das System diese mit benutzerfreundlichen Namen in der UI anzeigen
5. WHEN Diagramme in doc_output.py definiert sind THEN SHALL das System diese mit benutzerfreundlichen Namen in der UI anzeigen
6. WHEN die UI Diagramme anzeigt THEN SHALL das System ein `st.multiselect` Widget mit `chart_key_to_friendly_name_map` verwenden
7. WHEN ein Benutzer Diagramme auswählt THEN SHALL das System die Auswahl in `st.session_state['selected_charts_for_pdf']` speichern
8. WHEN ein Benutzer keine Diagramme auswählt THEN SHALL das System eine Warnung anzeigen
9. WHEN Diagramme generiert werden THEN SHALL das System nur die ausgewählten Diagramme generieren
10. WHEN Diagramme generiert werden THEN SHALL das System dynamische Werte aus `project_data` und `pv_details` verwenden
11. WHEN Diagramme in die PDF eingefügt werden THEN SHALL das System die generierten PDF-Bytes aus dem Session State verwenden
12. WHEN ein Diagramm nicht verfügbar ist THEN SHALL das System es in der UI als deaktiviert markieren
13. WHEN ein Diagramm Fehler beim Generieren hat THEN SHALL das System eine Fehlermeldung in der UI anzeigen
14. WHEN die UI Diagramme anzeigt THEN SHALL das System Vorschau-Thumbnails für jedes Diagramm anzeigen
15. WHEN ein Benutzer ein Diagramm auswählt THEN SHALL das System die geschätzte PDF-Größe aktualisieren
16. WHEN die PDF generiert wird THEN SHALL das System nur die ausgewählten Diagramme in der Reihenfolge der Auswahl einfügen
17. WHEN Diagramme kategorisiert sind THEN SHALL das System sie in Gruppen anzeigen (Finanzierung, Energie, Umwelt, etc.)
18. WHEN ein Benutzer "Alle auswählen" klickt THEN SHALL das System alle verfügbaren Diagramme auswählen
19. WHEN ein Benutzer "Keine auswählen" klickt THEN SHALL das System alle Diagramme abwählen
20. WHEN die Diagrammauswahl gespeichert wird THEN SHALL das System die Auswahl für zukünftige Sessions persistieren

### Requirement 4: Diagramm-Darstellung verbessern

**User Story:** Als Benutzer möchte ich, dass Diagramme optimal dargestellt werden mit dickeren Balken/Donuts, größeren Schriftarten und informativen Beschreibungen, damit sie leicht lesbar, verständlich und professionell aussehen.

#### Acceptance Criteria

1. WHEN ein Balkendiagramm generiert wird THEN SHALL das System Balken mit `width=0.6` oder größer verwenden
2. WHEN ein Donut-Diagramm generiert wird THEN SHALL das System `wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}` verwenden
3. WHEN ein Liniendiagramm generiert wird THEN SHALL das System `linewidth=2.5` oder größer verwenden
4. WHEN ein Scatter-Plot generiert wird THEN SHALL das System `s=100` oder größer für Marker-Größe verwenden
5. WHEN ein Diagramm Achsenbeschriftungen hat THEN SHALL das System `fontsize=12` oder größer verwenden
6. WHEN ein Diagramm einen Titel hat THEN SHALL das System `fontsize=14` oder größer und `fontweight='bold'` verwenden
7. WHEN ein Diagramm eine Legende hat THEN SHALL das System `fontsize=10` oder größer verwenden
8. WHEN ein Diagramm Tick-Labels hat THEN SHALL das System `fontsize=10` oder größer verwenden
9. WHEN ein Diagramm in die PDF eingefügt wird THEN SHALL das System eine Beschreibung als Paragraph unter dem Diagramm einfügen
10. WHEN eine Beschreibung generiert wird THEN SHALL sie den Diagrammtyp, Zweck und Haupterkenntnisse enthalten
11. WHEN eine Beschreibung generiert wird THEN SHALL sie die gleichen numerischen Werte wie das Diagramm verwenden
12. WHEN eine Beschreibung generiert wird THEN SHALL sie formatiert sein mit `styles['BodyText']` oder ähnlich
13. WHEN eine Beschreibung mehrere Werte enthält THEN SHALL sie diese in einer strukturierten Form darstellen
14. WHEN ein Diagramm Farben verwendet THEN SHALL das System kontrastreiche, professionelle Farben verwenden
15. WHEN ein Diagramm ein Gitternetz hat THEN SHALL das System `alpha=0.3` für subtile Gitternetzlinien verwenden
16. WHEN ein Diagramm Daten-Labels hat THEN SHALL das System diese mit `fontsize=9` oder größer anzeigen
17. WHEN ein Balkendiagramm Werte anzeigt THEN SHALL das System die Werte über den Balken mit `ha='center', va='bottom'` positionieren
18. WHEN ein Pie-Chart Prozentsätze anzeigt THEN SHALL das System `autopct='%1.1f%%'` mit `fontsize=10` verwenden
19. WHEN ein Diagramm generiert wird THEN SHALL das System `dpi=300` für hohe Auflösung verwenden
20. WHEN ein Diagramm in die PDF eingefügt wird THEN SHALL das System optimale Dimensionen (z.B. 14cm x 10cm) verwenden

### Requirement 5: Produktdatenblätter in PDF einbinden

**User Story:** Als Benutzer möchte ich, dass alle Produktdatenblätter aus der Produktdatenbank vollständig und korrekt in die PDF eingefügt werden, damit ich vollständige technische Informationen für jedes Produkt habe.

#### Acceptance Criteria

1. WHEN ein PV-Modul ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
2. WHEN ein Wechselrichter ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
3. WHEN ein Speicher ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
4. WHEN eine Wallbox ausgewählt ist THEN SHALL das System deren Datenblatt aus der Produktdatenbank laden und anhängen
5. WHEN ein EMS ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
6. WHEN ein Optimizer ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
7. WHEN ein Carport ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
8. WHEN ein Notstrom-System ausgewählt ist THEN SHALL das System dessen Datenblatt aus der Produktdatenbank laden und anhängen
9. WHEN eine Tierabwehr ausgewählt ist THEN SHALL das System deren Datenblatt aus der Produktdatenbank laden und anhängen
10. WHEN `include_additional_components` True ist THEN SHALL das System alle Zubehör-Datenblätter einschließen
11. WHEN `include_additional_components` False ist THEN SHALL das System nur Hauptkomponenten-Datenblätter einschließen
12. WHEN ein Produkt kein Datenblatt hat THEN SHALL das System dies im Log vermerken und fortfahren
13. WHEN ein Datenblatt-Pfad ungültig ist THEN SHALL das System dies im Log vermerken und fortfahren
14. WHEN ein Datenblatt nicht lesbar ist THEN SHALL das System einen Fehler loggen und fortfahren
15. WHEN Datenblätter angehängt werden THEN SHALL das System `PdfWriter` und `PdfReader` aus `pypdf` verwenden
16. WHEN Datenblätter angehängt werden THEN SHALL das System die Funktion `_append_datasheets_and_documents()` verwenden
17. WHEN Datenblätter angehängt werden THEN SHALL das System den Basis-Pfad `PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN` verwenden
18. WHEN ein Produkt mehrere Datenblätter hat THEN SHALL das System alle anhängen
19. WHEN Datenblätter angehängt werden THEN SHALL das System die Reihenfolge beibehalten (Module, Wechselrichter, Speicher, Zubehör)
20. WHEN alle Datenblätter angehängt sind THEN SHALL das System die finale PDF als Bytes zurückgeben
21. WHEN die Funktion `get_product_by_id_func` aufgerufen wird THEN SHALL das System die korrekte Produkt-ID übergeben
22. WHEN ein Datenblatt-Pfad relativ ist THEN SHALL das System ihn mit dem Basis-Pfad kombinieren
23. WHEN ein Datenblatt im PDF-Format vorliegt THEN SHALL das System es direkt anhängen
24. WHEN ein Datenblatt in einem anderen Format vorliegt THEN SHALL das System es konvertieren oder überspringen
25. WHEN Datenblätter angehängt werden THEN SHALL das System die Logik aus repair_pdf/pdf_generator.py Zeilen 4930-4970 verwenden

### Requirement 6: Firmendokumente in PDF einbinden

**User Story:** Als Benutzer möchte ich, dass firmenspe zifische Dokumente (Vollmachten, AGBs, Zertifikate) vollständig und korrekt in die PDF eingefügt werden, damit jede Firma ihre individuellen, exklusiven Dokumente in der PDF hat.

#### Acceptance Criteria

1. WHEN eine Firma über `active_company_id` identifiziert ist THEN SHALL das System deren spezifische Dokumente aus der Firmendatenbank laden
2. WHEN `company_document_ids_to_include` in `inclusion_options` definiert ist THEN SHALL das System nur diese Dokumente laden
3. WHEN `company_document_ids_to_include` leer ist THEN SHALL das System keine Firmendokumente anhängen
4. WHEN Firmendokumente geladen werden THEN SHALL das System `db_list_company_documents_func(active_company_id, None)` aufrufen
5. WHEN Firmendokumente gefiltert werden THEN SHALL das System nur Dokumente mit IDs in `company_document_ids_to_include` verwenden
6. WHEN ein Firmendokument einen relativen Pfad hat THEN SHALL das System ihn mit `COMPANY_DOCS_BASE_DIR_PDF_GEN` kombinieren
7. WHEN ein Firmendokument-Pfad existiert THEN SHALL das System das Dokument anhängen
8. WHEN ein Firmendokument-Pfad nicht existiert THEN SHALL das System einen Fehler loggen und fortfahren
9. WHEN mehrere Firmendokumente existieren THEN SHALL das System alle in der Reihenfolge der IDs anhängen
10. WHEN ein Firmendokument im PDF-Format vorliegt THEN SHALL das System es direkt anhängen
11. WHEN ein Firmendokument in einem anderen Format vorliegt THEN SHALL das System es konvertieren oder überspringen
12. WHEN Firmendokumente angehängt werden THEN SHALL das System `PdfWriter` und `PdfReader` verwenden
13. WHEN Firmendokumente angehängt werden THEN SHALL das System die Funktion `_append_datasheets_and_documents()` verwenden
14. WHEN keine `active_company_id` vorhanden ist THEN SHALL das System keine Firmendokumente anhängen
15. WHEN Firmendokumente angehängt werden THEN SHALL das System die Logik aus repair_pdf/pdf_generator.py Zeilen 4980-5000 verwenden
16. WHEN ein Firmendokument mehrere Seiten hat THEN SHALL das System alle Seiten anhängen
17. WHEN Firmendokumente und Produktdatenblätter beide angehängt werden THEN SHALL das System Produktdatenblätter zuerst anhängen
18. WHEN alle Firmendokumente angehängt sind THEN SHALL das System die finale PDF als Bytes zurückgeben
19. WHEN ein Firmendokument verschlüsselt ist THEN SHALL das System versuchen es zu entschlüsseln oder überspringen
20. WHEN Firmendokumente angehängt werden THEN SHALL das System jeden Schritt im Log dokumentieren

### Requirement 7: Seitenschutz für erweiterte Seiten implementieren

**User Story:** Als Benutzer möchte ich, dass Diagramme und ihre Beschreibungen immer zusammen auf einer Seite bleiben und nie getrennt werden, damit die PDF professionell aussieht und die Lesbarkeit optimal ist.

#### Acceptance Criteria

1. WHEN ein Diagramm mit Überschrift und Beschreibung eingefügt wird THEN SHALL das System alle drei Elemente mit `KeepTogether` gruppieren
2. WHEN nicht genug Platz auf der aktuellen Seite für die Gruppe ist THEN SHALL das System automatisch einen `PageBreak` einfügen
3. WHEN Seiten 1-8 (Standard-PDF) generiert werden THEN SHALL der Seitenschutz nicht gelten
4. WHEN Seiten ab 9 (erweiterte PDF) generiert werden THEN SHALL der Seitenschutz für alle Diagramme und Tabellen gelten
5. WHEN ein Diagramm am Seitenende platziert würde THEN SHALL das System es auf die nächste Seite verschieben
6. WHEN eine Tabelle mit Überschrift eingefügt wird THEN SHALL das System beide mit `KeepTogether` gruppieren
7. WHEN ein Finanzierungsplan eingefügt wird THEN SHALL das System Überschrift, Tabelle und Beschreibung mit `KeepTogether` gruppieren
8. WHEN mehrere zusammengehörige Elemente existieren THEN SHALL das System sie als eine Gruppe behandeln
9. WHEN ein `KeepTogether`-Element zu groß für eine Seite ist THEN SHALL das System es auf mehrere Seiten aufteilen
10. WHEN ein Diagramm mit Legende eingefügt wird THEN SHALL das System beide zusammenhalten
11. WHEN eine Überschrift am Seitenende stehen würde THEN SHALL das System sie auf die nächste Seite verschieben
12. WHEN ein Absatz nach einem Diagramm folgt THEN SHALL das System prüfen ob genug Platz ist
13. WHEN nicht genug Platz für einen Absatz ist THEN SHALL das System ihn auf die nächste Seite verschieben
14. WHEN Seitenschutz angewendet wird THEN SHALL das System mindestens 3cm Platz am Seitenende reservieren
15. WHEN ein Element auf eine neue Seite verschoben wird THEN SHALL das System dies im Log dokumentieren
16. WHEN Seitenschutz für Finanzierungsinformationen gilt THEN SHALL das System besonders strikt sein
17. WHEN mehrere Diagramme nacheinander eingefügt werden THEN SHALL das System zwischen ihnen angemessenen Abstand lassen
18. WHEN ein Diagramm mit Fußnoten eingefügt wird THEN SHALL das System alle Elemente zusammenhalten
19. WHEN Seitenschutz angewendet wird THEN SHALL das System die verfügbare Höhe mit `doc.height` berechnen
20. WHEN Seitenschutz implementiert wird THEN SHALL das System `KeepTogether` aus `reportlab.platypus` verwenden

### Requirement 8: Kopf- und Fußzeilen für erweiterte Seiten

**User Story:** Als Benutzer möchte ich, dass erweiterte Seiten (ab Seite 9) professionelle Kopf- und Fußzeilen mit Logo, Dreieck, Kundennamen und Seitenzahlen haben, damit die PDF einheitlich und professionell aussieht.

#### Acceptance Criteria

1. WHEN Seite 9+ generiert wird THEN SHALL das System ein Dreieck rechts oben mit Größe 20x20 Punkten einfügen
2. WHEN das Dreieck gezeichnet wird THEN SHALL das System die Farbe RGB(0, 0.33, 0.64) verwenden
3. WHEN das Dreieck gezeichnet wird THEN SHALL das System es im rechten oberen Eck positionieren
4. WHEN Seite 9+ generiert wird THEN SHALL das System das Firmenlogo links oben einfügen
5. WHEN das Logo eingefügt wird THEN SHALL das System es mit Breite 40 und Höhe 20 Punkten skalieren
6. WHEN das Logo eingefügt wird THEN SHALL das System `company_logo_base64_ref` dekodieren und als `ImageReader` verwenden
7. WHEN das Logo nicht verfügbar ist THEN SHALL das System diesen Schritt überspringen
8. WHEN Seite 9+ generiert wird THEN SHALL das System einen blauen Balken in der Fußzeile einfügen
9. WHEN der blaue Balken gezeichnet wird THEN SHALL das System Höhe 5 Punkte und Farbe RGB(0, 0.33, 0.64) verwenden
10. WHEN der blaue Balken gezeichnet wird THEN SHALL das System ihn über die gesamte Dokumentbreite erstrecken
11. WHEN Seite 9+ generiert wird THEN SHALL das System den Kundennamen links unten in der Fußzeile einfügen
12. WHEN der Kundenname eingefügt wird THEN SHALL das System `customer_name_ref` verwenden
13. WHEN der Kundenname eingefügt wird THEN SHALL das System Schriftart "Helvetica" mit Größe 8 verwenden
14. WHEN der Kundenname nicht verfügbar ist THEN SHALL das System diesen Schritt überspringen
15. WHEN Seite 9+ generiert wird THEN SHALL das System "Angebot [Datum]" mittig unten in der Fußzeile einfügen
16. WHEN das Angebotsdatum eingefügt wird THEN SHALL das System das Format "dd.mm.yyyy" verwenden
17. WHEN das Angebotsdatum eingefügt wird THEN SHALL das System `datetime.now().strftime("%d.%m.%Y")` verwenden
18. WHEN Seite 9+ generiert wird THEN SHALL das System "Seite X von XX" rechts unten in der Fußzeile einfügen
19. WHEN Seitenzahlen eingefügt werden THEN SHALL das System die aktuelle Seitenzahl mit `canvas_obj.getPageNumber()` ermitteln
20. WHEN Seitenzahlen eingefügt werden THEN SHALL das System die Gesamtseitenzahl dynamisch berechnen
21. WHEN Seitenzahlen eingefügt werden THEN SHALL das System Schriftart "Helvetica" mit Größe 8 verwenden
22. WHEN die Kopf-/Fußzeilen-Funktion aufgerufen wird THEN SHALL das System `page_layout_handler()` verwenden
23. WHEN `page_layout_handler()` implementiert wird THEN SHALL das System alle Parameter aus `layout_callback_kwargs_build` verwenden
24. WHEN `page_layout_handler()` aufgerufen wird THEN SHALL das System `canvas_obj.saveState()` und `canvas_obj.restoreState()` verwenden
25. WHEN Seiten 1-8 generiert werden THEN SHALL das System die Standard-Kopf-/Fußzeilen verwenden
26. WHEN die Logik implementiert wird THEN SHALL das System die Funktionen aus repair_pdf/pdf_generator.py Zeilen 103-428 verwenden
27. WHEN die PDF gebaut wird THEN SHALL das System `PageNumCanvas` mit `onPage_callback=page_layout_handler` verwenden
28. WHEN `PageNumCanvas` verwendet wird THEN SHALL das System `callback_kwargs=layout_callback_kwargs_build` übergeben
29. WHEN Kopf-/Fußzeilen gezeichnet werden THEN SHALL das System die Ränder `margin_left_ref`, `margin_right_ref`, `margin_top_ref`, `margin_bottom_ref` respektieren
30. WHEN alle Kopf-/Fußzeilen-Elemente gezeichnet sind THEN SHALL das System sicherstellen dass sie nicht mit dem Hauptinhalt überlappen

### Requirement 9: Finanzierungsinformationen priorisieren

**User Story:** Als Benutzer möchte ich, dass vollständige Finanzierungsinformationen mit allen Berechnungen, Tabellen und Plänen sofort ab Seite 9 erscheinen, damit wichtige Finanzdetails prominent und vollständig dargestellt werden.

#### Acceptance Criteria

1. WHEN die erweiterte PDF generiert wird THEN SHALL das System nach Seite 8 einen `PageBreak` einfügen
2. WHEN Seite 9 beginnt THEN SHALL das System als erstes die Überschrift "Finanzierungsinformationen" einfügen
3. WHEN Finanzierungsinformationen eingefügt werden THEN SHALL das System `final_end_preis` aus `project_data['pv_details']` verwenden
4. WHEN `final_end_preis` nicht verfügbar ist THEN SHALL das System einen Fehler loggen und 0 verwenden
5. WHEN Kreditfinanzierung berechnet wird THEN SHALL das System `calculate_annuity()` aus `financial_tools` verwenden
6. WHEN Kreditfinanzierung berechnet wird THEN SHALL das System `principal=final_end_preis` verwenden
7. WHEN Kreditfinanzierung berechnet wird THEN SHALL das System `interest_rate` aus `global_constants` verwenden
8. WHEN Kreditfinanzierung berechnet wird THEN SHALL das System `years` aus `global_constants` oder Benutzerauswahl verwenden
9. WHEN Kreditdaten berechnet sind THEN SHALL das System eine Tabelle mit Kreditbetrag, Zinssatz, Laufzeit, monatlicher Rate und Gesamtkosten erstellen
10. WHEN die Kredittabelle erstellt wird THEN SHALL das System `Table` mit `colWidths=[8*cm, 6*cm]` verwenden
11. WHEN die Kredittabelle erstellt wird THEN SHALL das System einen blauen Header mit weißem Text verwenden
12. WHEN die Kredittabelle erstellt wird THEN SHALL das System Gitternetzlinien mit `colors.grey` verwenden
13. WHEN Leasingfinanzierung berechnet wird THEN SHALL das System `calculate_leasing_costs()` aus `financial_tools` verwenden
14. WHEN Leasingfinanzierung berechnet wird THEN SHALL das System `asset_value=final_end_preis` verwenden
15. WHEN Leasingfinanzierung berechnet wird THEN SHALL das System `residual_value_percent` aus `global_constants` verwenden
16. WHEN Leasingdaten berechnet sind THEN SHALL das System eine Tabelle mit Leasingbetrag, Zinssatz, Laufzeit, monatlicher Rate und Restwert erstellen
17. WHEN die Leasingtabelle erstellt wird THEN SHALL das System das gleiche Styling wie die Kredittabelle verwenden
18. WHEN Amortisationsplan erstellt wird THEN SHALL das System jährliche Werte für 20-25 Jahre berechnen
19. WHEN Amortisationsplan erstellt wird THEN SHALL das System Spalten für Jahr, Einsparungen, Kosten, Netto-Cashflow und kumulierten Cashflow haben
20. WHEN Amortisationsplan erstellt wird THEN SHALL das System die Amortisationszeit hervorheben
21. WHEN Amortisationsplan erstellt wird THEN SHALL das System `Table` mit angemessenen Spaltenbreiten verwenden
22. WHEN Finanzierungsvergleich erstellt wird THEN SHALL das System Barkauf, Kredit und Leasing vergleichen
23. WHEN Finanzierungsvergleich erstellt wird THEN SHALL das System Gesamtkosten, monatliche Belastung und ROI vergleichen
24. WHEN Finanzierungsvergleich erstellt wird THEN SHALL das System eine Empfehlung basierend auf den Daten geben
25. WHEN Finanzierungsdiagramme verfügbar sind THEN SHALL das System diese nach den Tabellen einfügen
26. WHEN Finanzierungsinformationen mehrere Seiten benötigen THEN SHALL das System automatisch weitere Seiten erstellen
27. WHEN Finanzierungsinformationen abgeschlossen sind THEN SHALL das System einen `Spacer` vor dem nächsten Abschnitt einfügen
28. WHEN `inclusion_options['include_financing_details']` False ist THEN SHALL das System Finanzierungsinformationen überspringen
29. WHEN Finanzierungsinformationen eingefügt werden THEN SHALL das System alle Werte mit 2 Dezimalstellen und Tausendertrennzeichen formatieren
30. WHEN Finanzierungsberechnungen Fehler haben THEN SHALL das System Fehler loggen und mit Standardwerten fortfahren

### Requirement 10: Logik aus repair_pdf extrahieren und integrieren

**User Story:** Als Entwickler möchte ich, dass alle funktionierenden Logiken aus repair_pdf systematisch extrahiert, analysiert und vollständig in den aktuellen Code integriert werden, damit alle Features 100% funktionsfähig, robust und getestet sind.

#### Acceptance Criteria

1. WHEN repair_pdf/pdf_generator.py analysiert wird THEN SHALL das System alle relevanten Funktionen identifizieren
2. WHEN `page_layout_handler()` aus repair_pdf extrahiert wird THEN SHALL das System es in pdf_generator.py integrieren (Zeilen 103-428)
3. WHEN `_append_datasheets_and_documents()` aus repair_pdf extrahiert wird THEN SHALL das System es in pdf_generator.py integrieren (Zeilen 4930-5050)
4. WHEN `PageNumCanvas` aus repair_pdf extrahiert wird THEN SHALL das System es in pdf_generator.py integrieren (Zeilen 2660-2663)
5. WHEN `_header_footer()` aus repair_pdf extrahiert wird THEN SHALL das System es in pdf_generator.py integrieren
6. WHEN Logik aus repair_pdf/pdf_ui.py extrahiert wird THEN SHALL das System `chart_key_to_friendly_name_map` integrieren (Zeilen 262-265)
7. WHEN Diagrammauswahl-UI aus repair_pdf extrahiert wird THEN SHALL das System sie in pdf_ui.py integrieren
8. WHEN Session State Management aus repair_pdf extrahiert wird THEN SHALL das System es in pdf_ui.py integrieren
9. WHEN Logik aus repair_pdf/pdf_styles.py extrahiert wird THEN SHALL das System transparente Hintergrund-Logik integrieren (Zeilen 373-376)
10. WHEN Style-Definitionen aus repair_pdf extrahiert werden THEN SHALL das System sie in pdf_styles.py integrieren
11. WHEN Logik aus repair_pdf/calculations.py extrahiert wird THEN SHALL das System alle Chart-Generierungsfunktionen analysieren
12. WHEN transparente Hintergründe in repair_pdf/calculations.py gefunden werden THEN SHALL das System diese Logik in calculations.py integrieren
13. WHEN 2D-Diagramme in repair_pdf/calculations.py gefunden werden THEN SHALL das System diese Logik in calculations.py integrieren
14. WHEN Logik aus repair_pdf/calculations_extended.py extrahiert wird THEN SHALL das System alle erweiterten Chart-Funktionen analysieren
15. WHEN erweiterte Berechnungen in repair_pdf gefunden werden THEN SHALL das System diese in calculations_extended.py integrieren
16. WHEN Logik aus repair_pdf/analysis.py extrahiert wird THEN SHALL das System alle Analyse-Funktionen analysieren
17. WHEN Plotly-Diagramme mit transparenten Hintergründen in repair_pdf gefunden werden THEN SHALL das System diese Logik integrieren (Zeilen 2006-2010)
18. WHEN Logik aus repair_pdf/doc_output.py extrahiert wird THEN SHALL das System alle Dokumenten-Ausgabe-Funktionen analysieren
19. WHEN alle Logiken extrahiert sind THEN SHALL das System eine Integrations-Checkliste erstellen
20. WHEN Logiken integriert werden THEN SHALL das System bestehenden Code nicht überschreiben sondern erweitern
21. WHEN Logiken integriert werden THEN SHALL das System Konflikte identifizieren und auflösen
22. WHEN Logiken integriert werden THEN SHALL das System alle Imports aktualisieren
23. WHEN Logiken integriert werden THEN SHALL das System alle Funktionsaufrufe aktualisieren
24. WHEN Logiken integriert werden THEN SHALL das System alle Variablennamen konsistent halten
25. WHEN alle Logiken integriert sind THEN SHALL das System Unit Tests für jede integrierte Funktion haben
26. WHEN alle Logiken integriert sind THEN SHALL das System Integration Tests für das Gesamtsystem haben
27. WHEN Tests durchgeführt werden THEN SHALL das System alle Anforderungen 1-9 erfüllen
28. WHEN Tests fehlschlagen THEN SHALL das System detaillierte Fehlermeldungen ausgeben
29. WHEN die Integration abgeschlossen ist THEN SHALL das System eine Dokumentation der Änderungen erstellen
30. WHEN die Integration abgeschlossen ist THEN SHALL das System alle Punkte 1-10 vollständig und funktionsfähig implementiert haben
31. WHEN die Integration validiert wird THEN SHALL das System eine vollständige PDF mit allen Features generieren können
32. WHEN die Integration validiert wird THEN SHALL das System keine Fehler oder Warnungen ausgeben
33. WHEN die Integration validiert wird THEN SHALL das System Performance-Benchmarks erfüllen
34. WHEN die Integration validiert wird THEN SHALL das System alle Edge Cases korrekt behandeln
35. WHEN die Integration abgeschlossen ist THEN SHALL das System Code-Review-ready sein
