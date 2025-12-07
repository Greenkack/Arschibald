#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Mail-Integration - Verwendungsbeispiele
Zeigt wie die E-Mail-Integration in verschiedenen Szenarien verwendet wird

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
from typing import Any, Callable

# Import email_manager functions
try:
    from crm.features.email_manager import (
        create_email_tables,
        create_email_template,
        get_email_template_by_name,
        list_email_templates,
        send_email,
        send_email_with_template,
        save_email_to_history,
        get_email_history_for_customer,
        save_smtp_config,
        get_smtp_config,
        test_smtp_connection,
        replace_placeholders,
        create_default_templates
    )
except ImportError:
    from email_manager import (
        create_email_tables,
        create_email_template,
        get_email_template_by_name,
        list_email_templates,
        send_email,
        send_email_with_template,
        save_email_to_history,
        get_email_history_for_customer,
        save_smtp_config,
        get_smtp_config,
        test_smtp_connection,
        replace_placeholders,
        create_default_templates
    )


# ============================================================================
# Beispiel 1: SMTP-Konfiguration einrichten
# ============================================================================

def example_setup_smtp_config(save_admin_setting_func: Callable[[str, Any], bool]):
    """Beispiel: SMTP-Konfiguration einrichten"""
    
    # SMTP-Konfiguration für Gmail
    gmail_config = {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'ihre-email@gmail.com',
        'smtp_password': 'ihr-app-passwort',  # App-Passwort verwenden!
        'smtp_use_tls': True,
        'smtp_from_email': 'ihre-email@gmail.com',
        'smtp_from_name': 'Ihr Firmenname'
    }
    
    # Verbindung testen
    success, message = test_smtp_connection(gmail_config)
    if success:
        print(f" SMTP-Verbindung erfolgreich: {message}")
        
        # Konfiguration speichern
        if save_smtp_config(save_admin_setting_func, gmail_config):
            print(" SMTP-Konfiguration gespeichert")
        else:
            print(" Fehler beim Speichern der Konfiguration")
    else:
        print(f" SMTP-Verbindung fehlgeschlagen: {message}")


# ============================================================================
# Beispiel 2: E-Mail-Vorlage erstellen
# ============================================================================

def example_create_email_template(conn: sqlite3.Connection):
    """Beispiel: E-Mail-Vorlage erstellen"""
    
    # Vorlage für Angebots-Nachfass
    template_id = create_email_template(
        conn,
        name="Angebot Nachfass",
        subject="Ihr Solaranlagen-Angebot - {{customer_name}}",
        body="""Sehr geehrte/r {{customer_name}},

vielen Dank für Ihr Interesse an unseren Solaranlagen für Ihr Objekt in {{city}}.

Vor {{current_date}} Tagen haben wir Ihnen ein individuelles Angebot zugesendet.

Projektwert: {{project_value}} EUR

Haben Sie Fragen zu unserem Angebot? Wir beraten Sie gerne!

Mit freundlichen Grüßen
{{company_name}}

---
Kontakt:
E-Mail: {{email}}
Telefon: {{phone}}
""",
        category="Nachfass",
        placeholders=["customer_name", "city", "current_date", "project_value", "company_name", "email", "phone"]
    )
    
    if template_id:
        print(f" Vorlage erstellt mit ID: {template_id}")
    else:
        print(" Fehler beim Erstellen der Vorlage")
    
    return template_id


# ============================================================================
# Beispiel 3: E-Mail mit Vorlage senden
# ============================================================================

def example_send_email_with_template(
    conn: sqlite3.Connection,
    smtp_config: dict[str, Any],
    customer_data: dict[str, Any]
):
    """Beispiel: E-Mail mit Vorlage senden"""
    
    # Vorlage abrufen
    template = get_email_template_by_name(conn, "Angebot Nachfass")
    
    if not template:
        print(" Vorlage nicht gefunden")
        return
    
    # E-Mail senden
    success, message = send_email_with_template(
        conn,
        smtp_config,
        template['id'],
        customer_data,
        sent_by="Max Mustermann"
    )
    
    if success:
        print(f" E-Mail erfolgreich gesendet: {message}")
    else:
        print(f" Fehler beim Senden: {message}")


# ============================================================================
# Beispiel 4: E-Mail mit Anhängen senden
# ============================================================================

def example_send_email_with_attachments(
    conn: sqlite3.Connection,
    smtp_config: dict[str, Any],
    customer_data: dict[str, Any],
    pdf_bytes: bytes
):
    """Beispiel: E-Mail mit PDF-Anhang senden"""
    
    # E-Mail mit Anhang senden
    success, message = send_email(
        smtp_config,
        recipient_email=customer_data['email'],
        subject=f"Ihr Angebot - {customer_data['first_name']} {customer_data['last_name']}",
        body=f"""Sehr geehrte/r {customer_data['first_name']} {customer_data['last_name']},

anbei finden Sie Ihr persönliches Solaranlagen-Angebot.

Mit freundlichen Grüßen
Ihr Solar-Team""",
        html=False,
        attachments=[
            ("Angebot.pdf", pdf_bytes)
        ]
    )
    
    if success:
        print(f" E-Mail mit Anhang gesendet: {message}")
        
        # In Historie speichern
        save_email_to_history(
            conn,
            customer_id=customer_data['id'],
            recipient_email=customer_data['email'],
            subject=f"Ihr Angebot - {customer_data['first_name']} {customer_data['last_name']}",
            body="E-Mail mit PDF-Anhang",
            status='sent',
            attachments='["Angebot.pdf"]',
            sent_by="Max Mustermann"
        )
    else:
        print(f" Fehler beim Senden: {message}")


# ============================================================================
# Beispiel 5: E-Mail-Historie abrufen
# ============================================================================

def example_get_email_history(conn: sqlite3.Connection, customer_id: int):
    """Beispiel: E-Mail-Historie für Kunden abrufen"""
    
    # Historie abrufen
    history = get_email_history_for_customer(conn, customer_id, limit=10)
    
    print(f"\n E-Mail-Historie für Kunde {customer_id}:")
    print("=" * 70)
    
    if not history:
        print("Keine E-Mails gefunden.")
    else:
        for email in history:
            status_icon = "" if email['status'] == 'sent' else ""
            print(f"\n{status_icon} {email['sent_at']}")
            print(f"   Betreff: {email['subject']}")
            print(f"   An: {email['recipient_email']}")
            print(f"   Status: {email['status']}")
            
            if email.get('error_message'):
                print(f"   Fehler: {email['error_message']}")


# ============================================================================
# Beispiel 6: Platzhalter ersetzen
# ============================================================================

def example_replace_placeholders():
    """Beispiel: Platzhalter in Text ersetzen"""
    
    # Kundendaten
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'company_name': 'Musterfirma GmbH',
        'email': 'max@example.com',
        'phone_mobile': '+49 123 456789',
        'address': 'Musterstraße',
        'house_number': '42',
        'zip_code': '12345',
        'city': 'Musterstadt',
        'project_value': '25000'
    }
    
    # Text mit Platzhaltern
    text = """Sehr geehrte/r {{customer_name}},

vielen Dank für Ihr Interesse an unseren Solaranlagen für Ihr Objekt in {{city}}.

Projektwert: {{project_value}} EUR

Kontakt:
E-Mail: {{email}}
Telefon: {{phone}}

Mit freundlichen Grüßen
{{company_name}}"""
    
    # Platzhalter ersetzen
    result = replace_placeholders(text, customer_data)
    
    print("\n Platzhalter-Ersetzung:")
    print("=" * 70)
    print(result)


# ============================================================================
# Beispiel 7: Standard-Vorlagen erstellen
# ============================================================================

def example_create_default_templates(conn: sqlite3.Connection):
    """Beispiel: Standard-Vorlagen erstellen"""
    
    # Standard-Vorlagen erstellen
    create_default_templates(conn)
    
    print(" Standard-Vorlagen erstellt:")
    print("   - Willkommens-E-Mail")
    print("   - Angebots-Nachfass")
    print("   - Projekt-Bestätigung")
    print("   - Dankes-E-Mail")


# ============================================================================
# Beispiel 8: Alle Vorlagen auflisten
# ============================================================================

def example_list_all_templates(conn: sqlite3.Connection):
    """Beispiel: Alle E-Mail-Vorlagen auflisten"""
    
    # Alle aktiven Vorlagen
    templates = list_email_templates(conn, active_only=True)
    
    print("\n Verfügbare E-Mail-Vorlagen:")
    print("=" * 70)
    
    if not templates:
        print("Keine Vorlagen gefunden.")
    else:
        for template in templates:
            print(f"\n {template['name']}")
            print(f"   Kategorie: {template['category'] or 'Keine'}")
            print(f"   Betreff: {template['subject']}")
            print(f"   Erstellt: {template['created_at']}")
            
            if template['placeholders']:
                import json
                try:
                    placeholders = json.loads(template['placeholders']) if isinstance(template['placeholders'], str) else template['placeholders']
                    print(f"   Platzhalter: {', '.join(placeholders)}")
                except:
                    pass


# ============================================================================
# Vollständiges Beispiel: E-Mail-Workflow
# ============================================================================

def example_complete_email_workflow(
    conn: sqlite3.Connection,
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool]
):
    """Vollständiges Beispiel: Kompletter E-Mail-Workflow"""
    
    print("\n" + "=" * 70)
    print("VOLLSTÄNDIGER E-MAIL-WORKFLOW")
    print("=" * 70)
    
    # 1. SMTP-Konfiguration laden
    print("\n1⃣ SMTP-Konfiguration laden...")
    smtp_config = get_smtp_config(load_admin_setting_func)
    
    if not smtp_config.get('smtp_host'):
        print(" SMTP nicht konfiguriert. Bitte zuerst einrichten.")
        return
    
    print(f" SMTP-Host: {smtp_config['smtp_host']}")
    
    # 2. Vorlage erstellen (falls nicht vorhanden)
    print("\n2⃣ E-Mail-Vorlage erstellen...")
    template_id = create_email_template(
        conn,
        name="Demo Workflow",
        subject="Test-E-Mail für {{customer_name}}",
        body="Hallo {{customer_name}}, dies ist eine Test-E-Mail aus {{city}}.",
        category="Test"
    )
    
    if template_id:
        print(f" Vorlage erstellt: ID {template_id}")
    else:
        print("ℹ Vorlage existiert bereits")
    
    # 3. Test-Kundendaten
    print("\n3⃣ Test-Kundendaten vorbereiten...")
    customer_data = {
        'id': 1,
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
        'city': 'Musterstadt'
    }
    print(f" Kunde: {customer_data['first_name']} {customer_data['last_name']}")
    
    # 4. E-Mail senden (Mock-Modus für Demo)
    print("\n4⃣ E-Mail senden...")
    print("ℹ Im Produktivbetrieb würde jetzt eine echte E-Mail gesendet")
    
    # 5. Historie anzeigen
    print("\n5⃣ E-Mail-Historie abrufen...")
    history = get_email_history_for_customer(conn, customer_data['id'])
    print(f" {len(history)} E-Mail(s) in Historie")
    
    print("\n" + "=" * 70)
    print("WORKFLOW ABGESCHLOSSEN")
    print("=" * 70)


# ============================================================================
# Main - Beispiele ausführen
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("E-MAIL-INTEGRATION - VERWENDUNGSBEISPIELE")
    print("=" * 70)
    
    # In-Memory-Datenbank für Demo
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # E-Mail-Tabellen erstellen
    create_email_tables(conn)
    
    # Beispiele ausführen
    print("\n Beispiel 2: E-Mail-Vorlage erstellen")
    example_create_email_template(conn)
    
    print("\n Beispiel 6: Platzhalter ersetzen")
    example_replace_placeholders()
    
    print("\n Beispiel 7: Standard-Vorlagen erstellen")
    example_create_default_templates(conn)
    
    print("\n Beispiel 8: Alle Vorlagen auflisten")
    example_list_all_templates(conn)
    
    # Cleanup
    conn.close()
    
    print("\n" + "=" * 70)
    print("ALLE BEISPIELE ABGESCHLOSSEN")
    print("=" * 70)
