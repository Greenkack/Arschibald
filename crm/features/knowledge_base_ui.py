"""
Knowledge Base UI - Wissensdatenbank-Benutzeroberfläche (Task 17)

Streamlit-UI für die Wissensdatenbank mit:
- Artikel-Verwaltung
- Kategorien-Verwaltung
- Suche
- Bewertungen
- E-Mail-Share-Funktion

Author: CRM System Enhancement
Date: 2024
"""

import streamlit as st
from typing import Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from crm.features.knowledge_base import KnowledgeBaseManager
    from database import get_db_connection
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from crm.features.knowledge_base import KnowledgeBaseManager
    from database import get_db_connection


def render_knowledge_base_ui():
    """Hauptfunktion für die Wissensdatenbank-UI."""
    st.title(" Wissensdatenbank")
    
    # Initialisiere Manager
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung möglich.")
        return
    
    kb_manager = KnowledgeBaseManager(conn)
    
    # Tab-Navigation
    tabs = st.tabs([
        "Suchen & Durchsuchen",
        "Artikel verwalten",
        "Kategorien verwalten",
        "Statistiken"
    ])
    
    with tabs[0]:
        render_search_tab(kb_manager)
    
    with tabs[1]:
        render_articles_tab(kb_manager)
    
    with tabs[2]:
        render_categories_tab(kb_manager)
    
    with tabs[3]:
        render_statistics_tab(kb_manager)
    
    conn.close()


def render_search_tab(kb_manager: KnowledgeBaseManager):
    """Rendert den Such- und Durchsuch-Tab."""
    st.subheader("Artikel suchen und durchsuchen")
    
    # Suchleiste
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Suche",
            placeholder="Suchbegriff eingeben...",
            key="kb_search"
        )
    with col2:
        search_button = st.button("Suchen", type="primary", use_container_width=True)
    
    # Filter
    with st.expander("Filter"):
        col1, col2 = st.columns(2)
        with col1:
            categories = kb_manager.get_all_categories()
            category_options = {"Alle Kategorien": None}
            category_options.update({cat['name']: cat['id'] for cat in categories})
            selected_category = st.selectbox(
                "Kategorie",
                options=list(category_options.keys()),
                key="kb_filter_category"
            )
        with col2:
            show_featured = st.checkbox("Nur Featured-Artikel", key="kb_filter_featured")
    
    # Artikel laden
    if search_query and search_button:
        articles = kb_manager.search_articles(search_query, published_only=True)
        st.info(f"{len(articles)} Artikel gefunden für '{search_query}'")
    else:
        category_id = category_options.get(selected_category)
        articles = kb_manager.get_all_articles(
            category_id=category_id,
            published_only=True,
            featured_only=show_featured
        )
    
    # Artikel anzeigen
    if not articles:
        st.info("Keine Artikel gefunden.")
    else:
        for article in articles:
            render_article_card(kb_manager, article)


def render_article_card(kb_manager: KnowledgeBaseManager, article: dict):
    """Rendert eine Artikel-Karte."""
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Titel mit Featured-Badge
            title = article['title']
            if article.get('is_featured'):
                title = f" {title}"
            st.markdown(f"### {title}")
            
            # Metadaten
            meta_parts = []
            if article.get('category_name'):
                meta_parts.append(f"{article['category_name']}")
            if article.get('author'):
                meta_parts.append(f" {article['author']}")
            if article.get('view_count'):
                meta_parts.append(f" {article['view_count']} Aufrufe")
            if article.get('avg_rating'):
                stars = "" * int(round(article['avg_rating']))
                meta_parts.append(f"{stars} ({article.get('rating_count', 0)})")
            
            if meta_parts:
                st.caption(" | ".join(meta_parts))
        
        with col2:
            if st.button(" Öffnen", key=f"open_article_{article['id']}", use_container_width=True):
                st.session_state['kb_view_article_id'] = article['id']
                st.rerun()
        
        st.divider()
    
    # Artikel-Ansicht (wenn ausgewählt)
    if st.session_state.get('kb_view_article_id') == article['id']:
        render_article_view(kb_manager, article['id'])


def render_article_view(kb_manager: KnowledgeBaseManager, article_id: int):
    """Rendert die Detail-Ansicht eines Artikels."""
    article = kb_manager.get_article(article_id, increment_views=True)
    
    if not article:
        st.error("Artikel nicht gefunden.")
        return
    
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"## {article['title']}")
        with col2:
            if st.button(" Per E-Mail teilen", key=f"share_{article_id}"):
                st.session_state['kb_share_article_id'] = article_id
        with col3:
            if st.button(" Schließen", key=f"close_{article_id}"):
                if 'kb_view_article_id' in st.session_state:
                    del st.session_state['kb_view_article_id']
                st.rerun()
        
        # Metadaten
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Kategorie: {article.get('category_name', 'Keine')}")
        with col2:
            st.caption(f" Autor: {article.get('author', 'Unbekannt')}")
        with col3:
            st.caption(f" Erstellt: {article.get('created_at', '')[:10]}")
        
        st.divider()
        
        # Inhalt (Markdown)
        st.markdown(article['content'])
        
        st.divider()
        
        # Tags
        if article.get('tags'):
            st.caption(f" Tags: {article['tags']}")
        
        # Bewertungs-Sektion
        render_rating_section(kb_manager, article_id)
        
        # E-Mail-Share-Dialog
        if st.session_state.get('kb_share_article_id') == article_id:
            render_email_share_dialog(kb_manager, article)


def render_rating_section(kb_manager: KnowledgeBaseManager, article_id: int):
    """Rendert die Bewertungs-Sektion."""
    st.subheader(" Bewertungen")
    
    # Statistiken
    stats = kb_manager.get_article_rating_stats(article_id)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Durchschnitt", f"{stats['avg_rating']:.1f} / 5.0")
        st.caption(f"Basierend auf {stats['count']} Bewertungen")
    
    with col2:
        # Bewertungs-Verteilung
        if stats['distribution']:
            for rating in range(5, 0, -1):
                count = stats['distribution'].get(rating, 0)
                percentage = (count / stats['count'] * 100) if stats['count'] > 0 else 0
                st.progress(percentage / 100, text=f"{'' * rating} ({count})")
    
    st.divider()
    
    # Neue Bewertung abgeben
    with st.expander(" Artikel bewerten"):
        col1, col2 = st.columns([1, 3])
        with col1:
            rating = st.select_slider(
                "Bewertung",
                options=[1, 2, 3, 4, 5],
                value=5,
                key=f"rating_slider_{article_id}"
            )
        with col2:
            comment = st.text_area(
                "Kommentar (optional)",
                key=f"rating_comment_{article_id}",
                height=100
            )
        
        if st.button("Bewertung abgeben", key=f"submit_rating_{article_id}"):
            user_id = st.session_state.get('user_email', 'anonymous')
            try:
                kb_manager.rate_article(article_id, user_id, rating, comment)
                st.success("Bewertung gespeichert!")
                st.rerun()
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")
    
    # Bewertungen anzeigen
    ratings = kb_manager.get_article_ratings(article_id)
    if ratings:
        st.subheader("Alle Bewertungen")
        for rating_data in ratings[:10]:  # Zeige nur die ersten 10
            with st.container():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"**{'' * rating_data['rating']}**")
                with col2:
                    if rating_data.get('comment'):
                        st.markdown(rating_data['comment'])
                    st.caption(f"Von {rating_data.get('user_id', 'Anonym')} am {rating_data.get('created_at', '')[:10]}")
                st.divider()


def render_email_share_dialog(kb_manager: KnowledgeBaseManager, article: dict):
    """Rendert den E-Mail-Share-Dialog."""
    with st.expander(" Artikel per E-Mail teilen", expanded=True):
        recipient_email = st.text_input(
            "Empfänger E-Mail",
            key=f"share_email_{article['id']}"
        )
        
        message = st.text_area(
            "Nachricht (optional)",
            value=f"Ich möchte diesen Artikel mit dir teilen:\n\n{article['title']}\n\n{article['content'][:200]}...",
            key=f"share_message_{article['id']}",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(" Senden", key=f"send_email_{article['id']}", type="primary"):
                if recipient_email:
                    success = send_article_email(recipient_email, article, message)
                    if success:
                        st.success("E-Mail erfolgreich versendet!")
                        if 'kb_share_article_id' in st.session_state:
                            del st.session_state['kb_share_article_id']
                    else:
                        st.error("E-Mail konnte nicht versendet werden. Bitte E-Mail-Konfiguration prüfen.")
                else:
                    st.warning("Bitte E-Mail-Adresse eingeben.")
        
        with col2:
            if st.button("Abbrechen", key=f"cancel_email_{article['id']}"):
                if 'kb_share_article_id' in st.session_state:
                    del st.session_state['kb_share_article_id']
                st.rerun()


def send_article_email(recipient: str, article: dict, message: str) -> bool:
    """Sendet einen Artikel per E-Mail.
    
    Args:
        recipient: Empfänger E-Mail
        article: Artikel-Daten
        message: Nachricht
        
    Returns:
        True bei Erfolg
    """
    try:
        # E-Mail-Konfiguration aus Session State oder Umgebungsvariablen
        smtp_server = st.session_state.get('smtp_server', 'localhost')
        smtp_port = st.session_state.get('smtp_port', 587)
        smtp_user = st.session_state.get('smtp_user', '')
        smtp_password = st.session_state.get('smtp_password', '')
        sender_email = st.session_state.get('sender_email', 'noreply@example.com')
        
        # E-Mail erstellen
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Wissensdatenbank: {article['title']}"
        msg['From'] = sender_email
        msg['To'] = recipient
        
        # Text-Version
        text_content = f"{message}\n\n---\n{article['content']}"
        msg.attach(MIMEText(text_content, 'plain'))
        
        # HTML-Version
        html_content = f"""
        <html>
        <body>
            <p>{message.replace(chr(10), '<br>')}</p>
            <hr>
            <h2>{article['title']}</h2>
            <p><em>Kategorie: {article.get('category_name', 'Keine')}</em></p>
            <div>{article['content'].replace(chr(10), '<br>')}</div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        
        # E-Mail senden
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_user and smtp_password:
                server.starttls()
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"E-Mail-Fehler: {e}")
        return False


def render_articles_tab(kb_manager: KnowledgeBaseManager):
    """Rendert den Artikel-Verwaltungs-Tab."""
    st.subheader("Artikel verwalten")
    
    # Aktionen
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(" Neuer Artikel", type="primary", use_container_width=True):
            st.session_state['kb_create_article'] = True
    
    # Artikel erstellen/bearbeiten
    if st.session_state.get('kb_create_article') or st.session_state.get('kb_edit_article_id'):
        render_article_editor(kb_manager)
    
    # Artikel-Liste
    st.divider()
    articles = kb_manager.get_all_articles(published_only=False)
    
    if not articles:
        st.info("Noch keine Artikel vorhanden.")
    else:
        for article in articles:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    status = "Veröffentlicht" if article['is_published'] else "Entwurf"
                    featured = "" if article['is_featured'] else ""
                    st.markdown(f"**{featured} {article['title']}** ({status})")
                    st.caption(f"Kategorie: {article.get('category_name', 'Keine')} | Aufrufe: {article['view_count']}")
                
                with col2:
                    if st.button("", key=f"edit_article_{article['id']}", help="Bearbeiten"):
                        st.session_state['kb_edit_article_id'] = article['id']
                        st.rerun()
                
                with col3:
                    if st.button("", key=f"view_article_{article['id']}", help="Ansehen"):
                        st.session_state['kb_view_article_id'] = article['id']
                        st.rerun()
                
                with col4:
                    if st.button("", key=f"delete_article_{article['id']}", help="Löschen"):
                        if kb_manager.delete_article(article['id']):
                            st.success("Artikel gelöscht!")
                            st.rerun()
                
                st.divider()


def render_article_editor(kb_manager: KnowledgeBaseManager):
    """Rendert den Artikel-Editor."""
    article_id = st.session_state.get('kb_edit_article_id')
    article = kb_manager.get_article(article_id) if article_id else None
    
    with st.form("article_editor_form"):
        st.subheader(" Artikel bearbeiten" if article else " Neuer Artikel")
        
        title = st.text_input(
            "Titel *",
            value=article['title'] if article else "",
            key="article_title"
        )
        
        # Kategorie-Auswahl
        categories = kb_manager.get_all_categories()
        category_options = {"Keine Kategorie": None}
        category_options.update({cat['name']: cat['id'] for cat in categories})
        
        current_category = None
        if article and article.get('category_id'):
            for name, cat_id in category_options.items():
                if cat_id == article['category_id']:
                    current_category = name
                    break
        
        category = st.selectbox(
            "Kategorie",
            options=list(category_options.keys()),
            index=list(category_options.keys()).index(current_category) if current_category else 0,
            key="article_category"
        )
        
        content = st.text_area(
            "Inhalt (Markdown) *",
            value=article['content'] if article else "",
            height=400,
            key="article_content",
            help="Markdown-Formatierung wird unterstützt"
        )
        
        tags = st.text_input(
            "Tags (komma-getrennt)",
            value=article['tags'] if article and article['tags'] else "",
            key="article_tags"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            author = st.text_input(
                "Autor",
                value=article['author'] if article and article['author'] else st.session_state.get('user_name', ''),
                key="article_author"
            )
        with col2:
            is_published = st.checkbox(
                "Veröffentlicht",
                value=article['is_published'] if article else False,
                key="article_published"
            )
        with col3:
            is_featured = st.checkbox(
                "Featured",
                value=article['is_featured'] if article else False,
                key="article_featured"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button(" Speichern", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if submit:
            if not title or not content:
                st.error("Titel und Inhalt sind Pflichtfelder!")
            else:
                category_id = category_options[category]
                
                try:
                    if article:
                        # Update
                        kb_manager.update_article(
                            article_id,
                            title=title,
                            content=content,
                            category_id=category_id,
                            tags=tags,
                            is_published=is_published,
                            is_featured=is_featured
                        )
                        st.success("Artikel aktualisiert!")
                    else:
                        # Create
                        kb_manager.create_article(
                            title=title,
                            content=content,
                            category_id=category_id,
                            tags=tags,
                            author=author,
                            is_published=is_published,
                            is_featured=is_featured
                        )
                        st.success("Artikel erstellt!")
                    
                    # Cleanup
                    if 'kb_create_article' in st.session_state:
                        del st.session_state['kb_create_article']
                    if 'kb_edit_article_id' in st.session_state:
                        del st.session_state['kb_edit_article_id']
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")
        
        if cancel:
            if 'kb_create_article' in st.session_state:
                del st.session_state['kb_create_article']
            if 'kb_edit_article_id' in st.session_state:
                del st.session_state['kb_edit_article_id']
            st.rerun()


def render_categories_tab(kb_manager: KnowledgeBaseManager):
    """Rendert den Kategorien-Verwaltungs-Tab."""
    st.subheader("Kategorien verwalten")
    
    # Neue Kategorie erstellen
    with st.expander(" Neue Kategorie erstellen"):
        with st.form("create_category_form"):
            name = st.text_input("Name *")
            description = st.text_area("Beschreibung")
            
            col1, col2 = st.columns(2)
            with col1:
                icon = st.text_input("Icon (Emoji)", value="")
            with col2:
                sort_order = st.number_input("Sortierung", value=0, step=1)
            
            # Parent-Kategorie
            categories = kb_manager.get_all_categories()
            parent_options = {"Keine (Root-Kategorie)": None}
            parent_options.update({cat['name']: cat['id'] for cat in categories})
            parent = st.selectbox("Übergeordnete Kategorie", options=list(parent_options.keys()))
            
            if st.form_submit_button("Erstellen", type="primary"):
                if name:
                    parent_id = parent_options[parent]
                    kb_manager.create_category(
                        name=name,
                        parent_id=parent_id,
                        description=description,
                        icon=icon,
                        sort_order=sort_order,
                        created_by=st.session_state.get('user_name', 'System')
                    )
                    st.success("Kategorie erstellt!")
                    st.rerun()
                else:
                    st.error("Name ist ein Pflichtfeld!")
    
    st.divider()
    
    # Kategorien-Baum anzeigen
    st.subheader("Kategorien-Hierarchie")
    category_tree = kb_manager.get_category_tree()
    render_category_tree(kb_manager, category_tree)


def render_category_tree(kb_manager: KnowledgeBaseManager, categories: list, level: int = 0):
    """Rendert den Kategorien-Baum rekursiv."""
    for category in categories:
        indent = "" * level
        icon = category.get('icon', '')
        article_count = category.get('article_count', 0)
        
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            st.markdown(f"{indent}{icon} **{category['name']}** ({article_count} Artikel)")
            if category.get('description'):
                st.caption(f"{indent}{category['description']}")
        
        with col2:
            if st.button("", key=f"edit_cat_{category['id']}", help="Bearbeiten"):
                st.session_state['kb_edit_category_id'] = category['id']
        
        with col3:
            if st.button("", key=f"delete_cat_{category['id']}", help="Löschen"):
                try:
                    kb_manager.delete_category(category['id'])
                    st.success("Kategorie gelöscht!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        
        # Unterkategorien rekursiv rendern
        if category.get('children'):
            render_category_tree(kb_manager, category['children'], level + 1)


def render_statistics_tab(kb_manager: KnowledgeBaseManager):
    """Rendert den Statistik-Tab."""
    st.subheader("Wissensdatenbank-Statistiken")
    
    stats = kb_manager.get_statistics()
    
    # Gesamt-Statistiken
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gesamt Artikel", stats.get('total_articles', 0))
    with col2:
        st.metric("Veröffentlicht", stats.get('published_articles', 0))
    with col3:
        st.metric("Kategorien", stats.get('total_categories', 0))
    with col4:
        st.metric("Gesamt Aufrufe", stats.get('total_views', 0))
    
    st.divider()
    
    # Top-Artikel
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Beliebteste Artikel")
        popular = kb_manager.get_popular_articles(limit=5)
        for article in popular:
            st.markdown(f"**{article['title']}**")
            st.caption(f" {article['view_count']} Aufrufe")
            st.divider()
    
    with col2:
        st.subheader(" Am besten bewertet")
        top_rated = kb_manager.get_top_rated_articles(limit=5)
        for article in top_rated:
            st.markdown(f"**{article['title']}**")
            st.caption(f" {article.get('avg_rating', 0):.1f} ({article.get('rating_count', 0)} Bewertungen)")
            st.divider()
    
    st.divider()
    
    # Neueste Artikel
    st.subheader(" Neueste Artikel")
    recent = kb_manager.get_recent_articles(limit=5)
    for article in recent:
        st.markdown(f"**{article['title']}**")
        st.caption(f" {article.get('created_at', '')[:10]} | {article.get('category_name', 'Keine')}")
        st.divider()


# Hauptfunktion für direkten Aufruf
if __name__ == "__main__":
    render_knowledge_base_ui()
