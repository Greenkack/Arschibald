"""
CRM Reporting Engine

Dieses Modul implementiert ein umfassendes Reporting-System für das CRM mit:
- Vordefinierten Reports (Verkaufsübersicht, Conversion-Funnel, Lead-Quellen)
- Report-Builder mit Filtern und Gruppierungen
- Zeitraum-Auswahl (täglich, wöchentlich, monatlich)
- Visualisierungen mit Plotly
- Export-Funktionen (Excel, PDF, CSV)
- Report-Vorlagen-Speicherung

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import io
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ReportingEngine:
    """Hauptklasse für das CRM Reporting-System."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialisiert die Reporting Engine.
        
        Args:
            conn: SQLite Datenbankverbindung
        """
        self.conn = conn
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Erstellt die saved_reports Tabelle falls sie nicht existiert."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                report_type TEXT NOT NULL,
                config TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                last_used TIMESTAMP
            )
        """)
        self.conn.commit()
    
    # ==================== Vordefinierte Reports ====================
    
    def get_sales_overview(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Generiert eine Verkaufsübersicht.
        
        Args:
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
            period: Zeitraum-Gruppierung ('daily', 'weekly', 'monthly')
        
        Returns:
            Dictionary mit Report-Daten und Visualisierungen
        """
        # Standardzeitraum: letzte 12 Monate
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        
        # Verkaufsdaten aus Projekten mit Angebotsstatus
        query = """
            SELECT 
                p.id,
                p.project_name,
                p.offer_status,
                p.offer_sent_date,
                p.offer_accepted_date,
                p.offer_value,
                c.first_name || ' ' || c.last_name as customer_name,
                c.company_name
            FROM projects p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE p.offer_sent_date BETWEEN ? AND ?
            ORDER BY p.offer_sent_date
        """
        
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "message": "Keine Daten für den gewählten Zeitraum vorhanden",
                "data": pd.DataFrame(),
                "summary": {}
            }
        
        # DataFrame erstellen
        df = pd.DataFrame(rows, columns=[
            'id', 'project_name', 'offer_status', 'offer_sent_date',
            'offer_accepted_date', 'offer_value', 'customer_name', 'company_name'
        ])
        
        # Datums-Konvertierung
        df['offer_sent_date'] = pd.to_datetime(df['offer_sent_date'])
        df['offer_accepted_date'] = pd.to_datetime(df['offer_accepted_date'])
        
        # Zeitraum-Gruppierung
        if period == "daily":
            df['period'] = df['offer_sent_date'].dt.strftime('%Y-%m-%d')
        elif period == "weekly":
            df['period'] = df['offer_sent_date'].dt.to_period('W').astype(str)
        else:  # monthly
            df['period'] = df['offer_sent_date'].dt.strftime('%Y-%m')
        
        # Zusammenfassung
        summary = {
            "total_offers": len(df),
            "total_value": df['offer_value'].sum() if 'offer_value' in df.columns else 0,
            "accepted_offers": len(df[df['offer_status'] == 'accepted']),
            "rejected_offers": len(df[df['offer_status'] == 'rejected']),
            "pending_offers": len(df[df['offer_status'].isin(['sent', 'draft'])]),
            "conversion_rate": 0.0
        }
        
        if summary['total_offers'] > 0:
            summary['conversion_rate'] = (summary['accepted_offers'] / summary['total_offers']) * 100
        
        # Visualisierung erstellen
        fig = self._create_sales_overview_chart(df, period)
        
        return {
            "success": True,
            "data": df,
            "summary": summary,
            "chart": fig,
            "period": period,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_conversion_funnel(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert einen Conversion-Funnel Report.
        
        Args:
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
        
        Returns:
            Dictionary mit Funnel-Daten und Visualisierung
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        
        # Lead-Daten aus Pipeline
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM crm_leads
            WHERE created_at BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        
        lead_data = cursor.fetchall()
        
        # Funnel-Stufen definieren
        funnel_stages = {
            "lead": 0,
            "qualified": 0,
            "proposal": 0,
            "negotiation": 0,
            "won": 0,
            "lost": 0
        }
        
        for status, count in lead_data:
            if status in funnel_stages:
                funnel_stages[status] = count
        
        # Conversion-Raten berechnen
        total_leads = funnel_stages["lead"] + funnel_stages["qualified"] + \
                     funnel_stages["proposal"] + funnel_stages["negotiation"] + \
                     funnel_stages["won"]
        
        conversion_rates = {}
        if total_leads > 0:
            conversion_rates = {
                "lead_to_qualified": (funnel_stages["qualified"] / total_leads * 100) if total_leads > 0 else 0,
                "qualified_to_proposal": (funnel_stages["proposal"] / funnel_stages["qualified"] * 100) if funnel_stages["qualified"] > 0 else 0,
                "proposal_to_won": (funnel_stages["won"] / funnel_stages["proposal"] * 100) if funnel_stages["proposal"] > 0 else 0,
                "overall_conversion": (funnel_stages["won"] / total_leads * 100) if total_leads > 0 else 0
            }
        
        # Visualisierung erstellen
        fig = self._create_funnel_chart(funnel_stages)
        
        return {
            "success": True,
            "funnel_stages": funnel_stages,
            "conversion_rates": conversion_rates,
            "total_leads": total_leads,
            "chart": fig,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_lead_sources_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert einen Lead-Quellen Report.
        
        Args:
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
        
        Returns:
            Dictionary mit Lead-Quellen-Daten und Visualisierung
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        cursor = self.conn.cursor()
        
        # Lead-Quellen analysieren
        cursor.execute("""
            SELECT 
                source,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won_count,
                AVG(CASE WHEN estimated_value IS NOT NULL THEN estimated_value ELSE 0 END) as avg_value
            FROM crm_leads
            WHERE created_at BETWEEN ? AND ?
            GROUP BY source
            ORDER BY count DESC
        """, (start_date, end_date))
        
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "message": "Keine Lead-Quellen-Daten vorhanden",
                "data": pd.DataFrame()
            }
        
        df = pd.DataFrame(rows, columns=['source', 'count', 'won_count', 'avg_value'])
        
        # Conversion-Rate pro Quelle berechnen
        df['conversion_rate'] = (df['won_count'] / df['count'] * 100).round(2)
        
        # Visualisierung erstellen
        fig = self._create_lead_sources_chart(df)
        
        return {
            "success": True,
            "data": df,
            "chart": fig,
            "start_date": start_date,
            "end_date": end_date
        }
    
    # ==================== Report Builder ====================
    
    def build_custom_report(
        self,
        table: str,
        columns: List[str],
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Erstellt einen benutzerdefinierten Report mit flexiblen Filtern und Gruppierungen.
        
        Args:
            table: Tabellen-Name (customers, projects, crm_leads, etc.)
            columns: Liste der Spalten
            filters: Dictionary mit Filter-Bedingungen
            group_by: Liste der Gruppierungs-Spalten
            aggregations: Dictionary mit Aggregations-Funktionen (z.B. {'offer_value': 'SUM'})
            start_date: Startdatum für Zeitfilter
            end_date: Enddatum für Zeitfilter
            order_by: Sortier-Spalte
            limit: Maximale Anzahl Zeilen
        
        Returns:
            Dictionary mit Report-Daten
        """
        try:
            # Query zusammenbauen
            query_parts = []
            params = []
            
            # SELECT Klausel
            if aggregations and group_by:
                select_cols = []
                for col in group_by:
                    select_cols.append(col)
                for col, agg_func in aggregations.items():
                    select_cols.append(f"{agg_func}({col}) as {col}_{agg_func.lower()}")
                query_parts.append(f"SELECT {', '.join(select_cols)}")
            else:
                query_parts.append(f"SELECT {', '.join(columns)}")
            
            # FROM Klausel
            query_parts.append(f"FROM {table}")
            
            # WHERE Klausel
            where_conditions = []
            
            # Zeitfilter
            if start_date and end_date:
                # Versuche verschiedene Datums-Spalten
                date_columns = ['created_at', 'offer_sent_date', 'creation_date']
                for date_col in date_columns:
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute(f"SELECT {date_col} FROM {table} LIMIT 1")
                        where_conditions.append(f"{date_col} BETWEEN ? AND ?")
                        params.extend([start_date, end_date])
                        break
                    except:
                        continue
            
            # Benutzerdefinierte Filter
            if filters:
                for col, value in filters.items():
                    if isinstance(value, list):
                        placeholders = ','.join(['?' for _ in value])
                        where_conditions.append(f"{col} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_conditions.append(f"{col} = ?")
                        params.append(value)
            
            if where_conditions:
                query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
            
            # GROUP BY Klausel
            if group_by:
                query_parts.append(f"GROUP BY {', '.join(group_by)}")
            
            # ORDER BY Klausel
            if order_by:
                query_parts.append(f"ORDER BY {order_by}")
            
            # LIMIT Klausel
            if limit:
                query_parts.append(f"LIMIT {limit}")
            
            query = ' '.join(query_parts)
            
            # Query ausführen
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                return {
                    "success": False,
                    "message": "Keine Daten gefunden",
                    "data": pd.DataFrame(),
                    "query": query
                }
            
            # DataFrame erstellen
            col_names = [description[0] for description in cursor.description]
            df = pd.DataFrame(rows, columns=col_names)
            
            return {
                "success": True,
                "data": df,
                "query": query,
                "row_count": len(df)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Erstellen des Reports: {str(e)}",
                "data": pd.DataFrame()
            }
    
    # ==================== Visualisierungen ====================
    
    def _create_sales_overview_chart(self, df: pd.DataFrame, period: str) -> go.Figure:
        """Erstellt ein Verkaufsübersichts-Diagramm."""
        # Gruppierung nach Zeitraum und Status
        grouped = df.groupby(['period', 'offer_status']).size().reset_index(name='count')
        
        fig = px.bar(
            grouped,
            x='period',
            y='count',
            color='offer_status',
            title=f'Verkaufsübersicht ({period})',
            labels={'period': 'Zeitraum', 'count': 'Anzahl Angebote', 'offer_status': 'Status'},
            color_discrete_map={
                'draft': '#gray',
                'sent': '#FFA500',
                'accepted': '#28a745',
                'rejected': '#dc3545'
            }
        )
        
        fig.update_layout(
            xaxis_title='Zeitraum',
            yaxis_title='Anzahl Angebote',
            legend_title='Status',
            hovermode='x unified'
        )
        
        return fig
    
    def _create_funnel_chart(self, funnel_stages: Dict[str, int]) -> go.Figure:
        """Erstellt ein Funnel-Diagramm."""
        # Nur aktive Stufen (ohne "lost")
        stages = ['lead', 'qualified', 'proposal', 'negotiation', 'won']
        values = [funnel_stages.get(stage, 0) for stage in stages]
        labels = ['Leads', 'Qualifiziert', 'Angebot', 'Verhandlung', 'Gewonnen']
        
        fig = go.Figure(go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=['#007bff', '#17a2b8', '#ffc107', '#fd7e14', '#28a745']
            )
        ))
        
        fig.update_layout(
            title='Conversion Funnel',
            showlegend=False
        )
        
        return fig
    
    def _create_lead_sources_chart(self, df: pd.DataFrame) -> go.Figure:
        """Erstellt ein Lead-Quellen-Diagramm."""
        # Subplot mit zwei Diagrammen
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Lead-Verteilung nach Quelle', 'Conversion-Rate nach Quelle'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}]]
        )
        
        # Pie Chart für Lead-Verteilung
        fig.add_trace(
            go.Pie(
                labels=df['source'],
                values=df['count'],
                name='Leads'
            ),
            row=1, col=1
        )
        
        # Bar Chart für Conversion-Raten
        fig.add_trace(
            go.Bar(
                x=df['source'],
                y=df['conversion_rate'],
                name='Conversion Rate',
                marker_color='#28a745'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='Lead-Quellen Analyse',
            showlegend=False
        )
        
        fig.update_yaxes(title_text='Conversion Rate (%)', row=1, col=2)
        
        return fig
    
    # ==================== Export-Funktionen ====================
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = "report.xlsx") -> bytes:
        """
        Exportiert einen Report als Excel-Datei.
        
        Args:
            df: DataFrame mit Report-Daten
            filename: Dateiname
        
        Returns:
            Bytes des Excel-Files
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
            
            # Formatierung
            worksheet = writer.sheets['Report']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_csv(self, df: pd.DataFrame) -> str:
        """
        Exportiert einen Report als CSV.
        
        Args:
            df: DataFrame mit Report-Daten
        
        Returns:
            CSV-String
        """
        return df.to_csv(index=False)
    
    def export_chart_to_html(self, fig: go.Figure) -> str:
        """
        Exportiert ein Plotly-Diagramm als HTML.
        
        Args:
            fig: Plotly Figure
        
        Returns:
            HTML-String
        """
        return fig.to_html(include_plotlyjs='cdn', full_html=True)
    
    # ==================== Report-Vorlagen ====================
    
    def save_report_template(
        self,
        name: str,
        report_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Speichert eine Report-Vorlage.
        
        Args:
            name: Name der Vorlage
            report_type: Typ des Reports ('sales_overview', 'conversion_funnel', 'custom', etc.)
            config: Konfigurations-Dictionary
            description: Beschreibung der Vorlage
            created_by: Ersteller
        
        Returns:
            Dictionary mit Erfolgs-Status und Template-ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO saved_reports (name, description, report_type, config, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, report_type, json.dumps(config), created_by))
            
            self.conn.commit()
            template_id = cursor.lastrowid
            
            return {
                "success": True,
                "message": f"Report-Vorlage '{name}' erfolgreich gespeichert",
                "template_id": template_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Speichern der Vorlage: {str(e)}"
            }
    
    def load_report_template(self, template_id: int) -> Dict[str, Any]:
        """
        Lädt eine gespeicherte Report-Vorlage.
        
        Args:
            template_id: ID der Vorlage
        
        Returns:
            Dictionary mit Vorlagen-Daten
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, name, description, report_type, config, created_at, created_by
                FROM saved_reports
                WHERE id = ?
            """, (template_id))
            
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "message": "Vorlage nicht gefunden"
                }
            
            # Last used aktualisieren
            cursor.execute("""
                UPDATE saved_reports
                SET last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (template_id))
            self.conn.commit()
            
            return {
                "success": True,
                "template": {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "report_type": row[3],
                    "config": json.loads(row[4]),
                    "created_at": row[5],
                    "created_by": row[6]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Laden der Vorlage: {str(e)}"
            }
    
    def list_report_templates(self) -> List[Dict[str, Any]]:
        """
        Listet alle gespeicherten Report-Vorlagen auf.
        
        Returns:
            Liste von Vorlagen-Dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, name, description, report_type, created_at, created_by, last_used
                FROM saved_reports
                ORDER BY last_used DESC, created_at DESC
            """)
            
            rows = cursor.fetchall()
            
            templates = []
            for row in rows:
                templates.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "report_type": row[3],
                    "created_at": row[4],
                    "created_by": row[5],
                    "last_used": row[6]
                })
            
            return templates
        except Exception as e:
            print(f"Fehler beim Auflisten der Vorlagen: {e}")
            return []
    
    def delete_report_template(self, template_id: int) -> Dict[str, Any]:
        """
        Löscht eine Report-Vorlage.
        
        Args:
            template_id: ID der Vorlage
        
        Returns:
            Dictionary mit Erfolgs-Status
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM saved_reports WHERE id = ?", (template_id))
            self.conn.commit()
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": "Vorlage erfolgreich gelöscht"
                }
            else:
                return {
                    "success": False,
                    "message": "Vorlage nicht gefunden"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Löschen der Vorlage: {str(e)}"
            }


# ==================== Hilfsfunktionen ====================

def get_available_tables(conn: sqlite3.Connection) -> List[str]:
    """
    Gibt eine Liste aller verfügbaren Tabellen zurück.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Tabellennamen
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """
    Gibt eine Liste aller Spalten einer Tabelle zurück.
    
    Args:
        conn: Datenbankverbindung
        table: Tabellenname
    
    Returns:
        Liste von Spaltennamen
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def format_currency(value: float) -> str:
    """Formatiert einen Wert als Währung."""
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float) -> str:
    """Formatiert einen Wert als Prozentsatz."""
    return f"{value:.1f}%".replace(".", ",")
