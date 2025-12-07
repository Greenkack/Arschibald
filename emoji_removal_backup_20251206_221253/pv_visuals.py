"""
Datei: pv_visuals.py
Zweck: Stellt spezialisierte 2D-Visualisierungsfunktionen für PV-Analysedaten bereit.
       Alle Diagramme wurden von 3D zu 2D konvertiert für bessere Lesbarkeit und PDF-Kompatibilität.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-02
Letzte Änderung: 2025-10-10 - 3D zu 2D Konvertierung abgeschlossen
Version: 2.0 - Verbesserte Diagramm-Darstellung (Task 4.1-4.3)
"""

import math  # <--- KORREKTUR: Fehlender Import hinzugefügt
from typing import Any

import plotly.graph_objects as go
import streamlit as st

# Import der verbesserten Styling-Funktionen (Task 4.1-4.3)
from chart_styling_improvements import (
    FONT_SIZE_DATA_LABEL,
    apply_improved_plotly_style,
    create_improved_plotly_line_chart,
    generate_chart_description,
    save_plotly_chart_to_bytes,
)


# Hilfsfunktion für Texte innerhalb dieses Moduls
def get_text_pv_viz(texts: dict[str, str], key: str,
                    fallback_text: str | None = None) -> str:
    """
    Holt einen Text aus dem übergebenen Dictionary oder gibt einen Fallback-Text zurück.

    Args:
        texts (Dict[str, str]): Das Dictionary mit den Texten.
        key (str): Der Schlüssel für den gewünschten Text.
        fallback_text (Optional[str]): Ein optionaler Text, der zurückgegeben wird, wenn der Schlüssel nicht gefunden wird.
                                       Standardmäßig wird ein generischer Fallback basierend auf dem Schlüssel erzeugt.

    Returns:
        str: Der angeforderte Text oder der Fallback-Text.
    """
    if fallback_text is None:
        fallback_text = key.replace("_", " ").title() + " (PV Viz Text fehlt)"
    return texts.get(key, fallback_text)

# Hilfsfunktion für den Export von Plotly-Figuren


def _export_plotly_fig_to_bytes_pv_viz(
        fig: go.Figure | None, texts: dict[str, str]) -> bytes | None:
    """
    Exportiert eine Plotly-Figur als PNG-Bild-Bytes.

    Args:
        fig (Optional[go.Figure]): Die zu exportierende Plotly-Figur.
        texts (Dict[str,str]): Das Text-Dictionary für Fehlermeldungen.

    Returns:
        Optional[bytes]: Die Bild-Bytes im PNG-Format oder None bei einem Fehler.
    """
    if fig is None:
        return None
    try:
        # Erhöhe die Skalierung und definiere eine Standardgröße für bessere
        # Qualität im PDF
        img_bytes = fig.to_image(format="png", scale=2, width=900, height=550)
        return img_bytes
    except Exception:
        # Fehlerbehandlung wurde aus der Originaldatei übernommen
        # Im Idealfall würde dieser Fehler an eine zentrale Logging-Stelle gemeldet
        # und nicht direkt in die Konsole geschrieben, es sei denn, es ist ein Debug-Modus aktiv.
        # print(f"pv_visuals.py: Fehler beim Exportieren der Plotly Figur: {e}")
        # Eine UI-Warnung in Streamlit ist hier nicht angebracht, da dies eine Backend-Funktion ist.
        # Der Fehler sollte vom aufrufenden Modul (analysis.py) behandelt werden, falls nötig.
        # Für jetzt bleibt der Print-Befehl auskommentiert, um Konsolen-Spam zu vermeiden.
        # Der Nutzer wird den Fehler durch ein fehlendes Bild im PDF bemerken.
        return None


def render_yearly_production_pv_data(
        analysis_results: dict[str, Any], texts: dict[str, str]):
    """
    Rendert ein 2D-Balkendiagramm der monatlichen PV-Produktion für das erste Jahr.
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen,
                                           erwartet `monthly_productions_sim` (Liste von 12 Floats).
                                           Wird modifiziert, um `yearly_production_chart_bytes` hinzuzufügen.
        texts (Dict[str, str]): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(
        get_text_pv_viz(
            texts,
            "viz_yearly_prod_2d_subheader",
            "Jahresproduktion – Monatliche Übersicht"))

    month_labels_str = get_text_pv_viz(
        texts,
        "month_names_short_list",
        "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez")
    month_labels = month_labels_str.split(',')
    if len(month_labels) != 12:  # Fallback
        month_labels = [
            "Jan",
            "Feb",
            "Mrz",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Okt",
            "Nov",
            "Dez"]

    production_data = analysis_results.get('monthly_productions_sim')

    if not production_data or not isinstance(
            production_data, list) or len(production_data) != 12:
        st.warning(
            get_text_pv_viz(
                texts,
                "viz_data_missing_monthly_prod",
                "Monatliche Produktionsdaten für Jahresdiagramm nicht verfügbar oder unvollständig."))
        fig_fallback_yearly = go.Figure()
        fig_fallback_yearly.update_layout(
            title=get_text_pv_viz(
                texts,
                "viz_data_unavailable_title",
                "Daten nicht verfügbar"))
        st.plotly_chart(
            fig_fallback_yearly,
            use_container_width=True,
            key="pv_visuals_yearly_prod_fallback")
        analysis_results['yearly_production_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(
            fig_fallback_yearly, texts)
        return

    # Konvertiere Daten zu Float
    production_values = [float(p_val) if isinstance(p_val, (int, float)) and not (
        math.isnan(p_val) or math.isinf(p_val)) else 0.0 for p_val in production_data]

    # Erstelle 2D-Balkendiagramm mit verbessertem Styling (Task 4.1-4.2)
    colors = [f'hsl({(i / 12 * 300)}, 70%, 60%)' for i in range(12)]

    fig_yearly_prod = go.Figure()

    # Verwende verbesserte Balken-Funktion (Task 4.1)
    fig_yearly_prod.add_trace(go.Bar(
        x=month_labels,
        y=production_values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)  # Task 4.1: Dickere Kanten
        ),
        text=[f'{val:.0f} kWh' for val in production_values],
        textposition='outside',
        textfont=dict(
            size=FONT_SIZE_DATA_LABEL,
            color='black',
            weight='bold'),
        # Task 4.2
        hovertemplate='<b>%{x}</b><br>Produktion: %{y:.0f} kWh<extra></extra>'
    ))

    # Wende verbessertes Styling an (Task 4.1-4.3)
    apply_improved_plotly_style(
        fig_yearly_prod,
        title=get_text_pv_viz(
            texts,
            "viz_yearly_prod_2d_title",
            "Jährliche PV-Produktion nach Monaten"),
        xlabel=get_text_pv_viz(
            texts,
            "viz_month_axis_label",
            "Monat"),
        ylabel=get_text_pv_viz(
            texts,
            "viz_kwh_axis_label",
            "Produktion (kWh)"),
        show_grid=True,
        show_legend=False)
    st.plotly_chart(
        fig_yearly_prod,
        use_container_width=True,
        key="pv_visuals_yearly_prod")

    # Speichere mit verbesserter Auflösung (Task 4.3)
    analysis_results['yearly_production_chart_bytes'] = save_plotly_chart_to_bytes(
        fig_yearly_prod)

    # Generiere Beschreibung (Task 4.4)
    total_production = sum(production_values)
    max_month_idx = production_values.index(max(production_values))
    min_month_idx = production_values.index(min(production_values))

    chart_description = generate_chart_description(
        chart_type="Balkendiagramm",
        data={
            'values': production_values,
            'labels': month_labels},
        purpose="Visualisierung der monatlichen PV-Produktion über ein Jahr",
        key_insights=[
            f"Gesamtproduktion: {
                total_production:,.0f} kWh",
            f"Höchste Produktion im {
                month_labels[max_month_idx]}: {
                production_values[max_month_idx]:,.0f} kWh",
            f"Niedrigste Produktion im {
                month_labels[min_month_idx]}: {
                production_values[min_month_idx]:,.0f} kWh"])
    analysis_results['yearly_production_chart_description'] = chart_description


def render_break_even_pv_data(
        analysis_results: dict[str, Any], texts: dict[str, str]):
    """
    Rendert ein 2D-Liniendiagramm des kumulierten Kapitalflusses, um den Break-Even-Punkt zu visualisieren.
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen,
                                           erwartet `simulation_period_years_effective` (int) und
                                           `cumulative_cash_flows_sim` (Liste von Floats, Länge N+1).
                                           Wird modifiziert, um `break_even_chart_bytes` hinzuzufügen.
        texts (Dict[str, str]): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(
        get_text_pv_viz(
            texts,
            "viz_break_even_2d_subheader",
            "Break-Even Punkt – Kumulierter Kapitalfluss"))
    simulation_years = analysis_results.get(
        'simulation_period_years_effective', 0)
    cashflow_data_raw = analysis_results.get('cumulative_cash_flows_sim')

    if not isinstance(
        simulation_years,
        int) or simulation_years <= 0 or not cashflow_data_raw or not isinstance(
        cashflow_data_raw,
        list) or len(cashflow_data_raw) != (
            simulation_years + 1):
        st.warning(
            get_text_pv_viz(
                texts,
                "viz_data_missing_cashflow",
                "Kumulierte Cashflow-Daten für Break-Even-Diagramm nicht verfügbar oder unvollständig."))
        fig_fallback_break_even = go.Figure()
        fig_fallback_break_even.update_layout(
            title=get_text_pv_viz(
                texts,
                "viz_data_unavailable_title",
                "Daten nicht verfügbar"))
        st.plotly_chart(
            fig_fallback_break_even,
            use_container_width=True,
            key="pv_visuals_break_even_fallback")
        analysis_results['break_even_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(
            fig_fallback_break_even, texts)
        return

    cashflow_data = [float(cf) if isinstance(cf, (int, float)) and not (
        math.isnan(cf) or math.isinf(cf)) else 0.0 for cf in cashflow_data_raw]
    years_axis = list(range(simulation_years + 1))

    # Finde Break-Even Punkt
    break_even_year = None
    for i, cf in enumerate(cashflow_data):
        if cf >= 0:
            break_even_year = i
            break

    fig_break_even = go.Figure()

    # Kumulierter Kapitalfluss mit verbessertem Styling (Task 4.1)
    create_improved_plotly_line_chart(
        fig_break_even,
        x_data=years_axis,
        y_data=cashflow_data,
        name=get_text_pv_viz(
            texts,
            "viz_cashflow_label",
            "Kumulierter Kapitalfluss"),
        color='green',
        show_markers=True)

    # Füge Fill hinzu
    fig_break_even.data[0].fill = 'tozeroy'
    fig_break_even.data[0].fillcolor = 'rgba(0,128,0,0.1)'

    # Break-Even Linie (y=0) mit verbesserter Breite (Task 4.1)
    fig_break_even.add_trace(go.Scatter(
        x=[years_axis[0], years_axis[-1]],
        y=[0, 0],
        mode='lines',
        name='Break-Even Linie',
        line=dict(
            color='red',
            width=2.5,
            dash='dash'),
        # Task 4.1: Dickere Linie
        hoverinfo='skip'
    ))

    # Markiere Break-Even Punkt mit verbesserter Größe (Task 4.1)
    if break_even_year is not None:
        fig_break_even.add_trace(go.Scatter(
            x=[break_even_year],
            y=[0],
            mode='markers+text',
            name='Break-Even',
            marker=dict(
                size=18,
                color='red',
                symbol='star'),
            # Task 4.1: Größerer Marker
            text=[f'Break-Even<br>Jahr {break_even_year}'],
            textposition='top center',
            textfont=dict(
                size=FONT_SIZE_DATA_LABEL,
                color='red',
                weight='bold'),
            # Task 4.2
            hovertemplate=f'<b>Break-Even erreicht</b><br>Jahr: {break_even_year}<extra></extra>'
        ))

    # Wende verbessertes Styling an (Task 4.1-4.3)
    apply_improved_plotly_style(
        fig_break_even,
        title=get_text_pv_viz(
            texts,
            "viz_break_even_2d_title",
            "Kumulierter Kapitalfluss über die Laufzeit"),
        xlabel=get_text_pv_viz(
            texts,
            "viz_year_axis_label",
            "Jahr"),
        ylabel=get_text_pv_viz(
            texts,
            "viz_eur_axis_label",
            "Kapitalfluss (€)"),
        show_grid=True,
        show_legend=True)

    # Zusätzliche Nulllinie
    fig_break_even.update_yaxes(
        zeroline=True,
        zerolinecolor='rgba(255,0,0,0.3)',
        zerolinewidth=2
    )
    st.plotly_chart(
        fig_break_even,
        use_container_width=True,
        key="pv_visuals_break_even")

    # Speichere mit verbesserter Auflösung (Task 4.3)
    analysis_results['break_even_chart_bytes'] = save_plotly_chart_to_bytes(
        fig_break_even)

    # Generiere Beschreibung (Task 4.4)
    final_cashflow = cashflow_data[-1]
    chart_description = generate_chart_description(
        chart_type="Liniendiagramm",
        data={'values': cashflow_data, 'labels': [f"Jahr {y}" for y in years_axis]},
        purpose="Darstellung des kumulierten Kapitalflusses zur Identifikation des Break-Even-Punkts",
        key_insights=[
            f"Break-Even erreicht in Jahr {break_even_year}" if break_even_year else "Break-Even noch nicht erreicht",
            f"Finaler Kapitalfluss nach {simulation_years} Jahren: {final_cashflow:,.0f} €",
            f"Simulationszeitraum: {simulation_years} Jahre"
        ]
    )
    analysis_results['break_even_chart_description'] = chart_description


def render_amortisation_pv_data(
        analysis_results: dict[str, Any], texts: dict[str, str]):
    """
    Rendert ein 2D-Liniendiagramm des Amortisationsverlaufs (Investition vs. kumulierte Rückflüsse).
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen, erwartet
                                           `simulation_period_years_effective` (int),
                                           `total_investment_netto` (float), und
                                           `annual_benefits_sim` (Liste von Floats, Länge N).
                                           Wird modifiziert, um `amortisation_chart_bytes` hinzuzufügen.
        texts (Dict[str, str): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(
        get_text_pv_viz(
            texts,
            "viz_amortisation_2d_subheader",
            "Amortisation – Rückflusskurve"))
    simulation_years = analysis_results.get(
        'simulation_period_years_effective', 0)
    total_investment_raw = analysis_results.get('total_investment_netto', 0)
    annual_benefits_raw = analysis_results.get('annual_benefits_sim', [])

    total_investment = float(total_investment_raw) if isinstance(
        total_investment_raw, (int, float)) and not (
        math.isnan(total_investment_raw) or math.isinf(total_investment_raw)) else 0.0

    if not isinstance(
            simulation_years,
            int) or simulation_years <= 0 or total_investment <= 0 or not annual_benefits_raw or not isinstance(
            annual_benefits_raw,
            list) or len(annual_benefits_raw) != simulation_years:
        st.warning(
            get_text_pv_viz(
                texts,
                "viz_data_missing_amortisation",
                "Daten für Amortisationsdiagramm (Investition, jährl. Vorteile) nicht verfügbar oder unvollständig."))
        fig_fallback_amort = go.Figure()
        fig_fallback_amort.update_layout(
            title=get_text_pv_viz(
                texts,
                "viz_data_unavailable_title",
                "Daten nicht verfügbar"))
        st.plotly_chart(
            fig_fallback_amort,
            use_container_width=True,
            key="pv_visuals_amortisation_fallback")
        analysis_results['amortisation_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(
            fig_fallback_amort, texts)
        return

    annual_benefits = [float(b) if isinstance(b, (int, float)) and not (
        math.isnan(b) or math.isinf(b)) else 0.0 for b in annual_benefits_raw]
    years_axis = list(range(simulation_years + 1))
    kosten_linie = [total_investment] * (simulation_years + 1)

    kumulierte_rueckfluesse = [0.0]
    current_sum_rueckfluss = 0.0
    for benefit_val in annual_benefits:
        current_sum_rueckfluss += benefit_val
        kumulierte_rueckfluesse.append(current_sum_rueckfluss)

    # Finde Amortisationspunkt
    amortisation_year = None
    for i, rueckfluss in enumerate(kumulierte_rueckfluesse):
        if rueckfluss >= total_investment:
            amortisation_year = i
            break

    fig_amort = go.Figure()

    # Investitionskosten (horizontale Linie) mit verbesserter Breite (Task 4.1)
    fig_amort.add_trace(go.Scatter(
        x=years_axis,
        y=kosten_linie,
        mode='lines',
        name=get_text_pv_viz(
            texts,
            "viz_cost_label",
            "Investitionskosten (Netto)"),
        line=dict(
            color='red',
            width=2.5,
            dash='dash'),
        # Task 4.1: Dickere Linie
        hovertemplate='<b>Investition</b><br>%{y:,.0f} €<extra></extra>'
    ))

    # Kumulierter Rückfluss mit verbessertem Styling (Task 4.1)
    create_improved_plotly_line_chart(
        fig_amort,
        x_data=years_axis,
        y_data=kumulierte_rueckfluesse,
        name=get_text_pv_viz(
            texts,
            "viz_cumulative_return_label",
            "Kumulierter Rückfluss"),
        color='blue',
        show_markers=True)

    # Füge Fill hinzu
    fig_amort.data[1].fill = 'tozeroy'
    fig_amort.data[1].fillcolor = 'rgba(0,0,255,0.1)'

    # Markiere Amortisationspunkt mit verbesserter Größe (Task 4.1)
    if amortisation_year is not None:
        fig_amort.add_trace(go.Scatter(
            x=[amortisation_year],
            y=[total_investment],
            mode='markers+text',
            name='Amortisation',
            marker=dict(
                size=18,
                color='green',
                symbol='star'),
            # Task 4.1: Größerer Marker
            text=[f'Amortisiert<br>Jahr {amortisation_year}'],
            textposition='top center',
            textfont=dict(
                size=FONT_SIZE_DATA_LABEL,
                color='green',
                weight='bold'),
            # Task 4.2
            hovertemplate=f'<b>Amortisation erreicht</b><br>Jahr: {amortisation_year}<br>Betrag: {
                total_investment:,.0f} €<extra></extra>'
        ))

    # Wende verbessertes Styling an (Task 4.1-4.3)
    apply_improved_plotly_style(
        fig_amort,
        title=get_text_pv_viz(
            texts,
            "viz_amortisation_2d_title",
            "Amortisationsverlauf: Investition vs. Kumulierter Rückfluss"),
        xlabel=get_text_pv_viz(
            texts,
            "viz_year_axis_label",
            "Jahr"),
        ylabel=get_text_pv_viz(
            texts,
            "viz_eur_axis_label",
            "Betrag (€)"),
        show_grid=True,
        show_legend=True)
    st.plotly_chart(
        fig_amort,
        use_container_width=True,
        key="pv_visuals_amortisation")

    # Speichere mit verbesserter Auflösung (Task 4.3)
    analysis_results['amortisation_chart_bytes'] = save_plotly_chart_to_bytes(
        fig_amort)

    # Generiere Beschreibung (Task 4.4)
    final_return = kumulierte_rueckfluesse[-1]
    chart_description = generate_chart_description(
        chart_type="Liniendiagramm",
        data={'values': kumulierte_rueckfluesse, 'labels': [f"Jahr {y}" for y in years_axis]},
        purpose="Visualisierung des Amortisationsverlaufs durch Vergleich von Investition und kumuliertem Rückfluss",
        key_insights=[
            f"Investitionskosten (Netto): {total_investment:,.0f} €",
            f"Amortisation erreicht in Jahr {amortisation_year}" if amortisation_year else "Amortisation noch nicht erreicht",
            f"Kumulierter Rückfluss nach {simulation_years} Jahren: {final_return:,.0f} €",
            f"Gewinn nach {simulation_years} Jahren: {final_return - total_investment:,.0f} €"
        ]
    )
    analysis_results['amortisation_chart_description'] = chart_description


def render_co2_savings_visualization(
        analysis_results: dict[str, Any], texts: dict[str, str]) -> None:
    """
    Erstellt eine ansprechende 2D-Visualisierung der CO₂-Einsparungen mit Balkendiagramm
    für Auto, Flugzeug und Bäume.

    Args:
        analysis_results (Dict[str, Any]): Die Analyseergebnisse mit CO₂-Daten.
        texts (Dict[str, str]): Das Text-Dictionary für Labels.
    """
    co2_savings = analysis_results.get('annual_co2_savings_kg', 0.0)
    trees_equiv = analysis_results.get('co2_equivalent_trees_per_year', 0.0)
    car_km_equiv = analysis_results.get('co2_equivalent_car_km_per_year', 0.0)

    # Berechnung der Flugzeug-Äquivalente (ca. 230g CO₂ pro km)
    airplane_km_equiv = co2_savings / 0.23 if co2_savings > 0 else 0.0

    if co2_savings <= 0:
        st.info(
            get_text_pv_viz(
                texts,
                "co2_no_data",
                "Keine CO₂-Daten verfügbar für Visualisierung."))
        return

    # Erstelle 2D-Balkendiagramm mit verbessertem Styling (Task 4.1-4.2)
    categories = [
        f'🌳 Bäume<br>({trees_equiv:.0f} Stück)',
        f'🚗 Autokilometer<br>({car_km_equiv:,.0f} km)',
        f'✈️ Flugkilometer<br>({airplane_km_equiv:,.0f} km)'
    ]

    values = [trees_equiv, car_km_equiv, airplane_km_equiv]
    # Grün, Rot, Blau (Task 4.2: Kontrastreiche Farben)
    colors = ['#2E7D32', '#D32F2F', '#1976D2']

    fig_co2 = go.Figure()

    # Verwende verbesserte Balken mit dickeren Kanten (Task 4.1)
    fig_co2.add_trace(go.Bar(
        x=categories,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)  # Task 4.1: Dickere Kanten
        ),
        text=[f'{val:,.0f}' for val in values],
        textposition='outside',
        textfont=dict(
            size=FONT_SIZE_DATA_LABEL,
            color='black',
            weight='bold'),
        # Task 4.2
        hovertemplate='<b>%{x}</b><br>Wert: %{y:,.0f}<extra></extra>'
    ))

    # Wende verbessertes Styling an (Task 4.1-4.3)
    apply_improved_plotly_style(fig_co2,
                                title=get_text_pv_viz(texts,
                                                      "co2_2d_title",
                                                      f"Ihre jährliche CO₂-Einsparung: {co2_savings:,.0f} kg"),
                                xlabel='',
                                ylabel='Äquivalente',
                                show_grid=True,
                                show_legend=False)

    # Zusätzliche Anpassungen für Titel-Farbe
    fig_co2.update_layout(
        title=dict(
            text=get_text_pv_viz(
                texts, "co2_2d_title", f"Ihre jährliche CO₂-Einsparung: {co2_savings:,.0f} kg"),
            font=dict(
                size=16,
                color='darkgreen',
                family='Arial'),
            # Task 4.1: Größerer Titel
            x=0.5,
            xanchor='center'
        )
    )

    st.plotly_chart(
        fig_co2,
        use_container_width=True,
        key="co2_savings_2d_viz")

    # Export für PDF mit verbesserter Auflösung (Task 4.3)
    analysis_results['co2_savings_chart_bytes'] = save_plotly_chart_to_bytes(
        fig_co2)

    # Generiere Beschreibung (Task 4.4)
    chart_description = generate_chart_description(
        chart_type="Balkendiagramm",
        data={'values': values, 'labels': ['Bäume', 'Autokilometer', 'Flugkilometer']},
        purpose="Veranschaulichung der CO₂-Einsparung durch Vergleich mit alltäglichen Äquivalenten",
        key_insights=[
            f"Jährliche CO₂-Einsparung: {co2_savings:,.0f} kg",
            f"Entspricht {trees_equiv:.0f} Bäumen, die diese Menge CO₂ binden",
            f"Entspricht {car_km_equiv:,.0f} km Autofahrt",
            f"Entspricht {airplane_km_equiv:,.0f} km Flugstrecke"
        ]
    )
    analysis_results['co2_savings_chart_description'] = chart_description

    # Zusätzliche Info-Boxen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="🌳 Bäume (CO₂-Bindung)",
            value=f"{trees_equiv:.0f}",
            help="Anzahl Bäume, die dieselbe Menge CO₂ binden würden"
        )

    with col2:
        st.metric(
            label="🚗 Vermiedene Autokilometer",
            value=f"{car_km_equiv:,.0f} km",
            help="Entspricht der CO₂-Emission dieser Autokilometer"
        )

    with col3:
        st.metric(
            label="✈️ Vermiedene Flugkilometer",
            value=f"{airplane_km_equiv:,.0f} km",
            help="Entspricht der CO₂-Emission dieser Flugkilometer"
        )

# Änderungshistorie
# 2025-06-02, Gemini Ultra: Modul bereinigt, redundanten Code aus analysis.py entfernt. Fokus auf Kernfunktionen von pv_visuals.py.
#                           Keys für st.plotly_chart eindeutig gemacht. Fallback-Figuren bei fehlenden Daten implementiert.
#                           Robuste Datenvalidierung und -konvertierung in allen Rendering-Funktionen hinzugefügt.
#                           Funktion _apply_custom_style_to_fig aus analysis.py entfernt, da pv_visuals seine Styles selbst handhaben oder keine globalen Styles benötigt.
#                           Exportfunktion _export_plotly_fig_to_bytes_pv_viz beibehalten und für Fallback-Figuren genutzt.
# 2025-06-02, Gemini Ultra: Fehlenden `import math` hinzugefügt.
