"""
Information Portal / News System API

Provides REST API for news and information portal:
- News/information portal in CRM
- Market news (subsidies, feed-in tariffs)
- Internal updates and announcements
- News categories and filtering
- Notification system for important news

Requirements: funktionen.txt - "Informationsportal"
Task: 263. Information Portal / News System
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/news", tags=["News Portal"])


# ==================== Enums ====================

class NewsCategory(str, Enum):
    SUBSIDIES = "subsidies"
    FEED_IN_TARIFFS = "feed_in_tariffs"
    REGULATIONS = "regulations"
    PRODUCTS = "products"
    COMPANY = "company"
    MARKET = "market"
    TECHNOLOGY = "technology"
    EVENTS = "events"


class NewsPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NewsStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class NotificationType(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"


# ==================== Pydantic Models ====================

class NewsArticle(BaseModel):
    """News article"""
    id: str
    title: str
    summary: str
    content: str
    category: NewsCategory
    priority: NewsPriority = NewsPriority.NORMAL
    status: NewsStatus = NewsStatus.PUBLISHED
    author: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    views: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class CreateNewsRequest(BaseModel):
    """Request to create news article"""
    title: str
    summary: str
    content: str
    category: NewsCategory
    priority: NewsPriority = NewsPriority.NORMAL
    author: str = "System"
    source: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    publish_immediately: bool = True
    send_notification: bool = False


class NewsNotification(BaseModel):
    """News notification"""
    id: str
    news_id: str
    news_title: str
    notification_type: NotificationType
    sent_at: datetime
    read: bool = False
    read_at: Optional[datetime] = None


class NotificationSettings(BaseModel):
    """User notification settings"""
    enabled: bool = True
    categories: List[NewsCategory] = list(NewsCategory)
    min_priority: NewsPriority = NewsPriority.NORMAL
    notification_types: List[NotificationType] = [NotificationType.IN_APP]
    email_digest: bool = False
    digest_frequency: str = "daily"


class FeedInTariff(BaseModel):
    """Feed-in tariff information"""
    id: str
    system_size_kwp_min: float
    system_size_kwp_max: float
    tariff_eur_kwh: float
    valid_from: datetime
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class Subsidy(BaseModel):
    """Subsidy/funding program"""
    id: str
    name: str
    description: str
    provider: str
    amount_type: str  # "fixed", "percentage", "per_kwp"
    amount_value: float
    max_amount: Optional[float] = None
    eligible_systems: List[str]
    requirements: List[str]
    application_url: Optional[str] = None
    valid_from: datetime
    valid_until: Optional[datetime] = None
    region: str = "Deutschland"


# ==================== Mock Data Store ====================

_news_store: Dict[str, NewsArticle] = {}
_notifications_store: Dict[str, List[NewsNotification]] = {}
_notification_settings: NotificationSettings = NotificationSettings()


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def create_mock_news() -> List[NewsArticle]:
    """Create mock news articles"""
    now = datetime.now()
    return [
        NewsArticle(
            id=generate_id("news"),
            title="Neue Einspeisevergütung ab Januar 2025",
            summary="Die Bundesnetzagentur hat die neuen Vergütungssätze für PV-Anlagen veröffentlicht.",
            content="Ab dem 1. Januar 2025 gelten neue Einspeisevergütungen für Photovoltaikanlagen...",
            category=NewsCategory.FEED_IN_TARIFFS,
            priority=NewsPriority.HIGH,
            author="Redaktion",
            source="Bundesnetzagentur",
            tags=["einspeisevergütung", "pv", "2025"],
            effective_date=datetime(2025, 1, 1),
            views=245,
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=5),
            published_at=now - timedelta(days=5)
        ),
        NewsArticle(
            id=generate_id("news"),
            title="KfW-Förderung für Wärmepumpen erhöht",
            summary="Die KfW erhöht die Fördersätze für Wärmepumpen auf bis zu 40%.",
            content="Im Rahmen der Bundesförderung für effiziente Gebäude (BEG) werden die Fördersätze...",
            category=NewsCategory.SUBSIDIES,
            priority=NewsPriority.HIGH,
            author="Redaktion",
            source="KfW",
            source_url="https://www.kfw.de",
            tags=["förderung", "wärmepumpe", "kfw"],
            views=189,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3),
            published_at=now - timedelta(days=3)
        ),
        NewsArticle(
            id=generate_id("news"),
            title="Neue Solarmodule mit 25% Wirkungsgrad",
            summary="Hersteller präsentiert neue Hochleistungsmodule mit Rekord-Wirkungsgrad.",
            content="Der Modulhersteller hat auf der Intersolar neue Module vorgestellt...",
            category=NewsCategory.PRODUCTS,
            priority=NewsPriority.NORMAL,
            author="Technik-Team",
            tags=["module", "innovation", "wirkungsgrad"],
            views=156,
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=7),
            published_at=now - timedelta(days=7)
        ),
        NewsArticle(
            id=generate_id("news"),
            title="Schulung: Neue Wärmepumpen-Modelle",
            summary="Interne Schulung zu den neuen Wärmepumpen-Produkten am 15.12.",
            content="Liebe Kollegen, am 15. Dezember findet eine Schulung zu den neuen Wärmepumpen statt...",
            category=NewsCategory.COMPANY,
            priority=NewsPriority.NORMAL,
            author="Vertriebsleitung",
            tags=["schulung", "intern", "wärmepumpe"],
            views=45,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
            published_at=now - timedelta(days=2)
        )
    ]


def create_mock_tariffs() -> List[FeedInTariff]:
    """Create mock feed-in tariffs"""
    return [
        FeedInTariff(
            id="tariff_1",
            system_size_kwp_min=0,
            system_size_kwp_max=10,
            tariff_eur_kwh=0.0820,
            valid_from=datetime(2024, 8, 1),
            notes="Anlagen bis 10 kWp"
        ),
        FeedInTariff(
            id="tariff_2",
            system_size_kwp_min=10,
            system_size_kwp_max=40,
            tariff_eur_kwh=0.0710,
            valid_from=datetime(2024, 8, 1),
            notes="Anlagen 10-40 kWp"
        ),
        FeedInTariff(
            id="tariff_3",
            system_size_kwp_min=40,
            system_size_kwp_max=100,
            tariff_eur_kwh=0.0580,
            valid_from=datetime(2024, 8, 1),
            notes="Anlagen 40-100 kWp"
        )
    ]


def create_mock_subsidies() -> List[Subsidy]:
    """Create mock subsidies"""
    return [
        Subsidy(
            id="sub_1",
            name="BEG Wärmepumpen-Förderung",
            description="Bundesförderung für effiziente Gebäude - Wärmepumpen",
            provider="BAFA/KfW",
            amount_type="percentage",
            amount_value=30,
            max_amount=21000,
            eligible_systems=["Wärmepumpe", "Luft-Wasser", "Sole-Wasser"],
            requirements=["Mindest-JAZ 2.7", "Hydraulischer Abgleich"],
            application_url="https://www.bafa.de",
            valid_from=datetime(2024, 1, 1),
            region="Deutschland"
        ),
        Subsidy(
            id="sub_2",
            name="Klimabonus",
            description="Zusätzlicher Bonus bei Austausch fossiler Heizung",
            provider="BAFA",
            amount_type="percentage",
            amount_value=20,
            max_amount=None,
            eligible_systems=["Wärmepumpe"],
            requirements=["Austausch Öl/Gas-Heizung"],
            valid_from=datetime(2024, 1, 1),
            region="Deutschland"
        )
    ]


# Initialize mock data
for article in create_mock_news():
    _news_store[article.id] = article


# ==================== API Endpoints ====================

@router.get("/articles")
async def get_news_articles(
    category: Optional[NewsCategory] = None,
    priority: Optional[NewsPriority] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0
):
    """Get news articles with optional filters."""
    articles = [a for a in _news_store.values() if a.status == NewsStatus.PUBLISHED]
    
    if category:
        articles = [a for a in articles if a.category == category]
    if priority:
        articles = [a for a in articles if a.priority == priority]
    if search:
        search_lower = search.lower()
        articles = [a for a in articles if search_lower in a.title.lower() or search_lower in a.summary.lower()]
    if tag:
        articles = [a for a in articles if tag.lower() in [t.lower() for t in a.tags]]
    
    articles.sort(key=lambda a: a.published_at or a.created_at, reverse=True)
    
    return {
        "articles": articles[offset:offset + limit],
        "total": len(articles),
        "has_more": len(articles) > offset + limit
    }


@router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Get a specific news article."""
    if article_id not in _news_store:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    article = _news_store[article_id]
    article.views += 1
    
    return {"article": article}


@router.post("/articles")
async def create_article(request: CreateNewsRequest):
    """Create a new news article."""
    article_id = generate_id("news")
    now = datetime.now()
    
    article = NewsArticle(
        id=article_id,
        title=request.title,
        summary=request.summary,
        content=request.content,
        category=request.category,
        priority=request.priority,
        status=NewsStatus.PUBLISHED if request.publish_immediately else NewsStatus.DRAFT,
        author=request.author,
        source=request.source,
        source_url=request.source_url,
        image_url=request.image_url,
        tags=request.tags,
        effective_date=request.effective_date,
        expiry_date=request.expiry_date,
        created_at=now,
        updated_at=now,
        published_at=now if request.publish_immediately else None
    )
    
    _news_store[article_id] = article
    
    return {
        "article": article,
        "notification_sent": request.send_notification
    }


@router.put("/articles/{article_id}")
async def update_article(article_id: str, request: CreateNewsRequest):
    """Update a news article."""
    if article_id not in _news_store:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    existing = _news_store[article_id]
    
    updated = NewsArticle(
        id=article_id,
        title=request.title,
        summary=request.summary,
        content=request.content,
        category=request.category,
        priority=request.priority,
        status=existing.status,
        author=request.author,
        source=request.source,
        source_url=request.source_url,
        image_url=request.image_url,
        tags=request.tags,
        effective_date=request.effective_date,
        expiry_date=request.expiry_date,
        views=existing.views,
        created_at=existing.created_at,
        updated_at=datetime.now(),
        published_at=existing.published_at
    )
    
    _news_store[article_id] = updated
    
    return {"article": updated, "updated": True}


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str):
    """Delete a news article."""
    if article_id not in _news_store:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    
    del _news_store[article_id]
    
    return {"deleted": True, "article_id": article_id}


@router.get("/categories")
async def get_categories():
    """Get all news categories with counts."""
    articles = list(_news_store.values())
    
    return {
        "categories": [
            {
                "id": cat.value,
                "name": cat.name.replace("_", " ").title(),
                "count": len([a for a in articles if a.category == cat])
            }
            for cat in NewsCategory
        ]
    }


@router.get("/feed-in-tariffs")
async def get_feed_in_tariffs():
    """Get current feed-in tariffs."""
    tariffs = create_mock_tariffs()
    
    return {
        "tariffs": tariffs,
        "last_updated": datetime.now().isoformat(),
        "source": "Bundesnetzagentur"
    }


@router.get("/subsidies")
async def get_subsidies(
    system_type: Optional[str] = None,
    region: Optional[str] = None
):
    """Get available subsidies and funding programs."""
    subsidies = create_mock_subsidies()
    
    if system_type:
        subsidies = [s for s in subsidies if system_type in s.eligible_systems]
    if region:
        subsidies = [s for s in subsidies if s.region == region]
    
    return {
        "subsidies": subsidies,
        "total": len(subsidies),
        "last_updated": datetime.now().isoformat()
    }


@router.get("/notifications")
async def get_notifications(
    user_id: str = "default",
    unread_only: bool = False
):
    """Get user notifications."""
    notifications = _notifications_store.get(user_id, [])
    
    if unread_only:
        notifications = [n for n in notifications if not n.read]
    
    return {
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n.read])
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str = "default"):
    """Mark notification as read."""
    notifications = _notifications_store.get(user_id, [])
    
    for n in notifications:
        if n.id == notification_id:
            n.read = True
            n.read_at = datetime.now()
            return {"notification": n, "updated": True}
    
    raise HTTPException(status_code=404, detail="Benachrichtigung nicht gefunden")


@router.get("/notification-settings")
async def get_notification_settings(user_id: str = "default"):
    """Get notification settings."""
    return {"settings": _notification_settings}


@router.put("/notification-settings")
async def update_notification_settings(settings: NotificationSettings, user_id: str = "default"):
    """Update notification settings."""
    global _notification_settings
    _notification_settings = settings
    return {"settings": _notification_settings, "updated": True}


@router.get("/dashboard")
async def get_news_dashboard():
    """Get news dashboard with summary."""
    articles = list(_news_store.values())
    now = datetime.now()
    recent = [a for a in articles if a.published_at and (now - a.published_at).days <= 7]
    
    return {
        "total_articles": len(articles),
        "recent_articles": len(recent),
        "urgent_news": [a for a in articles if a.priority == NewsPriority.URGENT][:3],
        "top_viewed": sorted(articles, key=lambda a: a.views, reverse=True)[:5],
        "by_category": {cat.value: len([a for a in articles if a.category == cat]) for cat in NewsCategory},
        "current_tariffs": create_mock_tariffs(),
        "active_subsidies": len(create_mock_subsidies())
    }


@router.get("/health/check")
async def health_check():
    """Health check for news portal service."""
    return {
        "status": "healthy",
        "service": "news-portal",
        "articles_count": len(_news_store),
        "timestamp": datetime.now().isoformat()
    }
