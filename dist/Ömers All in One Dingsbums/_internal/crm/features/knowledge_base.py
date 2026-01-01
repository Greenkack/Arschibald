"""
Knowledge Base Manager - Wissensdatenbank-Verwaltung (Task 17)

Dieses Modul verwaltet die Wissensdatenbank mit Artikeln, Kategorien und Bewertungen.

Features:
- Artikel-CRUD-Operationen
- Kategorien-Hierarchie
- Volltextsuche (SQLite FTS5)
- Bewertungssystem
- Markdown-Unterstützung

Author: CRM System Enhancement
Date: 2024
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json


class KnowledgeBaseManager:
    """Manager für Wissensdatenbank-Operationen."""
    
    def __init__(self, conn: sqlite3.Connection):
        """Initialisiert den Knowledge Base Manager.
        
        Args:
            conn: SQLite Datenbankverbindung
        """
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
    
    # ============================================================================
    # KATEGORIEN-VERWALTUNG
    # ============================================================================
    
    def create_category(
        self,
        name: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: int = 0,
        created_by: Optional[str] = None
    ) -> int:
        """Erstellt eine neue Kategorie.
        
        Args:
            name: Kategorie-Name
            parent_id: ID der übergeordneten Kategorie (None für Root-Kategorie)
            description: Beschreibung
            icon: Icon-Name oder Emoji
            sort_order: Sortierreihenfolge
            created_by: Ersteller
            
        Returns:
            ID der erstellten Kategorie
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO kb_categories (name, parent_id, description, icon, sort_order, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, parent_id, description, icon, sort_order, created_by))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """Lädt eine Kategorie.
        
        Args:
            category_id: Kategorie-ID
            
        Returns:
            Kategorie-Daten oder None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM kb_categories WHERE id = ?", (category_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_categories(self, active_only: bool = True) -> List[Dict]:
        """Lädt alle Kategorien.
        
        Args:
            active_only: Nur aktive Kategorien laden
            
        Returns:
            Liste von Kategorien
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM kb_categories"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY sort_order, name"
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_category_tree(self, parent_id: Optional[int] = None) -> List[Dict]:
        """Lädt Kategorien als Hierarchie-Baum.
        
        Args:
            parent_id: ID der übergeordneten Kategorie (None für Root)
            
        Returns:
            Liste von Kategorien mit Unterkategorien
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM kb_categories 
            WHERE parent_id IS ? AND is_active = 1
            ORDER BY sort_order, name
        """, (parent_id))
        
        categories = []
        for row in cursor.fetchall():
            category = dict(row)
            category['children'] = self.get_category_tree(category['id'])
            category['article_count'] = self.get_article_count_by_category(category['id'])
            categories.append(category)
        
        return categories
    
    def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """Aktualisiert eine Kategorie.
        
        Args:
            category_id: Kategorie-ID
            name: Neuer Name
            parent_id: Neue übergeordnete Kategorie
            description: Neue Beschreibung
            icon: Neues Icon
            sort_order: Neue Sortierreihenfolge
            is_active: Aktiv-Status
            
        Returns:
            True bei Erfolg
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if parent_id is not None:
            updates.append("parent_id = ?")
            params.append(parent_id)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if icon is not None:
            updates.append("icon = ?")
            params.append(icon)
        if sort_order is not None:
            updates.append("sort_order = ?")
            params.append(sort_order)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if not updates:
            return False
        
        params.append(category_id)
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE kb_categories 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_category(self, category_id: int, cascade: bool = False) -> bool:
        """Löscht eine Kategorie.
        
        Args:
            category_id: Kategorie-ID
            cascade: Auch Unterkategorien löschen
            
        Returns:
            True bei Erfolg
        """
        cursor = self.conn.cursor()
        
        if not cascade:
            # Prüfe ob Unterkategorien existieren
            cursor.execute("SELECT COUNT(*) FROM kb_categories WHERE parent_id = ?", (category_id))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Kategorie hat Unterkategorien. Verwende cascade=True zum Löschen.")
        
        cursor.execute("DELETE FROM kb_categories WHERE id = ?", (category_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ============================================================================
    # ARTIKEL-VERWALTUNG
    # ============================================================================
    
    def create_article(
        self,
        title: str,
        content: str,
        category_id: Optional[int] = None,
        tags: Optional[str] = None,
        author: Optional[str] = None,
        is_published: bool = False,
        is_featured: bool = False
    ) -> int:
        """Erstellt einen neuen Artikel.
        
        Args:
            title: Artikel-Titel
            content: Artikel-Inhalt (Markdown)
            category_id: Kategorie-ID
            tags: Komma-getrennte Tags
            author: Autor
            is_published: Veröffentlicht
            is_featured: Als Featured markieren
            
        Returns:
            ID des erstellten Artikels
        """
        cursor = self.conn.cursor()
        published_at = datetime.now().isoformat() if is_published else None
        
        cursor.execute("""
            INSERT INTO kb_articles 
            (title, content, category_id, tags, author, is_published, is_featured, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, content, category_id, tags, author, 
              1 if is_published else 0, 1 if is_featured else 0, published_at))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_article(self, article_id: int, increment_views: bool = False) -> Optional[Dict]:
        """Lädt einen Artikel.
        
        Args:
            article_id: Artikel-ID
            increment_views: View-Counter erhöhen
            
        Returns:
            Artikel-Daten oder None
        """
        cursor = self.conn.cursor()
        
        if increment_views:
            cursor.execute("""
                UPDATE kb_articles 
                SET view_count = view_count + 1 
                WHERE id = ?
            """, (article_id))
            self.conn.commit()
        
        cursor.execute("""
            SELECT a.*, c.name as category_name,
                   (SELECT AVG(rating) FROM kb_ratings WHERE article_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM kb_ratings WHERE article_id = a.id) as rating_count
            FROM kb_articles a
            LEFT JOIN kb_categories c ON a.category_id = c.id
            WHERE a.id = ?
        """, (article_id))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_articles(
        self,
        category_id: Optional[int] = None,
        published_only: bool = True,
        featured_only: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """Lädt alle Artikel mit Filterung.
        
        Args:
            category_id: Nur Artikel dieser Kategorie
            published_only: Nur veröffentlichte Artikel
            featured_only: Nur Featured-Artikel
            limit: Maximale Anzahl
            offset: Offset für Pagination
            
        Returns:
            Liste von Artikeln
        """
        cursor = self.conn.cursor()
        
        conditions = []
        params = []
        
        if category_id is not None:
            conditions.append("a.category_id = ?")
            params.append(category_id)
        if published_only:
            conditions.append("a.is_published = 1")
        if featured_only:
            conditions.append("a.is_featured = 1")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT a.*, c.name as category_name,
                   (SELECT AVG(rating) FROM kb_ratings WHERE article_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM kb_ratings WHERE article_id = a.id) as rating_count
            FROM kb_articles a
            LEFT JOIN kb_categories c ON a.category_id = c.id
            WHERE {where_clause}
            ORDER BY a.is_featured DESC, a.created_at DESC
        """
        
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def search_articles(
        self,
        search_query: str,
        published_only: bool = True,
        limit: int = 50
    ) -> List[Dict]:
        """Sucht Artikel mit Volltextsuche.
        
        Args:
            search_query: Suchbegriff
            published_only: Nur veröffentlichte Artikel
            limit: Maximale Anzahl
            
        Returns:
            Liste von gefundenen Artikeln
        """
        cursor = self.conn.cursor()
        
        published_filter = "AND a.is_published = 1" if published_only else ""
        
        cursor.execute(f"""
            SELECT a.*, c.name as category_name,
                   (SELECT AVG(rating) FROM kb_ratings WHERE article_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM kb_ratings WHERE article_id = a.id) as rating_count,
                   fts.rank
            FROM kb_articles_fts fts
            JOIN kb_articles a ON fts.rowid = a.id
            LEFT JOIN kb_categories c ON a.category_id = c.id
            WHERE kb_articles_fts MATCH ?
            {published_filter}
            ORDER BY fts.rank, a.view_count DESC
            LIMIT ?
        """, (search_query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_article(
        self,
        article_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[int] = None,
        tags: Optional[str] = None,
        is_published: Optional[bool] = None,
        is_featured: Optional[bool] = None
    ) -> bool:
        """Aktualisiert einen Artikel.
        
        Args:
            article_id: Artikel-ID
            title: Neuer Titel
            content: Neuer Inhalt
            category_id: Neue Kategorie
            tags: Neue Tags
            is_published: Veröffentlichungs-Status
            is_featured: Featured-Status
            
        Returns:
            True bei Erfolg
        """
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if category_id is not None:
            updates.append("category_id = ?")
            params.append(category_id)
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        if is_published is not None:
            updates.append("is_published = ?")
            params.append(1 if is_published else 0)
            if is_published:
                updates.append("published_at = CURRENT_TIMESTAMP")
        if is_featured is not None:
            updates.append("is_featured = ?")
            params.append(1 if is_featured else 0)
        
        if len(params) == 0:
            return False
        
        params.append(article_id)
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE kb_articles 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_article(self, article_id: int) -> bool:
        """Löscht einen Artikel.
        
        Args:
            article_id: Artikel-ID
            
        Returns:
            True bei Erfolg
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM kb_articles WHERE id = ?", (article_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ============================================================================
    # BEWERTUNGS-SYSTEM
    # ============================================================================
    
    def rate_article(
        self,
        article_id: int,
        user_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> bool:
        """Bewertet einen Artikel.
        
        Args:
            article_id: Artikel-ID
            user_id: Benutzer-ID
            rating: Bewertung (1-5)
            comment: Optionaler Kommentar
            
        Returns:
            True bei Erfolg
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating muss zwischen 1 und 5 liegen")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO kb_ratings (article_id, user_id, rating, comment)
            VALUES (?, ?, ?, ?)
        """, (article_id, user_id, rating, comment))
        self.conn.commit()
        return True
    
    def get_article_ratings(self, article_id: int) -> List[Dict]:
        """Lädt alle Bewertungen eines Artikels.
        
        Args:
            article_id: Artikel-ID
            
        Returns:
            Liste von Bewertungen
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM kb_ratings 
            WHERE article_id = ?
            ORDER BY created_at DESC
        """, (article_id))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_article_rating_stats(self, article_id: int) -> Dict:
        """Lädt Bewertungs-Statistiken eines Artikels.
        
        Args:
            article_id: Artikel-ID
            
        Returns:
            Statistiken (avg_rating, count, distribution)
        """
        cursor = self.conn.cursor()
        
        # Durchschnitt und Anzahl
        cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as count
            FROM kb_ratings
            WHERE article_id = ?
        """, (article_id))
        row = cursor.fetchone()
        
        # Verteilung
        cursor.execute("""
            SELECT rating, COUNT(*) as count
            FROM kb_ratings
            WHERE article_id = ?
            GROUP BY rating
            ORDER BY rating DESC
        """, (article_id))
        distribution = {row['rating']: row['count'] for row in cursor.fetchall()}
        
        return {
            'avg_rating': round(row['avg_rating'], 2) if row['avg_rating'] else 0,
            'count': row['count'],
            'distribution': distribution
        }
    
    # ============================================================================
    # STATISTIKEN & HILFSFUNKTIONEN
    # ============================================================================
    
    def get_article_count_by_category(self, category_id: int) -> int:
        """Zählt Artikel in einer Kategorie.
        
        Args:
            category_id: Kategorie-ID
            
        Returns:
            Anzahl der Artikel
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM kb_articles 
            WHERE category_id = ? AND is_published = 1
        """, (category_id))
        return cursor.fetchone()[0]
    
    def get_popular_articles(self, limit: int = 10) -> List[Dict]:
        """Lädt die beliebtesten Artikel (nach Views).
        
        Args:
            limit: Maximale Anzahl
            
        Returns:
            Liste von Artikeln
        """
        return self.get_all_articles(published_only=True, limit=limit)
    
    def get_top_rated_articles(self, limit: int = 10) -> List[Dict]:
        """Lädt die am besten bewerteten Artikel.
        
        Args:
            limit: Maximale Anzahl
            
        Returns:
            Liste von Artikeln
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.*, c.name as category_name,
                   AVG(r.rating) as avg_rating,
                   COUNT(r.id) as rating_count
            FROM kb_articles a
            LEFT JOIN kb_categories c ON a.category_id = c.id
            LEFT JOIN kb_ratings r ON a.id = r.article_id
            WHERE a.is_published = 1
            GROUP BY a.id
            HAVING rating_count > 0
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT ?
        """, (limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict]:
        """Lädt die neuesten Artikel.
        
        Args:
            limit: Maximale Anzahl
            
        Returns:
            Liste von Artikeln
        """
        return self.get_all_articles(published_only=True, limit=limit)
    
    def get_statistics(self) -> Dict:
        """Lädt Gesamt-Statistiken der Wissensdatenbank.
        
        Returns:
            Statistiken
        """
        cursor = self.conn.cursor()
        
        # Artikel-Statistiken
        cursor.execute("""
            SELECT 
                COUNT(*) as total_articles,
                SUM(CASE WHEN is_published = 1 THEN 1 ELSE 0 END) as published_articles,
                SUM(view_count) as total_views
            FROM kb_articles
        """)
        article_stats = dict(cursor.fetchone())
        
        # Kategorien-Statistiken
        cursor.execute("SELECT COUNT(*) as total_categories FROM kb_categories WHERE is_active = 1")
        category_stats = dict(cursor.fetchone())
        
        # Bewertungs-Statistiken
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ratings,
                AVG(rating) as avg_rating
            FROM kb_ratings
        """)
        rating_stats = dict(cursor.fetchone())
        
        return {
            **article_stats,
            **category_stats,
            **rating_stats
        }
