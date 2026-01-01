# crm/features/call_integration_example.py
"""
Beispiel-Integration der Anruf-Protokollierung in bestehende CRM-UI.

Dieses Beispiel zeigt, wie die Anruf-Funktionen in verschiedene Teile
des CRM-Systems integriert werden können.
"""

import streamlit as st
from typing import Dict, Any

# Import der Anruf-Module
from crm.features.call_manager import (
    create_call, get_customer_calls, get_call_statistics,
    ensure_call_fields
)
from crm.features.call_ui import (
    render_call_dialog, render_call_list, render_call_statistics,
    integrate_call_logging_to_customer_profile
)


def example_1_customer_profile_integration():
    """
    Beispiel 1: Integration in Kundenprofil
    
    Zeigt, wie die Anruf-Protokollierung in ein bestehendes
    Kundenprofil integriert werden kann.
    """
    st.title("Kundenprofil mit Anruf-Protokollierung")
    
    # Beispiel-Kundendaten
    customer_data = {
        "id": 123,
        "name": "Max Mustermann",
        "email": "max@example.com",
        "phone": "+43 123 456789",
        "mobile": "+43 987 654321",
        "address": "Musterstraße 1, 1010 Wien"
    }
    
    # Zeige Kundendaten
    st.subheader("Kundendaten")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {customer_data['name']}")
        st.write(f"**E-Mail:** {customer_data['email']}")
    with col2:
        st.write(f"**Telefon:** {customer_data['phone']}")
        st.write(f"**Mobil:** {customer_data['mobile']}")
    
    # Integriere Anruf-Protokollierung
    integrate_call_logging_to_customer_profile(
        customer_id=customer_data["id"],
        customer_data=customer_data
    )


def example_2_quick_call_button():
    """
    Beispiel 2: Quick-Call-Button in Kundenliste
    
    Zeigt, wie ein schneller Anruf-Button in eine Kundenliste
    integriert werden kann.
    """
    st.title("Kundenliste mit Quick-Call")
    
    # Beispiel-Kundenliste
    customers = [
        {"id": 1, "name": "Max Mustermann", "phone": "+43 123 456789"},
        {"id": 2, "name": "Anna Schmidt", "phone": "+43 987 654321"},
        {"id": 3, "name": "Peter Müller", "phone": "+43 555 123456"}
    ]
    
    for customer in customers:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.write(f"**{customer['name']}**")
        
        with col2:
            st.write(customer['phone'])
        
        with col3:
            if st.button(" Anrufen", key=f"call_{customer['id']}"):
                st.session_state.show_call_dialog = True
                st.session_state.call_customer_id = customer['id']
                st.session_state.call_customer_name = customer['name']
                st.session_state.call_phone_number = customer['phone']
    
    # Zeige Dialog wenn aktiviert
    if st.session_state.get("show_call_dialog"):
        with st.container():
            st.markdown("---")
            render_call_dialog(
                customer_id=st.session_state.call_customer_id,
                customer_name=st.session_state.call_customer_name,
                phone_numbers=[st.session_state.call_phone_number]
            )


def example_3_call_statistics_dashboard():
    """
    Beispiel 3: Anruf-Statistiken im Dashboard
    
    Zeigt, wie Anruf-Statistiken in ein Dashboard integriert werden können.
    """
    st.title("CRM Dashboard mit Anruf-Statistiken")
    
    # Beispiel: Statistiken für mehrere Kunden
    customer_ids = [1, 2, 3, 4, 5]
    
    st.subheader("Anruf-Übersicht")
    
    # Gesamtstatistiken
    total_calls = 0
    total_incoming = 0
    total_outgoing = 0
    total_duration = 0
    
    for customer_id in customer_ids:
        stats = get_call_statistics(customer_id)
        total_calls += stats.get("total", 0)
        total_incoming += stats.get("incoming", 0)
        total_outgoing += stats.get("outgoing", 0)
        total_duration += stats.get("total_duration_seconds", 0)
    
    # Zeige Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gesamt Anrufe", total_calls)
    
    with col2:
        st.metric("Eingehend", total_incoming)
    
    with col3:
        st.metric("Ausgehend", total_outgoing)
    
    with col4:
        from crm.features.call_manager import format_duration
        st.metric("Gesamtdauer", format_duration(total_duration))
    
    # Detaillierte Statistiken pro Kunde
    st.subheader("Anrufe pro Kunde")
    
    for customer_id in customer_ids:
        stats = get_call_statistics(customer_id)
        if stats.get("total", 0) > 0:
            with st.expander(f"Kunde #{customer_id} - {stats['total']} Anrufe"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Eingehend", stats["incoming"])
                with col2:
                    st.metric("Ausgehend", stats["outgoing"])
                with col3:
                    st.metric("Ø Dauer", stats["average_duration_formatted"])


def example_4_call_timeline_integration():
    """
    Beispiel 4: Anrufe in Kommunikations-Timeline
    
    Zeigt, wie Anrufe zusammen mit anderen Aktivitäten
    in einer Timeline angezeigt werden können.
    """
    st.title("Kommunikations-Timeline")
    
    customer_id = 123
    
    # Hole alle Aktivitäten (inkl. Anrufe)
    from crm.features.note_manager import get_customer_activities
    
    activities = get_customer_activities(customer_id=customer_id, limit=50)
    
    if not activities:
        st.info("Noch keine Aktivitäten vorhanden.")
        return
    
    # Zeige Timeline
    for activity in activities:
        # Icon basierend auf Typ
        icon = {
            "call": "",
            "email": "",
            "note": "",
            "appointment": "",
            "meeting": ""
        }.get(activity["activity_type"], "")
        
        with st.expander(f"{icon} {activity['title']} - {activity['created_at']}"):
            # Zeige spezielle Anruf-Informationen
            if activity["activity_type"] == "call":
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Richtung:** {activity.get('call_direction_display', 'N/A')}")
                    st.write(f"**Telefonnummer:** {activity.get('call_phone_number', 'N/A')}")
                with col2:
                    st.write(f"**Dauer:** {activity.get('call_duration_formatted', 'N/A')}")
                    st.write(f"**Erstellt von:** {activity['created_by']}")
            
            # Zeige Content
            if activity["content"]:
                st.markdown(activity["content"])


def example_5_automated_call_logging():
    """
    Beispiel 5: Automatische Anruf-Protokollierung
    
    Zeigt, wie Anrufe automatisch protokolliert werden können,
    z.B. bei Integration mit VoIP-System.
    """
    st.title("Automatische Anruf-Protokollierung")
    
    st.info("""
    Dieses Beispiel zeigt, wie Anrufe automatisch protokolliert werden können,
    wenn sie über ein VoIP-System eingehen.
    """)
    
    # Simuliere eingehenden Anruf
    if st.button("Simuliere eingehenden Anruf"):
        # In echter Integration würde dies durch VoIP-Webhook ausgelöst
        call_id = create_call(
            customer_id=123,
            phone_number="+43 123 456789",
            direction="incoming",
            duration_seconds=0,  # Wird später aktualisiert
            notes="Automatisch protokolliert durch VoIP-System",
            created_by="VoIP-System"
        )
        
        if call_id:
            st.success(f"Anruf automatisch protokolliert (ID: {call_id})")
            st.info("In echter Integration würde jetzt ein Popup erscheinen mit Kundeninformationen.")
        else:
            st.error("Fehler beim Protokollieren")
    
    # Zeige letzte automatisch protokollierte Anrufe
    st.subheader("Letzte automatische Anrufe")
    calls = get_customer_calls(customer_id=123, limit=5)
    
    for call in calls:
        if call["created_by"] == "VoIP-System":
            st.write(f" {call['call_direction_display']} - {call['call_phone_number']} - {call['created_at']}")


def example_6_call_reporting():
    """
    Beispiel 6: Anruf-Reporting
    
    Zeigt, wie Anruf-Daten für Reports verwendet werden können.
    """
    st.title("Anruf-Reporting")
    
    st.subheader("Anruf-Aktivität nach Zeitraum")
    
    # Zeitraum-Auswahl
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Von")
    with col2:
        end_date = st.date_input("Bis")
    
    # In echter Implementation würde hier nach Datum gefiltert
    customer_ids = [1, 2, 3, 4, 5]
    
    # Sammle Daten
    report_data = []
    for customer_id in customer_ids:
        stats = get_call_statistics(customer_id)
        if stats.get("total", 0) > 0:
            report_data.append({
                "Kunde ID": customer_id,
                "Gesamt": stats["total"],
                "Eingehend": stats["incoming"],
                "Ausgehend": stats["outgoing"],
                "Dauer": stats["total_duration_formatted"]
            })
    
    if report_data:
        import pandas as pd
        df = pd.DataFrame(report_data)
        st.dataframe(df, use_container_width=True)
        
        # Export-Button
        csv = df.to_csv(index=False)
        st.download_button(
            label=" Als CSV exportieren",
            data=csv,
            file_name="anruf_report.csv",
            mime="text/csv"
        )
    else:
        st.info("Keine Anrufe im ausgewählten Zeitraum.")


# Hauptfunktion für Demo
def main():
    """Hauptfunktion für Demo-App."""
    
    # Stelle sicher, dass Anruf-Felder existieren
    ensure_call_fields()
    
    st.sidebar.title("Anruf-Protokollierung Demo")
    
    example = st.sidebar.selectbox(
        "Wähle ein Beispiel:",
        [
            "1. Kundenprofil Integration",
            "2. Quick-Call-Button",
            "3. Dashboard-Statistiken",
            "4. Timeline-Integration",
            "5. Automatische Protokollierung",
            "6. Reporting"
        ]
    )
    
    if example.startswith("1"):
        example_1_customer_profile_integration()
    elif example.startswith("2"):
        example_2_quick_call_button()
    elif example.startswith("3"):
        example_3_call_statistics_dashboard()
    elif example.startswith("4"):
        example_4_call_timeline_integration()
    elif example.startswith("5"):
        example_5_automated_call_logging()
    elif example.startswith("6"):
        example_6_call_reporting()


if __name__ == "__main__":
    main()
