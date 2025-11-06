# pdf_dynamic_tariff_section.py
"""
PDF-Generator Sektion für Dynamischer Stromtarif & Stromcloud
Integration in pdf_generator.py

Author: GitHub Copilot
Version: 1.0
Date: 2025-01-13
"""

from typing import Any
from io import BytesIO
import plotly.graph_objects as go


def add_dynamic_tariff_section_to_pdf(
    pdf: Any,  # reportlab Canvas object
    project_data: dict[str, Any],
    page_width: float = 595,  # A4 width in points
    page_height: float = 842   # A4 height in points
) -> None:
    """
    Fügt Dynamischer Stromtarif Sektion zum PDF hinzu
    
    Args:
        pdf: reportlab Canvas Objekt
        project_data: Projekt-Daten mit dynamic_tariff_* Feldern
        page_width: Seitenbreite in Points
        page_height: Seitenhöhe in Points
    
    Returns:
        None (modifiziert PDF direkt)
    """
    
    # Prüfen ob Feature genutzt wird
    if not project_data.get("dynamic_tariff_enabled", False):
        return  # Feature nicht aktiv, überspringen
    
    # ========================================================================
    # NEUE SEITE: Dynamischer Stromtarif Übersicht
    # ========================================================================
    
    pdf.showPage()  # Neue Seite
    y_position = page_height - 50  # Start von oben
    
    # Titel
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y_position, "⚡ Dynamischer Stromtarif & Stromcloud")
    y_position -= 30
    
    # Untertitel
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y_position, "Intelligentes Last-Management für maximale Kosteneffizienz")
    y_position -= 40
    
    # ========================================================================
    # SEKTION 1: Tarif-Vergleich
    # ========================================================================
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_position, "1. Tarif-Vergleich: Statisch vs. Dynamisch")
    y_position -= 25
    
    # Daten auslesen
    provider = project_data.get("tariff_provider", "N/A")
    savings_eur = project_data.get("dynamic_tariff_annual_savings_eur", 0)
    savings_percent = project_data.get("dynamic_tariff_savings_percent", 0)
    avg_price = project_data.get("dynamic_tariff_avg_price_eur_kwh", 0)
    
    # Tabelle: Vergleich
    pdf.setFont("Helvetica", 11)
    table_data = [
        ["Anbieter:", provider],
        ["Durchschnittspreis Dynamisch:", f"{avg_price:.3f} EUR/kWh"],
        ["Jährliche Einsparung:", f"{savings_eur:,.2f} EUR"],
        ["Einsparung Prozentual:", f"{savings_percent:.1f}%"],
    ]
    
    for label, value in table_data:
        pdf.drawString(60, y_position, label)
        pdf.drawString(300, y_position, str(value))
        y_position -= 20
    
    y_position -= 20
    
    # Smart Meter Info
    if project_data.get("smart_meter_installed", False):
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(60, y_position, "Smart Meter:")
        y_position -= 18
        
        pdf.setFont("Helvetica", 10)
        meter_cost = project_data.get("smart_meter_installation_cost_eur", 0)
        meter_fee = project_data.get("smart_meter_annual_fee_eur", 0)
        
        pdf.drawString(70, y_position, f"• Einmalkosten: {meter_cost:,.0f} EUR")
        y_position -= 15
        pdf.drawString(70, y_position, f"• Jahresgebühr: {meter_fee:,.0f} EUR")
        y_position -= 25
    
    # ========================================================================
    # SEKTION 2: Stromcloud
    # ========================================================================
    
    if project_data.get("stromcloud_enabled", False):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "2. Stromcloud-Analyse")
        y_position -= 25
        
        cloud_provider = project_data.get("stromcloud_provider", "N/A")
        cloud_plan = project_data.get("stromcloud_plan", "N/A")
        cloud_freimenge = project_data.get("stromcloud_freimenge_kwh", 0)
        cloud_savings = project_data.get("stromcloud_annual_savings_eur", 0)
        cloud_autarkie_with = project_data.get("stromcloud_autarkie_with_percent", 0)
        cloud_autarkie_without = project_data.get("stromcloud_autarkie_without_percent", 0)
        
        pdf.setFont("Helvetica", 11)
        cloud_table = [
            ["Anbieter:", cloud_provider],
            ["Tarif:", cloud_plan],
            ["Freimenge:", f"{cloud_freimenge:,.0f} kWh/Jahr"],
            ["Autarkie ohne Cloud:", f"{cloud_autarkie_without:.1f}%"],
            ["Autarkie mit Cloud:", f"{cloud_autarkie_with:.1f}%"],
            ["Autarkie-Steigerung:", f"+{cloud_autarkie_with - cloud_autarkie_without:.1f}%"],
            ["Jährliche Ersparnis:", f"{cloud_savings:,.2f} EUR"],
        ]
        
        for label, value in cloud_table:
            pdf.drawString(60, y_position, label)
            pdf.drawString(300, y_position, str(value))
            y_position -= 20
        
        y_position -= 20
    
    # ========================================================================
    # SEKTION 3: Energiemanagement-System (EMS)
    # ========================================================================
    
    if project_data.get("ems_enabled", False):
        # Neue Seite wenn zu wenig Platz
        if y_position < 200:
            pdf.showPage()
            y_position = page_height - 50
        
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "3. Energiemanagement-System (EMS)")
        y_position -= 25
        
        ems_type = project_data.get("ems_type", "N/A")
        ems_battery = project_data.get("ems_battery_size_kwh", 0)
        ems_load_shifted = project_data.get("ems_load_shifted_kwh", 0)
        ems_autarkie_increase = project_data.get("ems_autarkie_increase_percent", 0)
        ems_savings = project_data.get("ems_annual_savings_eur", 0)
        ems_payback = project_data.get("ems_payback_years", 0)
        
        pdf.setFont("Helvetica", 11)
        ems_table = [
            ["EMS-Typ:", ems_type],
            ["Batteriegröße:", f"{ems_battery:.0f} kWh"],
            ["Load-Shifting Potenzial:", f"{ems_load_shifted:,.0f} kWh/Jahr"],
            ["Autarkie-Steigerung:", f"+{ems_autarkie_increase:.1f}%"],
            ["Jährliche Einsparung:", f"{ems_savings:,.2f} EUR"],
            ["Amortisationszeit:", f"{ems_payback:.1f} Jahre"],
        ]
        
        for label, value in ems_table:
            pdf.drawString(60, y_position, label)
            pdf.drawString(300, y_position, str(value))
            y_position -= 20
        
        y_position -= 20
    
    # ========================================================================
    # SEKTION 4: Smart-Home-Integration
    # ========================================================================
    
    if project_data.get("smart_home_enabled", False):
        # Neue Seite wenn nötig
        if y_position < 200:
            pdf.showPage()
            y_position = page_height - 50
        
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "4. Smart-Home-Integration")
        y_position -= 25
        
        automation_level = project_data.get("smart_home_automation_level", "N/A")
        devices = project_data.get("smart_home_devices", [])
        sh_savings = project_data.get("smart_home_annual_savings_eur", 0)
        sh_comfort = project_data.get("smart_home_comfort_score", 0)
        sh_payback = project_data.get("smart_home_payback_years", 0)
        
        pdf.setFont("Helvetica", 11)
        sh_table = [
            ["Automatisierungs-Level:", automation_level.upper()],
            ["Aktive Geräte:", f"{len(devices)} Geräte"],
            ["Jährliche Einsparung:", f"{sh_savings:,.2f} EUR"],
            ["Komfort-Score:", f"{sh_comfort:.1f}/10"],
            ["Amortisationszeit:", f"{sh_payback:.1f} Jahre"],
        ]
        
        for label, value in sh_table:
            pdf.drawString(60, y_position, label)
            pdf.drawString(300, y_position, str(value))
            y_position -= 20
        
        # Geräte-Liste
        if devices:
            y_position -= 10
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(60, y_position, "Gesteuerte Geräte:")
            y_position -= 18
            
            pdf.setFont("Helvetica", 10)
            for device in devices:
                device_name = device.replace("_", " ").title()
                pdf.drawString(70, y_position, f"• {device_name}")
                y_position -= 15
        
        y_position -= 20
    
    # ========================================================================
    # SEKTION 5: Jahres-Simulation (8760h)
    # ========================================================================
    
    if project_data.get("annual_simulation_performed", False):
        # Neue Seite
        pdf.showPage()
        y_position = page_height - 50
        
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "5. Jahres-Simulation (8760 Stunden)")
        y_position -= 25
        
        total_consumption = project_data.get("annual_simulation_total_consumption_kwh", 0)
        avg_price_sim = project_data.get("annual_simulation_avg_price_eur_kwh", 0)
        total_cost = project_data.get("annual_simulation_total_cost_eur", 0)
        
        pdf.setFont("Helvetica", 11)
        sim_table = [
            ["Jahresverbrauch Gesamt:", f"{total_consumption:,.0f} kWh"],
            ["Durchschnittspreis:", f"{avg_price_sim:.3f} EUR/kWh"],
            ["Jahreskosten Gesamt:", f"{total_cost:,.2f} EUR"],
        ]
        
        for label, value in sim_table:
            pdf.drawString(60, y_position, label)
            pdf.drawString(300, y_position, str(value))
            y_position -= 20
        
        y_position -= 20
        
        # Peak-Hours
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(60, y_position, "Extremwerte:")
        y_position -= 18
        
        most_expensive_hour = project_data.get("annual_simulation_most_expensive_hour", 0)
        cheapest_hour = project_data.get("annual_simulation_cheapest_hour", 0)
        highest_consumption_hour = project_data.get("annual_simulation_highest_consumption_hour", 0)
        
        pdf.setFont("Helvetica", 10)
        pdf.drawString(70, y_position, f"• Teuerste Stunde: #{most_expensive_hour}")
        y_position -= 15
        pdf.drawString(70, y_position, f"• Günstigste Stunde: #{cheapest_hour}")
        y_position -= 15
        pdf.drawString(70, y_position, f"• Höchster Verbrauch: #{highest_consumption_hour}")
        y_position -= 25
    
    # ========================================================================
    # SEKTION 6: Zusammenfassung & Empfehlung
    # ========================================================================
    
    # Neue Seite
    pdf.showPage()
    y_position = page_height - 50
    
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y_position, "✅ Zusammenfassung & Empfehlung")
    y_position -= 30
    
    # Gesamt-Einsparung berechnen
    total_savings_year = 0
    total_savings_year += project_data.get("dynamic_tariff_annual_savings_eur", 0)
    total_savings_year += project_data.get("stromcloud_annual_savings_eur", 0)
    total_savings_year += project_data.get("ems_annual_savings_eur", 0)
    total_savings_year += project_data.get("smart_home_annual_savings_eur", 0)
    
    total_savings_10y = total_savings_year * 10
    total_savings_20y = total_savings_year * 20
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(60, y_position, f"Gesamte jährliche Einsparung: {total_savings_year:,.2f} EUR")
    y_position -= 25
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(60, y_position, f"• 10-Jahres-Ersparnis: {total_savings_10y:,.2f} EUR")
    y_position -= 20
    pdf.drawString(60, y_position, f"• 20-Jahres-Ersparnis: {total_savings_20y:,.2f} EUR")
    y_position -= 30
    
    # Empfehlung
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y_position, "Unsere Empfehlung:")
    y_position -= 20
    
    pdf.setFont("Helvetica", 11)
    recommendations = [
        "✅ Dynamischer Stromtarif lohnt sich bei Ihrem Profil deutlich",
        "✅ Smart-Home-Automatisierung maximiert Einspar-Potenzial",
        "✅ Kombination mit PV + Batteriespeicher optimal",
        "✅ Amortisation typischerweise innerhalb von 3-5 Jahren",
    ]
    
    for rec in recommendations:
        pdf.drawString(70, y_position, rec)
        y_position -= 18
    
    y_position -= 20
    
    # Nächste Schritte
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y_position, "Nächste Schritte:")
    y_position -= 20
    
    pdf.setFont("Helvetica", 11)
    next_steps = [
        "1. Smart Meter beim Netzbetreiber beantragen",
        "2. Dynamischen Tarif-Anbieter auswählen und anmelden",
        "3. Smart-Home-System einrichten (optional)",
        "4. Nach 3-6 Monaten Einsparung überprüfen",
    ]
    
    for step in next_steps:
        pdf.drawString(70, y_position, step)
        y_position -= 18
    
    # Fußnote
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, 50, "Hinweis: Alle Berechnungen basieren auf Durchschnittswerten und aktuellen Marktpreisen (2024/2025).")
    pdf.drawString(50, 35, "Tatsächliche Einsparungen können je nach individuellem Verbrauchsverhalten variieren.")


# ============================================================================
# INTEGRATION IN pdf_generator.py
# ============================================================================

"""
Integration in bestehende pdf_generator.py Datei:

1. Import hinzufügen:
   from pdf_dynamic_tariff_section import add_dynamic_tariff_section_to_pdf

2. In Haupt-Funktion (z.B. generate_complete_pdf) aufrufen:
   
   def generate_complete_pdf(project_data, analysis_results, output_path):
       pdf = canvas.Canvas(output_path, pagesize=A4)
       
       # ... Existing sections (Titelseite, PV-Analyse, etc.) ...
       
       # NEU: Dynamischer Stromtarif Sektion
       add_dynamic_tariff_section_to_pdf(pdf, project_data)
       
       # ... Weitere Sektionen ...
       
       pdf.save()

3. Charts als PNG einbetten (optional):
   
   from heatpump_dynamic_tariff_charts import create_hourly_price_chart
   import plotly.io as pio
   from PIL import Image
   
   # Chart erstellen
   chart = create_hourly_price_chart(hourly_data)
   
   # Als PNG speichern
   img_bytes = pio.to_image(chart, format='png', width=800, height=400)
   
   # In PDF einbetten
   from reportlab.platypus import Image as RLImage
   img = RLImage(BytesIO(img_bytes), width=400, height=200)
   pdf.drawImage(img, x=50, y=y_position, width=400, height=200)
"""
