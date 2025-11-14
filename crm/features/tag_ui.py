# crm/features/tag_ui.py
"""
Tag Management UI für CRM
Benutzeroberfläche für Tag-Verwaltung und Kunden-Segmentierung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
from typing import Any

try:
    from database import get_db_connection
    from crm.features.tag_manager import (
        create_tag,
        get_all_tags,
        update_tag,
        delete_tag,
        assign_tag_to_customer,
        remove_tag_from_customer,
        get_customer_tags,
        get_customers_by_tags,
        assign_tags_to_customers,
        get_tag_statistics,
        get_tag_categories,
    )
    TAG_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Tag Manager nicht verfügbar: {e}")
    TAG_MANAGER_AVAILABLE = False


def render_tag_management_ui(texts: dict[str, str]):
    """Hauptfunktion für Tag-Verwaltung UI."""
    
    if not TAG_MANAGER_AVAILABLE:
        st.error("🏷️ Tag-Verwaltung nicht verfügbar - Module fehlen")
        return
    
    st.subheader("🏷️ Tag-Verwaltung")
    st.markdown("Verwalten Sie Tags zur Kategorisierung und Segmentierung von Kunden")
    
    # Tabs für verschiedene Bereiche
    tabs = st.tabs([
        "📋 Alle Tags",
        "➕ Neuer Tag",
        "[CHART] Statistiken"
    ])
    
    with tabs[0]:
        render_all_tags_section(texts)
    
    with tabs[1]:
        render_create_tag_section(texts)
    
    with tabs[2]:
        render_tag_statistics_section(texts)


def render_all_tags_section(texts: dict[str, str]):
    """Zeigt alle Tags an."""
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        # Filter-Optionen
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            categories = get_tag_categories(conn)
            category_filter = st.selectbox(
                "Kategorie filtern",
                options=["Alle"] + categories,
                key="tag_category_filter"
            )
        
        with col_filter2:
            show_inactive = st.checkbox(
                "Inaktive Tags anzeigen",
                value=False,
                key="show_inactive_tags"
            )
        
        # Tags laden
        tags = get_all_tags(
            conn,
            category=None if category_filter == "Alle" else category_filter,
            active_only=not show_inactive
        )
        
        if not tags:
            st.info("Keine Tags vorhanden. Erstellen Sie einen neuen Tag.")
            return
        
        st.markdown(f"**{len(tags)}** Tags gefunden")
        st.markdown("---")
        
        # Tags als Cards anzeigen (3 Spalten)
        cols_per_row = 3
        for i in range(0, len(tags), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(tags):
                    tag = tags[i + j]
                    with cols[j]:
                        render_tag_card(tag, conn, texts)
    
    finally:
        conn.close()


def render_tag_card(tag: dict[str, Any], conn, texts: dict[str, str]):
    """Rendert eine Tag-Card."""
    
    color = tag.get('color', '#808080')
    name = tag.get('name', 'Unbekannt')
    category = tag.get('category', 'Keine Kategorie')
    description = tag.get('description', '')
    is_active = tag.get('is_active', 1)
    
    # Status-Badge
    status_badge = "[OK] Aktiv" if is_active else "[ERROR] Inaktiv"
    
    st.markdown(f"""
        <div style="
            border: 2px solid {color};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="
                    width: 20px;
                    height: 20px;
                    background-color: {color};
                    border-radius: 50%;
                    margin-right: 10px;
                    border: 2px solid white;
                "></div>
                <h4 style="margin: 0; color: white;">{name}</h4>
            </div>
            <p style="margin: 5px 0; font-size: 0.85em; color: #e0e0e0;">
                [FOLDER] {category}
            </p>
            <p style="margin: 5px 0; font-size: 0.8em; color: #d0d0d0;">
                {status_badge}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if description:
        with st.expander("[INFO] Beschreibung"):
            st.write(description)
    
    # Aktionen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✏️", key=f"edit_tag_{tag['id']}", help="Bearbeiten", use_container_width=True):
            st.session_state[f'edit_tag_{tag["id"]}'] = True
            st.rerun()
    
    with col2:
        # Toggle Aktiv/Inaktiv
        new_status = not is_active
        status_icon = "[OK]" if new_status else "[ERROR]"
        if st.button(status_icon, key=f"toggle_tag_{tag['id']}", help="Status ändern", use_container_width=True):
            if update_tag(conn, tag['id'], is_active=new_status):
                st.success(f"Tag {'aktiviert' if new_status else 'deaktiviert'}")
                st.rerun()
    
    with col3:
        if st.button("[DELETE]", key=f"delete_tag_{tag['id']}", help="Löschen", use_container_width=True):
            confirm_key = f"confirm_delete_tag_{tag['id']}"
            if st.session_state.get(confirm_key, False):
                if delete_tag(conn, tag['id']):
                    st.success("Tag gelöscht")
                    del st.session_state[confirm_key]
                    st.rerun()
            else:
                st.warning("Nochmal klicken zum Bestätigen!")
                st.session_state[confirm_key] = True
    
    # Bearbeitungs-Dialog
    if st.session_state.get(f'edit_tag_{tag["id"]}', False):
        with st.form(f"edit_tag_form_{tag['id']}"):
            st.subheader(f"Tag bearbeiten: {name}")
            
            new_name = st.text_input("Name", value=name)
            new_color = st.color_picker("Farbe", value=color)
            new_category = st.text_input("Kategorie", value=category or "")
            new_description = st.text_area("Beschreibung", value=description or "")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                if st.form_submit_button("💾 Speichern", use_container_width=True):
                    if update_tag(
                        conn,
                        tag['id'],
                        name=new_name,
                        color=new_color,
                        category=new_category if new_category else None,
                        description=new_description if new_description else None
                    ):
                        st.success("Tag aktualisiert")
                        del st.session_state[f'edit_tag_{tag["id"]}']
                        st.rerun()
                    else:
                        st.error("Fehler beim Aktualisieren")
            
            with col_cancel:
                if st.form_submit_button("[ERROR] Abbrechen", use_container_width=True):
                    del st.session_state[f'edit_tag_{tag["id"]}']
                    st.rerun()


def render_create_tag_section(texts: dict[str, str]):
    """Formular zum Erstellen eines neuen Tags."""
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        with st.form("create_tag_form", clear_on_submit=True):
            st.markdown("### Neuen Tag erstellen")
            
            name = st.text_input(
                "Tag-Name *",
                placeholder="z.B. VIP-Kunde, Interessent, Gewerbe",
                help="Eindeutiger Name für den Tag"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                color = st.color_picker(
                    "Farbe",
                    value="#1f77b4",
                    help="Farbe für die Darstellung des Tags"
                )
            
            with col2:
                # Vorhandene Kategorien laden
                categories = get_tag_categories(conn)
                category = st.selectbox(
                    "Kategorie",
                    options=["Neue Kategorie..."] + categories,
                    help="Kategorie zur Gruppierung von Tags"
                )
                
                if category == "Neue Kategorie...":
                    category = st.text_input(
                        "Neue Kategorie",
                        placeholder="z.B. Kundentyp, Status, Branche"
                    )
            
            description = st.text_area(
                "Beschreibung (optional)",
                placeholder="Beschreibung des Tags und seiner Verwendung",
                height=100
            )
            
            created_by = st.text_input(
                "Erstellt von (optional)",
                placeholder="Ihr Name"
            )
            
            if st.form_submit_button("➕ Tag erstellen", use_container_width=True):
                if not name or not name.strip():
                    st.error("Bitte geben Sie einen Tag-Namen ein")
                else:
                    tag_id = create_tag(
                        conn,
                        name=name,
                        color=color,
                        category=category if category and category != "Neue Kategorie..." else None,
                        description=description if description else None,
                        created_by=created_by if created_by else None
                    )
                    
                    if tag_id:
                        st.success(f"[OK] Tag '{name}' erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error("[ERROR] Fehler beim Erstellen des Tags (Name bereits vergeben?)")
    
    finally:
        conn.close()


def render_tag_statistics_section(texts: dict[str, str]):
    """Zeigt Tag-Statistiken an."""
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        st.markdown("### [CHART] Tag-Statistiken")
        
        stats = get_tag_statistics(conn)
        
        if not stats:
            st.info("Keine Tag-Statistiken verfügbar")
            return
        
        # Gesamtstatistiken
        total_tags = len(stats)
        total_assignments = sum(s['customer_count'] for s in stats)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gesamt Tags", total_tags)
        
        with col2:
            st.metric("Gesamt Zuordnungen", total_assignments)
        
        with col3:
            avg_per_tag = total_assignments / total_tags if total_tags > 0 else 0
            st.metric("Ø Kunden pro Tag", f"{avg_per_tag:.1f}")
        
        st.markdown("---")
        
        # Top Tags
        st.markdown("#### [WINNER] Meistgenutzte Tags")
        
        for stat in stats[:10]:  # Top 10
            color = stat.get('color', '#808080')
            name = stat.get('name', 'Unbekannt')
            category = stat.get('category', 'Keine Kategorie')
            count = stat.get('customer_count', 0)
            
            # Progress Bar für visuelle Darstellung
            max_count = max(s['customer_count'] for s in stats) if stats else 1
            progress = count / max_count if max_count > 0 else 0
            
            st.markdown(f"""
                <div style="
                    border-left: 4px solid {color};
                    padding: 10px;
                    margin-bottom: 8px;
                    background: linear-gradient(90deg, rgba(128,128,128,0.3) 0%, rgba(128,128,128,0.1) 100%);
                    border-radius: 5px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.1em;">{name}</strong><br>
                            <span style="font-size: 0.85em; opacity: 0.8;">[FOLDER] {category}</span>
                        </div>
                        <div style="text-align: right;">
                            <strong style="font-size: 1.3em; color: {color};">{count}</strong><br>
                            <span style="font-size: 0.8em; opacity: 0.8;">Kunden</span>
                        </div>
                    </div>
                    <div style="
                        width: 100%;
                        height: 4px;
                        background-color: rgba(255,255,255,0.2);
                        border-radius: 2px;
                        margin-top: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            width: {progress * 100}%;
                            height: 100%;
                            background-color: {color};
                        "></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    finally:
        conn.close()


def render_customer_tag_selector(
    customer_id: int,
    texts: dict[str, str],
    key_suffix: str = ""
):
    """Rendert Tag-Auswahl für einen Kunden.
    
    Args:
        customer_id: Kunden-ID
        texts: Übersetzungs-Dictionary
        key_suffix: Suffix für eindeutige Keys
    """
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        st.markdown("#### 🏷️ Tags")
        
        # Aktuelle Tags des Kunden
        current_tags = get_customer_tags(conn, customer_id)
        current_tag_ids = [t['id'] for t in current_tags]
        
        # Alle verfügbaren Tags
        all_tags = get_all_tags(conn, active_only=True)
        
        if not all_tags:
            st.info("Keine Tags verfügbar. Erstellen Sie zuerst Tags in der Tag-Verwaltung.")
            return
        
        # Zeige aktuelle Tags
        if current_tags:
            st.markdown("**Zugewiesene Tags:**")
            cols = st.columns(min(len(current_tags), 4))
            for idx, tag in enumerate(current_tags):
                with cols[idx % 4]:
                    color = tag.get('color', '#808080')
                    name = tag.get('name', 'Unbekannt')
                    st.markdown(f"""
                        <div style="
                            background-color: {color};
                            color: white;
                            padding: 5px 10px;
                            border-radius: 15px;
                            text-align: center;
                            font-size: 0.85em;
                            margin-bottom: 5px;
                        ">
                            {name}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Keine Tags zugewiesen")
        
        # Tag hinzufügen/entfernen
        with st.expander("🏷️ Tags verwalten"):
            # Multiselect für Tags
            tag_options = {tag['id']: f"{tag['name']} ({tag.get('category', 'Keine Kategorie')})" 
                          for tag in all_tags}
            
            selected_tag_ids = st.multiselect(
                "Tags auswählen",
                options=list(tag_options.keys()),
                default=current_tag_ids,
                format_func=lambda x: tag_options[x],
                key=f"customer_tags_{customer_id}_{key_suffix}"
            )
            
            # Änderungen speichern
            if st.button("💾 Tags speichern", key=f"save_tags_{customer_id}_{key_suffix}"):
                # Tags hinzufügen
                for tag_id in selected_tag_ids:
                    if tag_id not in current_tag_ids:
                        assign_tag_to_customer(conn, customer_id, tag_id)
                
                # Tags entfernen
                for tag_id in current_tag_ids:
                    if tag_id not in selected_tag_ids:
                        remove_tag_from_customer(conn, customer_id, tag_id)
                
                st.success("Tags aktualisiert")
                st.rerun()
    
    finally:
        conn.close()


def render_bulk_tag_assignment(customer_ids: list[int], texts: dict[str, str]):
    """Rendert Massen-Tagging UI.
    
    Args:
        customer_ids: Liste von Kunden-IDs
        texts: Übersetzungs-Dictionary
    """
    
    if not customer_ids:
        st.warning("Keine Kunden ausgewählt")
        return
    
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung")
        return
    
    try:
        st.markdown(f"### 🏷️ Massen-Tagging für {len(customer_ids)} Kunden")
        
        all_tags = get_all_tags(conn, active_only=True)
        
        if not all_tags:
            st.info("Keine Tags verfügbar")
            return
        
        tag_options = {tag['id']: f"{tag['name']} ({tag.get('category', 'Keine Kategorie')})" 
                      for tag in all_tags}
        
        selected_tag_ids = st.multiselect(
            "Tags auswählen",
            options=list(tag_options.keys()),
            format_func=lambda x: tag_options[x],
            key="bulk_tag_selection"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Tags hinzufügen", use_container_width=True):
                if selected_tag_ids:
                    stats = assign_tags_to_customers(conn, customer_ids, selected_tag_ids)
                    st.success(f"[OK] {stats['success']} Tags zugewiesen, {stats['skipped']} übersprungen")
                    st.rerun()
                else:
                    st.warning("Bitte wählen Sie mindestens einen Tag aus")
        
        with col2:
            if st.button("➖ Tags entfernen", use_container_width=True):
                if selected_tag_ids:
                    removed = remove_tags_from_customers(conn, customer_ids, selected_tag_ids)
                    st.success(f"[OK] {removed} Tag-Zuordnungen entfernt")
                    st.rerun()
                else:
                    st.warning("Bitte wählen Sie mindestens einen Tag aus")
    
    finally:
        conn.close()


# Export-Funktionen
__all__ = [
    'render_tag_management_ui',
    'render_customer_tag_selector',
    'render_bulk_tag_assignment',
]
