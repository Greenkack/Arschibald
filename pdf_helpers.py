"""
PDF Hilfsfunktionen für erweiterte Header/Footer-Funktionalität
Ergänzt die bestehende pdf_generator.py
"""

from reportlab.platypus import Flowable


class PageTitleSetter(Flowable):
    """
    Flowable um den Seitentitel für die Kopfzeile zu setzen
    
    Verwendung:
    story.append(PageTitleSetter("Technische Komponenten"))
    """

    def __init__(self, title):
        Flowable.__init__(self)
        self.title = title
        self.width = 0
        self.height = 0

    def draw(self):
        # Setzt den Titel im Canvas für die nächste Seite
        if hasattr(self.canv, 'current_chapter_title_for_header'):
            self.canv.current_chapter_title_for_header = self.title


class TotalPagesSetter(Flowable):
    """
    Flowable um die Gesamtzahl der Seiten im Canvas zu setzen
    
    Wird automatisch am Ende des PDF-Erstellungsprozesses aufgerufen
    """

    def __init__(self, total_pages):
        Flowable.__init__(self)
        self.total_pages = total_pages
        self.width = 0
        self.height = 0

    def draw(self):
        # Setzt die Gesamtseitenzahl im Canvas
        self.canv.total_pages = self.total_pages


def add_page_title_to_story(story, title):
    """
    Fügt einen Seitentitel zur Story hinzu, der in der Kopfzeile angezeigt wird
    
    Args:
        story: Die PDF Story (Liste von Flowables)
        title: Der Titel für die Kopfzeile dieser Seite
    """
    story.append(PageTitleSetter(title))


def prepare_pdf_with_correct_page_numbers(doc, story):
    """
    Erstellt das PDF mit korrekten Seitenzahlen in zwei Durchläufen
    
    Args:
        doc: SimpleDocTemplate
        story: Liste der PDF-Inhalte
        
    Returns:
        bytes: PDF-Bytes
    """
    import io

    # Erster Durchlauf: Ermittlung der Gesamtseitenzahl
    temp_buffer = io.BytesIO()
    temp_doc = doc.__class__(
        temp_buffer,
        pagesize=doc.pagesize,
        topMargin=doc.topMargin,
        bottomMargin=doc.bottomMargin,
        leftMargin=doc.leftMargin,
        rightMargin=doc.rightMargin
    )

    # Temporärer Build um Seitenzahl zu ermitteln
    temp_doc.build(story)
    total_pages = temp_doc.page
    temp_buffer.close()

    # Gesamtseitenzahl zu Story hinzufügen
    story.insert(0, TotalPagesSetter(total_pages))

    # Zweiter Durchlauf: Finales PDF mit korrekten Seitenzahlen
    final_buffer = io.BytesIO()
    final_doc = doc.__class__(
        final_buffer,
        pagesize=doc.pagesize,
        topMargin=doc.topMargin,
        bottomMargin=doc.bottomMargin,
        leftMargin=doc.leftMargin,
        rightMargin=doc.rightMargin
    )

    # Finales PDF erstellen
    final_doc.build(story)
    pdf_bytes = final_buffer.getvalue()
    final_buffer.close()

    return pdf_bytes


def create_section_title_mapping():
    """
    Erstellt ein Mapping von Abschnitts-Keys zu benutzerfreundlichen Titeln
    für die Kopfzeilen
    
    Returns:
        dict: Mapping von section_key zu display_title
    """
    return {
        "ProjectOverview": "Projektübersicht",
        "TechnicalComponents": "Technische Komponenten",
        "CostDetails": "Kostenaufstellung",
        "Economics": "Wirtschaftlichkeit",
        "SimulationDetails": "Simulationsdetails",
        "CO2Savings": "CO₂-Einsparungen",
        "Visualizations": "Diagramme & Visualisierungen",
        "FutureAspects": "Zukunftsperspektiven",
        "ProductDetails": "Produktdetails",
        "Installation": "Installation & Montage",
        "Maintenance": "Wartung & Service",
        "Warranty": "Garantieleistungen",
        "Financing": "Finanzierung",
        "Legal": "Rechtliche Hinweise"
    }


def integrate_dynamic_headers_into_existing_pdf():
    """
    Beispiel-Integration in die bestehende PDF-Generierung
    
    Diese Funktion zeigt, wie die dynamischen Header in den bestehenden
    pdf_generator.py Code integriert werden können.
    """

    integration_example = '''
    # In der bestehenden generate_offer_pdf Funktion:
    
    from pdf_helpers import add_page_title_to_story, create_section_title_mapping
    
    # Titel-Mapping erstellen
    section_titles = create_section_title_mapping()
    
    # In der Schleife für die Sektionen:
    for section_key in sections_to_include:
        if section_key in section_titles:
            # Seitentitel für Header setzen
            add_page_title_to_story(story, section_titles[section_key])
        
        # Bestehender Sektions-Code...
        if section_key == "ProjectOverview":
            # Projektübersicht Inhalt...
        elif section_key == "TechnicalComponents":
            # Technische Komponenten Inhalt...
        # etc.
    '''

    return integration_example


# Beispiel für die Verwendung in Streamlit
def create_streamlit_pdf_with_enhanced_headers(
    project_data, analysis_results, company_info,
    header_logo_base64=None, footer_logo_base64=None
):
    """
    Beispiel-Funktion für die Integration in Streamlit
    """
    import io

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    # PDF Buffer
    buffer = io.BytesIO()

    # Dokument erstellen
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=3*cm,  # Mehr Platz für Header
        bottomMargin=3*cm,  # Mehr Platz für Footer
        leftMargin=2*cm,
        rightMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    # Story erstellen
    story = []

    # Titel-Mapping
    section_titles = create_section_title_mapping()

    # Deckblatt
    add_page_title_to_story(story, "Angebot")
    story.append(Paragraph("Photovoltaik-Angebot", styles['Title']))
    story.append(Spacer(1, 2*cm))

    # Verschiedene Sektionen
    sections = ["ProjectOverview", "TechnicalComponents", "CostDetails"]

    for section in sections:
        # Seitentitel setzen
        add_page_title_to_story(story, section_titles.get(section, section))

        # Sektions-Inhalt
        story.append(Paragraph(section_titles.get(section, section), styles['Heading1']))
        story.append(Paragraph("Hier kommt der Inhalt für " + section, styles['Normal']))
        story.append(Spacer(1, 1*cm))

    # PDF erstellen mit Layout Handler
    def layout_func(canvas, doc):
        from pdf_generator import page_layout_handler
        page_layout_handler(
            canvas, doc, {}, company_info,
            header_logo_base64, "",
            A4[0], A4[1], 2*cm, 2*cm, 3*cm, 3*cm,
            A4[0]-4*cm, A4[1]-6*cm
        )

    doc.build(story, onFirstPage=layout_func, onLaterPages=layout_func)

    return buffer.getvalue()
