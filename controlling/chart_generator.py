"""
Controlling System Chart Generator

Provides chart generation with shadcn/ui styling for the Employee Controlling
System.

Requirements: 12.1, 12.2, 12.3
"""

import logging
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ChartGenerator:
    """
    Chart generator for creating visualizations with shadcn/ui styling.

    Requirements: 12.1, 12.2, 12.3
    """

    def __init__(self):
        """Initialize the chart generator."""
        self.default_colors = [
            "#3b82f6",  # Blue
            "#10b981",  # Green
            "#f59e0b",  # Amber
            "#ef4444",  # Red
            "#8b5cf6",  # Purple
            "#ec4899",  # Pink
            "#06b6d4",  # Cyan
            "#f97316",  # Orange
        ]

    def apply_shadcn_theme(self, fig: go.Figure) -> go.Figure:
        """
        Apply shadcn/ui theme styling to a Plotly figure.

        Args:
            fig: Plotly figure to style

        Returns:
            Styled Plotly figure

        Requirements: 12.2
        """
        if fig is None:
            return fig

        try:
            # Base layout with shadcn/ui styling
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title=dict(
                    x=0.02,
                    y=0.98,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=18, color="#1f2937")
                ),
                margin=dict(l=40, r=30, t=60, b=40),
                hovermode="x unified",
                legend=dict(
                    bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12, color="#6b7280")
                ),
                font=dict(family="Inter, sans-serif", color="#374151")
            )

            # Axis styling
            fig.update_xaxes(
                showgrid=True,
                gridcolor="rgba(0,0,0,0.06)",
                zeroline=False,
                linecolor="rgba(0,0,0,0.15)",
                ticks="outside",
                tickcolor="rgba(0,0,0,0.15)",
                ticklen=5,
                tickfont=dict(size=11, color="#6b7280")
            )

            fig.update_yaxes(
                showgrid=True,
                gridcolor="rgba(0,0,0,0.06)",
                zeroline=False,
                linecolor="rgba(0,0,0,0.15)",
                ticks="outside",
                tickcolor="rgba(0,0,0,0.15)",
                ticklen=5,
                tickfont=dict(size=11, color="#6b7280")
            )

            # Style bar charts with rounded appearance
            if hasattr(fig, "data"):
                for trace in fig.data:
                    if getattr(trace, "type", "") == "bar":
                        try:
                            trace.update(
                                marker_line_color="rgba(17,24,39,0.10)",
                                marker_line_width=1.2
                            )
                        except Exception:
                            pass

        except Exception as e:
            logger.warning(f"Error applying shadcn theme: {e}")

        return fig

    def create_bar_chart(
        self,
        data: Dict[str, float],
        title: str,
        x_label: str = "",
        y_label: str = ""
    ) -> go.Figure:
        """
        Create a horizontal bar chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Plotly figure

        Requirements: 12.1
        """
        if not data:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Daten verfügbar",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="#9ca3af")
            )
            return self.apply_shadcn_theme(fig)

        labels = list(data.keys())
        values = list(data.values())

        fig = go.Figure(data=[
            go.Bar(
                y=labels,
                x=values,
                orientation='h',
                marker=dict(
                    color=self.default_colors[0],
                    line=dict(width=0)
                ),
                text=[f"{v:.1f}%" if v < 100 else f"{v:.0f}"
                      for v in values],
                textposition='auto',
                textfont=dict(size=11, color="white"),
                hovertemplate='<b>%{y}</b><br>%{x:.2f}%<extra></extra>'
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=max(300, len(labels) * 40)
        )

        return self.apply_shadcn_theme(fig)

    def create_column_chart(
        self,
        data: Dict[str, float],
        title: str,
        x_label: str = "",
        y_label: str = ""
    ) -> go.Figure:
        """
        Create a vertical column chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Plotly figure

        Requirements: 12.1
        """
        if not data:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Daten verfügbar",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="#9ca3af")
            )
            return self.apply_shadcn_theme(fig)

        labels = list(data.keys())
        values = list(data.values())

        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker=dict(
                    color=self.default_colors[1],
                    line=dict(width=0)
                ),
                text=[f"{v:.1f}%" if v < 100 else f"{v:.0f}"
                      for v in values],
                textposition='outside',
                textfont=dict(size=11, color="#374151"),
                hovertemplate='<b>%{x}</b><br>%{y:.2f}%<extra></extra>'
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=400
        )

        return self.apply_shadcn_theme(fig)

    def create_donut_chart(
        self,
        data: Dict[str, float],
        title: str
    ) -> go.Figure:
        """
        Create a donut chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title

        Returns:
            Plotly figure

        Requirements: 12.1
        """
        if not data:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Daten verfügbar",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="#9ca3af")
            )
            return self.apply_shadcn_theme(fig)

        labels = list(data.keys())
        values = list(data.values())

        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=self.default_colors[:len(labels)],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                textfont=dict(size=11),
                hovertemplate='<b>%{label}</b><br>%{value:.2f}%<br>' +
                              '%{percent}<extra></extra>'
            )
        ])

        fig.update_layout(
            title=title,
            height=400,
            showlegend=True
        )

        return self.apply_shadcn_theme(fig)

    def create_dashboard(
        self,
        report_data: Dict[str, Any]
    ) -> List[go.Figure]:
        """
        Create a complete dashboard with multiple charts from report data.

        Args:
            report_data: Report data dictionary containing quotas and
                         aggregated data

        Returns:
            List of Plotly figures for dashboard display

        Requirements: 12.3
        """
        figures = []

        # Extract data
        quotas = report_data.get("quotas", {})
        ratio_descriptions = report_data.get("ratio_descriptions", {})
        aggregated_data = report_data.get("aggregated_data", {})
        raw_data = aggregated_data.get("raw_data", {})

        # 1. Quotas Bar Chart (Hauptdiagramm)
        if quotas:
            quota_chart = self.create_bar_chart(
                data=quotas,
                title="Leistungsquoten Übersicht",
                x_label="Prozent (%)",
                y_label="Quote"
            )
            figures.append(quota_chart)

        # 2. Quotas Distribution Donut Chart (nur non-zero Werte)
        if quotas:
            # Filter out zero values for donut chart
            non_zero_quotas = {k: v for k, v in quotas.items() if v > 0}
            if non_zero_quotas:
                donut_chart = self.create_donut_chart(
                    data=non_zero_quotas,
                    title="Quoten Verteilung"
                )
                figures.append(donut_chart)

        # 3. Raw Performance Data (alle Kriterien, nicht nur Top 10)
        if raw_data:
            raw_data_chart = self.create_column_chart(
                data=raw_data,
                title="Leistungskriterien Übersicht",
                x_label="Kriterium",
                y_label="Anzahl"
            )
            figures.append(raw_data_chart)

        # If no figures were created, add a placeholder
        if not figures:
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Daten für Dashboard verfügbar",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#9ca3af")
            )
            figures.append(self.apply_shadcn_theme(fig))

        return figures

    def create_comparison_charts(
        self,
        comparison_report: Dict[str, Any]
    ) -> List[go.Figure]:
        """
        Create comparison charts for team reports with multiple employees.

        Args:
            comparison_report: Team comparison report data with multiple employees

        Returns:
            List of Plotly figures for comparison display

        Requirements: 12.3
        """
        figures = []

        employees = comparison_report.get("employees", [])
        
        if not employees:
            fig = go.Figure()
            fig.add_annotation(
                text="Keine Mitarbeiterdaten für Vergleich verfügbar",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="#9ca3af")
            )
            figures.append(self.apply_shadcn_theme(fig))
            return figures

        # Extract employee names and quota data
        employee_names = [emp.get("full_name", "Unbekannt") for emp in employees]
        
        # 1. Abschlussquote Vergleich
        abschlussquote_data = {}
        for emp in employees:
            quotas = emp.get("quotas", {})
            abschlussquote = quotas.get("Abschlussquote", 0)
            abschlussquote_data[emp.get("full_name", "Unbekannt")] = abschlussquote
        
        if abschlussquote_data:
            fig = self.create_column_chart(
                data=abschlussquote_data,
                title="Abschlussquote Vergleich",
                x_label="Mitarbeiter",
                y_label="Quote (%)"
            )
            figures.append(fig)
        
        # 2. Top 3 Quotas Comparison (grouped bar chart)
        top_quota_names = ["Abschlussquote", "Terminvereinbarungsquote", "Termine-Anfahrquote"]
        
        fig = go.Figure()
        
        for quota_name in top_quota_names:
            quota_values = []
            for emp in employees:
                quotas = emp.get("quotas", {})
                quota_values.append(quotas.get(quota_name, 0))
            
            fig.add_trace(go.Bar(
                name=quota_name,
                x=employee_names,
                y=quota_values,
                text=[f"{v:.1f}%" for v in quota_values],
                textposition='auto',
                textfont=dict(size=10, color="white"),
                hovertemplate=f'<b>{quota_name}</b><br>%{{x}}<br>%{{y:.2f}}%<extra></extra>'
            ))
        
        fig.update_layout(
            title="Top 3 Quotas im Vergleich",
            xaxis_title="Mitarbeiter",
            yaxis_title="Quote (%)",
            barmode='group',
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        figures.append(self.apply_shadcn_theme(fig))
        
        # 3. Rohdaten Vergleich (Kontakte, Termine, Abschlüsse)
        raw_data_labels = ["Kontakte", "Termine", "Abschlüsse"]
        
        fig = go.Figure()
        
        for label in raw_data_labels:
            values = []
            for emp in employees:
                raw_data = emp.get("aggregated_data", {}).get("raw_data", {})
                values.append(raw_data.get(label, 0))
            
            fig.add_trace(go.Bar(
                name=label,
                x=employee_names,
                y=values,
                text=[f"{int(v)}" for v in values],
                textposition='auto',
                textfont=dict(size=10, color="white"),
                hovertemplate=f'<b>{label}</b><br>%{{x}}<br>%{{y}}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Aktivitäten im Vergleich",
            xaxis_title="Mitarbeiter",
            yaxis_title="Anzahl",
            barmode='group',
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        figures.append(self.apply_shadcn_theme(fig))
        
        # 4. Durchschnittliche Performance (Radar Chart alternative: Multi-line)
        # Alle Quotas im Vergleich als Liniendiagramm
        all_quota_names = set()
        for emp in employees:
            all_quota_names.update(emp.get("quotas", {}).keys())
        
        all_quota_names = sorted(list(all_quota_names))[:8]  # Max 8 quotas
        
        if all_quota_names:
            fig = go.Figure()
            
            for emp in employees:
                quotas = emp.get("quotas", {})
                quota_values = [quotas.get(qn, 0) for qn in all_quota_names]
                
                fig.add_trace(go.Scatter(
                    x=all_quota_names,
                    y=quota_values,
                    mode='lines+markers',
                    name=emp.get("full_name", "Unbekannt"),
                    line=dict(width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}%<extra></extra>'
                ))
            
            fig.update_layout(
                title="Alle Quotas im Vergleich",
                xaxis_title="Quote",
                yaxis_title="Prozent (%)",
                height=500,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                xaxis=dict(tickangle=45)
            )
            
            figures.append(self.apply_shadcn_theme(fig))

        return figures
