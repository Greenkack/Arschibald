"""
Script to create sample PDF documents for the knowledge base.
Creates comprehensive documents about photovoltaics and heat pumps.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def create_photovoltaics_pdf():
    """Create a comprehensive PDF about photovoltaics."""

    # Create knowledge_base directory if it doesn't exist
    os.makedirs("knowledge_base", exist_ok=True)

    filename = "knowledge_base/photovoltaics_guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )

    # Title
    elements.append(
        Paragraph(
            "Photovoltaik-Systeme: Technischer Leitfaden",
            title_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Introduction
    elements.append(Paragraph("Einführung in die Photovoltaik", heading_style))
    intro_text = """
    Photovoltaik (PV) ist die direkte Umwandlung von Sonnenlicht in elektrische Energie
    mittels Solarzellen. Diese Technologie hat sich in den letzten Jahren zu einer der
    wichtigsten erneuerbaren Energiequellen entwickelt. PV-Anlagen bieten eine nachhaltige,
    umweltfreundliche und wirtschaftlich attraktive Lösung für die Energieversorgung von
    Privathaushalten, Unternehmen und öffentlichen Einrichtungen.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Technical Specifications
    elements.append(Paragraph("Technische Spezifikationen", heading_style))

    tech_text = """
    <b>Modultypen und Wirkungsgrade:</b><br/>
    Moderne PV-Module erreichen Wirkungsgrade zwischen 18% und 23%. Monokristalline Module
    bieten die höchste Effizienz (20-23%), während polykristalline Module bei 18-20% liegen.
    Dünnschichtmodule erreichen 15-18% Wirkungsgrad, sind aber kostengünstiger.
    """
    elements.append(Paragraph(tech_text, body_style))

    # Technical specifications table
    tech_data = [
        ['Modultyp', 'Wirkungsgrad', 'Leistung/m²', 'Lebensdauer'],
        ['Monokristallin', '20-23%', '180-220 Wp', '25-30 Jahre'],
        ['Polykristallin', '18-20%', '160-180 Wp', '25-30 Jahre'],
        ['Dünnschicht', '15-18%', '130-160 Wp', '20-25 Jahre'],
    ]

    tech_table = Table(tech_data, colWidths=[4 * cm, 3 * cm, 3 * cm, 3 * cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 0.5 * cm))

    # System Components
    elements.append(Paragraph("Systemkomponenten", heading_style))
    components_text = """
    Eine vollständige PV-Anlage besteht aus mehreren Komponenten:<br/>
    <b>1. Solarmodule:</b> Wandeln Sonnenlicht in Gleichstrom um.<br/>
    <b>2. Wechselrichter:</b> Konvertiert Gleichstrom in Wechselstrom (230V/400V).<br/>
    <b>3. Montagesystem:</b> Befestigung auf Dach oder Freifläche.<br/>
    <b>4. Verkabelung:</b> DC- und AC-Kabel mit entsprechenden Querschnitten.<br/>
    <b>5. Zähler:</b> Erfassung von Erzeugung und Einspeisung.<br/>
    <b>6. Speicher (optional):</b> Batteriespeicher für Eigenverbrauchsoptimierung.
    """
    elements.append(Paragraph(components_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Economic Data
    elements.append(Paragraph("Wirtschaftliche Kennzahlen", heading_style))

    economic_text = """
    <b>Investitionskosten (2024):</b><br/>
    Die durchschnittlichen Kosten für eine PV-Anlage liegen bei 1.200-1.800 €/kWp
    (inklusive Installation). Eine typische 10 kWp Anlage kostet somit 12.000-18.000 €.
    """
    elements.append(Paragraph(economic_text, body_style))

    # Economic data table
    economic_data = [
        ['Anlagengröße', 'Investition', 'Jahresertrag', 'Amortisation'],
        ['5 kWp', '6.000-9.000 €', '4.500-5.500 kWh', '10-12 Jahre'],
        ['10 kWp', '12.000-18.000 €', '9.000-11.000 kWh', '9-11 Jahre'],
        ['15 kWp', '18.000-27.000 €', '13.500-16.500 kWh', '8-10 Jahre'],
        ['20 kWp', '24.000-36.000 €', '18.000-22.000 kWh', '8-10 Jahre'],
    ]

    economic_table = Table(
        economic_data,
        colWidths=[
            3 * cm,
            3.5 * cm,
            3.5 * cm,
            3.5 * cm])
    economic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(economic_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Benefits
    elements.append(Paragraph("Vorteile der Photovoltaik", heading_style))
    benefits_text = """
    <b>1. Kosteneinsparungen:</b> Reduzierung der Stromkosten um 60-80% durch Eigenverbrauch.<br/>
    <b>2. Unabhängigkeit:</b> Weniger Abhängigkeit von Energieversorgern und steigenden Strompreisen.<br/>
    <b>3. Umweltschutz:</b> CO2-Einsparung von ca. 600 kg pro 1.000 kWh erzeugtem Solarstrom.<br/>
    <b>4. Wertsteigerung:</b> Immobilien mit PV-Anlage erzielen höhere Verkaufspreise.<br/>
    <b>5. Förderung:</b> Attraktive staatliche Förderungen und Einspeisevergütung.<br/>
    <b>6. Wartungsarm:</b> Minimaler Wartungsaufwand, lange Lebensdauer von 25-30 Jahren.
    """
    elements.append(Paragraph(benefits_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ROI Calculation
    elements.append(Paragraph("Renditeberechnung", heading_style))
    roi_text = """
    <b>Beispielrechnung für 10 kWp Anlage:</b><br/>
    Investition: 15.000 €<br/>
    Jahresertrag: 10.000 kWh<br/>
    Eigenverbrauch (70%): 7.000 kWh × 0,35 €/kWh = 2.450 €<br/>
    Einspeisung (30%): 3.000 kWh × 0,08 €/kWh = 240 €<br/>
    Gesamtersparnis pro Jahr: 2.690 €<br/>
    Amortisationszeit: 15.000 € ÷ 2.690 € = 5,6 Jahre<br/>
    Rendite über 25 Jahre: ca. 52.250 € (abzgl. Wartung)
    """
    elements.append(Paragraph(roi_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Installation Requirements
    elements.append(Paragraph("Installationsvoraussetzungen", heading_style))
    installation_text = """
    <b>Dacheignung:</b> Südausrichtung optimal (±45° akzeptabel), Neigung 25-35° ideal.<br/>
    <b>Verschattung:</b> Minimale Verschattung erforderlich für optimale Leistung.<br/>
    <b>Dachzustand:</b> Statik muss zusätzliche Last von 15-25 kg/m² tragen können.<br/>
    <b>Netzanschluss:</b> Ausreichende Kapazität des Hausanschlusses erforderlich.<br/>
    <b>Genehmigung:</b> In den meisten Fällen genehmigungsfrei, Meldung beim Netzbetreiber.
    """
    elements.append(Paragraph(installation_text, body_style))

    # Build PDF
    doc.build(elements)
    print(f"✓ Created: {filename}")


def create_heatpump_pdf():
    """Create a comprehensive PDF about heat pumps."""

    # Create knowledge_base directory if it doesn't exist
    os.makedirs("knowledge_base", exist_ok=True)

    filename = "knowledge_base/heatpump_guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#c8102e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#c8102e'),
        spaceAfter=12,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )

    # Title
    elements.append(
        Paragraph(
            "Wärmepumpen: Technischer Leitfaden",
            title_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Introduction
    elements.append(
        Paragraph(
            "Einführung in Wärmepumpentechnologie",
            heading_style))
    intro_text = """
    Wärmepumpen sind hocheffiziente Heizsysteme, die Umweltwärme aus Luft, Erde oder
    Grundwasser nutzen und auf ein höheres Temperaturniveau heben. Sie gelten als
    Schlüsseltechnologie für die Wärmewende und ermöglichen eine nachhaltige,
    umweltfreundliche Beheizung von Gebäuden. Mit einer Jahresarbeitszahl (JAZ) von
    3,5 bis 5,0 erzeugen moderne Wärmepumpen aus 1 kWh Strom 3,5 bis 5 kWh Wärme.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Types of Heat Pumps
    elements.append(Paragraph("Wärmepumpentypen", heading_style))

    types_text = """
    <b>1. Luft-Wasser-Wärmepumpe:</b><br/>
    Nutzt Außenluft als Wärmequelle. Einfache Installation, keine Genehmigung erforderlich.
    JAZ: 3,0-4,0. Ideal für Bestandsgebäude und Modernisierung.<br/><br/>

    <b>2. Sole-Wasser-Wärmepumpe (Erdwärme):</b><br/>
    Nutzt Erdwärme über Erdkollektoren oder Erdsonden. Sehr effizient, konstante Wärmequelle.
    JAZ: 4,0-5,0. Genehmigung erforderlich, höhere Investition.<br/><br/>

    <b>3. Wasser-Wasser-Wärmepumpe:</b><br/>
    Nutzt Grundwasser als Wärmequelle. Höchste Effizienz, JAZ: 4,5-5,5.
    Wasserrechtliche Genehmigung erforderlich, nicht überall möglich.
    """
    elements.append(Paragraph(types_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Technical Specifications Table
    tech_data = [
        ['Typ', 'JAZ', 'Investition', 'Betriebskosten/Jahr'],
        ['Luft-Wasser', '3,0-4,0', '12.000-18.000 €', '800-1.200 €'],
        ['Sole-Wasser', '4,0-5,0', '20.000-30.000 €', '600-900 €'],
        ['Wasser-Wasser', '4,5-5,5', '25.000-35.000 €', '500-800 €'],
    ]

    tech_table = Table(
        tech_data,
        colWidths=[
            3.5 * cm,
            2.5 * cm,
            4 * cm,
            4 * cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c8102e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 0.5 * cm))

    # System Components
    elements.append(Paragraph("Systemkomponenten", heading_style))
    components_text = """
    <b>Hauptkomponenten einer Wärmepumpe:</b><br/>
    1. <b>Verdampfer:</b> Nimmt Wärme aus der Umwelt auf<br/>
    2. <b>Verdichter:</b> Komprimiert das Kältemittel und erhöht die Temperatur<br/>
    3. <b>Verflüssiger:</b> Gibt Wärme an das Heizsystem ab<br/>
    4. <b>Expansionsventil:</b> Entspannt das Kältemittel<br/>
    5. <b>Pufferspeicher:</b> Speichert Wärme für gleichmäßige Versorgung<br/>
    6. <b>Regelung:</b> Intelligente Steuerung für optimalen Betrieb
    """
    elements.append(Paragraph(components_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Economic Data
    elements.append(Paragraph("Wirtschaftlichkeit", heading_style))

    economic_text = """
    <b>Kostenvergleich Heizsysteme (Einfamilienhaus, 150 m², 20.000 kWh/Jahr):</b>
    """
    elements.append(Paragraph(economic_text, body_style))

    comparison_data = [
        ['Heizsystem', 'Investition', 'Jahreskosten', 'CO2/Jahr'],
        ['Gasheizung', '8.000-12.000 €', '2.400 €', '4.800 kg'],
        ['Ölheizung', '9.000-13.000 €', '2.800 €', '6.400 kg'],
        ['Luft-WP', '12.000-18.000 €', '1.200 €', '1.200 kg'],
        ['Sole-WP', '20.000-30.000 €', '900 €', '900 kg'],
    ]

    comparison_table = Table(
        comparison_data, colWidths=[
            3.5 * cm, 3.5 * cm, 3 * cm, 3 * cm])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c8102e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(comparison_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Benefits
    elements.append(Paragraph("Vorteile von Wärmepumpen", heading_style))
    benefits_text = """
    <b>1. Niedrige Betriebskosten:</b> Bis zu 50% Einsparung gegenüber fossilen Heizsystemen.<br/>
    <b>2. Umweltfreundlich:</b> Bis zu 80% CO2-Reduktion, besonders mit Ökostrom.<br/>
    <b>3. Unabhängigkeit:</b> Keine Abhängigkeit von Gas- oder Ölpreisen.<br/>
    <b>4. Förderung:</b> Bis zu 40% Zuschuss durch BAFA-Förderung.<br/>
    <b>5. Kühlfunktion:</b> Viele Modelle bieten passive Kühlung im Sommer.<br/>
    <b>6. Wertsteigerung:</b> Moderne Heiztechnik steigert Immobilienwert.<br/>
    <b>7. Zukunftssicher:</b> Erfüllt alle aktuellen und zukünftigen Umweltauflagen.
    """
    elements.append(Paragraph(benefits_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ROI Calculation
    elements.append(Paragraph("Amortisationsrechnung", heading_style))
    roi_text = """
    <b>Beispiel: Luft-Wasser-Wärmepumpe vs. Gasheizung</b><br/>
    Mehrkosten Wärmepumpe: 8.000 € (nach Förderung)<br/>
    Jährliche Einsparung: 1.200 € (Betriebskosten)<br/>
    Amortisationszeit: 6,7 Jahre<br/>
    Einsparung über 20 Jahre: 24.000 € - 8.000 € = 16.000 €<br/>
    CO2-Einsparung über 20 Jahre: 72 Tonnen
    """
    elements.append(Paragraph(roi_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Installation Requirements
    elements.append(
        Paragraph(
            "Voraussetzungen für Installation",
            heading_style))
    requirements_text = """
    <b>Gebäudeeignung:</b><br/>
    - Gute Dämmung (U-Wert < 0,24 W/m²K empfohlen)<br/>
    - Niedertemperatur-Heizsystem (Fußbodenheizung ideal, max. 55°C Vorlauf)<br/>
    - Ausreichend Platz für Außeneinheit (Luft-WP) oder Erdarbeiten (Sole-WP)<br/>
    - Elektrischer Anschluss mit ausreichender Leistung (meist 3-phasig)<br/><br/>

    <b>Genehmigungen:</b><br/>
    - Luft-WP: Meist genehmigungsfrei, Lärmschutz beachten<br/>
    - Sole-WP: Genehmigung für Erdbohrung erforderlich<br/>
    - Wasser-WP: Wasserrechtliche Genehmigung notwendig
    """
    elements.append(Paragraph(requirements_text, body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Efficiency Tips
    elements.append(Paragraph("Effizienz-Tipps", heading_style))
    tips_text = """
    <b>Maximale Effizienz erreichen:</b><br/>
    1. Niedrige Vorlauftemperaturen nutzen (35-45°C optimal)<br/>
    2. Pufferspeicher für gleichmäßigen Betrieb einsetzen<br/>
    3. Kombination mit PV-Anlage für günstigen Eigenstrom<br/>
    4. Smart-Grid-Ready-Funktion für variable Stromtarife nutzen<br/>
    5. Regelmäßige Wartung (jährlich) durchführen<br/>
    6. Hydraulischen Abgleich durchführen lassen
    """
    elements.append(Paragraph(tips_text, body_style))

    # Build PDF
    doc.build(elements)
    print(f"✓ Created: {filename}")


def main():
    """Create all sample knowledge base documents."""
    print("Creating sample knowledge base documents...")
    print("-" * 50)

    try:
        create_photovoltaics_pdf()
        create_heatpump_pdf()
        print("-" * 50)
        print("✓ Successfully created all sample documents!")
        print("\nDocuments created:")
        print("  - knowledge_base/photovoltaics_guide.pdf")
        print("  - knowledge_base/heatpump_guide.pdf")
        print("\nThese documents contain:")
        print("  ✓ Technical specifications")
        print("  ✓ Economic data and calculations")
        print("  ✓ System components")
        print("  ✓ Benefits and advantages")
        print("  ✓ Installation requirements")
        print("  ✓ ROI calculations")
    except Exception as e:
        print(f"✗ Error creating documents: {e}")
        raise


if __name__ == "__main__":
    main()
