# advanced_charts.py
"""
Erweiterte Chart-Funktionen für fehlende Visualisierungen
Implementiert Feature 6 und 7
"""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

# ============================================================================
# FEATURE 6: Break-Even Detailed Chart - Detaillierter Break-Even
# ============================================================================


def create_break_even_detailed_chart(
    analysis_results: dict[str, Any],
    texts: dict[str, str]
) -> go.Figure:
    """
    Erstellt ein detailliertes Break-Even Chart mit mehreren Szenarien.

    Zeigt:
    - Kumulativer Cashflow über Zeit
    - Break-Even Punkt (wo Kurve die 0-Linie kreuzt)
    - Verschiedene Szenarien (Best/Worst/Realistic Case)
    - Investitionspunkt
    - ROI-Entwicklung

    Args:
        analysis_results: Analyseergebnisse
        texts: Sprachdateien

    Returns:
        Plotly Figure
    """
    try:
        # Daten extrahieren
        total_investment = analysis_results.get('total_investment', 0)
        annual_benefit = analysis_results.get(
            'annual_savings_after_pv', 0) + analysis_results.get('annual_feed_in_revenue', 0)

        # Jahre simulieren (0-25)
        years = list(range(26))

        # Szenarien
        scenarios = {}

        # 1. Realistic Case (Standard)
        realistic = [-total_investment]
        cumulative = -total_investment
        for year in range(1, 26):
            # Degradation: -0.5% pro Jahr
            degradation_factor = (1 - 0.005) ** year
            yearly_benefit = annual_benefit * degradation_factor
            cumulative += yearly_benefit
            realistic.append(cumulative)
        scenarios['Realistisch'] = realistic

        # 2. Optimistic Case (Best)
        optimistic = [-total_investment]
        cumulative = -total_investment
        for year in range(1, 26):
            # Degradation: -0.3% pro Jahr (besser)
            # Strompreis-Steigerung: +3% pro Jahr
            degradation_factor = (1 - 0.003) ** year
            price_increase_factor = (1 + 0.03) ** year
            yearly_benefit = annual_benefit * degradation_factor * price_increase_factor
            cumulative += yearly_benefit
            optimistic.append(cumulative)
        scenarios['Optimistisch'] = optimistic

        # 3. Pessimistic Case (Worst)
        pessimistic = [-total_investment]
        cumulative = -total_investment
        for year in range(1, 26):
            # Degradation: -0.7% pro Jahr (schlechter)
            # Strompreis-Steigerung: +1% pro Jahr (geringer)
            # Zusätzliche Kosten: 200€/Jahr
            degradation_factor = (1 - 0.007) ** year
            price_increase_factor = (1 + 0.01) ** year
            yearly_benefit = annual_benefit * degradation_factor * price_increase_factor - 200
            cumulative += yearly_benefit
            pessimistic.append(cumulative)
        scenarios['Pessimistisch'] = pessimistic

        # Break-Even Punkte finden
        break_even_points = {}
        for scenario_name, values in scenarios.items():
            for i, value in enumerate(values):
                if value >= 0:
                    break_even_points[scenario_name] = i
                    break

        # Chart erstellen
        fig = go.Figure()

        # Null-Linie
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        # Szenarien plotten
        colors = {
            'Realistisch': '#1F4B99',  # Blau
            'Optimistisch': '#22C55E',  # Grün
            'Pessimistisch': '#EF4444'  # Rot
        }

        for scenario_name, values in scenarios.items():
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=values,
                    name=scenario_name,
                    mode='lines+markers',
                    line=dict(
                        width=3,
                        color=colors.get(
                            scenario_name,
                            '#1F4B99')),
                    marker=dict(
                        size=6),
                    hovertemplate=f'{scenario_name}<br>Jahr %{x} <br>Cashflow: %{
                        y:,.0f}  €<extra></extra>'))

            # Break-Even Marker
            if scenario_name in break_even_points:
                be_year = break_even_points[scenario_name]
                be_value = values[be_year]
                fig.add_trace(
                    go.Scatter(
                        x=[be_year],
                        y=[be_value],
                        name=f'Break-Even ({scenario_name})',
                        mode='markers+text',
                        marker=dict(
                            size=15,
                            color=colors.get(scenario_name),
                            symbol='star'),
                        text=[
                            f'Jahr {be_year}'],
                        textposition='top center',
                        showlegend=False,
                        hovertemplate=f'{scenario_name} Break-Even<br>Jahr: {be_year}<extra></extra>'))

        # Investitionspunkt markieren
        fig.add_trace(go.Scatter(
            x=[0],
            y=[-total_investment],
            name='Investition',
            mode='markers+text',
            marker=dict(size=12, color='black', symbol='diamond'),
            text=[f'-{total_investment:,.0f} €'],
            textposition='bottom center',
            showlegend=False
        ))

        # Layout
        fig.update_layout(
            title='Detaillierte Break-Even Analyse',
            xaxis_title='Jahre',
            yaxis_title='Kumulativer Cashflow (€)',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )

        # Y-Achse formatieren
        fig.update_yaxes(tickformat=",.0f", ticksuffix=" €")

        return fig

    except Exception as e:
        # Fehler-Chart
        fig = go.Figure()
        fig.add_annotation(
            text=f"Fehler beim Erstellen des Charts: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig


# ============================================================================
# FEATURE 7: Lifecycle Cost Chart - Lebenszykluskosten
# ============================================================================

def create_lifecycle_cost_chart(
    analysis_results: dict[str, Any],
    project_data: dict[str, Any],
    texts: dict[str, str]
) -> go.Figure:
    """
    Erstellt ein Lebenszykluskosten-Chart (Total Cost of Ownership).

    Zeigt:
    - Anschaffungskosten
    - Betriebskosten (Wartung, Versicherung)
    - Reparatur-/Ersatzkosten (Wechselrichter, Batterie)
    - Einsparungen
    - Netto-TCO über Lebenszyklus

    Args:
        analysis_results: Analyseergebnisse
        project_data: Projektdaten
        texts: Sprachdateien

    Returns:
        Plotly Figure (Waterfall Chart)
    """
    try:
        # Basis-Daten
        total_investment = analysis_results.get('total_investment', 0)
        annual_benefit = analysis_results.get(
            'annual_savings_after_pv', 0) + analysis_results.get('annual_feed_in_revenue', 0)
        has_battery = analysis_results.get('has_battery_storage', False)
        pv_power_kw = project_data.get('pv_power_kw', 10)

        # Lebenszyklus: 25 Jahre
        lifetime_years = 25

        # 1. Anschaffungskosten (Jahr 0)
        initial_cost = total_investment

        # 2. Betriebskosten (jährlich)
        # Wartung: ~1% der Investition pro Jahr
        # Versicherung: ~0.5% pro Jahr
        annual_maintenance = total_investment * 0.01
        annual_insurance = total_investment * 0.005
        annual_operating = annual_maintenance + annual_insurance
        total_operating_25y = annual_operating * lifetime_years

        # 3. Wechselrichter-Austausch (nach 12-15 Jahren)
        inverter_replacement_year = 12
        inverter_cost = pv_power_kw * 200  # ca. 200€/kW

        # 4. Batterie-Austausch (nach 10-15 Jahren, falls vorhanden)
        if has_battery:
            battery_capacity = analysis_results.get('battery_capacity_kwh', 10)
            battery_replacement_year = 12
            # ca. 600€/kWh (günstiger als Neupreis)
            battery_cost = battery_capacity * 600
        else:
            battery_cost = 0

        # 5. Reinigung (alle 2-3 Jahre)
        cleaning_frequency = 3  # Jahre
        cleaning_cost_per_time = 200
        cleaning_count = lifetime_years // cleaning_frequency
        total_cleaning = cleaning_count * cleaning_cost_per_time

        # 6. Gesamte Kosten
        total_costs = initial_cost + total_operating_25y + \
            inverter_cost + battery_cost + total_cleaning

        # 7. Einsparungen über 25 Jahre
        # Mit Degradation
        total_savings = 0
        for year in range(1, lifetime_years + 1):
            degradation_factor = (1 - 0.005) ** year
            yearly_benefit = annual_benefit * degradation_factor
            total_savings += yearly_benefit

        # 8. Netto-TCO
        net_tco = total_costs - total_savings

        # Waterfall Chart erstellen
        measures = [
            "Anschaffung",
            "Betrieb (25J)",
            "Wechselrichter",
        ]
        values = [
            initial_cost,
            total_operating_25y,
            inverter_cost,
        ]

        if has_battery:
            measures.append("Batterie")
            values.append(battery_cost)

        measures.extend([
            "Reinigung",
            "Einsparungen",
            "Netto-TCO"
        ])
        values.extend([
            total_cleaning,
            -total_savings,  # Negativ = Einnahmen
            net_tco
        ])

        # Measure-Typen
        measure_types = ["relative"] * (len(measures) - 1) + ["total"]

        # Farben
        colors = []
        for i, val in enumerate(values):
            if i == len(values) - 1:  # Letzter Wert (Total)
                colors.append("#1F4B99" if val < 0 else "#EF4444")
            elif val < 0:  # Einsparungen
                colors.append("#22C55E")
            else:  # Kosten
                colors.append("#EF4444")

        fig = go.Figure(go.Waterfall(
            name="Lebenszykluskosten",
            orientation="v",
            measure=measure_types,
            x=measures,
            textposition="outside",
            text=[f"{v:,.0f} €" for v in values],
            y=values,
            connector={"line": {"color": "gray", "dash": "dot"}},
            decreasing={"marker": {"color": "#22C55E"}},
            increasing={"marker": {"color": "#EF4444"}},
            totals={"marker": {"color": "#1F4B99"}}
        ))

        # Layout
        fig.update_layout(
            title=f"Total Cost of Ownership (TCO) - {lifetime_years} Jahre",
            xaxis_title="Kostenart",
            yaxis_title="Betrag (€)",
            showlegend=False,
            height=600
        )

        # Y-Achse formatieren
        fig.update_yaxes(tickformat=",.0f", ticksuffix=" €")

        # Annotations für Details
        fig.add_annotation(
            text=f"Netto-TCO: {net_tco:,.0f} €<br>ROI: {((total_savings - total_costs) / total_costs * 100):,.1f}%",
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.98,
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="gray",
            borderwidth=1,
            align="left"
        )

        return fig

    except Exception as e:
        # Fehler-Chart
        fig = go.Figure()
        fig.add_annotation(
            text=f"Fehler beim Erstellen des Charts: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def _export_plotly_fig_to_bytes(
        fig: go.Figure, texts: dict[str, str]) -> bytes:
    """
    Exportiert Plotly Figure zu Bytes für PDF-Export.

    Args:
        fig: Plotly Figure
        texts: Sprachdateien

    Returns:
        PNG Bytes
    """
    try:
        img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
        return img_bytes
    except Exception as e:
        print(f"Fehler beim Export: {e}")
        return b""


def create_all_advanced_charts(
    analysis_results: dict[str, Any],
    project_data: dict[str, Any],
    texts: dict[str, str]
) -> dict[str, Any]:
    """
    Erstellt alle erweiterten Charts und exportiert sie.

    Args:
        analysis_results: Analyseergebnisse
        project_data: Projektdaten
        texts: Sprachdateien

    Returns:
        Dict mit Chart-Bytes für PDF-Export
    """
    charts = {}

    # Break-Even Detailed
    try:
        fig_breakeven = create_break_even_detailed_chart(
            analysis_results, texts)
        charts['break_even_detailed_chart_bytes'] = _export_plotly_fig_to_bytes(
            fig_breakeven, texts)
    except Exception as e:
        print(f"Fehler bei Break-Even Chart: {e}")

    # Lifecycle Cost
    try:
        fig_lifecycle = create_lifecycle_cost_chart(
            analysis_results, project_data, texts)
        charts['lifecycle_cost_chart_bytes'] = _export_plotly_fig_to_bytes(
            fig_lifecycle, texts)
    except Exception as e:
        print(f"Fehler bei Lifecycle Chart: {e}")

    return charts
