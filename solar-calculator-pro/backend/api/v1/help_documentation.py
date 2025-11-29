"""
Help and Documentation System API

Provides REST API for help and documentation:
- Context-sensitive help system
- User manual sections
- FAQ management
- Video tutorial links
- Search functionality for help content

Requirements: funktionen.txt - "Hilfe und Dokumentation"
Task: 285. Help and Documentation System
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/help", tags=["Help & Documentation"])


# ==================== Enums ====================

class ContentType(str, Enum):
    ARTICLE = "article"
    FAQ = "faq"
    VIDEO = "video"
    TUTORIAL = "tutorial"
    QUICK_TIP = "quick_tip"


class HelpCategory(str, Enum):
    GETTING_STARTED = "getting_started"
    CALCULATOR = "calculator"
    PV_SYSTEMS = "pv_systems"
    HEAT_PUMPS = "heat_pumps"
    PDF_GENERATION = "pdf_generation"
    CRM = "crm"
    ADMIN = "admin"
    TROUBLESHOOTING = "troubleshooting"


# ==================== Pydantic Models ====================

class HelpContent(BaseModel):
    """Help content item"""
    id: str
    title: str
    content: str
    content_type: ContentType
    category: HelpCategory
    tags: List[str] = []
    context_keys: List[str] = []
    video_url: Optional[str] = None
    related_articles: List[str] = []
    views: int = 0
    helpful_votes: int = 0
    created_at: datetime
    updated_at: datetime


class FAQ(BaseModel):
    """FAQ item"""
    id: str
    question: str
    answer: str
    category: HelpCategory
    tags: List[str] = []
    views: int = 0
    helpful_votes: int = 0
    created_at: datetime


class VideoTutorial(BaseModel):
    """Video tutorial"""
    id: str
    title: str
    description: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    category: HelpCategory
    tags: List[str] = []
    views: int = 0
    created_at: datetime


class SearchResult(BaseModel):
    """Search result"""
    id: str
    title: str
    content_type: ContentType
    category: HelpCategory
    excerpt: str
    relevance_score: float


# ==================== Help Content Data ====================

_help_content: Dict[str, HelpContent] = {}
_faqs: Dict[str, FAQ] = {}
_video_tutorials: Dict[str, VideoTutorial] = {}


def init_help_content():
    """Initialize help content"""
    # Getting Started Articles
    _help_content["getting_started_overview"] = HelpContent(
        id="getting_started_overview",
        title="Erste Schritte mit Solar Calculator Pro",
        content="""# Willkommen bei Solar Calculator Pro

Solar Calculator Pro ist Ihre professionelle Lösung für die Berechnung und Planung von Photovoltaik- und Wärmepumpenanlagen.

## Hauptfunktionen

1. **PV-Kalkulator**: Berechnung von Solaranlagen
2. **Wärmepumpen-Kalkulator**: Dimensionierung von Wärmepumpen
3. **Kombinierte Berechnung**: PV + Wärmepumpe
4. **PDF-Generierung**: Professionelle Angebote
5. **CRM-System**: Kundenverwaltung

## Schnellstart

1. Erstellen Sie ein neues Projekt
2. Geben Sie die Kundendaten ein
3. Wählen Sie den Berechnungstyp
4. Konfigurieren Sie das System
5. Generieren Sie das Angebot
""",
        content_type=ContentType.ARTICLE,
        category=HelpCategory.GETTING_STARTED,
        tags=["einführung", "übersicht", "schnellstart"],
        context_keys=["dashboard", "home"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _help_content["pv_calculation_guide"] = HelpContent(
        id="pv_calculation_guide",
        title="PV-Anlagen berechnen - Schritt für Schritt",
        content="""# PV-Anlagen Berechnung

## Eingabeparameter

### Gebäudedaten
- **Dachfläche**: Verfügbare Fläche in m²
- **Dachneigung**: Winkel in Grad (optimal: 30-35°)
- **Ausrichtung**: Himmelsrichtung (optimal: Süd)
- **Verschattung**: Berücksichtigung von Hindernissen

### Systemkonfiguration
- **Modultyp**: Leistung und Abmessungen
- **Wechselrichter**: Passend zur Modulleistung
- **Batteriespeicher**: Optional für höhere Eigenverbrauchsquote

### Verbrauchsdaten
- **Jahresverbrauch**: Aktueller Stromverbrauch in kWh
- **Verbrauchsprofil**: Tageszeit der Nutzung

## Berechnungsschritte

1. **Modulanzahl bestimmen**: Basierend auf verfügbarer Fläche
2. **Ertrag berechnen**: PVGIS-Daten oder Standardwerte
3. **Eigenverbrauch ermitteln**: Abhängig von Verbrauchsprofil
4. **Wirtschaftlichkeit**: ROI und Amortisationszeit
""",
        content_type=ContentType.TUTORIAL,
        category=HelpCategory.PV_SYSTEMS,
        tags=["pv", "berechnung", "anleitung"],
        context_keys=["pv_calculator", "solar_calc"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _help_content["heatpump_guide"] = HelpContent(
        id="heatpump_guide",
        title="Wärmepumpen-Dimensionierung",
        content="""# Wärmepumpen-Dimensionierung

## Gebäudedaten erfassen

### Wichtige Parameter
- **Wohnfläche**: Beheizte Fläche in m²
- **Baujahr**: Für Dämmstandard-Einschätzung
- **Heizsystem**: Fußbodenheizung oder Heizkörper
- **Aktueller Verbrauch**: Gas/Öl in kWh oder Litern

### Heizlastberechnung
Die Heizlast wird aus Gebäudedaten geschätzt:
- Neubau: ca. 30-50 W/m²
- Saniert: ca. 50-80 W/m²
- Altbau: ca. 80-120 W/m²

## Wärmepumpen-Auswahl

### Typen
- **Luft-Wasser**: Einfache Installation
- **Sole-Wasser**: Höhere Effizienz
- **Wasser-Wasser**: Beste Effizienz

### Kennzahlen
- **COP**: Leistungszahl (momentan)
- **JAZ**: Jahresarbeitszahl (Durchschnitt)
""",
        content_type=ContentType.TUTORIAL,
        category=HelpCategory.HEAT_PUMPS,
        tags=["wärmepumpe", "heizung", "dimensionierung"],
        context_keys=["heatpump_calculator", "wp_calc"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # FAQs
    _faqs["faq_001"] = FAQ(
        id="faq_001",
        question="Wie berechne ich die optimale Modulanzahl?",
        answer="Die optimale Modulanzahl hängt von der verfügbaren Dachfläche und Ihrem Stromverbrauch ab. Als Faustregel gilt: Pro kWp benötigen Sie etwa 6-8 m² Dachfläche. Für einen Haushalt mit 4000 kWh Jahresverbrauch sind 6-8 kWp (ca. 20-25 Module) optimal.",
        category=HelpCategory.PV_SYSTEMS,
        tags=["module", "berechnung", "optimierung"],
        created_at=datetime.now()
    )
    
    _faqs["faq_002"] = FAQ(
        id="faq_002",
        question="Welche Dachausrichtung ist am besten?",
        answer="Die optimale Ausrichtung ist Süd mit einer Neigung von 30-35°. Aber auch Ost-West-Dächer können wirtschaftlich sein, da sie eine gleichmäßigere Stromproduktion über den Tag bieten.",
        category=HelpCategory.PV_SYSTEMS,
        tags=["ausrichtung", "dach", "ertrag"],
        created_at=datetime.now()
    )
    
    _faqs["faq_003"] = FAQ(
        id="faq_003",
        question="Lohnt sich ein Batteriespeicher?",
        answer="Ein Batteriespeicher erhöht den Eigenverbrauch von ca. 30% auf 60-80%. Die Wirtschaftlichkeit hängt von Strompreis, Speicherkosten und Verbrauchsprofil ab. Bei hohem Tagesverbrauch und steigenden Strompreisen ist ein Speicher oft sinnvoll.",
        category=HelpCategory.PV_SYSTEMS,
        tags=["speicher", "batterie", "wirtschaftlichkeit"],
        created_at=datetime.now()
    )
    
    _faqs["faq_004"] = FAQ(
        id="faq_004",
        question="Wie funktioniert die PDF-Generierung?",
        answer="Die PDF-Generierung erstellt professionelle Angebote basierend auf Ihren Berechnungen. Wählen Sie eine Vorlage, passen Sie das Design an und generieren Sie das PDF mit einem Klick. Das PDF enthält alle relevanten Daten, Diagramme und Ihr Firmenlogo.",
        category=HelpCategory.PDF_GENERATION,
        tags=["pdf", "angebot", "generierung"],
        created_at=datetime.now()
    )
    
    _faqs["faq_005"] = FAQ(
        id="faq_005",
        question="Was ist die Jahresarbeitszahl (JAZ)?",
        answer="Die JAZ gibt an, wie effizient eine Wärmepumpe über das gesamte Jahr arbeitet. Eine JAZ von 4 bedeutet: Aus 1 kWh Strom werden 4 kWh Wärme erzeugt. Typische Werte: Luft-Wasser 3-4, Sole-Wasser 4-5.",
        category=HelpCategory.HEAT_PUMPS,
        tags=["jaz", "effizienz", "wärmepumpe"],
        created_at=datetime.now()
    )
    
    # Video Tutorials
    _video_tutorials["video_001"] = VideoTutorial(
        id="video_001",
        title="Erstes Projekt erstellen",
        description="Lernen Sie, wie Sie Ihr erstes Projekt in Solar Calculator Pro erstellen und konfigurieren.",
        video_url="https://example.com/videos/first-project",
        duration_seconds=300,
        category=HelpCategory.GETTING_STARTED,
        tags=["projekt", "erstellen", "tutorial"],
        created_at=datetime.now()
    )
    
    _video_tutorials["video_002"] = VideoTutorial(
        id="video_002",
        title="PV-Anlage berechnen",
        description="Schritt-für-Schritt Anleitung zur Berechnung einer Photovoltaikanlage.",
        video_url="https://example.com/videos/pv-calculation",
        duration_seconds=480,
        category=HelpCategory.PV_SYSTEMS,
        tags=["pv", "berechnung", "tutorial"],
        created_at=datetime.now()
    )
    
    _video_tutorials["video_003"] = VideoTutorial(
        id="video_003",
        title="PDF-Angebot erstellen",
        description="So erstellen Sie professionelle PDF-Angebote für Ihre Kunden.",
        video_url="https://example.com/videos/pdf-generation",
        duration_seconds=360,
        category=HelpCategory.PDF_GENERATION,
        tags=["pdf", "angebot", "tutorial"],
        created_at=datetime.now()
    )


init_help_content()


# ==================== Helper Functions ====================

def search_content(query: str, category: Optional[HelpCategory] = None) -> List[SearchResult]:
    """Search help content"""
    results = []
    query_lower = query.lower()
    
    # Search articles
    for content in _help_content.values():
        if category and content.category != category:
            continue
        
        score = 0
        if query_lower in content.title.lower():
            score += 10
        if query_lower in content.content.lower():
            score += 5
        if any(query_lower in tag.lower() for tag in content.tags):
            score += 3
        
        if score > 0:
            excerpt = content.content[:200] + "..." if len(content.content) > 200 else content.content
            results.append(SearchResult(
                id=content.id,
                title=content.title,
                content_type=content.content_type,
                category=content.category,
                excerpt=excerpt,
                relevance_score=score
            ))
    
    # Search FAQs
    for faq in _faqs.values():
        if category and faq.category != category:
            continue
        
        score = 0
        if query_lower in faq.question.lower():
            score += 8
        if query_lower in faq.answer.lower():
            score += 4
        
        if score > 0:
            results.append(SearchResult(
                id=faq.id,
                title=faq.question,
                content_type=ContentType.FAQ,
                category=faq.category,
                excerpt=faq.answer[:200] + "..." if len(faq.answer) > 200 else faq.answer,
                relevance_score=score
            ))
    
    # Sort by relevance
    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return results


def get_context_help(context_key: str) -> List[HelpContent]:
    """Get context-sensitive help"""
    return [content for content in _help_content.values() if context_key in content.context_keys]


# ==================== API Endpoints ====================

@router.get("/articles")
async def get_help_articles(
    category: Optional[HelpCategory] = None,
    content_type: Optional[ContentType] = None,
    limit: int = 20
):
    """Get help articles."""
    articles = list(_help_content.values())
    
    if category:
        articles = [a for a in articles if a.category == category]
    if content_type:
        articles = [a for a in articles if a.content_type == content_type]
    
    articles.sort(key=lambda a: a.views, reverse=True)
    
    return {
        "articles": articles[:limit],
        "total": len(articles)
    }


@router.get("/articles/{article_id}")
async def get_help_article(article_id: str):
    """Get specific help article."""
    if article_id not in _help_content:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    article = _help_content[article_id]
    article.views += 1
    
    return {"article": article}


@router.get("/faqs")
async def get_faqs(category: Optional[HelpCategory] = None, limit: int = 50):
    """Get FAQs."""
    faqs = list(_faqs.values())
    
    if category:
        faqs = [f for f in faqs if f.category == category]
    
    faqs.sort(key=lambda f: f.views, reverse=True)
    
    return {
        "faqs": faqs[:limit],
        "total": len(faqs)
    }


@router.get("/faqs/{faq_id}")
async def get_faq(faq_id: str):
    """Get specific FAQ."""
    if faq_id not in _faqs:
        raise HTTPException(status_code=404, detail="FAQ nicht gefunden")
    
    faq = _faqs[faq_id]
    faq.views += 1
    
    return {"faq": faq}


@router.get("/videos")
async def get_video_tutorials(category: Optional[HelpCategory] = None, limit: int = 20):
    """Get video tutorials."""
    videos = list(_video_tutorials.values())
    
    if category:
        videos = [v for v in videos if v.category == category]
    
    videos.sort(key=lambda v: v.views, reverse=True)
    
    return {
        "videos": videos[:limit],
        "total": len(videos)
    }


@router.get("/videos/{video_id}")
async def get_video_tutorial(video_id: str):
    """Get specific video tutorial."""
    if video_id not in _video_tutorials:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")
    
    video = _video_tutorials[video_id]
    video.views += 1
    
    return {"video": video}


@router.get("/search")
async def search_help(
    q: str = Query(..., min_length=2, description="Suchbegriff"),
    category: Optional[HelpCategory] = None,
    limit: int = 20
):
    """Search help content."""
    results = search_content(q, category)
    
    return {
        "query": q,
        "results": results[:limit],
        "total": len(results)
    }


@router.get("/context/{context_key}")
async def get_context_sensitive_help(context_key: str):
    """Get context-sensitive help for a specific page/feature."""
    articles = get_context_help(context_key)
    
    return {
        "context_key": context_key,
        "articles": articles,
        "total": len(articles)
    }


@router.post("/articles/{article_id}/helpful")
async def mark_article_helpful(article_id: str, helpful: bool = True):
    """Mark article as helpful."""
    if article_id not in _help_content:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    if helpful:
        _help_content[article_id].helpful_votes += 1
    
    return {"article_id": article_id, "helpful_votes": _help_content[article_id].helpful_votes}


@router.post("/faqs/{faq_id}/helpful")
async def mark_faq_helpful(faq_id: str, helpful: bool = True):
    """Mark FAQ as helpful."""
    if faq_id not in _faqs:
        raise HTTPException(status_code=404, detail="FAQ nicht gefunden")
    
    if helpful:
        _faqs[faq_id].helpful_votes += 1
    
    return {"faq_id": faq_id, "helpful_votes": _faqs[faq_id].helpful_votes}


@router.get("/categories")
async def get_help_categories():
    """Get all help categories with counts."""
    categories = {}
    
    for cat in HelpCategory:
        articles = len([a for a in _help_content.values() if a.category == cat])
        faqs = len([f for f in _faqs.values() if f.category == cat])
        videos = len([v for v in _video_tutorials.values() if v.category == cat])
        
        categories[cat.value] = {
            "name": cat.value,
            "articles": articles,
            "faqs": faqs,
            "videos": videos,
            "total": articles + faqs + videos
        }
    
    return {"categories": categories}


@router.get("/quick-tips")
async def get_quick_tips(limit: int = 5):
    """Get quick tips for dashboard."""
    tips = [
        {
            "id": "tip_001",
            "title": "Tastenkürzel nutzen",
            "content": "Drücken Sie Strg+S um das aktuelle Projekt zu speichern.",
            "category": "productivity"
        },
        {
            "id": "tip_002",
            "title": "PDF-Vorschau",
            "content": "Nutzen Sie die Vorschau-Funktion bevor Sie das finale PDF generieren.",
            "category": "pdf"
        },
        {
            "id": "tip_003",
            "title": "Speicher-Dimensionierung",
            "content": "Ein Speicher von 1 kWh pro 1000 kWh Jahresverbrauch ist ein guter Richtwert.",
            "category": "calculation"
        },
        {
            "id": "tip_004",
            "title": "Kundendaten importieren",
            "content": "Sie können Kundendaten per CSV-Import schnell anlegen.",
            "category": "crm"
        },
        {
            "id": "tip_005",
            "title": "3D-Ansicht exportieren",
            "content": "Die 3D-Ansicht kann als Bild für Präsentationen exportiert werden.",
            "category": "visualization"
        }
    ]
    
    return {"tips": tips[:limit]}


@router.get("/health/check")
async def health_check():
    """Health check for help service."""
    return {
        "status": "healthy",
        "service": "help-documentation",
        "articles": len(_help_content),
        "faqs": len(_faqs),
        "videos": len(_video_tutorials),
        "timestamp": datetime.now().isoformat()
    }
