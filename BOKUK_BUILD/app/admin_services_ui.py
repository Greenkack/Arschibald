"""
admin_services_ui.py

Admin UI für Dienstleistungen & Service Einstellungen
CRUD-Funktionalität für Services mit Upload und manueller Eingabe
"""

import sqlite3
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st


# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        from database import get_db_connection as get_db_conn
        return get_db_conn()
    except ImportError:
        # Fallback to direct connection
        return sqlite3.connect('data/app_data.db')


def init_services_table():
    """Initialize services table if not exists"""
    conn = get_db_connection()
    if not conn:
        print("Error: Could not get database connection")
        return

    cursor = conn.cursor()

    try:
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                price REAL,
                calculate_per TEXT DEFAULT 'Stück',
                is_standard BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Check if pdf_order column exists, if not add it
        cursor.execute("PRAGMA table_info(services)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'pdf_order' not in columns:
            cursor.execute(
                'ALTER TABLE services ADD COLUMN pdf_order INTEGER DEFAULT 0')
            print("Added pdf_order column to services table")

        conn.commit()
    except Exception as e:
        print(f"Error initializing services table: {e}")
        conn.rollback()
    finally:
        conn.close()


def load_services() -> list[dict[str, Any]]:
    """Load all services from database"""
    init_services_table()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if pdf_order column exists before querying
    cursor.execute("PRAGMA table_info(services)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'pdf_order' in columns:
        cursor.execute('''
            SELECT id, name, description, category, price, calculate_per,
                   is_standard, is_active, pdf_order, created_at, updated_at
            FROM services
            WHERE is_active = 1
            ORDER BY pdf_order ASC, category, name
        ''')
    else:
        # Fallback query without pdf_order column
        cursor.execute('''
            SELECT id, name, description, category, price, calculate_per,
                   is_standard, is_active, created_at, updated_at
            FROM services
            WHERE is_active = 1
            ORDER BY category, name
        ''')

    services = []
    for row in cursor.fetchall():
        if 'pdf_order' in columns:
            services.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'price': row[4],
                'calculate_per': row[5],
                'is_standard': bool(row[6]),
                'is_active': bool(row[7]),
                'pdf_order': row[8] or 0,
                'created_at': row[9],
                'updated_at': row[10]
            })
        else:
            services.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'price': row[4],
                'calculate_per': row[5],
                'is_standard': bool(row[6]),
                'is_active': bool(row[7]),
                'pdf_order': 0,  # Default value
                'created_at': row[8],
                'updated_at': row[9]
            })

    conn.close()
    return services


def save_service(service_data: dict[str, Any]) -> bool:
    """Save service to database"""
    try:
        init_services_table()
        conn = get_db_connection()
        if not conn:
            st.error("Keine Datenbankverbindung möglich")
            return False

        cursor = conn.cursor()

        # Check if pdf_order column exists
        cursor.execute("PRAGMA table_info(services)")
        columns = [column[1] for column in cursor.fetchall()]
        has_pdf_order = 'pdf_order' in columns

        if service_data.get('id'):
            # Update existing service
            if has_pdf_order:
                cursor.execute('''
                    UPDATE services
                    SET name=?, description=?, category=?, price=?, calculate_per=?,
                        is_standard=?, pdf_order=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (
                    service_data['name'],
                    service_data['description'],
                    service_data['category'],
                    service_data['price'],
                    service_data['calculate_per'],
                    service_data['is_standard'],
                    service_data.get('pdf_order', 0),
                    service_data['id']
                ))
            else:
                cursor.execute('''
                    UPDATE services
                    SET name=?, description=?, category=?, price=?, calculate_per=?,
                        is_standard=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (
                    service_data['name'],
                    service_data['description'],
                    service_data['category'],
                    service_data['price'],
                    service_data['calculate_per'],
                    service_data['is_standard'],
                    service_data['id']
                ))
        else:
            # Insert new service
            if has_pdf_order:
                cursor.execute('''
                    INSERT INTO services (name, description, category, price, calculate_per, is_standard, pdf_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    service_data['name'],
                    service_data['description'],
                    service_data['category'],
                    service_data['price'],
                    service_data['calculate_per'],
                    service_data['is_standard'],
                    service_data.get('pdf_order', 0)
                ))
            else:
                cursor.execute('''
                    INSERT INTO services (name, description, category, price, calculate_per, is_standard)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    service_data['name'],
                    service_data['description'],
                    service_data['category'],
                    service_data['price'],
                    service_data['calculate_per'],
                    service_data['is_standard']
                ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {str(e)}")
        return False


def delete_service(service_id: int) -> bool:
    """Soft delete service"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE services
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (service_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Fehler beim Löschen: {str(e)}")
        return False


def render_services_admin_ui():
    """Render the services administration UI"""
    st.header("🛠️ Dienstleistungen & Service Einstellungen")

    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Übersicht", "➕ Hinzufügen", "📤 Import/Export", "📄 PDF-Reihenfolge"])

    with tab1:
        render_services_overview()

    with tab2:
        render_add_service_form()

    with tab3:
        render_import_export()

    with tab4:
        render_pdf_order_management()


def render_services_overview():
    """Render services overview with CRUD operations"""
    st.subheader("Dienstleistungen Übersicht")

    services = load_services()

    if not services:
        st.info("Keine Dienstleistungen vorhanden. Fügen Sie welche hinzu.")
        return

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        categories = list(set([s['category']
                          for s in services if s['category']]))
        selected_category = st.selectbox(
            "Kategorie filtern",
            ["Alle"] + categories,
            key="services_category_filter"
        )

    with col2:
        show_standard_only = st.checkbox(
            "Nur Standard-Services",
            key="show_standard_only")

    # Filter services
    filtered_services = services
    if selected_category != "Alle":
        filtered_services = [
            s for s in filtered_services if s['category'] == selected_category]
    if show_standard_only:
        filtered_services = [s for s in filtered_services if s['is_standard']]

    # Display services table
    if filtered_services:
        for service in filtered_services:
            with st.expander(f"{'⭐ ' if service['is_standard'] else ''}🛠️ {service['name']}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(
                        f"**Beschreibung:** {service['description'] or 'Keine Beschreibung'}")
                    st.write(
                        f"**Kategorie:** {service['category'] or 'Keine Kategorie'}")
                    st.write(
                        f"**Preis:** {service['price']:.2f} € pro {service['calculate_per']}")
                    st.write(f"**PDF-Reihenfolge:** {service['pdf_order']}")
                    if service['is_standard']:
                        st.success(
                            "✅ Standard-Service (automatisch in Berechnung)")
                    else:
                        st.info("ℹ️ Optional (manuell hinzufügbar)")

                with col2:
                    if st.button(
                        "✏️ Bearbeiten",
                        key=f"edit_service_{
                            service['id']}"):
                        st.session_state[f"edit_service_data_{service['id']}"] = service
                        st.rerun()

                with col3:
                    if st.button(
                        "🗑️ Löschen", key=f"delete_service_{
                            service['id']}"):
                        if delete_service(service['id']):
                            st.success("Service gelöscht!")
                            st.rerun()

                # Edit form if editing
                if f"edit_service_data_{service['id']}" in st.session_state:
                    render_edit_service_form(service['id'])


def render_edit_service_form(service_id: int):
    """Render edit form for a service"""
    service_data = st.session_state[f"edit_service_data_{service_id}"]

    st.markdown("---")
    st.subheader("Service bearbeiten")

    with st.form(f"edit_service_form_{service_id}"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Name", value=service_data['name'])
            category = st.text_input(
                "Kategorie", value=service_data['category'] or "")
            price = st.number_input(
                "Preis (€)",
                value=float(
                    service_data['price']),
                min_value=0.0,
                step=0.01)

        with col2:
            description = st.text_area(
                "Beschreibung", value=service_data['description'] or "")
            calculate_per = st.selectbox(
                "Berechnungseinheit", [
                    "Stück", "m²", "kWp", "Stunde", "Pauschal"], index=[
                    "Stück", "m²", "kWp", "Stunde", "Pauschal"].index(
                    service_data['calculate_per']) if service_data['calculate_per'] in [
                    "Stück", "m²", "kWp", "Stunde", "Pauschal"] else 0)
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                is_standard = st.checkbox(
                    "Als Standard markieren",
                    value=service_data['is_standard'])
            with col2_2:
                pdf_order = st.number_input(
                    "PDF-Reihenfolge",
                    value=service_data.get(
                        'pdf_order',
                        0),
                    min_value=0,
                    step=1)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Speichern", type="primary"):
                updated_data = {
                    'id': service_id,
                    'name': name,
                    'description': description,
                    'category': category,
                    'price': price,
                    'calculate_per': calculate_per,
                    'is_standard': is_standard,
                    'pdf_order': pdf_order
                }

                if save_service(updated_data):
                    st.success("Service aktualisiert!")
                    del st.session_state[f"edit_service_data_{service_id}"]
                    st.rerun()

        with col2:
            if st.form_submit_button("❌ Abbrechen"):
                del st.session_state[f"edit_service_data_{service_id}"]
                st.rerun()


def render_add_service_form():
    """Render form to add new service"""
    st.subheader("Neue Dienstleistung hinzufügen")

    with st.form("add_service_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name *", placeholder="z.B. Installation PV-Anlage")
            category = st.text_input(
                "Kategorie", placeholder="z.B. Installation, Wartung, Beratung")
            price = st.number_input(
                "Preis (€) *", min_value=0.0, step=0.01, value=0.0)

        with col2:
            description = st.text_area(
                "Beschreibung",
                placeholder="Detaillierte Beschreibung der Dienstleistung")
            calculate_per = st.selectbox(
                "Berechnungseinheit",
                ["Stück", "m²", "kWp", "Stunde", "Pauschal"],
                help="Einheit für die Preisberechnung"
            )
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                is_standard = st.checkbox(
                    "Als Standard markieren",
                    help="Standard-Services werden automatisch in die Berechnung einbezogen")
            with col2_2:
                pdf_order = st.number_input(
                    "PDF-Reihenfolge",
                    value=0,
                    min_value=0,
                    step=1,
                    help="Reihenfolge in der PDF (0 = erste Position)"
                )

        if st.form_submit_button(
            "➕ Dienstleistung hinzufügen",
                type="primary"):
            if name and price >= 0:
                service_data = {
                    'name': name,
                    'description': description,
                    'category': category,
                    'price': price,
                    'calculate_per': calculate_per,
                    'is_standard': is_standard,
                    'pdf_order': pdf_order
                }

                if save_service(service_data):
                    st.success("Dienstleistung erfolgreich hinzugefügt!")
                    st.rerun()
            else:
                st.error("Bitte füllen Sie alle Pflichtfelder (*) aus.")


def render_import_export():
    """Render import/export functionality"""
    st.subheader("Import/Export")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📤 Export")
        if st.button("Services als CSV exportieren"):
            services = load_services()
            if services:
                df = pd.DataFrame(services)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 CSV herunterladen",
                    data=csv,
                    file_name=f"services_export_{
                        datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv")
            else:
                st.info("Keine Services zum Exportieren vorhanden.")

    with col2:
        st.markdown("#### 📥 Import")
        uploaded_file = st.file_uploader(
            "CSV-Datei hochladen",
            type=['csv'],
            help="CSV mit Spalten: name, description, category, price, calculate_per, is_standard"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)

                # Validate required columns
                required_columns = ['name', 'price']
                missing_columns = [
                    col for col in required_columns if col not in df.columns]

                if missing_columns:
                    st.error(f"Fehlende Spalten: {', '.join(missing_columns)}")
                else:
                    st.write("Vorschau der zu importierenden Daten:")
                    st.dataframe(df.head())

                    if st.button("📥 Import starten"):
                        success_count = 0
                        error_count = 0

                        for _, row in df.iterrows():
                            try:
                                service_data = {
                                    'name': row['name'], 'description': row.get(
                                        'description', ''), 'category': row.get(
                                        'category', ''), 'price': float(
                                        row['price']), 'calculate_per': row.get(
                                        'calculate_per', 'Stück'), 'is_standard': bool(
                                        row.get(
                                            'is_standard', False))}

                                if save_service(service_data):
                                    success_count += 1
                                else:
                                    error_count += 1
                            except Exception as e:
                                error_count += 1
                                st.error(
                                    f"Fehler bei Zeile {
                                        row.name}: {
                                        str(e)}")

                        st.success(
                            f"Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
                        if success_count > 0:
                            st.rerun()

            except Exception as e:
                st.error(f"Fehler beim Lesen der CSV-Datei: {str(e)}")

# Helper functions for integration


def get_standard_services() -> list[dict[str, Any]]:
    """Get all standard services for automatic inclusion in calculations"""
    services = load_services()
    return [s for s in services if s['is_standard']]


def get_optional_services() -> list[dict[str, Any]]:
    """Get all optional services for manual selection"""
    services = load_services()
    return [s for s in services if not s['is_standard']]


def get_all_services() -> list[dict[str, Any]]:
    """Get all active services"""
    return load_services()


def update_service_pdf_order(service_id: int, pdf_order: int) -> bool:
    """Update PDF order for a specific service"""
    try:
        init_services_table()  # Ensure table and columns exist
        conn = get_db_connection()
        if not conn:
            st.error("Keine Datenbankverbindung möglich")
            return False

        cursor = conn.cursor()

        # Check if pdf_order column exists
        cursor.execute("PRAGMA table_info(services)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'pdf_order' in columns:
            cursor.execute('''
                UPDATE services
                SET pdf_order = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (pdf_order, service_id))

            conn.commit()
            conn.close()
            return True
        st.warning("PDF-Reihenfolge Spalte existiert nicht in der Datenbank")
        conn.close()
        return False
    except Exception as e:
        st.error(f"Fehler beim Aktualisieren der PDF-Reihenfolge: {str(e)}")
        return False


def render_pdf_order_management():
    """Render PDF order management interface"""
    st.subheader("📄 PDF-Reihenfolge verwalten")

    st.info("""
    Hier können Sie die Reihenfolge der Dienstleistungen in der PDF-Ausgabe individuell bestimmen.
    - **Niedrigere Zahlen** erscheinen **früher** in der PDF
    - **Höhere Zahlen** erscheinen **später** in der PDF
    - Services mit gleicher Reihenfolge werden alphabetisch sortiert
    """)

    services = load_services()

    if not services:
        st.info("Keine Dienstleistungen vorhanden. Fügen Sie zuerst Services hinzu.")
        return

    # Sort by current PDF order for display
    services_sorted = sorted(
        services, key=lambda x: (
            x['pdf_order'], x['name']))

    st.markdown("### Aktuelle PDF-Reihenfolge")

    # Show current order with drag-and-drop style interface
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("**Reihenfolge**")
    with col2:
        st.markdown("**Service**")

    st.markdown("---")

    # Create form for bulk update
    with st.form("pdf_order_form"):
        updated_orders = {}

        for i, service in enumerate(services_sorted):
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                new_order = st.number_input(
                    f"order_{service['id']}",
                    value=service['pdf_order'],
                    min_value=0,
                    step=1,
                    key=f"pdf_order_{service['id']}",
                    label_visibility="collapsed"
                )
                updated_orders[service['id']] = new_order

            with col2:
                status_icon = "⭐" if service['is_standard'] else "🔧"
                st.write(f"{status_icon} **{service['name']}**")
                if service['description']:
                    st.caption(service['description'])
                st.caption(
                    f"Kategorie: {
                        service['category'] or 'Keine'} | {
                        service['price']:.2f} € pro {
                        service['calculate_per']}")

            with col3:
                if service['is_standard']:
                    st.success("Standard")
                else:
                    st.info("Optional")

        # Bulk update button
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.form_submit_button(
                "💾 Reihenfolge speichern",
                    type="primary"):
                success_count = 0
                error_count = 0

                for service_id, new_order in updated_orders.items():
                    if update_service_pdf_order(service_id, new_order):
                        success_count += 1
                    else:
                        error_count += 1

                if success_count > 0:
                    st.success(f"✅ {success_count} Services aktualisiert!")
                    if error_count == 0:
                        st.rerun()

                if error_count > 0:
                    st.error(
                        f"❌ {error_count} Services konnten nicht aktualisiert werden.")

        with col2:
            if st.form_submit_button("🔄 Automatisch sortieren"):
                # Auto-assign orders based on current position
                for i, service in enumerate(services_sorted):
                    update_service_pdf_order(
                        service['id'], i * 10)  # Use increments of 10

                st.success("✅ Automatische Sortierung angewendet!")
                st.rerun()

        with col3:
            if st.form_submit_button("↩️ Zurücksetzen"):
                # Reset all to 0
                for service in services:
                    update_service_pdf_order(service['id'], 0)

                st.success("✅ Alle Reihenfolgen zurückgesetzt!")
                st.rerun()

    # Preview section
    st.markdown("---")
    st.markdown("### 👀 PDF-Vorschau der Reihenfolge")

    # Show how it would appear in PDF
    services_pdf_order = sorted(
        services, key=lambda x: (
            x['pdf_order'], x['name']))

    st.markdown("**So würden die Services in der PDF erscheinen:**")

    for i, service in enumerate(services_pdf_order, 1):
        status_icon = "⭐" if service['is_standard'] else "🔧"
        col1, col2 = st.columns([1, 4])

        with col1:
            st.write(f"**{i}.**")

        with col2:
            st.write(
                f"{status_icon} {
                    service['name']} - {
                    service['price']:.2f} € pro {
                    service['calculate_per']}")
            if service['description']:
                st.caption(f"   {service['description']}")

    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Schnellaktionen")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📈 Standard-Services nach oben"):
            # Move standard services to top
            standard_services = [s for s in services if s['is_standard']]
            optional_services = [s for s in services if not s['is_standard']]

            # Assign orders
            for i, service in enumerate(standard_services):
                update_service_pdf_order(service['id'], i * 10)

            for i, service in enumerate(optional_services):
                update_service_pdf_order(
                    service['id'], (len(standard_services) + i) * 10)

            st.success("✅ Standard-Services nach oben verschoben!")
            st.rerun()

    with col2:
        if st.button("📂 Nach Kategorie sortieren"):
            # Sort by category, then by name
            services_by_category = sorted(
                services, key=lambda x: (
                    x['category'] or 'ZZZ', x['name']))

            for i, service in enumerate(services_by_category):
                update_service_pdf_order(service['id'], i * 10)

            st.success("✅ Nach Kategorie sortiert!")
            st.rerun()

    with col3:
        if st.button("💰 Nach Preis sortieren"):
            # Sort by price (ascending)
            services_by_price = sorted(services, key=lambda x: x['price'])

            for i, service in enumerate(services_by_price):
                update_service_pdf_order(service['id'], i * 10)

            st.success("✅ Nach Preis sortiert!")
            st.rerun()
