# Wissensdatenbank - Quick Reference

## Übersicht

Die Wissensdatenbank ermöglicht die zentrale Verwaltung von Wissensartikeln mit Kategorien, Volltextsuche und Bewertungssystem.

## Features

✅ **Artikel-Verwaltung**
- Erstellen, Bearbeiten, Löschen von Artikeln
- Markdown-Unterstützung für Formatierung
- Veröffentlichungs-Status (Entwurf/Veröffentlicht)
- Featured-Artikel hervorheben
- View-Counter für Popularität

✅ **Kategorien-Hierarchie**
- Unbegrenzte Verschachtelung
- Icons und Beschreibungen
- Sortierreihenfolge
- Artikel-Zähler pro Kategorie

✅ **Volltextsuche (SQLite FTS5)**
- Schnelle Suche in Titel, Inhalt und Tags
- Ranking nach Relevanz
- Filter nach Veröffentlichungs-Status

✅ **Bewertungssystem**
- 5-Sterne-Bewertungen
- Kommentare zu Bewertungen
- Bewertungs-Statistiken
- Top-bewertete Artikel

✅ **E-Mail-Share-Funktion**
- Artikel per E-Mail teilen
- HTML und Text-Format
- SMTP-Konfiguration

## Verwendung

### 1. Wissensdatenbank-UI aufrufen

```python
from crm.features.knowledge_base_ui import render_knowledge_base_ui

# In Streamlit-App
render_knowledge_base_ui()
```

### 2. Programmatische Verwendung

```python
from database import get_db_connection
from crm.features.knowledge_base import KnowledgeBaseManager

# Manager initialisieren
conn = get_db_connection()
kb_manager = KnowledgeBaseManager(conn)

# Kategorie erstellen
cat_id = kb_manager.create_category(
    name="Solar-Technik",
    description="Alles über Solartechnik",
    icon="☀️"
)

# Artikel erstellen
article_id = kb_manager.create_article(
    title="PV-Module Vergleich",
    content="# Überschrift\n\nDies ist **Markdown** Text.",
    category_id=cat_id,
    tags="pv, module, vergleich",
    author="Solar-Experte",
    is_published=True,
    is_featured=True
)

# Artikel suchen
results = kb_manager.search_articles("Photovoltaik")

# Artikel bewerten
kb_manager.rate_article(article_id, "user1", 5, "Sehr hilfreich!")

# Statistiken abrufen
stats = kb_manager.get_statistics()

conn.close()
```

## API-Referenz

### KnowledgeBaseManager

#### Kategorien

```python
# Erstellen
create_category(name, parent_id=None, description=None, icon=None, sort_order=0, created_by=None) -> int

# Laden
get_category(category_id) -> Dict
get_all_categories(active_only=True) -> List[Dict]
get_category_tree(parent_id=None) -> List[Dict]

# Aktualisieren
update_category(category_id, name=None, parent_id=None, description=None, icon=None, sort_order=None, is_active=None) -> bool

# Löschen
delete_category(category_id, cascade=False) -> bool
```

#### Artikel

```python
# Erstellen
create_article(title, content, category_id=None, tags=None, author=None, is_published=False, is_featured=False) -> int

# Laden
get_article(article_id, increment_views=False) -> Dict
get_all_articles(category_id=None, published_only=True, featured_only=False, limit=None, offset=0) -> List[Dict]

# Suchen
search_articles(search_query, published_only=True, limit=50) -> List[Dict]

# Aktualisieren
update_article(article_id, title=None, content=None, category_id=None, tags=None, is_published=None, is_featured=None) -> bool

# Löschen
delete_article(article_id) -> bool
```

#### Bewertungen

```python
# Bewerten
rate_article(article_id, user_id, rating, comment=None) -> bool

# Laden
get_article_ratings(article_id) -> List[Dict]
get_article_rating_stats(article_id) -> Dict

# Top-Artikel
get_top_rated_articles(limit=10) -> List[Dict]
```

#### Statistiken

```python
# Artikel-Anzahl
get_article_count_by_category(category_id) -> int

# Beliebte Artikel
get_popular_articles(limit=10) -> List[Dict]

# Neueste Artikel
get_recent_articles(limit=10) -> List[Dict]

# Gesamt-Statistiken
get_statistics() -> Dict
```

## Datenbank-Schema

### kb_categories

```sql
CREATE TABLE kb_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    description TEXT,
    icon TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY (parent_id) REFERENCES kb_categories(id) ON DELETE CASCADE
);
```

### kb_articles

```sql
CREATE TABLE kb_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category_id INTEGER,
    tags TEXT,
    author TEXT,
    is_published INTEGER DEFAULT 0,
    is_featured INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES kb_categories(id) ON DELETE SET NULL
);
```

### kb_ratings

```sql
CREATE TABLE kb_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES kb_articles(id) ON DELETE CASCADE,
    UNIQUE(article_id, user_id)
);
```

### kb_articles_fts (Volltextsuche)

```sql
CREATE VIRTUAL TABLE kb_articles_fts USING fts5(
    title,
    content,
    tags,
    content='kb_articles',
    content_rowid='id'
);
```

## Markdown-Unterstützung

Die Wissensdatenbank unterstützt vollständiges Markdown:

```markdown
# Überschrift 1
## Überschrift 2
### Überschrift 3

**Fett** und *kursiv*

- Liste
- Punkt 2

1. Nummerierte
2. Liste

[Link](https://example.com)

![Bild](url)

`Code inline`

```python
# Code-Block
def hello():
    print("Hello")
```

> Zitat
```

## E-Mail-Konfiguration

Für die E-Mail-Share-Funktion müssen SMTP-Einstellungen konfiguriert werden:

```python
import streamlit as st

# In Session State setzen
st.session_state['smtp_server'] = 'smtp.gmail.com'
st.session_state['smtp_port'] = 587
st.session_state['smtp_user'] = 'your-email@gmail.com'
st.session_state['smtp_password'] = 'your-password'
st.session_state['sender_email'] = 'your-email@gmail.com'
```

## Best Practices

### 1. Kategorien-Struktur

```
📚 Wissensdatenbank
├── ☀️ Solar-Technik
│   ├── 📦 PV-Module
│   ├── 🔌 Wechselrichter
│   └── 🔋 Speicher
├── 🌡️ Wärmepumpen
│   ├── 💨 Luft-Wasser
│   └── 🌍 Sole-Wasser
└── 📋 Installation
    ├── 🔧 Planung
    └── ⚡ Elektrik
```

### 2. Artikel-Tags

Verwende konsistente Tags für bessere Suche:
- Produkttypen: `pv`, `wärmepumpe`, `speicher`
- Themen: `installation`, `wartung`, `planung`
- Schwierigkeit: `anfänger`, `fortgeschritten`, `experte`

### 3. Artikel-Struktur

```markdown
# Titel des Artikels

## Zusammenfassung
Kurze Übersicht in 2-3 Sätzen.

## Hauptinhalt
Detaillierte Erklärung mit Unterüberschriften.

### Unterabschnitt 1
...

### Unterabschnitt 2
...

## Fazit
Zusammenfassung der wichtigsten Punkte.

## Weiterführende Links
- [Link 1](url)
- [Link 2](url)
```

### 4. Bewertungen moderieren

```python
# Negative Bewertungen finden
ratings = kb_manager.get_article_ratings(article_id)
negative = [r for r in ratings if r['rating'] <= 2]

# Artikel mit schlechten Bewertungen
stats = kb_manager.get_article_rating_stats(article_id)
if stats['avg_rating'] < 3.0:
    print(f"Artikel {article_id} benötigt Überarbeitung")
```

## Troubleshooting

### Problem: Tabellen existieren nicht

```python
from database import get_db_connection, create_knowledge_base_tables

conn = get_db_connection()
create_knowledge_base_tables(conn)
conn.close()
```

### Problem: Volltextsuche funktioniert nicht

```sql
-- FTS-Index neu aufbauen
DELETE FROM kb_articles_fts;
INSERT INTO kb_articles_fts(rowid, title, content, tags)
SELECT id, title, content, tags FROM kb_articles;
```

### Problem: E-Mail-Versand schlägt fehl

1. SMTP-Einstellungen prüfen
2. Firewall-Regeln überprüfen
3. SMTP-Authentifizierung aktivieren
4. TLS/SSL-Einstellungen anpassen

## Tests

Umfassende Test-Suite verfügbar:

```bash
# Alle Tests ausführen
python -m pytest crm/features/test_knowledge_base.py -v

# Einzelne Tests
python -m pytest crm/features/test_knowledge_base.py::test_create_article -v

# Verifikation
python crm/features/verify_knowledge_base_complete.py
```

## Integration in CRM

Die Wissensdatenbank kann in das CRM-System integriert werden:

```python
# In crm.py oder crm_dashboard_ui.py
from crm.features.knowledge_base_ui import render_knowledge_base_ui

# Als Tab hinzufügen
tab_kb = st.tabs(["Dashboard", "Kunden", "Wissensdatenbank"])
with tab_kb[2]:
    render_knowledge_base_ui()
```

## Weitere Informationen

- **Modul**: `crm/features/knowledge_base.py`
- **UI**: `crm/features/knowledge_base_ui.py`
- **Tests**: `crm/features/test_knowledge_base.py`
- **Verifikation**: `crm/features/verify_knowledge_base_complete.py`

---

**Erstellt**: 2024  
**Task**: 17 - Wissensdatenbank implementieren  
**Status**: ✅ Vollständig implementiert
