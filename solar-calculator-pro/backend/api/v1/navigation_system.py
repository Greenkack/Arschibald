"""
Multi-Page Navigation System API

Provides REST API for navigation system:
- Page-based navigation
- Sidebar with menu items
- Breadcrumb navigation
- Deep linking to pages
- Navigation history

Requirements: funktionen.txt - "Multi-Page Streamlit App"
Task: 280. Multi-Page Navigation System
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/navigation", tags=["Navigation System"])


# ==================== Enums ====================

class PageCategory(str, Enum):
    MAIN = "main"
    CALCULATOR = "calculator"
    CRM = "crm"
    ADMIN = "admin"
    REPORTS = "reports"
    SETTINGS = "settings"


class MenuItemType(str, Enum):
    PAGE = "page"
    SECTION = "section"
    DIVIDER = "divider"
    EXTERNAL_LINK = "external_link"


# ==================== Pydantic Models ====================

class PageDefinition(BaseModel):
    """Page definition"""
    id: str
    title: str
    path: str
    category: PageCategory
    icon: Optional[str] = None
    description: Optional[str] = None
    requires_auth: bool = True
    required_permissions: List[str] = []
    visible_in_menu: bool = True
    order: int = 0
    parent_id: Optional[str] = None


class MenuItem(BaseModel):
    """Menu item"""
    id: str
    type: MenuItemType = MenuItemType.PAGE
    title: str
    path: Optional[str] = None
    icon: Optional[str] = None
    badge: Optional[str] = None
    children: List["MenuItem"] = []
    expanded: bool = False
    active: bool = False
    disabled: bool = False
    order: int = 0


class Breadcrumb(BaseModel):
    """Breadcrumb item"""
    title: str
    path: str
    icon: Optional[str] = None
    is_current: bool = False


class NavigationState(BaseModel):
    """Current navigation state"""
    current_page_id: str
    current_path: str
    breadcrumbs: List[Breadcrumb]
    sidebar_collapsed: bool = False
    history: List[str] = []


class DeepLink(BaseModel):
    """Deep link definition"""
    id: str
    path: str
    page_id: str
    params: Dict[str, str] = {}
    title: str
    created_at: datetime


class NavigationHistory(BaseModel):
    """Navigation history entry"""
    page_id: str
    path: str
    title: str
    timestamp: datetime
    params: Dict[str, str] = {}


class SidebarConfig(BaseModel):
    """Sidebar configuration"""
    collapsed: bool = False
    width_expanded: int = 280
    width_collapsed: int = 64
    show_icons: bool = True
    show_labels: bool = True
    enable_hover_expand: bool = True


# ==================== Page Definitions ====================

DEFAULT_PAGES = [
    # Main
    PageDefinition(id="dashboard", title="Dashboard", path="/", category=PageCategory.MAIN, icon="home", order=1),
    PageDefinition(id="projects", title="Projekte", path="/projects", category=PageCategory.MAIN, icon="folder", order=2),
    
    # Calculator
    PageDefinition(id="solar_calc", title="Solar-Kalkulator", path="/calculator/solar", category=PageCategory.CALCULATOR, icon="sun", order=10),
    PageDefinition(id="heatpump_calc", title="Wärmepumpen-Kalkulator", path="/calculator/heatpump", category=PageCategory.CALCULATOR, icon="thermometer", order=11),
    PageDefinition(id="combined_calc", title="Kombinierte Berechnung", path="/calculator/combined", category=PageCategory.CALCULATOR, icon="zap", order=12),
    PageDefinition(id="quick_calc", title="Schnellkalkulation", path="/calculator/quick", category=PageCategory.CALCULATOR, icon="flash", order=13),
    
    # CRM
    PageDefinition(id="customers", title="Kunden", path="/crm/customers", category=PageCategory.CRM, icon="users", order=20),
    PageDefinition(id="offers", title="Angebote", path="/crm/offers", category=PageCategory.CRM, icon="file-text", order=21),
    PageDefinition(id="calendar", title="Kalender", path="/crm/calendar", category=PageCategory.CRM, icon="calendar", order=22),
    PageDefinition(id="tasks", title="Aufgaben", path="/crm/tasks", category=PageCategory.CRM, icon="check-square", order=23),
    
    # Reports
    PageDefinition(id="reports_overview", title="Berichte", path="/reports", category=PageCategory.REPORTS, icon="bar-chart", order=30),
    PageDefinition(id="pdf_generator", title="PDF-Generator", path="/reports/pdf", category=PageCategory.REPORTS, icon="file", order=31),
    
    # Admin
    PageDefinition(id="admin_users", title="Benutzer", path="/admin/users", category=PageCategory.ADMIN, icon="user", order=40, required_permissions=["admin:users"]),
    PageDefinition(id="admin_products", title="Produkte", path="/admin/products", category=PageCategory.ADMIN, icon="package", order=41, required_permissions=["admin:products"]),
    PageDefinition(id="admin_pricing", title="Preismatrix", path="/admin/pricing", category=PageCategory.ADMIN, icon="dollar-sign", order=42, required_permissions=["admin:pricing"]),
    PageDefinition(id="admin_companies", title="Firmen", path="/admin/companies", category=PageCategory.ADMIN, icon="building", order=43, required_permissions=["admin:companies"]),
    PageDefinition(id="admin_tariffs", title="Tarife", path="/admin/tariffs", category=PageCategory.ADMIN, icon="tag", order=44, required_permissions=["admin:tariffs"]),
    
    # Settings
    PageDefinition(id="settings", title="Einstellungen", path="/settings", category=PageCategory.SETTINGS, icon="settings", order=50),
    PageDefinition(id="settings_profile", title="Profil", path="/settings/profile", category=PageCategory.SETTINGS, icon="user", order=51, parent_id="settings"),
    PageDefinition(id="settings_system", title="System", path="/settings/system", category=PageCategory.SETTINGS, icon="sliders", order=52, parent_id="settings"),
]


# ==================== Data Store ====================

_pages: Dict[str, PageDefinition] = {p.id: p for p in DEFAULT_PAGES}
_navigation_history: Dict[str, List[NavigationHistory]] = {}  # user_id -> history
_sidebar_config = SidebarConfig()


# ==================== Helper Functions ====================

def build_menu_tree(pages: List[PageDefinition], user_permissions: List[str] = None) -> List[MenuItem]:
    """Build menu tree from pages"""
    categories = {}
    
    for page in sorted(pages, key=lambda p: p.order):
        if not page.visible_in_menu:
            continue
        
        # Check permissions
        if page.required_permissions and user_permissions:
            if not any(p in user_permissions for p in page.required_permissions):
                continue
        
        cat = page.category.value
        if cat not in categories:
            categories[cat] = []
        
        categories[cat].append(MenuItem(
            id=page.id,
            type=MenuItemType.PAGE,
            title=page.title,
            path=page.path,
            icon=page.icon,
            order=page.order
        ))
    
    # Build final menu
    menu = []
    category_titles = {
        "main": "Hauptmenü",
        "calculator": "Kalkulator",
        "crm": "CRM",
        "reports": "Berichte",
        "admin": "Administration",
        "settings": "Einstellungen"
    }
    
    for cat_id, items in categories.items():
        if cat_id == "main":
            menu.extend(items)
        else:
            menu.append(MenuItem(
                id=f"section_{cat_id}",
                type=MenuItemType.SECTION,
                title=category_titles.get(cat_id, cat_id),
                children=items,
                order=items[0].order if items else 0
            ))
    
    return sorted(menu, key=lambda m: m.order)


def build_breadcrumbs(page_id: str) -> List[Breadcrumb]:
    """Build breadcrumbs for page"""
    breadcrumbs = [Breadcrumb(title="Home", path="/", icon="home")]
    
    if page_id not in _pages:
        return breadcrumbs
    
    page = _pages[page_id]
    
    # Add parent if exists
    if page.parent_id and page.parent_id in _pages:
        parent = _pages[page.parent_id]
        breadcrumbs.append(Breadcrumb(title=parent.title, path=parent.path))
    
    # Add category
    category_paths = {
        PageCategory.CALCULATOR: ("/calculator", "Kalkulator"),
        PageCategory.CRM: ("/crm", "CRM"),
        PageCategory.ADMIN: ("/admin", "Administration"),
        PageCategory.REPORTS: ("/reports", "Berichte"),
        PageCategory.SETTINGS: ("/settings", "Einstellungen"),
    }
    
    if page.category in category_paths and page.category != PageCategory.MAIN:
        path, title = category_paths[page.category]
        if not any(b.path == path for b in breadcrumbs):
            breadcrumbs.append(Breadcrumb(title=title, path=path))
    
    # Add current page
    breadcrumbs.append(Breadcrumb(title=page.title, path=page.path, is_current=True))
    
    return breadcrumbs


# ==================== API Endpoints ====================

@router.get("/pages")
async def get_pages(category: Optional[PageCategory] = None, include_hidden: bool = False):
    """Get all page definitions."""
    pages = list(_pages.values())
    
    if category:
        pages = [p for p in pages if p.category == category]
    if not include_hidden:
        pages = [p for p in pages if p.visible_in_menu]
    
    return {
        "pages": sorted(pages, key=lambda p: p.order),
        "total": len(pages)
    }


@router.get("/pages/{page_id}")
async def get_page(page_id: str):
    """Get specific page definition."""
    if page_id not in _pages:
        raise HTTPException(status_code=404, detail="Seite nicht gefunden")
    
    return {"page": _pages[page_id]}


@router.get("/menu")
async def get_menu(user_permissions: Optional[str] = None):
    """Get menu structure."""
    permissions = user_permissions.split(",") if user_permissions else None
    menu = build_menu_tree(list(_pages.values()), permissions)
    
    return {"menu": menu}


@router.get("/breadcrumbs/{page_id}")
async def get_breadcrumbs(page_id: str):
    """Get breadcrumbs for page."""
    breadcrumbs = build_breadcrumbs(page_id)
    return {"breadcrumbs": breadcrumbs}


@router.get("/state")
async def get_navigation_state(current_path: str = "/"):
    """Get current navigation state."""
    # Find page by path
    page_id = "dashboard"
    for pid, page in _pages.items():
        if page.path == current_path:
            page_id = pid
            break
    
    return NavigationState(
        current_page_id=page_id,
        current_path=current_path,
        breadcrumbs=build_breadcrumbs(page_id),
        sidebar_collapsed=_sidebar_config.collapsed
    )


@router.post("/navigate")
async def navigate_to(page_id: str, user_id: str = "default", params: Dict[str, str] = None):
    """Navigate to page and record history."""
    if page_id not in _pages:
        raise HTTPException(status_code=404, detail="Seite nicht gefunden")
    
    page = _pages[page_id]
    
    # Record history
    if user_id not in _navigation_history:
        _navigation_history[user_id] = []
    
    _navigation_history[user_id].append(NavigationHistory(
        page_id=page_id,
        path=page.path,
        title=page.title,
        timestamp=datetime.now(),
        params=params or {}
    ))
    
    # Keep only last 50 entries
    if len(_navigation_history[user_id]) > 50:
        _navigation_history[user_id] = _navigation_history[user_id][-50:]
    
    return {
        "page": page,
        "breadcrumbs": build_breadcrumbs(page_id),
        "navigated": True
    }


@router.get("/history")
async def get_history(user_id: str = "default", limit: int = Query(default=20, le=50)):
    """Get navigation history."""
    history = _navigation_history.get(user_id, [])
    return {
        "history": list(reversed(history[-limit:])),
        "total": len(history)
    }


@router.delete("/history")
async def clear_history(user_id: str = "default"):
    """Clear navigation history."""
    if user_id in _navigation_history:
        _navigation_history[user_id] = []
    return {"cleared": True}


@router.get("/sidebar/config")
async def get_sidebar_config():
    """Get sidebar configuration."""
    return {"config": _sidebar_config}


@router.put("/sidebar/config")
async def update_sidebar_config(config: SidebarConfig):
    """Update sidebar configuration."""
    global _sidebar_config
    _sidebar_config = config
    return {"config": _sidebar_config, "updated": True}


@router.put("/sidebar/toggle")
async def toggle_sidebar():
    """Toggle sidebar collapsed state."""
    _sidebar_config.collapsed = not _sidebar_config.collapsed
    return {"collapsed": _sidebar_config.collapsed}


@router.get("/deep-link")
async def create_deep_link(page_id: str, params: Optional[str] = None):
    """Create deep link for page."""
    if page_id not in _pages:
        raise HTTPException(status_code=404, detail="Seite nicht gefunden")
    
    page = _pages[page_id]
    param_dict = {}
    
    if params:
        for p in params.split(","):
            if "=" in p:
                k, v = p.split("=", 1)
                param_dict[k] = v
    
    # Build URL
    url = page.path
    if param_dict:
        url += "?" + "&".join(f"{k}={v}" for k, v in param_dict.items())
    
    return DeepLink(
        id=f"dl_{uuid.uuid4().hex[:8]}",
        path=url,
        page_id=page_id,
        params=param_dict,
        title=page.title,
        created_at=datetime.now()
    )


@router.get("/search")
async def search_pages(query: str):
    """Search pages by title or description."""
    query_lower = query.lower()
    results = []
    
    for page in _pages.values():
        if query_lower in page.title.lower() or (page.description and query_lower in page.description.lower()):
            results.append(page)
    
    return {"results": results, "query": query}


@router.get("/categories")
async def get_categories():
    """Get page categories."""
    return {
        "categories": [
            {"id": "main", "name": "Hauptmenü", "icon": "home"},
            {"id": "calculator", "name": "Kalkulator", "icon": "calculator"},
            {"id": "crm", "name": "CRM", "icon": "users"},
            {"id": "reports", "name": "Berichte", "icon": "bar-chart"},
            {"id": "admin", "name": "Administration", "icon": "settings"},
            {"id": "settings", "name": "Einstellungen", "icon": "sliders"}
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for navigation service."""
    return {
        "status": "healthy",
        "service": "navigation-system",
        "pages_count": len(_pages),
        "timestamp": datetime.now().isoformat()
    }
