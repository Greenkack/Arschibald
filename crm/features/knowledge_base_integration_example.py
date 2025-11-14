"""
Knowledge Base Integration Example

Zeigt, wie die Wissensdatenbank in das CRM-System integriert werden kann.

Author: CRM System Enhancement
Date: 2024
"""

import streamlit as st
from database import get_db_connection
from crm.features.knowledge_base import KnowledgeBaseManager
from crm.features.knowledge_base_ui import render_knowledge_base_ui


def demo_basic_usage():
    """Zeigt grundlegende Verwendung der Wissensdatenbank."""
    st.header("📚 Wissensdatenbank - Grundlegende Verwendung")
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung möglich")
        return
    
    kb_manager = KnowledgeBaseManager(conn)
    
    # Beispiel-Daten erstellen
    if st.button("[PACKAGE] Beispiel-Daten erstellen"):
        with st.spinner("Erstelle Beispiel-Daten..."):
            # Kategorien
            solar_cat = kb_manager.create_category(
                name="Solar-Technik",
                description="Alles über Photovoltaik und Solartechnik",
                icon="☀️",
                sort_order=1
            )
            
            pv_cat = kb_manager.create_category(
                name="PV-Module",
                parent_id=solar_cat,
                description="Informationen zu Photovoltaik-Modulen",
                icon="[PACKAGE]",
                sort_order=1
            )
            
            wp_cat = kb_manager.create_category(
                name="Wärmepumpen",
                description="Alles über Wärmepumpen",
                icon="[TEMP]",
                sort_order=2
            )
            
            # Artikel
            article1 = kb_manager.create_article(
                title="PV-Module: Monokristallin vs. Polykristallin",
                content="""
# PV-Module im Vergleich

## Monokristalline Module

Monokristalline Solarmodule bestehen aus hochreinen Siliziumkristallen und bieten:

- **Höherer Wirkungsgrad**: 18-22%
- **Bessere Leistung bei wenig Licht**
- **Längere Lebensdauer**: 25-30 Jahre
- **Höherer Preis**

## Polykristalline Module

Polykristalline Module sind günstiger, aber:

- **Geringerer Wirkungsgrad**: 15-17%
- **Größerer Platzbedarf**
- **Günstiger in der Anschaffung**
- **Lebensdauer**: 20-25 Jahre

## Fazit

Für kleine Dachflächen sind monokristalline Module die bessere Wahl, 
bei großen Flächen können polykristalline Module wirtschaftlicher sein.
""",
                category_id=pv_cat,
                tags="pv, module, vergleich, monokristallin, polykristallin",
                author="Solar-Experte",
                is_published=True,
                is_featured=True
            )
            
            article2 = kb_manager.create_article(
                title="Wärmepumpen-Installation: Schritt für Schritt",
                content="""
# Wärmepumpen-Installation

## Vorbereitung

1. **Standort wählen**: Außengerät möglichst nah am Haus
2. **Fundament vorbereiten**: Betonplatte oder Schwingungsdämpfer
3. **Elektroanschluss planen**: 400V Drehstrom erforderlich

## Installation

1. Außengerät aufstellen
2. Innengerät montieren
3. Kältemittelleitungen verlegen
4. Elektrische Verbindung herstellen
5. Hydraulik anschließen

## Inbetriebnahme

- System entlüften
- Kältemittel prüfen
- Testlauf durchführen
- Einstellungen optimieren

## Wichtig

[WARNING] Installation nur durch Fachbetrieb!
""",
                category_id=wp_cat,
                tags="wärmepumpe, installation, anleitung",
                author="Heizungs-Experte",
                is_published=True,
                is_featured=False
            )
            
            # Bewertungen
            kb_manager.rate_article(article1, "kunde1", 5, "Sehr informativ!")
            kb_manager.rate_article(article1, "kunde2", 5, "Genau was ich gesucht habe")
            kb_manager.rate_article(article1, "kunde3", 4, "Gut erklärt")
            
            kb_manager.rate_article(article2, "kunde1", 5, "Perfekte Anleitung")
            kb_manager.rate_article(article2, "kunde2", 4, "Hilfreich")
            
            st.success("[OK] Beispiel-Daten erfolgreich erstellt!")
    
    # Statistiken anzeigen
    st.subheader("[CHART] Statistiken")
    stats = kb_manager.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Artikel", stats.get('total_articles', 0))
    with col2:
        st.metric("Veröffentlicht", stats.get('published_articles', 0))
    with col3:
        st.metric("Kategorien", stats.get('total_categories', 0))
    with col4:
        st.metric("Bewertungen", stats.get('total_ratings', 0))
    
    conn.close()


def demo_search():
    """Zeigt Suchfunktionalität."""
    st.header("[SEARCH] Suche in der Wissensdatenbank")
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung möglich")
        return
    
    kb_manager = KnowledgeBaseManager(conn)
    
    search_query = st.text_input("Suchbegriff eingeben", placeholder="z.B. Photovoltaik")
    
    if search_query:
        results = kb_manager.search_articles(search_query, published_only=True)
        
        st.info(f"[SEARCH] {len(results)} Artikel gefunden")
        
        for article in results:
            with st.expander(f"[FILE] {article['title']}"):
                st.markdown(article['content'][:300] + "...")
                st.caption(f"Kategorie: {article.get('category_name', 'Keine')} | "
                          f"Aufrufe: {article['view_count']} | "
                          f"⭐ {article.get('avg_rating', 0):.1f}")
    
    conn.close()


def demo_top_articles():
    """Zeigt Top-Artikel."""
    st.header("⭐ Top-bewertete Artikel")
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung möglich")
        return
    
    kb_manager = KnowledgeBaseManager(conn)
    
    top_articles = kb_manager.get_top_rated_articles(limit=5)
    
    if not top_articles:
        st.info("Noch keine bewerteten Artikel vorhanden.")
    else:
        for i, article in enumerate(top_articles, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i}. {article['title']}**")
                    st.caption(f"Kategorie: {article.get('category_name', 'Keine')}")
                with col2:
                    st.metric("Rating", f"{article.get('avg_rating', 0):.1f} ⭐")
                    st.caption(f"{article.get('rating_count', 0)} Bewertungen")
                st.divider()
    
    conn.close()


def demo_integration_in_crm():
    """Zeigt Integration in CRM-Dashboard."""
    st.header("🔗 Integration in CRM-Dashboard")
    
    st.markdown("""
    ### Möglichkeiten zur Integration:
    
    #### 1. Als separater Tab im CRM
    ```python
    # In crm.py oder crm_dashboard_ui.py
    from crm.features.knowledge_base_ui import render_knowledge_base_ui
    
    tabs = st.tabs(["Dashboard", "Kunden", "Pipeline", "Wissensdatenbank"])
    
    with tabs[3]:
        render_knowledge_base_ui()
    ```
    
    #### 2. Als Widget im Dashboard
    ```python
    from crm.features.knowledge_base import KnowledgeBaseManager
    from database import get_db_connection
    
    conn = get_db_connection()
    kb_manager = KnowledgeBaseManager(conn)
    
    # Top-Artikel Widget
    st.subheader("📚 Beliebte Wissensdatenbank-Artikel")
    top_articles = kb_manager.get_top_rated_articles(limit=3)
    for article in top_articles:
        st.markdown(f"- [{article['title']}](#)")
    
    conn.close()
    ```
    
    #### 3. Kontextuelle Hilfe
    ```python
    # Bei Kundengesprächen relevante Artikel anzeigen
    if st.session_state.get('current_customer_topic') == 'pv':
        st.info("[IDEA] Hilfreiche Artikel:")
        results = kb_manager.search_articles("Photovoltaik")
        for article in results[:3]:
            st.markdown(f"- [{article['title']}](#)")
    ```
    
    #### 4. E-Mail-Integration
    ```python
    # Artikel per E-Mail an Kunden senden
    from crm.features.knowledge_base_ui import send_article_email
    
    if st.button("📧 Artikel an Kunde senden"):
        article = kb_manager.get_article(article_id)
        success = send_article_email(
            recipient=customer_email,
            article=article,
            message="Hier ist der Artikel, den wir besprochen haben."
        )
    ```
    """)


def main():
    """Hauptfunktion für Demo."""
    st.set_page_config(
        page_title="Wissensdatenbank - Integration Demo",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Wissensdatenbank - Integration Demo")
    
    st.markdown("""
    Diese Demo zeigt verschiedene Möglichkeiten, die Wissensdatenbank 
    in das CRM-System zu integrieren.
    """)
    
    # Sidebar Navigation
    demo_mode = st.sidebar.radio(
        "Demo auswählen",
        [
            "Grundlegende Verwendung",
            "Suche",
            "Top-Artikel",
            "Integration in CRM",
            "Vollständige UI"
        ]
    )
    
    if demo_mode == "Grundlegende Verwendung":
        demo_basic_usage()
    elif demo_mode == "Suche":
        demo_search()
    elif demo_mode == "Top-Artikel":
        demo_top_articles()
    elif demo_mode == "Integration in CRM":
        demo_integration_in_crm()
    elif demo_mode == "Vollständige UI":
        st.info("Vollständige Wissensdatenbank-UI:")
        render_knowledge_base_ui()


if __name__ == "__main__":
    main()
