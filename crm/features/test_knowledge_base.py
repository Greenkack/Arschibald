"""
Test Suite for Knowledge Base Manager (Task 17.1)

Tests für:
- Artikel-Erstellung und -Verwaltung
- Kategorien-Hierarchie
- Volltextsuche (SQLite FTS5)
- Bewertungssystem
- Statistiken

Author: CRM System Enhancement
Date: 2024
"""

import sqlite3
import pytest
import tempfile
import os
from datetime import datetime

# Import the module to test
try:
    from crm.features.knowledge_base import KnowledgeBaseManager
    from database import create_knowledge_base_tables
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from crm.features.knowledge_base import KnowledgeBaseManager
    from database import create_knowledge_base_tables


@pytest.fixture
def test_db():
    """Erstellt eine temporäre Test-Datenbank."""
    # Erstelle temporäre Datei
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Verbindung erstellen
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Tabellen erstellen
    create_knowledge_base_tables(conn)
    
    yield conn
    
    # Cleanup
    conn.close()
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def kb_manager(test_db):
    """Erstellt einen KnowledgeBaseManager mit Test-DB."""
    return KnowledgeBaseManager(test_db)


# ============================================================================
# KATEGORIEN-TESTS
# ============================================================================

def test_create_category(kb_manager):
    """Test: Kategorie erstellen."""
    category_id = kb_manager.create_category(
        name="Solar-Technik",
        description="Alles über Solartechnik",
        icon="☀️",
        sort_order=1,
        created_by="test_user"
    )
    
    assert category_id > 0
    
    # Kategorie laden und prüfen
    category = kb_manager.get_category(category_id)
    assert category is not None
    assert category['name'] == "Solar-Technik"
    assert category['description'] == "Alles über Solartechnik"
    assert category['icon'] == "☀️"
    assert category['sort_order'] == 1
    assert category['is_active'] == 1


def test_create_subcategory(kb_manager):
    """Test: Unterkategorie erstellen."""
    # Parent-Kategorie
    parent_id = kb_manager.create_category(name="Hauptkategorie")
    
    # Unterkategorie
    child_id = kb_manager.create_category(
        name="Unterkategorie",
        parent_id=parent_id
    )
    
    child = kb_manager.get_category(child_id)
    assert child['parent_id'] == parent_id


def test_get_all_categories(kb_manager):
    """Test: Alle Kategorien laden."""
    # Erstelle mehrere Kategorien
    kb_manager.create_category(name="Kategorie 1", sort_order=2)
    kb_manager.create_category(name="Kategorie 2", sort_order=1)
    cat3_id = kb_manager.create_category(name="Kategorie 3", sort_order=3)
    
    # Deaktiviere Kategorie 3
    kb_manager.update_category(cat3_id, is_active=False)
    
    # Nur aktive laden
    categories = kb_manager.get_all_categories(active_only=True)
    assert len(categories) == 2
    
    # Alle laden
    categories = kb_manager.get_all_categories(active_only=False)
    assert len(categories) == 3


def test_get_category_tree(kb_manager):
    """Test: Kategorien-Hierarchie laden."""
    # Erstelle Hierarchie
    root1 = kb_manager.create_category(name="Root 1")
    root2 = kb_manager.create_category(name="Root 2")
    child1 = kb_manager.create_category(name="Child 1", parent_id=root1)
    child2 = kb_manager.create_category(name="Child 2", parent_id=root1)
    grandchild = kb_manager.create_category(name="Grandchild", parent_id=child1)
    
    # Baum laden
    tree = kb_manager.get_category_tree()
    
    assert len(tree) == 2  # 2 Root-Kategorien
    assert len(tree[0]['children']) == 2  # Root 1 hat 2 Kinder
    assert len(tree[0]['children'][0]['children']) == 1  # Child 1 hat 1 Kind


def test_update_category(kb_manager):
    """Test: Kategorie aktualisieren."""
    category_id = kb_manager.create_category(name="Alt")
    
    success = kb_manager.update_category(
        category_id,
        name="Neu",
        description="Neue Beschreibung",
        is_active=False
    )
    
    assert success is True
    
    category = kb_manager.get_category(category_id)
    assert category['name'] == "Neu"
    assert category['description'] == "Neue Beschreibung"
    assert category['is_active'] == 0


def test_delete_category(kb_manager):
    """Test: Kategorie löschen."""
    category_id = kb_manager.create_category(name="Zu löschen")
    
    success = kb_manager.delete_category(category_id)
    assert success is True
    
    category = kb_manager.get_category(category_id)
    assert category is None


def test_delete_category_with_children_fails(kb_manager):
    """Test: Kategorie mit Kindern kann nicht gelöscht werden (ohne cascade)."""
    parent_id = kb_manager.create_category(name="Parent")
    child_id = kb_manager.create_category(name="Child", parent_id=parent_id)
    
    with pytest.raises(ValueError):
        kb_manager.delete_category(parent_id, cascade=False)


# ============================================================================
# ARTIKEL-TESTS
# ============================================================================

def test_create_article(kb_manager):
    """Test: Artikel erstellen."""
    category_id = kb_manager.create_category(name="Test-Kategorie")
    
    article_id = kb_manager.create_article(
        title="Test-Artikel",
        content="# Überschrift\n\nDies ist ein Test-Artikel mit **Markdown**.",
        category_id=category_id,
        tags="test, markdown",
        author="Test User",
        is_published=True,
        is_featured=False
    )
    
    assert article_id > 0
    
    # Artikel laden
    article = kb_manager.get_article(article_id)
    assert article is not None
    assert article['title'] == "Test-Artikel"
    assert "Markdown" in article['content']
    assert article['category_id'] == category_id
    assert article['tags'] == "test, markdown"
    assert article['author'] == "Test User"
    assert article['is_published'] == 1
    assert article['is_featured'] == 0
    assert article['view_count'] == 0


def test_get_article_increment_views(kb_manager):
    """Test: Artikel laden mit View-Counter."""
    article_id = kb_manager.create_article(
        title="Test",
        content="Content",
        is_published=True
    )
    
    # Laden ohne Increment
    article = kb_manager.get_article(article_id, increment_views=False)
    assert article['view_count'] == 0
    
    # Laden mit Increment
    article = kb_manager.get_article(article_id, increment_views=True)
    assert article['view_count'] == 1
    
    # Nochmal
    article = kb_manager.get_article(article_id, increment_views=True)
    assert article['view_count'] == 2


def test_get_all_articles(kb_manager):
    """Test: Alle Artikel laden mit Filterung."""
    cat1 = kb_manager.create_category(name="Kategorie 1")
    cat2 = kb_manager.create_category(name="Kategorie 2")
    
    # Erstelle verschiedene Artikel
    kb_manager.create_article(title="Artikel 1", content="Content", category_id=cat1, is_published=True)
    kb_manager.create_article(title="Artikel 2", content="Content", category_id=cat1, is_published=False)
    kb_manager.create_article(title="Artikel 3", content="Content", category_id=cat2, is_published=True, is_featured=True)
    
    # Alle veröffentlichten
    articles = kb_manager.get_all_articles(published_only=True)
    assert len(articles) == 2
    
    # Nur Kategorie 1
    articles = kb_manager.get_all_articles(category_id=cat1, published_only=False)
    assert len(articles) == 2
    
    # Nur Featured
    articles = kb_manager.get_all_articles(featured_only=True)
    assert len(articles) == 1


def test_update_article(kb_manager):
    """Test: Artikel aktualisieren."""
    article_id = kb_manager.create_article(
        title="Alt",
        content="Alter Inhalt",
        is_published=False
    )
    
    success = kb_manager.update_article(
        article_id,
        title="Neu",
        content="Neuer Inhalt",
        is_published=True,
        is_featured=True
    )
    
    assert success is True
    
    article = kb_manager.get_article(article_id)
    assert article['title'] == "Neu"
    assert article['content'] == "Neuer Inhalt"
    assert article['is_published'] == 1
    assert article['is_featured'] == 1


def test_delete_article(kb_manager):
    """Test: Artikel löschen."""
    article_id = kb_manager.create_article(title="Zu löschen", content="Content")
    
    success = kb_manager.delete_article(article_id)
    assert success is True
    
    article = kb_manager.get_article(article_id)
    assert article is None


# ============================================================================
# VOLLTEXTSUCHE-TESTS
# ============================================================================

def test_search_articles(kb_manager):
    """Test: Volltextsuche."""
    # Erstelle Artikel mit verschiedenen Inhalten
    kb_manager.create_article(
        title="Photovoltaik Grundlagen",
        content="Photovoltaik wandelt Sonnenlicht in elektrische Energie um.",
        tags="solar, pv",
        is_published=True
    )
    kb_manager.create_article(
        title="Wärmepumpen Installation",
        content="Wärmepumpen nutzen Umweltwärme zum Heizen.",
        tags="wärmepumpe, heizung",
        is_published=True
    )
    kb_manager.create_article(
        title="Solar und Wärmepumpe kombinieren",
        content="Die Kombination von Photovoltaik und Wärmepumpe ist sehr effizient.",
        tags="solar, wärmepumpe, kombination",
        is_published=True
    )
    
    # Suche nach "Photovoltaik"
    results = kb_manager.search_articles("Photovoltaik")
    assert len(results) >= 2  # Mindestens 2 Artikel enthalten "Photovoltaik"
    
    # Suche nach "Wärmepumpe"
    results = kb_manager.search_articles("Wärmepumpe")
    assert len(results) >= 2
    
    # Suche nach "Solar"
    results = kb_manager.search_articles("Solar")
    assert len(results) >= 2


def test_search_articles_published_only(kb_manager):
    """Test: Suche nur in veröffentlichten Artikeln."""
    kb_manager.create_article(
        title="Veröffentlicht",
        content="Dieser Artikel ist veröffentlicht und enthält Photovoltaik.",
        is_published=True
    )
    kb_manager.create_article(
        title="Entwurf",
        content="Dieser Artikel ist ein Entwurf und enthält auch Photovoltaik.",
        is_published=False
    )
    
    # Suche nur in veröffentlichten
    results = kb_manager.search_articles("Photovoltaik", published_only=True)
    assert len(results) == 1
    assert results[0]['title'] == "Veröffentlicht"
    
    # Suche in allen
    results = kb_manager.search_articles("Photovoltaik", published_only=False)
    assert len(results) == 2


# ============================================================================
# BEWERTUNGS-TESTS
# ============================================================================

def test_rate_article(kb_manager):
    """Test: Artikel bewerten."""
    article_id = kb_manager.create_article(title="Test", content="Content", is_published=True)
    
    success = kb_manager.rate_article(
        article_id=article_id,
        user_id="user1",
        rating=5,
        comment="Sehr hilfreich!"
    )
    
    assert success is True
    
    # Bewertungen laden
    ratings = kb_manager.get_article_ratings(article_id)
    assert len(ratings) == 1
    assert ratings[0]['rating'] == 5
    assert ratings[0]['comment'] == "Sehr hilfreich!"


def test_rate_article_invalid_rating(kb_manager):
    """Test: Ungültige Bewertung wird abgelehnt."""
    article_id = kb_manager.create_article(title="Test", content="Content")
    
    with pytest.raises(ValueError):
        kb_manager.rate_article(article_id, "user1", 6)  # Rating > 5
    
    with pytest.raises(ValueError):
        kb_manager.rate_article(article_id, "user1", 0)  # Rating < 1


def test_rate_article_update_existing(kb_manager):
    """Test: Bestehende Bewertung aktualisieren."""
    article_id = kb_manager.create_article(title="Test", content="Content")
    
    # Erste Bewertung
    kb_manager.rate_article(article_id, "user1", 3, "Okay")
    
    # Bewertung aktualisieren
    kb_manager.rate_article(article_id, "user1", 5, "Jetzt besser!")
    
    ratings = kb_manager.get_article_ratings(article_id)
    assert len(ratings) == 1  # Nur eine Bewertung pro User
    assert ratings[0]['rating'] == 5
    assert ratings[0]['comment'] == "Jetzt besser!"


def test_get_article_rating_stats(kb_manager):
    """Test: Bewertungs-Statistiken."""
    article_id = kb_manager.create_article(title="Test", content="Content")
    
    # Mehrere Bewertungen
    kb_manager.rate_article(article_id, "user1", 5)
    kb_manager.rate_article(article_id, "user2", 4)
    kb_manager.rate_article(article_id, "user3", 5)
    kb_manager.rate_article(article_id, "user4", 3)
    
    stats = kb_manager.get_article_rating_stats(article_id)
    
    assert stats['count'] == 4
    assert stats['avg_rating'] == 4.25  # (5+4+5+3)/4
    assert stats['distribution'][5] == 2
    assert stats['distribution'][4] == 1
    assert stats['distribution'][3] == 1


# ============================================================================
# STATISTIK-TESTS
# ============================================================================

def test_get_article_count_by_category(kb_manager):
    """Test: Artikel pro Kategorie zählen."""
    cat1 = kb_manager.create_category(name="Kategorie 1")
    cat2 = kb_manager.create_category(name="Kategorie 2")
    
    kb_manager.create_article(title="A1", content="C", category_id=cat1, is_published=True)
    kb_manager.create_article(title="A2", content="C", category_id=cat1, is_published=True)
    kb_manager.create_article(title="A3", content="C", category_id=cat1, is_published=False)  # Nicht veröffentlicht
    kb_manager.create_article(title="A4", content="C", category_id=cat2, is_published=True)
    
    count1 = kb_manager.get_article_count_by_category(cat1)
    count2 = kb_manager.get_article_count_by_category(cat2)
    
    assert count1 == 2  # Nur veröffentlichte
    assert count2 == 1


def test_get_top_rated_articles(kb_manager):
    """Test: Am besten bewertete Artikel."""
    # Erstelle Artikel mit Bewertungen
    a1 = kb_manager.create_article(title="Artikel 1", content="C", is_published=True)
    a2 = kb_manager.create_article(title="Artikel 2", content="C", is_published=True)
    a3 = kb_manager.create_article(title="Artikel 3", content="C", is_published=True)
    
    # Bewertungen
    kb_manager.rate_article(a1, "u1", 5)
    kb_manager.rate_article(a1, "u2", 5)
    
    kb_manager.rate_article(a2, "u1", 4)
    kb_manager.rate_article(a2, "u2", 4)
    
    kb_manager.rate_article(a3, "u1", 3)
    
    # Top-Artikel laden
    top = kb_manager.get_top_rated_articles(limit=2)
    
    assert len(top) == 2
    assert top[0]['id'] == a1  # Beste Bewertung
    assert top[1]['id'] == a2


def test_get_statistics(kb_manager):
    """Test: Gesamt-Statistiken."""
    cat1 = kb_manager.create_category(name="Kategorie 1")
    
    # Erstelle Artikel
    a1 = kb_manager.create_article(title="A1", content="C", category_id=cat1, is_published=True)
    a2 = kb_manager.create_article(title="A2", content="C", category_id=cat1, is_published=False)
    
    # Views simulieren
    kb_manager.get_article(a1, increment_views=True)
    kb_manager.get_article(a1, increment_views=True)
    kb_manager.get_article(a1, increment_views=True)
    
    # Bewertungen
    kb_manager.rate_article(a1, "u1", 5)
    kb_manager.rate_article(a1, "u2", 4)
    
    stats = kb_manager.get_statistics()
    
    assert stats['total_articles'] == 2
    assert stats['published_articles'] == 1
    assert stats['total_categories'] == 1
    assert stats['total_views'] == 3
    assert stats['total_ratings'] == 2
    assert stats['avg_rating'] == 4.5


# ============================================================================
# INTEGRATION-TESTS
# ============================================================================

def test_full_workflow(kb_manager):
    """Test: Vollständiger Workflow."""
    # 1. Kategorien erstellen
    root_cat = kb_manager.create_category(name="Solar-Technik", icon="☀️")
    sub_cat = kb_manager.create_category(name="Photovoltaik", parent_id=root_cat)
    
    # 2. Artikel erstellen
    article_id = kb_manager.create_article(
        title="PV-Module Vergleich",
        content="# PV-Module im Vergleich\n\n## Monokristallin vs. Polykristallin\n\nMonokristalline Module haben einen höheren Wirkungsgrad...",
        category_id=sub_cat,
        tags="pv, module, vergleich",
        author="Solar-Experte",
        is_published=True,
        is_featured=True
    )
    
    # 3. Artikel aufrufen (Views erhöhen)
    for _ in range(5):
        kb_manager.get_article(article_id, increment_views=True)
    
    # 4. Bewertungen abgeben
    kb_manager.rate_article(article_id, "kunde1", 5, "Sehr informativ!")
    kb_manager.rate_article(article_id, "kunde2", 5, "Genau was ich gesucht habe")
    kb_manager.rate_article(article_id, "kunde3", 4, "Gut erklärt")
    
    # 5. Suche testen
    results = kb_manager.search_articles("Monokristallin")
    assert len(results) >= 1
    assert results[0]['id'] == article_id
    
    # 6. Statistiken prüfen
    stats = kb_manager.get_article_rating_stats(article_id)
    assert stats['count'] == 3
    assert stats['avg_rating'] > 4.5
    
    # 7. Kategorien-Baum prüfen
    tree = kb_manager.get_category_tree()
    assert len(tree) == 1
    assert tree[0]['name'] == "Solar-Technik"
    assert len(tree[0]['children']) == 1
    assert tree[0]['children'][0]['name'] == "Photovoltaik"
    assert tree[0]['children'][0]['article_count'] == 1
    
    # 8. Top-Artikel prüfen
    top = kb_manager.get_top_rated_articles(limit=5)
    assert len(top) >= 1
    assert top[0]['id'] == article_id
    
    print("[OK] Vollständiger Workflow erfolgreich getestet!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Knowledge Base Manager - Test Suite")
    print("=" * 70)
    
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
