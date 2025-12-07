# crm/features/dashboard_widgets.py
"""
Dashboard Widget System
Konfigurierbares Widget-System für das CRM Dashboard

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import json
from datetime import datetime, timedelta
from typing import Any

import plotly.graph_objects as go
import streamlit as st

try:
    from database import get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class DashboardWidget:
    """Basis-Klasse für Dashboard Widgets"""

    def __init__(
            self,
            widget_id: str,
            title: str,
            icon: str = "",
            default_visible: bool = True):
        self.widget_id = widget_id
        self.title = title
        self.icon = icon
        self.default_visible = default_visible

    def render(self, **kwargs):
        """Rendert das Widget - muss von Subklassen implementiert werden"""
        raise NotImplementedError("Subklassen müssen render() implementieren")

    def get_data(self):
        """Holt die Daten für das Widget - kann überschrieben werden"""
        return {}


class OpenTasksWidget(DashboardWidget):
    """Widget für offene Aufgaben"""

    def __init__(self):
        super().__init__(
            widget_id="open_tasks",
            title="Offene Aufgaben",
            icon=""
        )

    def get_data(self):
        """Holt offene Aufgaben aus der Datenbank"""
        if not DATABASE_AVAILABLE:
            return []

        conn = get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, priority, due_date, customer_id
                FROM crm_tasks
                WHERE status != 'completed'
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    due_date ASC
                LIMIT 10
            """)
            tasks = cursor.fetchall()
            conn.close()

            result = []
            for task in tasks:
                result.append({
                    'id': task[0],
                    'title': task[1],
                    'priority': task[2] or 'medium',
                    'due_date': task[3],
                    'customer_id': task[4]
                })
            return result
        except Exception as e:
            print(f"Fehler beim Laden der Aufgaben: {e}")
            conn.close()
            return []

    def render(self, **kwargs):
        """Rendert das Aufgaben-Widget"""
        tasks = self.get_data()

        if not tasks:
            st.info("Keine offenen Aufgaben")
            return

        # Zähle überfällige Aufgaben
        today = datetime.now().date()
        overdue_count = 0
        for task in tasks:
            if task['due_date']:
                try:
                    due_date = datetime.strptime(
                        task['due_date'], '%Y-%m-%d').date()
                    if due_date < today:
                        overdue_count += 1
                except ValueError:
                    pass

        # Header mit Statistik
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {self.icon} {self.title}")
        with col2:
            if overdue_count > 0:
                st.markdown(
                    f"<span style='color: red; font-weight: bold;'>"
                    f"{overdue_count} überfällig</span>",
                    unsafe_allow_html=True
                )

        # Aufgaben anzeigen
        for task in tasks[:5]:  # Zeige nur die ersten 5
            priority_color = {
                'high': '#ff4444',
                'medium': '#ffaa00',
                'low': '#44ff44'
            }.get(task['priority'], '#808080')

            priority_icon = {
                'high': '',
                'medium': '🟡',
                'low': '🟢'
            }.get(task['priority'], '')

            # Prüfe ob überfällig
            is_overdue = False
            due_text = "Kein Fälligkeitsdatum"
            if task['due_date']:
                try:
                    due_date = datetime.strptime(
                        task['due_date'], '%Y-%m-%d').date()
                    if due_date < today:
                        is_overdue = True
                        due_text = f"Überfällig seit {
                            (today - due_date).days} Tagen"
                    elif due_date == today:
                        due_text = " Heute fällig"
                    else:
                        days_until = (due_date - today).days
                        due_text = f" Fällig in {days_until} Tagen"
                except ValueError:
                    pass

            bg_color = '#ffcccc' if is_overdue else '#f0f0f0'

            st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border-left: 4px solid {priority_color};
                ">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>{priority_icon} {task['title']}</strong><br>
                            <small style="color: #666;">{due_text}</small>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


class UpcomingAppointmentsWidget(DashboardWidget):
    """Widget für anstehende Termine"""

    def __init__(self):
        super().__init__(
            widget_id="upcoming_appointments",
            title="Anstehende Termine",
            icon=""
        )

    def get_data(self):
        """Holt anstehende Termine aus der Datenbank"""
        if not DATABASE_AVAILABLE:
            return []

        conn = get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            # Hole Termine der nächsten 7 Tage
            today = datetime.now().date()
            next_week = today + timedelta(days=7)

            cursor.execute("""
                SELECT id, title, appointment_date, appointment_time,
                       customer_id, location
                FROM crm_appointments
                WHERE appointment_date >= ? AND appointment_date <= ?
                ORDER BY appointment_date ASC, appointment_time ASC
                LIMIT 10
            """, (today.isoformat(), next_week.isoformat()))

            appointments = cursor.fetchall()
            conn.close()

            result = []
            for apt in appointments:
                result.append({
                    'id': apt[0],
                    'title': apt[1],
                    'date': apt[2],
                    'time': apt[3],
                    'customer_id': apt[4],
                    'location': apt[5]
                })
            return result
        except Exception as e:
            print(f"Fehler beim Laden der Termine: {e}")
            conn.close()
            return []

    def render(self, **kwargs):
        """Rendert das Termin-Widget"""
        appointments = self.get_data()

        if not appointments:
            st.info(" Keine anstehenden Termine in den nächsten 7 Tagen")
            return

        st.markdown(f"### {self.icon} {self.title}")

        today = datetime.now().date()

        for apt in appointments[:5]:  # Zeige nur die ersten 5
            try:
                apt_date = datetime.strptime(apt['date'], '%Y-%m-%d').date()
                is_today = apt_date == today
                is_tomorrow = apt_date == today + timedelta(days=1)

                if is_today:
                    date_text = " Heute"
                    bg_color = '#ffe6e6'
                elif is_tomorrow:
                    date_text = "🟡 Morgen"
                    bg_color = '#fff6e6'
                else:
                    days_until = (apt_date - today).days
                    date_text = f" In {days_until} Tagen"
                    bg_color = '#f0f0f0'

                time_text = apt['time'] if apt['time'] else "Ganztägig"
                location_text = apt['location'] if apt['location'] else ""

                st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        border-left: 4px solid #4CAF50;
                    ">
                        <div>
                            <strong>{apt['title']}</strong><br>
                            <small style="color: #666;">
                                {date_text} • {time_text}
                                {' • ' + location_text if location_text else ''}
                            </small>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            except ValueError:
                pass


class PipelineOverviewWidget(DashboardWidget):
    """Widget für Pipeline-Übersicht"""

    def __init__(self):
        super().__init__(
            widget_id="pipeline_overview",
            title="Pipeline-Übersicht",
            icon=""
        )

    def get_data(self):
        """Holt Pipeline-Daten aus der Datenbank"""
        if not DATABASE_AVAILABLE:
            return {}

        conn = get_db_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count, SUM(estimated_value) as value
                FROM crm_leads
                GROUP BY status
            """)
            results = cursor.fetchall()
            conn.close()

            data = {}
            for row in results:
                data[row[0]] = {
                    'count': row[1],
                    'value': row[2] or 0
                }
            return data
        except Exception as e:
            print(f"Fehler beim Laden der Pipeline-Daten: {e}")
            conn.close()
            return {}

    def render(self, **kwargs):
        """Rendert das Pipeline-Widget"""
        data = self.get_data()

        if not data:
            st.info("Keine Pipeline-Daten verfügbar")
            return

        st.markdown(f"### {self.icon} {self.title}")

        # Status-Mapping
        status_labels = {
            'new': 'Neu',
            'qualified': 'Qualifiziert',
            'proposal': 'Angebot',
            'negotiation': 'Verhandlung',
            'won': 'Gewonnen',
            'lost': 'Verloren'
        }

        status_colors = {
            'new': '#2196F3',
            'qualified': '#4CAF50',
            'proposal': '#FF9800',
            'negotiation': '#9C27B0',
            'won': '#4CAF50',
            'lost': '#F44336'
        }

        # Zeige aktive Stages (nicht won/lost)
        active_stages = ['new', 'qualified', 'proposal', 'negotiation']

        cols = st.columns(len(active_stages))
        for idx, stage in enumerate(active_stages):
            stage_data = data.get(stage, {'count': 0, 'value': 0})
            with cols[idx]:
                color = status_colors.get(stage, '#808080')
                label = status_labels.get(stage, stage)

                st.markdown(f"""
                    <div style="
                        background: linear-gradient(145deg, {color} 0%, {
                    color}cc 100%);
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        color: white;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    ">
                        <h4 style="margin: 0; font-size: 0.9em;">{label}</h4>
                        <h2 style="margin: 5px 0; font-size: 1.8em;">{
                    stage_data['count']}</h2>
                        <p style="margin: 0; font-size: 0.8em; opacity: 0.9;">
                            {stage_data['value']:,.0f} €
                        </p>
                    </div>
                """, unsafe_allow_html=True)


class RevenueTrackingWidget(DashboardWidget):
    """Widget für Umsatz-Tracking"""

    def __init__(self):
        super().__init__(
            widget_id="revenue_tracking",
            title="Umsatz-Tracking",
            icon=""
        )

    def get_data(self):
        """Holt Umsatz-Daten aus der Datenbank"""
        if not DATABASE_AVAILABLE:
            return {}

        conn = get_db_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()

            # Monatsumsatz
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute("""
                SELECT SUM(estimated_value)
                FROM crm_leads
                WHERE status = 'won'
                AND strftime('%Y-%m', created_at) = ?
            """, (current_month,))
            monthly_revenue = cursor.fetchone()[0] or 0

            # Jahresumsatz
            current_year = datetime.now().strftime('%Y')
            cursor.execute("""
                SELECT SUM(estimated_value)
                FROM crm_leads
                WHERE status = 'won'
                AND strftime('%Y', created_at) = ?
            """, (current_year,))
            yearly_revenue = cursor.fetchone()[0] or 0

            # Durchschnittliche Deal-Größe
            cursor.execute("""
                SELECT AVG(estimated_value)
                FROM crm_leads
                WHERE status = 'won'
                AND strftime('%Y', created_at) = ?
            """, (current_year,))
            avg_deal_size = cursor.fetchone()[0] or 0

            # Conversion Rate
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN status = 'won' THEN 1 END) as won,
                    COUNT(*) as total
                FROM crm_leads
                WHERE status IN ('won', 'lost')
                AND strftime('%Y', created_at) = ?
            """, (current_year,))
            result = cursor.fetchone()
            won_count = result[0] or 0
            total_count = result[1] or 1
            conversion_rate = (won_count / total_count * 100) if total_count > 0 else 0

            conn.close()

            return {
                'monthly_revenue': monthly_revenue,
                'yearly_revenue': yearly_revenue,
                'avg_deal_size': avg_deal_size,
                'conversion_rate': conversion_rate
            }
        except Exception as e:
            print(f"Fehler beim Laden der Umsatz-Daten: {e}")
            conn.close()
            return {}

    def render(self, **kwargs):
        """Rendert das Umsatz-Widget"""
        data = self.get_data()

        if not data:
            st.info("Keine Umsatz-Daten verfügbar")
            return

        st.markdown(f"### {self.icon} {self.title}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #4CAF50 0%, #45a049 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin: 0; font-size: 0.8em;">Monatsumsatz</h4>
                    <h2 style="margin: 5px 0; font-size: 1.5em;">{
                data['monthly_revenue']:,.0f} €</h2>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #2196F3 0%, #1976D2 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin: 0; font-size: 0.8em;">Jahresumsatz</h4>
                    <h2 style="margin: 5px 0; font-size: 1.5em;">{
                data['yearly_revenue']:,.0f} €</h2>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #FF9800 0%, #F57C00 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin: 0; font-size: 0.8em;">Ø Deal-Größe</h4>
                    <h2 style="margin: 5px 0; font-size: 1.5em;">{
                data['avg_deal_size']:,.0f} €</h2>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #9C27B0 0%, #7B1FA2 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin: 0; font-size: 0.8em;">Conversion Rate</h4>
                    <h2 style="margin: 5px 0; font-size: 1.5em;">{
                data['conversion_rate']:.1f}%</h2>
                </div>
            """, unsafe_allow_html=True)


class WidgetManager:
    """Verwaltet Dashboard Widgets und deren Konfiguration"""

    def __init__(self):
        self.widgets = {
            'open_tasks': OpenTasksWidget(),
            'upcoming_appointments': UpcomingAppointmentsWidget(),
            'pipeline_overview': PipelineOverviewWidget(),
            'revenue_tracking': RevenueTrackingWidget()
        }

    def get_widget_config(self, user_id: str = "default") -> dict:
        """Lädt Widget-Konfiguration für einen Benutzer"""
        if not DATABASE_AVAILABLE:
            return self._get_default_config()

        conn = get_db_connection()
        if not conn:
            return self._get_default_config()

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT widget_config
                FROM user_dashboard_settings
                WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                return json.loads(result[0])
            return self._get_default_config()
        except Exception as e:
            print(f"Fehler beim Laden der Widget-Konfiguration: {e}")
            return self._get_default_config()
        finally:
            conn.close()

    def save_widget_config(self, user_id: str, config: dict) -> bool:
        """Speichert Widget-Konfiguration für einen Benutzer"""
        if not DATABASE_AVAILABLE:
            return False

        conn = get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_dashboard_settings
                (user_id, widget_config, updated_at)
                VALUES (?, ?, ?)
            """, (user_id, json.dumps(config), datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Widget-Konfiguration: {e}")
            return False
        finally:
            conn.close()

    def _get_default_config(self) -> dict:
        """Gibt Standard-Konfiguration zurück"""
        return {
            'open_tasks': {'visible': True, 'order': 1},
            'upcoming_appointments': {'visible': True, 'order': 2},
            'pipeline_overview': {'visible': True, 'order': 3},
            'revenue_tracking': {'visible': True, 'order': 4}
        }

    def render_widgets(self, user_id: str = "default", **kwargs):
        """Rendert alle sichtbaren Widgets in konfigurierter Reihenfolge"""
        config = self.get_widget_config(user_id)

        # Sortiere Widgets nach Order
        sorted_widgets = sorted(
            config.items(),
            key=lambda x: x[1].get('order', 999)
        )

        for widget_id, widget_config in sorted_widgets:
            if not widget_config.get('visible', True):
                continue

            widget = self.widgets.get(widget_id)
            if widget:
                with st.container():
                    widget.render(**kwargs)
                    st.markdown("---")

    def render_widget_config_ui(self, user_id: str = "default"):
        """Rendert UI zur Widget-Konfiguration"""
        st.subheader(" Widget-Einstellungen")

        config = self.get_widget_config(user_id)

        st.markdown("""
            Passen Sie an, welche Widgets auf Ihrem Dashboard angezeigt werden
            und in welcher Reihenfolge.
        """)

        updated_config = {}

        for widget_id, widget in self.widgets.items():
            widget_config = config.get(widget_id, {
                                       'visible': True, 'order': 999})

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{widget.icon} {widget.title}**")

            with col2:
                visible = st.checkbox(
                    "Sichtbar",
                    value=widget_config.get('visible', True),
                    key=f"visible_{widget_id}"
                )

            with col3:
                order = st.number_input(
                    "Position",
                    min_value=1,
                    max_value=10,
                    value=widget_config.get('order', 1),
                    key=f"order_{widget_id}"
                )

            updated_config[widget_id] = {
                'visible': visible,
                'order': order
            }

        if st.button(" Einstellungen speichern", type="primary"):
            if self.save_widget_config(user_id, updated_config):
                st.success("Einstellungen gespeichert!")
                st.rerun()
            else:
                st.error("Fehler beim Speichern der Einstellungen")


def render_dashboard_with_widgets(
        texts: dict[str, str],
        user_id: str = "default",
        auto_refresh: bool = False,
        refresh_interval: int = 60):
    """
    Rendert Dashboard mit Widget-System

    Args:
        texts: Übersetzungstexte
        user_id: Benutzer-ID für personalisierte Einstellungen
        auto_refresh: Aktiviert automatisches Refresh
        refresh_interval: Refresh-Intervall in Sekunden
    """
    st.header("CRM Dashboard")

    # Auto-Refresh Konfiguration
    if auto_refresh:
        st.markdown(f"""
            <div style="
                background: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                text-align: center;
            ">
                 Auto-Refresh aktiv (alle {refresh_interval} Sekunden)
            </div>
        """, unsafe_allow_html=True)

        # Implementiere Auto-Refresh mit st.rerun()
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()

        time_since_refresh = (
            datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= refresh_interval:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    # Tabs für Dashboard und Einstellungen
    tab1, tab2 = st.tabs(["Dashboard", " Einstellungen"])

    with tab1:
        # Rendere Widgets
        manager = WidgetManager()
        manager.render_widgets(user_id=user_id)

    with tab2:
        # Widget-Konfiguration
        manager = WidgetManager()
        manager.render_widget_config_ui(user_id=user_id)

        st.markdown("---")

        # Auto-Refresh Einstellungen
        st.subheader(" Auto-Refresh Einstellungen")

        col1, col2 = st.columns(2)

        with col1:
            enable_refresh = st.checkbox(
                "Auto-Refresh aktivieren",
                value=auto_refresh,
                key="enable_auto_refresh"
            )

        with col2:
            interval = st.selectbox(
                "Refresh-Intervall",
                options=[30, 60, 120, 300],
                format_func=lambda x: f"{x} Sekunden",
                index=1,
                key="refresh_interval_select"
            )

        if st.button(" Jetzt aktualisieren"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
