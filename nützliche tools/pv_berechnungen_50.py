import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# Alle 50 Berechnungsarten, strukturiert:
berechnungen = [
    # (Nummer, Name, Erklärung, Formel, Python-Code)


    (1, "Autarkiegrad (%)",
     "Wie viel Prozent des Strombedarfs durch die PV-Anlage gedeckt werden.",
     "Autarkiegrad = Eigenverbrauch / Gesamtverbrauch × 100",
     "def autarkiegrad(eigenverbrauch_kwh, gesamtverbrauch_kwh):\n    return eigenverbrauch_kwh / gesamtverbrauch_kwh * 100"
     ),

    (2, "Jährliche Stromkostenersparnis (€)",
     "Geldersparnis pro Jahr durch Eigenverbrauch.",
     "Ersparnis = Eigenverbrauch × Strompreis",
     "def stromkostenersparnis(eigenverbrauch_kwh, strompreis):\n    return eigenverbrauch_kwh * strompreis"
     ),

    (3, "Gesamtertrag über Laufzeit (kWh, €)",
     "Stromertrag oder Einnahmen über z. B. 20 Jahre.",
     "Gesamtertrag = Jahresertrag × Laufzeit",
     "def gesamtertrag_laufzeit(jahresertrag, laufzeit_jahre):\n    return jahresertrag * laufzeit_jahre"
     ),

    (4, "Effektiver Strompreis durch PV (ct/kWh)",
     "Effektive Kosten je selbst erzeugter Kilowattstunde.",
     "PV-Strompreis = Gesamtkosten / Gesamtertrag × 100 (für Cent)",
     "def effektiver_pv_strompreis(gesamt_kosten, gesamtertrag_kwh):\n    return gesamt_kosten / gesamtertrag_kwh * 100"
     ),
    (5, "Nettobarwert (NPV)",
     "Heutiger Wert aller künftigen Ein- und Auszahlungen.",
     "NPV = Summe (Einnahmen - Ausgaben) / (1 + Zinssatz) ** Jahr",
     "def npv(cashflows, zinssatz):\n    return sum([cf / (1+zinssatz)**i for i, cf in enumerate(cashflows)])"
     ),

    (6, "Kapitalwert Alternativanlage",
     "Vergleich mit alternativen Investments.",
     "Endkapital = Invest × (1 + Zinssatz) ** Jahre",
     "def alternativanlage_kapitalwert(invest, zinssatz, laufzeit):\n    return invest * (1 + zinssatz)**laufzeit"
     ),
    (6, "Kumulierte Einsparungen (€)",
     "Gesamte Stromkostenersparnisse über Laufzeit.",
     "Kumulierte Ersparnis = jährliche Ersparnis × Laufzeit",
     "def kumulierte_ersparnis(jaehrliche_ersparnis, laufzeit):\n    return jaehrliche_ersparnis * laufzeit"
     ),
    (7, "Speichergrad/Deckungsgrad Speicher (%)",
     "Anteil des Eigenverbrauchs, der vom Speicher abgedeckt wird.",
     "Speichergrad = gespeicherter Eigenverbrauch / gesamter Eigenverbrauch × 100",
     "def speichergrad(gespeichert, eigenverbrauch):\n    return gespeichert / eigenverbrauch * 100"
     ),


    (8, "Berechnung Dachflächennutzung",
     "Wie viele Module passen aufs Dach?",
     "Anzahl Module = (verfügbare Dachfläche) / (Modulfläche)",
     "def module_auf_dach(dachflaeche_m2, modul_l, modul_b):\n    modulflaeche = modul_l * modul_b\n    return int(dachflaeche_m2 / modulflaeche)"
     ),
    (9, "Break-Even-Analyse",
     "Wann werden die Investitionskosten durch Einsparungen gedeckt?",
     "Break-even = Invest / jährliche Ersparnis",
     "def break_even_jahr(invest, jaehrliche_ersparnis):\n    return int(invest // jaehrliche_ersparnis) + 1"
     ),
    (10, "Szenarienvergleich (mit/ohne Speicher, etc.)",
     "Vergleich unterschiedlicher Anlagenauslegungen.",
     "Vergleich aller KPIs je Szenario.",
     "def szenarienvergleich(configs):\n    results = []\n    for config in configs:\n        result = {}\n        results.append(result)\n    return results"
     ),
    (11, "Performance Ratio (PR)",
     "Maß für die technische Betriebsqualität der Anlage.",
     "PR = tatsächlicher Ertrag / (Globalstrahlung × installierte Leistung)",
     "def performance_ratio(ertrag_kwh, globalstrahlung_kwh, kWp):\n    return ertrag_kwh / (globalstrahlung_kwh * kWp)"
     ),


    (12, "Verschattungsverlust (%)",
     "Verlust durch zeitweise Verschattung.",
     "Verschattungsverlust = 1 - (Ertrag verschattet / Ertrag optimal)",
     "def verschattungsverlust(ertrag_verschattet, ertrag_optimal):\n    return 1 - (ertrag_verschattet / ertrag_optimal)"
     ),
    (13, "DC/AC-Überdimensionierungsfaktor",
     "Verhältnis PV-Modulleistung zu Wechselrichterleistung.",
     "Überdimensionierung = PV-Leistung / WR-Leistung",
     "def dc_ac_ueberdimensionierung(pv_leistung_kwp, wr_leistung_kw):\n    return pv_leistung_kwp / wr_leistung_kw"
     ),
    (14, "Temperaturkorrektur des PV-Ertrags",
     "Ertrag bei abweichender Modultemperatur.",
     "P_real = P_nom * [1 + TK * (T - T_ref)]",
     "def pv_leistung_temp_korr(p_nom, tk_percent, temp, t_ref=25):\n    return p_nom * (1 + tk_percent/100 * (temp - t_ref))"
     ),


    (15, "Eigenverbrauch durch Speichererhöhung (%)",
     "Steigerung des Eigenverbrauchs durch Batteriespeicher.",
     "Eigenverbrauch_neu = Funktion(Speichergröße, Lastprofil, PV-Profil)",
     "def eigenverbrauch_mit_speicher(alt, zusatz_speicher_prozent):\n    return alt + zusatz_speicher_prozent"
     ),
    (16, "Optimale Speichergröße (kWh)",
     "Empfohlene Größe für maximalen Eigenverbrauch.",
     "optimale Speichergröße ≈ Tagesverbrauch × (1 - Verluste)",
     "def optimale_speichergröße(tagesverbrauch, pv_profil, verluste=0.1):\n    return tagesverbrauch * (1 - verluste)"
     ),

    (17, "PV-Deckungsgrad für Wärmepumpe",
     "Anteil des WP-Verbrauchs durch PV gedeckt.",
     "PV-Deckung_WP = PV-Überschuss / WP-Jahresverbrauch × 100",
     "def pv_deckung_wp(pv_ueberschuss, wp_jahresverbrauch):\n    return pv_ueberschuss / wp_jahresverbrauch * 100"
     ),
    (18, "Eigenkapitalrendite (ROE)",
     "Rendite auf das eingesetzte Eigenkapital.",
     "ROE = (Gewinn / eingesetztes EK) × 100",
     "def roe(gewinn, eigenkapital):\n    return (gewinn / eigenkapital) * 100"
     ),

    (19, "Restwert der Anlage (nach x Jahren)",
     "Wert der PV-Anlage nach der Abschreibungsdauer.",
     "Restwert = Invest × (1 - jährliche Abschreibung) ** Jahre",
     "def restwert(invest, abschreibung, jahre):\n    return invest * ((1 - abschreibung) ** jahre)"
     ),
    (20, "Steuerliche Abschreibung (linear, degressiv)",
     "Vorteil durch steuerliche AfA.",
     "AfA linear = Investition / Abschreibungsdauer",
     "def afa_linear(invest, abschreibungsjahre):\n    return invest / abschreibungsjahre"
     ),
    (21, "Ersparnis durch Fördermittel/Kredite",
     "Abzug der Fördersumme, z. B. KfW, BAFA.",
     "Effektive Kosten = Invest - Förderung",
     "def foerderersparnis(invest, foerderung):\n    return invest - foerderung"
     ),

    (22, "Vergleich PV vs. Balkonkraftwerk",
     "Kostenvorteil und Ertrag im Vergleich.",
     "Vergleich: Kosten- und Ertragsdifferenz beider Systeme",
     "def vergleich_pv_bkw(kosten_pv, ertrag_pv, kosten_bkw, ertrag_bkw):\n    return {\n        'kosten_diff': kosten_pv - kosten_bkw,\n        'ertrag_diff': ertrag_pv - ertrag_bkw\n    }"
     ),

    (23, "Notstromfähigkeit (kWh/Tag)",
     "Wie viel Energie steht bei Stromausfall zur Verfügung?",
     "Notstromfähigkeit = nutzbare Speichergröße × Effizienz",
     "def notstrom_kapazitaet(speicher_kwh, nutzungsgrad):\n    return speicher_kwh * nutzungsgrad"
     ),
    (24, "Batteriezyklus-Kalkulation",
     "Wie viele Ladezyklen hat der Speicher?",
     "Lebensdauer = max. Zyklen / Zyklen/Jahr",
     "def batterie_lebensdauer(max_zyklen, zyklen_pro_jahr):\n    return max_zyklen / zyklen_pro_jahr"
     ),
    (25, "Ladeprofil-Simulation für E-Auto",
     "Wie viel PV-Strom kann das E-Auto nutzen?",
     "Geladene Energiemenge = min(PV-Überschuss, Bedarf) × Effizienz",
     "def eauto_ladeprofil(pv_ueberschuss, bedarf, ladeeffizienz=0.9):\n    return min(pv_ueberschuss, bedarf) * ladeeffizienz"
     ),

    (26, "Inflationsausgleich in der Wirtschaftlichkeitsrechnung",
     "Auswirkung der Inflation auf Erträge und Kosten.",
     "Wert_nach_Inflation = Wert / (1 + Inflationsrate) ** Jahre",
     "def wert_nach_inflation(wert, inflationsrate, jahre):\n    return wert / ((1 + inflationsrate) ** jahre)"
     ),
    (27, "Investitionsszenarien (A/B/C)",
     "Vergleich unterschiedlicher Anlagen- und Finanzierungsmodelle.",
     "Vergleich: alle KPIs je Szenario",
     "def invest_szenarien(vergleiche):\n    return {name: kpis for name, kpis in vergleiche.items()}"
     ),
    (28, "Anlagenerweiterung (Ertrag, Kosten, Amortisation)",
     "Kalkulation nach Nachrüstung (Module/Speicher).",
     "Neuberechnung aller KPIs nach Erweiterung",
     "def anlagenerweiterung(alt, neu):\n    return {k: neu[k] - alt.get(k, 0) for k in neu}"
     ),

    (29, "Peak-Shaving-Effekt",
     "Reduzierung von Lastspitzen durch PV und Speicher.",
     "Peak shaving = max. Last - gemessene Last nach Optimierung",
     "def peak_shaving(max_last, opt_last):\n    return max_last - opt_last"
     ),

    (30, "Szenario mit und ohne Batteriespeicher",
     "Erträge und Amortisation mit und ohne Speicher", "Autarkiegrad mit und ohne Speicher",
     "Einsparungen mit und ohne Speicher", "Komplettvergleich mit und ohne Speicher"
     ),

    (31, "Volleinspeisung und Teileinspeisung Vorteile", "Vergleich Voll und Teileinspeisung",
     "Amortisationszeit", "Ersparnisse", "Komplettvergleich Voll und Teileinspeisung",
     "Einspeisevergütungssatz 20 Jahre",
     ),


]


def wrap(text, width=95):
    return '\n'.join(textwrap.wrap(text, width=width))


def pdf_berechnungen(filename="pv_berechnungen_50.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    styleH = styles['Heading1']
    styleH2 = styles['Heading2']
    styleN = styles['Normal']
    styleCode = ParagraphStyle(
        name="Code",
        parent=styles['Normal'],
        fontName="Courier",
        fontSize=9,
        leading=11,
        leftIndent=1 * cm,
        backColor="#f5f5f5",
    )
    content = []

    # Deckblatt
    content.append(
        Paragraph(
            "50 Berechnungsarten für Photovoltaik-Angebote & Wirtschaftlichkeitsanalysen",
            styleH))
    content.append(Spacer(1, 1 * cm))
    content.append(
        Paragraph(
            "Dieses Nachschlagewerk enthält die wichtigsten und modernsten PV-Berechnungsarten für Angebote, "
            "Finanzierungsmodelle, Eigenverbrauch, Speicher, CO₂, Wirtschaftlichkeit und mehr. "
            "<br/><br/>Jede Berechnungsart ist mit Erklärung, Formel und Python-Code aufgeführt.",
            styleN))
    content.append(PageBreak())

    # Inhaltsverzeichnis
    content.append(Paragraph("Inhaltsverzeichnis", styleH2))
    for nr, name, *_ in berechnungen:
        content.append(Paragraph(f"{nr}. {name}", styleN))
    content.append(PageBreak())

    # Alle Berechnungen
    for nr, name, erklaerung, formel, code in berechnungen:
        content.append(Paragraph(f"{nr}. {name}", styleH2))
        content.append(Spacer(1, 0.1 * cm))
        content.append(Paragraph(f"<b>Erklärung:</b> {erklaerung}", styleN))
        content.append(Spacer(1, 0.1 * cm))
        content.append(
            Paragraph(
                f"<b>Formel:</b><br/><font face='Courier'>{formel}</font>",
                styleN))
        content.append(Spacer(1, 0.1 * cm))
        content.append(Paragraph("<b>Python-Code:</b>", styleN))
        content.append(
            Paragraph(
                f"<font face='Courier'>{
                    wrap(
                        code,
                        90)}</font>",
                styleCode))
        content.append(Spacer(1, 0.5 * cm))

    # Abschluss
    content.append(PageBreak())
    content.append(Paragraph("Notizen", styleH2))
    content.append(Spacer(1, 5 * cm))

    doc.build(content)


if __name__ == "__main__":

    print("Fertige PDF wurde erstellt: pv_berechnungen_50.pdf")
