# crm/features/offer_ui.py
"""
Angebotsverfolgung UI Modul
Benutzeroberfläche für die Verwaltung von Angeboten
"""

import sqlite3
from datetime import datetime
from typing import Any

import streamlit as st

from crm.features.offer_tracker import (
    create_offer_tracking_tables,
    get_all_offers,
    get_offer_statistics,
    get_offer_status,
    get_pending_follow_ups,
    mark_follow_up_completed,
    update_lead_status_from_offer,
    update_offer_status)


def render_offer_tracking_ui(conn: sqlite3.Connection, texts: dict[str, str]) -> None:
    """
    Rendert die Hauptoberfläche für Angebotsverfolgung.
    
    Args:
        conn: Datenbankverbindung
        texts: Übersetzungstexte
    """
    # Stelle sicher, dass Tabellen existieren
    create_offer_tracking_tables(conn)
    
    st.header(" Angebotsverfolgung (Offer Tracking)")
    
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3 = st.tabs([
        "Übersicht",
        "Alle Angebote",
        "⏰ Follow-ups"
    ])
    
    with tab1:
        render_offer_overview(conn, texts)
    
    with tab2:
        render_all_offers(conn, texts)
    
    with tab3:
        render_follow_ups(conn, texts)


def render_offer_overview(conn: sqlite3.Connection, texts: dict[str, str]) -> None:
    """Rendert die Übersichtsseite mit Statistiken."""
    st.subheader("Angebots-Übersicht")
    
    # Lade Statistiken
    stats = get_offer_statistics(conn)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                padding: 15px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            ">
                <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Gesamt Angebote</p>
                <h2 style="margin: 5px 0; font-size: 2em;">{stats['total_offers']}</h2>
                <p style="margin: 0; font-size: 0.8em;">Alle Status</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #F59E0B 0%, #D97706 100%);
                padding: 15px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            ">
                <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Versendet</p>
                <h2 style="margin: 5px 0; font-size: 2em;">{stats['sent']}</h2>
                <p style="margin: 0; font-size: 0.8em;">Warten auf Antwort</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #10B981 0%, #059669 100%);
                padding: 15px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            ">
                <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Angenommen</p>
                <h2 style="margin: 5px 0; font-size: 2em;">{stats['accepted']}</h2>
                <p style="margin: 0; font-size: 0.8em;">{stats['conversion_rate']:.1f}% Conversion</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #EF4444 0%, #DC2626 100%);
                padding: 15px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            ">
                <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Ausstehende Follow-ups</p>
                <h2 style="margin: 5px 0; font-size: 2em;">{stats['pending_follow_ups']}</h2>
                <p style="margin: 0; font-size: 0.8em;">Aktion erforderlich</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Weitere Statistiken
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Durchschnittlicher Angebotswert",
            f"{stats['avg_offer_value']:,.2f} €"
        )
    
    with col2:
        st.metric(
            "Entwürfe",
            stats['draft']
        )
    
    # Status-Verteilung
    st.markdown("### Status-Verteilung")
    
    status_labels = {
        'draft': 'Entwurf',
        'sent': ' Versendet',
        'accepted': 'Angenommen',
        'rejected': 'Abgelehnt'
    }
    
    for status, label in status_labels.items():
        count = stats.get(status, 0)
        if stats != 0:
            percentage = (count / stats['total_offers'] * 100) if stats['total_offers'] > 0 else 0
        else:
            percentage = 0.0
        
        st.markdown(f"""
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>{label}</span>
                    <span><strong>{count}</strong> ({percentage:.1f}%)</span>
                </div>
                <div style="
                    background-color: #e0e0e0;
                    border-radius: 10px;
                    height: 20px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(90deg, #808080, #6a6a6a);
                        height: 100%;
                        width: {percentage}%;
                        transition: width 0.3s ease;
                    "></div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_all_offers(conn: sqlite3.Connection, texts: dict[str, str]) -> None:
    """Rendert die Liste aller Angebote mit Filtermöglichkeiten."""
    st.subheader("Alle Angebote")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status filtern",
            options=['all', 'draft', 'sent', 'accepted', 'rejected'],
            format_func=lambda x: {
                'all': 'Alle Status',
                'draft': 'Entwurf',
                'sent': ' Versendet',
                'accepted': 'Angenommen',
                'rejected': 'Abgelehnt'
            }[x]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sortieren nach",
            options=['date_desc', 'date_asc', 'value_desc', 'value_asc'],
            format_func=lambda x: {
                'date_desc': 'Datum (neueste zuerst)',
                'date_asc': 'Datum (älteste zuerst)',
                'value_desc': 'Wert (höchste zuerst)',
                'value_asc': 'Wert (niedrigste zuerst)'
            }[x]
        )
    
    with col3:
        search_query = st.text_input(
            "Suche",
            placeholder="Projektname oder Kunde..."
        )
    
    # Lade Angebote
    filter_status = None if status_filter == 'all' else status_filter
    offers = get_all_offers(conn, status_filter=filter_status, include_customer_info=True)
    
    # Suche anwenden
    if search_query:
        search_lower = search_query.lower()
        offers = [
            o for o in offers
            if search_lower in o.get('project_name', '').lower()
            or search_lower in o.get('customer_company_name', '').lower()
            or search_lower in f"{o.get('customer_first_name', '')} {o.get('customer_last_name', '')}".lower()
        ]
    
    # Sortierung anwenden
    if sort_by == 'date_desc':
        offers.sort(key=lambda x: x.get('offer_sent_date') or '0000-00-00', reverse=True)
    elif sort_by == 'date_asc':
        offers.sort(key=lambda x: x.get('offer_sent_date') or '9999-99-99')
    elif sort_by == 'value_desc':
        offers.sort(key=lambda x: x.get('offer_value') or 0, reverse=True)
    elif sort_by == 'value_asc':
        offers.sort(key=lambda x: x.get('offer_value') or 0)
    
    st.markdown(f"**{len(offers)}** Angebote gefunden")
    st.markdown("---")
    
    # Angebote anzeigen
    if offers:
        for offer in offers:
            render_offer_card(conn, offer, texts)
    else:
        st.info("Keine Angebote gefunden.")


def render_offer_card(conn: sqlite3.Connection, offer: dict[str, Any], texts: dict[str, str]) -> None:
    """Rendert eine einzelne Angebots-Karte."""
    status_colors = {
        'draft': '#94A3B8',
        'sent': '#F59E0B',
        'accepted': '#10B981',
        'rejected': '#EF4444'
    }
    
    status_icons = {
        'draft': '',
        'sent': '',
        'accepted': '',
        'rejected': ''
    }
    
    status_labels = {
        'draft': 'Entwurf',
        'sent': 'Versendet',
        'accepted': 'Angenommen',
        'rejected': 'Abgelehnt'
    }
    
    status = offer.get('offer_status', 'draft')
    color = status_colors.get(status, '#808080')
    icon = status_icons.get(status, '')
    label = status_labels.get(status, status)
    
    customer_name = offer.get('customer_company_name') or f"{offer.get('customer_first_name', '')} {offer.get('customer_last_name', '')}".strip()
    
    with st.expander(f"{icon} {offer['project_name']} - {customer_name}", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Projekt-Details:**")
            st.text(f"Projekt: {offer['project_name']}")
            st.text(f"Kunde: {customer_name}")
            if offer.get('customer_email'):
                st.text(f" {offer['customer_email']}")
            if offer.get('customer_phone'):
                st.text(f" {offer['customer_phone']}")
        
        with col2:
            st.markdown("**Angebots-Info:**")
            st.markdown(f"Status: <span style='color: {color}; font-weight: bold;'>{icon} {label}</span>", unsafe_allow_html=True)
            if offer.get('offer_value'):
                st.text(f"Wert: {offer['offer_value']:,.2f} €")
            st.text(f"Version: {offer.get('offer_version', 1)}")
            
            if offer.get('offer_sent_date'):
                sent_date = datetime.fromisoformat(offer['offer_sent_date'])
                days_ago = (datetime.now() - sent_date).days
                st.text(f" Versendet: vor {days_ago} Tagen")
        
        with col3:
            st.markdown("**Aktionen:**")
            
            # Status-Änderungs-Buttons
            if status == 'draft':
                if st.button(" Als versendet markieren", key=f"send_{offer['id']}"):
                    if update_offer_status(conn, offer['id'], 'sent'):
                        st.success("Status auf 'Versendet' aktualisiert!")
                        st.rerun()
            
            elif status == 'sent':
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Angenommen", key=f"accept_{offer['id']}"):
                        if update_offer_status(conn, offer['id'], 'accepted'):
                            update_lead_status_from_offer(conn, offer['id'], 'accepted')
                            st.success("Angebot angenommen!")
                            st.rerun()
                
                with col_b:
                    if st.button("Abgelehnt", key=f"reject_{offer['id']}"):
                        st.session_state[f'show_rejection_form_{offer["id"]}'] = True
                        st.rerun()
        
        # Ablehnungsformular
        if st.session_state.get(f'show_rejection_form_{offer["id"]}', False):
            st.markdown("---")
            st.markdown("**Ablehnungsgrund erfassen:**")
            
            rejection_reason = st.selectbox(
                "Grund",
                options=[
                    'Preis zu hoch',
                    'Konkurrenzangebot gewählt',
                    'Projekt verschoben',
                    'Kein Interesse mehr',
                    'Sonstiges'
                ],
                key=f"rejection_reason_{offer['id']}"
            )
            
            rejection_notes = st.text_area(
                "Zusätzliche Notizen",
                key=f"rejection_notes_{offer['id']}"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(" Ablehnung speichern", key=f"save_rejection_{offer['id']}"):
                    if update_offer_status(
                        conn,
                        offer['id'],
                        'rejected',
                        rejection_reason=rejection_reason,
                        rejection_notes=rejection_notes
                    ):
                        update_lead_status_from_offer(conn, offer['id'], 'rejected')
                        st.success("Ablehnung gespeichert!")
                        del st.session_state[f'show_rejection_form_{offer["id"]}']
                        st.rerun()
            
            with col_b:
                if st.button("Abbrechen", key=f"cancel_rejection_{offer['id']}"):
                    del st.session_state[f'show_rejection_form_{offer["id"]}']
                    st.rerun()
        
        # Ablehnungsgrund anzeigen (falls vorhanden)
        if status == 'rejected' and offer.get('rejection_reason'):
            st.markdown("---")
            st.markdown("**Ablehnungsgrund:**")
            st.warning(f"**{offer['rejection_reason']}**")
            if offer.get('rejection_notes'):
                st.text(offer['rejection_notes'])


def render_follow_ups(conn: sqlite3.Connection, texts: dict[str, str]) -> None:
    """Rendert die Follow-up-Übersicht."""
    st.subheader("⏰ Ausstehende Follow-ups")
    
    follow_ups = get_pending_follow_ups(conn)
    
    if not follow_ups:
        st.success(" Keine ausstehenden Follow-ups! Alle Angebote sind aktuell.")
        return
    
    st.warning(f"**{len(follow_ups)}** Angebote benötigen ein Follow-up!")
    st.markdown("---")
    
    for follow_up in follow_ups:
        follow_up_date = datetime.fromisoformat(follow_up['follow_up_date'])
        days_overdue = (datetime.now() - follow_up_date).days
        
        customer_name = follow_up.get('customer_company_name') or f"{follow_up.get('customer_first_name', '')} {follow_up.get('customer_last_name', '')}".strip()
        
        # Dringlichkeits-Farbe
        if days_overdue > 7:
            urgency_color = '#EF4444'  # Rot
            urgency_label = ' Sehr dringend'
        elif days_overdue > 3:
            urgency_color = '#F59E0B'  # Orange
            urgency_label = '🟠 Dringend'
        else:
            urgency_color = '#10B981'  # Grün
            urgency_label = '🟢 Fällig'
        
        with st.container():
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
                    border-left: 4px solid {urgency_color};
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h4 style="margin: 0 0 10px 0; color: #333;">
                         {follow_up['project_name']}
                    </h4>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>Kunde:</strong> {customer_name}
                    </p>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>Status:</strong> {urgency_label} - Vor {days_overdue} Tagen fällig
                    </p>
                    {f"<p style='margin: 5px 0; color: #666;'><strong>Wert:</strong> {follow_up['offer_value']:,.2f} €</p>" if follow_up.get('offer_value') else ""}
                    {f"<p style='margin: 5px 0; color: #666;'><strong>E-Mail:</strong> {follow_up['customer_email']}</p>" if follow_up.get('customer_email') else ""}
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Follow-up erledigt", key=f"complete_followup_{follow_up['id']}"):
                    if mark_follow_up_completed(conn, follow_up['id']):
                        st.success("Follow-up als erledigt markiert!")
                        st.rerun()
            
            with col2:
                if st.button(" E-Mail senden", key=f"email_followup_{follow_up['id']}"):
                    st.info("E-Mail-Funktion wird in Task 9 implementiert.")
            
            with col3:
                if st.button(" Details", key=f"view_followup_{follow_up['id']}"):
                    st.session_state['selected_project_id'] = follow_up['id']
                    st.session_state['crm_view_mode'] = 'view_project'
                    st.rerun()
