"""
PDF Services Integration Module - Integriert Dienstleistungen in das PDF-System

Dieses Modul stellt Funktionen zur Verfügung, um ausgewählte Dienstleistungen
in die PDF-Generierung zu integrieren und auf Seite 6 anzuzeigen.
"""

from typing import Any


def get_selected_services_for_pdf(
        project_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extrahiert die ausgewählten Dienstleistungen aus den Projektdaten für die PDF-Generierung.

    Args:
        project_data: Die Projektdaten mit ausgewählten Dienstleistungen

    Returns:
        Liste der ausgewählten Dienstleistungen mit Details
    """
    selected_services = []

    # Versuche Dienstleistungen aus verschiedenen Quellen zu extrahieren
    services_data = None

    # 1. Direkt aus project_data
    if 'selected_services' in project_data:
        services_data = project_data['selected_services']

    # 2. Aus customer_data (falls dort gespeichert)
    elif 'customer_data' in project_data and 'selected_services' in project_data['customer_data']:
        services_data = project_data['customer_data']['selected_services']

    # 3. Aus project_details (falls dort gespeichert)
    elif 'project_details' in project_data and 'selected_services' in project_data['project_details']:
        services_data = project_data['project_details']['selected_services']

    # 4. Aus session_state (Streamlit)
    try:
        import streamlit as st
        if hasattr(
                st,
                'session_state') and 'selected_services' in st.session_state:
            services_data = st.session_state['selected_services']
    except ImportError:
        pass

    if services_data and isinstance(services_data, list):
        for service in services_data:
            if isinstance(
                    service,
                    dict) and 'name' in service and 'price' in service:
                selected_services.append({
                    'name': service.get('name', ''),
                    'description': service.get('description', ''),
                    'price': float(service.get('price', 0)),
                    'category': service.get('category', 'Sonstiges')
                })

    return selected_services


def format_services_for_pdf_display(
        services: list[dict[str, Any]]) -> dict[str, str]:
    """
    Formatiert die Dienstleistungen für die Anzeige in der PDF.

    Args:
        services: Liste der ausgewählten Dienstleistungen

    Returns:
        Dictionary mit formatierten Strings für die PDF-Platzhalter
    """
    if not services:
        return {
            'services_list': 'Keine optionalen Dienstleistungen ausgewählt',
            'services_total': '0,00 €',
            'services_count': '0'
        }

    # Erstelle formatierte Liste
    services_lines = []
    total_cost = 0

    for service in services:
        price = service.get('price', 0)
        total_cost += price

        # Formatiere Preis
        price_str = f"{
            price:,.2f} €".replace(
            ',',
            'X').replace(
            '.',
            ',').replace(
                'X',
            '.')

        # Erstelle Zeile
        line = f"• {service.get('name', 'Unbekannt')}: {price_str}"
        if service.get('description'):
            line += f" ({service['description']})"

        services_lines.append(line)

    # Formatiere Gesamtkosten
    total_str = f"{
        total_cost:,.2f} €".replace(
        ',',
        'X').replace(
            '.',
            ',').replace(
                'X',
        '.')

    return {
        'services_list': '\n'.join(services_lines),
        'services_total': total_str,
        'services_count': str(len(services))
    }


def integrate_services_into_placeholders(
        result: dict[str, str], project_data: dict[str, Any]) -> dict[str, str]:
    """
    Integriert die Dienstleistungen in die PDF-Platzhalter.

    Args:
        result: Das bestehende Platzhalter-Dictionary
        project_data: Die Projektdaten

    Returns:
        Das erweiterte Platzhalter-Dictionary mit Dienstleistungen
    """
    # Extrahiere ausgewählte Dienstleistungen
    selected_services = get_selected_services_for_pdf(project_data)

    # Formatiere für PDF-Anzeige
    formatted_services = format_services_for_pdf_display(selected_services)

    # Füge zu Platzhaltern hinzu
    result.update({
        'optional_services_list': formatted_services['services_list'],
        'optional_services_total': formatted_services['services_total'],
        'optional_services_count': formatted_services['services_count']
    })

    print(
        f"DEBUG: Services Integration - {len(selected_services)} Dienstleistungen gefunden")
    for service in selected_services:
        print(f"  - {service['name']}: {service['price']}€")

    return result
