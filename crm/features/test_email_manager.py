#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests für E-Mail-Integration
Testet E-Mail-Versand (Mock), Platzhalter-Ersetzung und Vorlagen-System

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
Requirements: 4.1, 4.2, 4.3
"""

import sys
import sqlite3
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import email manager functions
try:
    # Try relative import first
    try:
        from email_manager import (
            create_email_tables,
            create_email_template,
            get_email_template,
            get_email_template_by_name,
            list_email_templates,
            update_email_template,
            delete_email_template,
            replace_placeholders,
            extract_placeholders,
            send_email,
            send_email_with_template,
            save_email_to_history,
            get_email_history_for_customer,
            test_smtp_connection
        )
    except ImportError:
        # Try absolute import
        from crm.features.email_manager import (
            create_email_tables,
            create_email_template,
            get_email_template,
            get_email_template_by_name,
            list_email_templates,
            update_email_template,
            delete_email_template,
            replace_placeholders,
            extract_placeholders,
            send_email,
            send_email_with_template,
            save_email_to_history,
            get_email_history_for_customer,
            test_smtp_connection
        )
except ImportError as e:
    print(f"Konnte email_manager nicht importieren: {e}")
    print("Stelle sicher, dass der Pfad korrekt ist")
    sys.exit(1)


# ============================================================================
# Test-Setup und Hilfsfunktionen
# ============================================================================

def setup_test_db() -> sqlite3.Connection:
    """Erstellt eine In-Memory-Testdatenbank mit E-Mail-Tabellen."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Erstelle E-Mail-Tabellen
    create_email_tables(conn)
    
    # Erstelle auch customers Tabelle für Tests
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            company_name TEXT,
            phone_mobile TEXT,
            phone_landline TEXT,
            address TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT
        )
    """)
    conn.commit()
    
    return conn


def cleanup_test_db(conn: sqlite3.Connection):
    """Schließt die Testdatenbank."""
    if conn:
        conn.close()


def create_test_customer(conn: sqlite3.Connection) -> int:
    """Erstellt einen Test-Kunden und gibt die ID zurück."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (
            first_name, last_name, email, company_name,
            phone_mobile, address, house_number, zip_code, city
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Max", "Mustermann", "max@example.com", "Musterfirma GmbH",
        "+49 123 456789", "Musterstraße", "42", "12345", "Musterstadt"
    ))
    conn.commit()
    return cursor.lastrowid


# ============================================================================
# Test 1: Vorlagen-System (Requirement 4.2)
# ============================================================================

def test_create_email_template():
    """Test: E-Mail-Vorlage erstellen"""
    print("\n=== Test: create_email_template ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle Vorlage
        template_id = create_email_template(
            conn,
            name="Test-Vorlage",
            subject="Test-Betreff {{customer_name}}",
            body="Hallo {{customer_name}}, dies ist ein Test.",
            category="Test",
            placeholders=["customer_name"]
        )
        
        assert template_id is not None, "Template-ID sollte nicht None sein"
        
        # Verifiziere
        template = get_email_template(conn, template_id)
        assert template is not None, "Template sollte gefunden werden"
        assert template['name'] == "Test-Vorlage", "Name stimmt nicht"
        assert template['subject'] == "Test-Betreff {{customer_name}}", "Betreff stimmt nicht"
        assert template['category'] == "Test", "Kategorie stimmt nicht"
        assert "customer_name" in template['placeholders'], "Platzhalter fehlt"
        
        print("   E-Mail-Vorlage erfolgreich erstellt")
        print(f"   Template-ID: {template_id}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_create_duplicate_template():
    """Test: Duplikat-Vorlage sollte fehlschlagen"""
    print("\n=== Test: create_duplicate_template ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle erste Vorlage
        template_id1 = create_email_template(
            conn,
            name="Duplikat-Test",
            subject="Test",
            body="Test"
        )
        assert template_id1 is not None
        
        # Versuche Duplikat zu erstellen
        template_id2 = create_email_template(
            conn,
            name="Duplikat-Test",
            subject="Test 2",
            body="Test 2"
        )
        
        assert template_id2 is None, "Duplikat sollte None zurückgeben"
        
        print("   Duplikat-Vorlage korrekt abgelehnt")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_get_template_by_name():
    """Test: Vorlage nach Name abrufen"""
    print("\n=== Test: get_template_by_name ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle Vorlage
        create_email_template(
            conn,
            name="Name-Test",
            subject="Test",
            body="Test Body"
        )
        
        # Abrufen nach Name
        template = get_email_template_by_name(conn, "Name-Test")
        
        assert template is not None, "Template sollte gefunden werden"
        assert template['name'] == "Name-Test", "Name stimmt nicht"
        assert template['subject'] == "Test", "Betreff stimmt nicht"
        
        print("   Vorlage erfolgreich nach Name abgerufen")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_list_email_templates():
    """Test: Alle Vorlagen auflisten"""
    print("\n=== Test: list_email_templates ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle mehrere Vorlagen
        create_email_template(conn, "Vorlage 1", "Betreff 1", "Body 1", "Kategorie A")
        create_email_template(conn, "Vorlage 2", "Betreff 2", "Body 2", "Kategorie B")
        create_email_template(conn, "Vorlage 3", "Betreff 3", "Body 3", "Kategorie A")
        
        # Liste alle
        all_templates = list_email_templates(conn, active_only=True)
        assert len(all_templates) == 3, f"Sollte 3 Vorlagen finden, fand {len(all_templates)}"
        
        # Liste nach Kategorie
        cat_a_templates = list_email_templates(conn, category="Kategorie A")
        assert len(cat_a_templates) == 2, f"Sollte 2 Vorlagen in Kategorie A finden"
        
        print("   Vorlagen erfolgreich aufgelistet")
        print(f"   Gesamt: {len(all_templates)}, Kategorie A: {len(cat_a_templates)}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_update_email_template():
    """Test: Vorlage aktualisieren"""
    print("\n=== Test: update_email_template ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle Vorlage
        template_id = create_email_template(
            conn,
            name="Update-Test",
            subject="Alter Betreff",
            body="Alter Body"
        )
        
        # Aktualisiere
        success = update_email_template(
            conn,
            template_id,
            subject="Neuer Betreff",
            body="Neuer Body"
        )
        
        assert success, "Update sollte erfolgreich sein"
        
        # Verifiziere
        template = get_email_template(conn, template_id)
        assert template['subject'] == "Neuer Betreff", "Betreff nicht aktualisiert"
        assert template['body'] == "Neuer Body", "Body nicht aktualisiert"
        
        print("   Vorlage erfolgreich aktualisiert")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_delete_email_template():
    """Test: Vorlage löschen (soft delete)"""
    print("\n=== Test: delete_email_template ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle Vorlage
        template_id = create_email_template(
            conn,
            name="Delete-Test",
            subject="Test",
            body="Test"
        )
        
        # Lösche
        success = delete_email_template(conn, template_id)
        assert success, "Löschen sollte erfolgreich sein"
        
        # Verifiziere (sollte nicht mehr in aktiven Vorlagen sein)
        active_templates = list_email_templates(conn, active_only=True)
        assert len(active_templates) == 0, "Sollte keine aktiven Vorlagen mehr geben"
        
        # Aber noch in DB vorhanden (soft delete)
        all_templates = list_email_templates(conn, active_only=False)
        assert len(all_templates) == 1, "Vorlage sollte noch in DB sein"
        assert not all_templates[0]['is_active'], "Vorlage sollte inaktiv sein"
        
        print("   Vorlage erfolgreich gelöscht (soft delete)")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


# ============================================================================
# Test 2: Platzhalter-Ersetzung (Requirement 4.2)
# ============================================================================

def test_replace_placeholders_basic():
    """Test: Grundlegende Platzhalter-Ersetzung"""
    print("\n=== Test: replace_placeholders_basic ===")
    
    try:
        customer_data = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'max@example.com'
        }
        
        text = "Hallo {{customer_name}}, Ihre E-Mail ist {{email}}."
        result = replace_placeholders(text, customer_data)
        
        assert "Max Mustermann" in result, "customer_name nicht ersetzt"
        assert "max@example.com" in result, "email nicht ersetzt"
        assert "{{" not in result, "Platzhalter nicht vollständig ersetzt"
        
        print("   Grundlegende Platzhalter erfolgreich ersetzt")
        print(f"   Ergebnis: {result}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_replace_placeholders_all_types():
    """Test: Alle Platzhalter-Typen"""
    print("\n=== Test: replace_placeholders_all_types ===")
    
    try:
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
        
        text = """
        Name: {{customer_name}}
        Vorname: {{first_name}}
        Nachname: {{last_name}}
        Firma: {{company_name}}
        E-Mail: {{email}}
        Telefon: {{phone}}
        Adresse: {{address}}
        Stadt: {{city}}
        PLZ: {{zip_code}}
        Projektwert: {{project_value}}
        Datum: {{current_date}}
        """
        
        result = replace_placeholders(text, customer_data)
        
        # Verifiziere alle Ersetzungen
        assert "Max Mustermann" in result, "customer_name nicht ersetzt"
        assert "Max" in result, "first_name nicht ersetzt"
        assert "Mustermann" in result, "last_name nicht ersetzt"
        assert "Musterfirma GmbH" in result, "company_name nicht ersetzt"
        assert "max@example.com" in result, "email nicht ersetzt"
        assert "+49 123 456789" in result, "phone nicht ersetzt"
        assert "Musterstraße 42" in result, "address nicht ersetzt"
        assert "Musterstadt" in result, "city nicht ersetzt"
        assert "12345" in result, "zip_code nicht ersetzt"
        assert "25000" in result, "project_value nicht ersetzt"
        assert "{{" not in result, "Noch Platzhalter übrig"
        
        print("   Alle Platzhalter-Typen erfolgreich ersetzt")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_replace_placeholders_missing_data():
    """Test: Platzhalter-Ersetzung mit fehlenden Daten"""
    print("\n=== Test: replace_placeholders_missing_data ===")
    
    try:
        customer_data = {
            'first_name': 'Max',
            # last_name fehlt
            'email': 'max@example.com'
        }
        
        text = "Hallo {{customer_name}}, E-Mail: {{email}}"
        result = replace_placeholders(text, customer_data)
        
        # Sollte mit leeren Strings ersetzen
        assert "Hallo Max" in result, "Sollte mit vorhandenem Namen ersetzen"
        assert "max@example.com" in result, "E-Mail sollte ersetzt werden"
        
        print("   Fehlende Daten korrekt behandelt (leere Strings)")
        print(f"   Ergebnis: {result}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_extract_placeholders():
    """Test: Platzhalter aus Text extrahieren"""
    print("\n=== Test: extract_placeholders ===")
    
    try:
        text = "Hallo {{customer_name}}, Ihre E-Mail {{email}} und Telefon {{phone}}."
        placeholders = extract_placeholders(text)
        
        assert len(placeholders) == 3, f"Sollte 3 Platzhalter finden, fand {len(placeholders)}"
        assert "customer_name" in placeholders, "customer_name fehlt"
        assert "email" in placeholders, "email fehlt"
        assert "phone" in placeholders, "phone fehlt"
        
        print("   Platzhalter erfolgreich extrahiert")
        print(f"   Gefunden: {placeholders}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


# ============================================================================
# Test 3: E-Mail-Versand (Mock) (Requirement 4.1)
# ============================================================================

def test_send_email_mock():
    """Test: E-Mail-Versand mit Mock"""
    print("\n=== Test: send_email_mock ===")
    
    try:
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'smtp_use_tls': True,
            'smtp_from_email': 'test@example.com',
            'smtp_from_name': 'Test Sender'
        }
        
        # Mock SMTP
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            # Sende E-Mail
            success, message = send_email(
                config,
                recipient_email='recipient@example.com',
                subject='Test-Betreff',
                body='Test-Nachricht',
                html=False
            )
            
            # Verifiziere
            assert success, f"E-Mail-Versand sollte erfolgreich sein: {message}"
            assert "erfolgreich" in message.lower(), "Erfolgsmeldung erwartet"
            
            # Verifiziere SMTP-Aufrufe
            mock_smtp.assert_called_once_with('smtp.example.com', 587, timeout=30)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@example.com', 'password')
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
            
            print("   E-Mail erfolgreich versendet (Mock)")
            print(f"   Nachricht: {message}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_send_email_with_attachments_mock():
    """Test: E-Mail mit Anhängen versenden (Mock)"""
    print("\n=== Test: send_email_with_attachments_mock ===")
    
    try:
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'smtp_use_tls': True,
            'smtp_from_email': 'test@example.com'
        }
        
        attachments = [
            ('test.pdf', b'PDF content'),
            ('image.jpg', b'Image content')
        ]
        
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            success, message = send_email(
                config,
                recipient_email='recipient@example.com',
                subject='Test mit Anhängen',
                body='Test-Nachricht',
                attachments=attachments
            )
            
            assert success, "E-Mail mit Anhängen sollte erfolgreich sein"
            mock_server.send_message.assert_called_once()
            
            print("   E-Mail mit Anhängen erfolgreich versendet (Mock)")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_send_email_authentication_error_mock():
    """Test: E-Mail-Versand mit Authentifizierungsfehler (Mock)"""
    print("\n=== Test: send_email_authentication_error_mock ===")
    
    try:
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'wrong_password',
            'smtp_use_tls': True,
            'smtp_from_email': 'test@example.com'
        }
        
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            # Simuliere Authentifizierungsfehler
            import smtplib
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
            
            success, message = send_email(
                config,
                recipient_email='recipient@example.com',
                subject='Test',
                body='Test'
            )
            
            assert not success, "E-Mail-Versand sollte fehlschlagen"
            assert "authentifizierung" in message.lower(), "Fehlermeldung sollte Authentifizierung erwähnen"
            
            print("   Authentifizierungsfehler korrekt behandelt")
            print(f"   Fehlermeldung: {message}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_send_email_incomplete_config():
    """Test: E-Mail-Versand mit unvollständiger Konfiguration"""
    print("\n=== Test: send_email_incomplete_config ===")
    
    try:
        # Unvollständige Konfiguration (fehlt smtp_password)
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': '',  # Leer
            'smtp_use_tls': True
        }
        
        success, message = send_email(
            config,
            recipient_email='recipient@example.com',
            subject='Test',
            body='Test'
        )
        
        assert not success, "E-Mail-Versand sollte fehlschlagen"
        assert "unvollständig" in message.lower(), "Fehlermeldung sollte 'unvollständig' enthalten"
        
        print("   Unvollständige Konfiguration korrekt erkannt")
        print(f"   Fehlermeldung: {message}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


def test_test_smtp_connection_mock():
    """Test: SMTP-Verbindungstest (Mock)"""
    print("\n=== Test: test_smtp_connection_mock ===")
    
    try:
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'smtp_use_tls': True
        }
        
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            success, message = test_smtp_connection(config)
            
            assert success, f"Verbindungstest sollte erfolgreich sein: {message}"
            assert "erfolgreich" in message.lower(), "Erfolgsmeldung erwartet"
            
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.quit.assert_called_once()
            
            print("   SMTP-Verbindungstest erfolgreich (Mock)")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise


# ============================================================================
# Test 4: E-Mail mit Vorlage versenden (Requirement 4.3)
# ============================================================================

def test_send_email_with_template_mock():
    """Test: E-Mail mit Vorlage versenden (Mock)"""
    print("\n=== Test: send_email_with_template_mock ===")
    
    conn = setup_test_db()
    
    try:
        # Erstelle Kunde
        customer_id = create_test_customer(conn)
        
        # Erstelle Vorlage
        template_id = create_email_template(
            conn,
            name="Test-Vorlage",
            subject="Angebot für {{customer_name}}",
            body="Sehr geehrte/r {{customer_name}},\n\nIhre E-Mail: {{email}}\nStadt: {{city}}\n\nMit freundlichen Grüßen"
        )
        
        # Hole Kundendaten
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer_data = dict(cursor.fetchone())
        customer_data['id'] = customer_id
        
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'smtp_use_tls': True,
            'smtp_from_email': 'test@example.com'
        }
        
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            success, message = send_email_with_template(
                conn,
                config,
                template_id,
                customer_data,
                sent_by='Test User'
            )
            
            assert success, f"E-Mail mit Vorlage sollte erfolgreich sein: {message}"
            
            # Verifiziere E-Mail-Historie
            history = get_email_history_for_customer(conn, customer_id)
            assert len(history) == 1, "Sollte 1 E-Mail in Historie haben"
            assert "Max Mustermann" in history[0]['subject'], "Platzhalter im Betreff nicht ersetzt"
            assert "max@example.com" in history[0]['body'], "Platzhalter im Body nicht ersetzt"
            assert history[0]['status'] == 'sent', "Status sollte 'sent' sein"
            
            print("   E-Mail mit Vorlage erfolgreich versendet (Mock)")
            print(f"   Betreff: {history[0]['subject']}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_send_email_with_template_failed_mock():
    """Test: Fehlgeschlagener E-Mail-Versand mit Vorlage (Mock)"""
    print("\n=== Test: send_email_with_template_failed_mock ===")
    
    conn = setup_test_db()
    
    try:
        customer_id = create_test_customer(conn)
        
        template_id = create_email_template(
            conn,
            name="Test-Vorlage-Fehler",
            subject="Test",
            body="Test"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer_data = dict(cursor.fetchone())
        customer_data['id'] = customer_id
        
        config = {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_username': 'test@example.com',
            'smtp_password': 'password',
            'smtp_use_tls': True,
            'smtp_from_email': 'test@example.com'
        }
        
        with patch('email_manager.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            # Simuliere Fehler
            import smtplib
            mock_server.send_message.side_effect = smtplib.SMTPException("Test error")
            
            success, message = send_email_with_template(
                conn,
                config,
                template_id,
                customer_data
            )
            
            assert not success, "E-Mail-Versand sollte fehlschlagen"
            
            # Verifiziere E-Mail-Historie (sollte Fehler enthalten)
            history = get_email_history_for_customer(conn, customer_id)
            assert len(history) == 1, "Sollte 1 E-Mail in Historie haben"
            assert history[0]['status'] == 'failed', "Status sollte 'failed' sein"
            assert history[0]['error_message'] is not None, "Fehlermeldung sollte gespeichert sein"
            
            print("   Fehlgeschlagener Versand korrekt in Historie gespeichert")
            print(f"   Fehlermeldung: {history[0]['error_message']}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


# ============================================================================
# Test 5: E-Mail-Historie
# ============================================================================

def test_save_email_to_history():
    """Test: E-Mail in Historie speichern"""
    print("\n=== Test: save_email_to_history ===")
    
    conn = setup_test_db()
    
    try:
        customer_id = create_test_customer(conn)
        
        # Speichere E-Mail
        email_id = save_email_to_history(
            conn,
            customer_id=customer_id,
            recipient_email='test@example.com',
            subject='Test-Betreff',
            body='Test-Body',
            status='sent',
            sent_by='Test User'
        )
        
        assert email_id is not None, "E-Mail-ID sollte nicht None sein"
        
        # Verifiziere
        history = get_email_history_for_customer(conn, customer_id)
        assert len(history) == 1, "Sollte 1 E-Mail in Historie haben"
        assert history[0]['subject'] == 'Test-Betreff', "Betreff stimmt nicht"
        assert history[0]['status'] == 'sent', "Status stimmt nicht"
        
        print("   E-Mail erfolgreich in Historie gespeichert")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


def test_get_email_history_multiple():
    """Test: Mehrere E-Mails in Historie"""
    print("\n=== Test: get_email_history_multiple ===")
    
    conn = setup_test_db()
    
    try:
        customer_id = create_test_customer(conn)
        
        # Speichere mehrere E-Mails
        for i in range(3):
            save_email_to_history(
                conn,
                customer_id=customer_id,
                recipient_email='test@example.com',
                subject=f'E-Mail {i+1}',
                body=f'Body {i+1}',
                status='sent'
            )
        
        # Hole Historie
        history = get_email_history_for_customer(conn, customer_id)
        
        assert len(history) == 3, f"Sollte 3 E-Mails haben, hat {len(history)}"
        
        # Sollte nach Datum sortiert sein (neueste zuerst)
        # Da alle zur gleichen Zeit erstellt wurden, prüfen wir nur die Anzahl
        subjects = [h['subject'] for h in history]
        assert 'E-Mail 1' in subjects and 'E-Mail 2' in subjects and 'E-Mail 3' in subjects, "Alle E-Mails sollten vorhanden sein"
        
        print("   Mehrere E-Mails korrekt in Historie")
        print(f"   Anzahl: {len(history)}")
        
    except AssertionError as e:
        print(f"   Test fehlgeschlagen: {e}")
        raise
    finally:
        cleanup_test_db(conn)


# ============================================================================
# Test-Runner
# ============================================================================

def run_all_tests():
    """Führt alle Tests aus."""
    print("\n" + "=" * 70)
    print("E-Mail-Integration - Unit Tests")
    print("=" * 70)
    
    tests = [
        # Vorlagen-System (Requirement 4.2)
        ("Vorlagen: Erstellen", test_create_email_template),
        ("Vorlagen: Duplikat ablehnen", test_create_duplicate_template),
        ("Vorlagen: Nach Name abrufen", test_get_template_by_name),
        ("Vorlagen: Auflisten", test_list_email_templates),
        ("Vorlagen: Aktualisieren", test_update_email_template),
        ("Vorlagen: Löschen (soft delete)", test_delete_email_template),
        
        # Platzhalter-Ersetzung (Requirement 4.2)
        ("Platzhalter: Grundlegend", test_replace_placeholders_basic),
        ("Platzhalter: Alle Typen", test_replace_placeholders_all_types),
        ("Platzhalter: Fehlende Daten", test_replace_placeholders_missing_data),
        ("Platzhalter: Extrahieren", test_extract_placeholders),
        
        # E-Mail-Versand (Mock) (Requirement 4.1)
        ("E-Mail-Versand: Basic (Mock)", test_send_email_mock),
        ("E-Mail-Versand: Mit Anhängen (Mock)", test_send_email_with_attachments_mock),
        ("E-Mail-Versand: Auth-Fehler (Mock)", test_send_email_authentication_error_mock),
        ("E-Mail-Versand: Unvollständige Config", test_send_email_incomplete_config),
        ("E-Mail-Versand: Verbindungstest (Mock)", test_test_smtp_connection_mock),
        
        # E-Mail mit Vorlage (Requirement 4.3)
        ("Vorlage-Versand: Erfolgreich (Mock)", test_send_email_with_template_mock),
        ("Vorlage-Versand: Fehlgeschlagen (Mock)", test_send_email_with_template_failed_mock),
        
        # E-Mail-Historie
        ("Historie: Speichern", test_save_email_to_history),
        ("Historie: Mehrere E-Mails", test_get_email_history_multiple),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\nTest '{test_name}' fehlgeschlagen: {e}")
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("Test-Zusammenfassung")
    print("=" * 70)
    print(f"Bestanden: {passed}/{len(tests)}")
    print(f"Fehlgeschlagen: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n Alle Tests erfolgreich!")
        print("\nGetestete Funktionalität:")
        print("  E-Mail-Vorlagen-System (CRUD) (Requirement 4.2)")
        print("  Platzhalter-Ersetzung (alle Typen) (Requirement 4.2)")
        print("  E-Mail-Versand mit Mock (Requirement 4.1)")
        print("  E-Mail-Versand mit Vorlagen (Requirement 4.3)")
        print("  E-Mail-Historie und Tracking")
        print("  Fehlerbehandlung und Validierung")
    else:
        print(f"\n{failed} Test(s) fehlgeschlagen - bitte überprüfen!")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
