"""
CRM Email Manager Module
Handles email sending, templates, and email history

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import json
import smtplib
import sqlite3
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any


def create_email_tables(conn: sqlite3.Connection) -> None:
    """Create email_templates and email_history tables"""
    cursor = conn.cursor()
    
    # Email Templates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT,
            placeholders TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Email History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            recipient_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            template_id INTEGER,
            attachments TEXT,
            status TEXT DEFAULT 'sent',
            error_message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_by TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (template_id) REFERENCES email_templates(id)
        )
    """)
    
    conn.commit()


def ensure_email_tables(conn: sqlite3.Connection) -> None:
    """Ensure email tables exist"""
    try:
        create_email_tables(conn)
    except Exception as e:
        print(f"Error ensuring email tables: {e}")


# ============================================================================
# SMTP Configuration Management
# ============================================================================

def get_smtp_config(load_admin_setting_func) -> dict[str, Any]:
    """Get SMTP configuration from admin settings"""
    default_config = {
        'smtp_host': '',
        'smtp_port': 587,
        'smtp_username': '',
        'smtp_password': '',
        'smtp_use_tls': True,
        'smtp_from_email': '',
        'smtp_from_name': ''
    }
    
    try:
        config = load_admin_setting_func('smtp_config', default_config)
        return config if isinstance(config, dict) else default_config
    except Exception:
        return default_config


def save_smtp_config(save_admin_setting_func, config: dict[str, Any]) -> bool:
    """Save SMTP configuration to admin settings"""
    try:
        return save_admin_setting_func('smtp_config', config)
    except Exception as e:
        print(f"Error saving SMTP config: {e}")
        return False


def test_smtp_connection(config: dict[str, Any]) -> tuple[bool, str]:
    """Test SMTP connection with given configuration"""
    try:
        smtp_host = config.get('smtp_host', '')
        smtp_port = config.get('smtp_port', 587)
        smtp_username = config.get('smtp_username', '')
        smtp_password = config.get('smtp_password', '')
        use_tls = config.get('smtp_use_tls', True)
        
        if not smtp_host or not smtp_username or not smtp_password:
            return False, "SMTP-Konfiguration unvollständig"
        
        # Connect to SMTP server
        if use_tls:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        
        # Login
        server.login(smtp_username, smtp_password)
        server.quit()
        
        return True, "Verbindung erfolgreich"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentifizierung fehlgeschlagen - Benutzername oder Passwort falsch"
    except smtplib.SMTPException as e:
        return False, f"SMTP-Fehler: {str(e)}"
    except Exception as e:
        return False, f"Verbindungsfehler: {str(e)}"


# ============================================================================
# Email Template Management
# ============================================================================

def create_email_template(
    conn: sqlite3.Connection,
    name: str,
    subject: str,
    body: str,
    category: str | None = None,
    placeholders: list[str] | None = None
) -> int | None:
    """Create a new email template"""
    try:
        cursor = conn.cursor()
        placeholders_json = json.dumps(placeholders) if placeholders else None
        
        cursor.execute("""
            INSERT INTO email_templates (name, subject, body, category, placeholders)
            VALUES (?, ?, ?, ?, ?)
        """, (name, subject, body, category, placeholders_json))
        
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Template with name '{name}' already exists")
        return None
    except Exception as e:
        print(f"Error creating email template: {e}")
        return None


def get_email_template(conn: sqlite3.Connection, template_id: int) -> dict[str, Any] | None:
    """Get email template by ID"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, subject, body, category, placeholders, is_active, 
                   created_at, updated_at
            FROM email_templates
            WHERE id = ?
        """, (template_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'body': row[3],
                'category': row[4],
                'placeholders': json.loads(row[5]) if row[5] else [],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            }
        return None
    except Exception as e:
        print(f"Error getting email template: {e}")
        return None


def get_email_template_by_name(conn: sqlite3.Connection, name: str) -> dict[str, Any] | None:
    """Get email template by name"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, subject, body, category, placeholders, is_active, 
                   created_at, updated_at
            FROM email_templates
            WHERE name = ? AND is_active = 1
        """, (name,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'body': row[3],
                'category': row[4],
                'placeholders': json.loads(row[5]) if row[5] else [],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            }
        return None
    except Exception as e:
        print(f"Error getting email template by name: {e}")
        return None


def list_email_templates(
    conn: sqlite3.Connection,
    category: str | None = None,
    active_only: bool = True
) -> list[dict[str, Any]]:
    """List all email templates"""
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, subject, body, category, placeholders, is_active, 
                   created_at, updated_at
            FROM email_templates
        """
        params = []
        
        conditions = []
        if active_only:
            conditions.append("is_active = 1")
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            templates.append({
                'id': row[0],
                'name': row[1],
                'subject': row[2],
                'body': row[3],
                'category': row[4],
                'placeholders': json.loads(row[5]) if row[5] else [],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        return templates
    except Exception as e:
        print(f"Error listing email templates: {e}")
        return []


def update_email_template(
    conn: sqlite3.Connection,
    template_id: int,
    name: str | None = None,
    subject: str | None = None,
    body: str | None = None,
    category: str | None = None,
    placeholders: list[str] | None = None,
    is_active: bool | None = None
) -> bool:
    """Update an email template"""
    try:
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if subject is not None:
            updates.append("subject = ?")
            params.append(subject)
        if body is not None:
            updates.append("body = ?")
            params.append(body)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if placeholders is not None:
            updates.append("placeholders = ?")
            params.append(json.dumps(placeholders))
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        params.append(template_id)
        
        query = f"UPDATE email_templates SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating email template: {e}")
        return False


def delete_email_template(conn: sqlite3.Connection, template_id: int) -> bool:
    """Delete an email template (soft delete by setting is_active to 0)"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE email_templates 
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), template_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting email template: {e}")
        return False


# ============================================================================
# Placeholder Replacement
# ============================================================================

def replace_placeholders(text: str, customer_data: dict[str, Any]) -> str:
    """Replace placeholders in text with customer data
    
    Supported placeholders:
    - {{customer_name}} - Full customer name
    - {{first_name}} - Customer first name
    - {{last_name}} - Customer last name
    - {{company_name}} - Company name
    - {{email}} - Customer email
    - {{phone}} - Customer phone
    - {{address}} - Full address
    - {{city}} - City
    - {{zip_code}} - ZIP code
    - {{project_value}} - Project value
    - {{current_date}} - Current date
    """
    replacements = {
        '{{customer_name}}': f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
        '{{first_name}}': customer_data.get('first_name', ''),
        '{{last_name}}': customer_data.get('last_name', ''),
        '{{company_name}}': customer_data.get('company_name', ''),
        '{{email}}': customer_data.get('email', ''),
        '{{phone}}': customer_data.get('phone_mobile') or customer_data.get('phone_landline', ''),
        '{{address}}': f"{customer_data.get('address', '')} {customer_data.get('house_number', '')}".strip(),
        '{{city}}': customer_data.get('city', ''),
        '{{zip_code}}': customer_data.get('zip_code', ''),
        '{{project_value}}': str(customer_data.get('project_value', '')),
        '{{current_date}}': datetime.now().strftime('%d.%m.%Y')
    }
    
    result = text
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, str(value))
    
    return result


def extract_placeholders(text: str) -> list[str]:
    """Extract all placeholders from text"""
    import re
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, text)
    return list(set(matches))


# ============================================================================
# Email Sending
# ============================================================================

def send_email(
    config: dict[str, Any],
    recipient_email: str,
    subject: str,
    body: str,
    attachments: list[tuple[str, bytes]] | None = None,
    html: bool = False
) -> tuple[bool, str]:
    """Send an email using SMTP
    
    Args:
        config: SMTP configuration dictionary
        recipient_email: Recipient email address
        subject: Email subject
        body: Email body
        attachments: List of (filename, file_bytes) tuples
        html: Whether body is HTML
    
    Returns:
        Tuple of (success, message)
    """
    try:
        smtp_host = config.get('smtp_host', '')
        smtp_port = config.get('smtp_port', 587)
        smtp_username = config.get('smtp_username', '')
        smtp_password = config.get('smtp_password', '')
        use_tls = config.get('smtp_use_tls', True)
        from_email = config.get('smtp_from_email', smtp_username)
        from_name = config.get('smtp_from_name', '')
        
        if not smtp_host or not smtp_username or not smtp_password:
            return False, "SMTP-Konfiguration unvollständig"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>" if from_name else from_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body
        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Add attachments
        if attachments:
            for filename, file_bytes in attachments:
                part = MIMEApplication(file_bytes, Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
        
        # Connect and send
        if use_tls:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True, "E-Mail erfolgreich versendet"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentifizierung fehlgeschlagen"
    except smtplib.SMTPRecipientsRefused:
        return False, "Empfänger-Adresse ungültig"
    except smtplib.SMTPException as e:
        return False, f"SMTP-Fehler: {str(e)}"
    except Exception as e:
        return False, f"Fehler beim Senden: {str(e)}"


def send_email_with_template(
    conn: sqlite3.Connection,
    config: dict[str, Any],
    template_id: int,
    customer_data: dict[str, Any],
    recipient_email: str | None = None,
    attachments: list[tuple[str, bytes]] | None = None,
    sent_by: str | None = None
) -> tuple[bool, str]:
    """Send email using a template
    
    Args:
        conn: Database connection
        config: SMTP configuration
        template_id: Email template ID
        customer_data: Customer data for placeholder replacement
        recipient_email: Override recipient email (uses customer email if None)
        attachments: List of (filename, file_bytes) tuples
        sent_by: Username of sender
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Get template
        template = get_email_template(conn, template_id)
        if not template:
            return False, "Vorlage nicht gefunden"
        
        # Get recipient email
        if not recipient_email:
            recipient_email = customer_data.get('email', '')
        
        if not recipient_email:
            return False, "Keine E-Mail-Adresse angegeben"
        
        # Replace placeholders
        subject = replace_placeholders(template['subject'], customer_data)
        body = replace_placeholders(template['body'], customer_data)
        
        # Send email
        success, message = send_email(
            config,
            recipient_email,
            subject,
            body,
            attachments,
            html=False
        )
        
        # Save to history
        save_email_to_history(
            conn,
            customer_id=customer_data.get('id'),
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            template_id=template_id,
            attachments=[filename for filename, _ in attachments] if attachments else None,
            status='sent' if success else 'failed',
            error_message=None if success else message,
            sent_by=sent_by
        )
        
        return success, message
    except Exception as e:
        error_msg = f"Fehler beim Senden: {str(e)}"
        # Try to save failed attempt to history
        try:
            save_email_to_history(
                conn,
                customer_id=customer_data.get('id'),
                recipient_email=recipient_email or customer_data.get('email', ''),
                subject=template.get('subject', '') if template else '',
                body='',
                template_id=template_id,
                status='failed',
                error_message=error_msg,
                sent_by=sent_by
            )
        except Exception:
            pass
        
        return False, error_msg


# ============================================================================
# Email History
# ============================================================================

def save_email_to_history(
    conn: sqlite3.Connection,
    customer_id: int | None,
    recipient_email: str,
    subject: str,
    body: str,
    template_id: int | None = None,
    attachments: list[str] | None = None,
    status: str = 'sent',
    error_message: str | None = None,
    sent_by: str | None = None
) -> int | None:
    """Save sent email to history"""
    try:
        cursor = conn.cursor()
        attachments_json = json.dumps(attachments) if attachments else None
        
        cursor.execute("""
            INSERT INTO email_history 
            (customer_id, recipient_email, subject, body, template_id, 
             attachments, status, error_message, sent_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, recipient_email, subject, body, template_id,
              attachments_json, status, error_message, sent_by))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving email to history: {e}")
        return None


def get_email_history_for_customer(
    conn: sqlite3.Connection,
    customer_id: int,
    limit: int = 50
) -> list[dict[str, Any]]:
    """Get email history for a customer"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, recipient_email, subject, body, template_id, 
                   attachments, status, error_message, sent_at, sent_by
            FROM email_history
            WHERE customer_id = ?
            ORDER BY sent_at DESC
            LIMIT ?
        """, (customer_id, limit))
        
        rows = cursor.fetchall()
        history = []
        
        for row in rows:
            history.append({
                'id': row[0],
                'recipient_email': row[1],
                'subject': row[2],
                'body': row[3],
                'template_id': row[4],
                'attachments': json.loads(row[5]) if row[5] else [],
                'status': row[6],
                'error_message': row[7],
                'sent_at': row[8],
                'sent_by': row[9]
            })
        
        return history
    except Exception as e:
        print(f"Error getting email history: {e}")
        return []


def get_all_email_history(
    conn: sqlite3.Connection,
    limit: int = 100,
    status: str | None = None
) -> list[dict[str, Any]]:
    """Get all email history"""
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT eh.id, eh.customer_id, eh.recipient_email, eh.subject, 
                   eh.body, eh.template_id, eh.attachments, eh.status, 
                   eh.error_message, eh.sent_at, eh.sent_by,
                   c.first_name, c.last_name
            FROM email_history eh
            LEFT JOIN customers c ON eh.customer_id = c.id
        """
        params = []
        
        if status:
            query += " WHERE eh.status = ?"
            params.append(status)
        
        query += " ORDER BY eh.sent_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'customer_id': row[1],
                'recipient_email': row[2],
                'subject': row[3],
                'body': row[4],
                'template_id': row[5],
                'attachments': json.loads(row[6]) if row[6] else [],
                'status': row[7],
                'error_message': row[8],
                'sent_at': row[9],
                'sent_by': row[10],
                'customer_name': f"{row[11]} {row[12]}" if row[11] and row[12] else None
            })
        
        return history
    except Exception as e:
        print(f"Error getting all email history: {e}")
        return []


# ============================================================================
# Default Templates
# ============================================================================

def create_default_templates(conn: sqlite3.Connection) -> None:
    """Create default email templates"""
    default_templates = [
        {
            'name': 'Angebot versendet',
            'subject': 'Ihr Solar-Angebot von {{company_name}}',
            'body': '''Sehr geehrte/r {{customer_name}},

vielen Dank für Ihr Interesse an einer Photovoltaikanlage.

Im Anhang finden Sie Ihr persönliches Angebot. Gerne stehe ich Ihnen für Rückfragen zur Verfügung.

Mit freundlichen Grüßen
{{current_date}}''',
            'category': 'Angebot',
            'placeholders': ['customer_name', 'company_name', 'current_date']
        },
        {
            'name': 'Follow-up nach Angebot',
            'subject': 'Nachfrage zu Ihrem Solar-Angebot',
            'body': '''Sehr geehrte/r {{customer_name}},

vor einigen Tagen haben Sie von uns ein Angebot für eine Photovoltaikanlage erhalten.

Haben Sie Fragen zu unserem Angebot? Gerne bespreche ich die Details persönlich mit Ihnen.

Mit freundlichen Grüßen
{{current_date}}''',
            'category': 'Follow-up',
            'placeholders': ['customer_name', 'current_date']
        },
        {
            'name': 'Terminbestätigung',
            'subject': 'Terminbestätigung - {{company_name}}',
            'body': '''Sehr geehrte/r {{customer_name}},

hiermit bestätigen wir unseren Termin am [DATUM] um [UHRZEIT] Uhr.

Adresse: {{address}}, {{zip_code}} {{city}}

Wir freuen uns auf Ihren Besuch!

Mit freundlichen Grüßen
{{current_date}}''',
            'category': 'Termin',
            'placeholders': ['customer_name', 'company_name', 'address', 'zip_code', 'city', 'current_date']
        },
        {
            'name': 'Auftragsbestätigung',
            'subject': 'Auftragsbestätigung - {{company_name}}',
            'body': '''Sehr geehrte/r {{customer_name}},

vielen Dank für Ihren Auftrag!

Wir werden uns in Kürze mit Ihnen in Verbindung setzen, um die nächsten Schritte zu besprechen.

Mit freundlichen Grüßen
{{current_date}}''',
            'category': 'Auftrag',
            'placeholders': ['customer_name', 'company_name', 'current_date']
        }
    ]
    
    for template_data in default_templates:
        try:
            create_email_template(
                conn,
                name=template_data['name'],
                subject=template_data['subject'],
                body=template_data['body'],
                category=template_data['category'],
                placeholders=template_data['placeholders']
            )
        except Exception as e:
            print(f"Error creating default template '{template_data['name']}': {e}")
