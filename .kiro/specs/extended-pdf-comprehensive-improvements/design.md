# Design Document

## Overview

Dieses Design-Dokument beschreibt die umfassende, robuste und vollständige Verbesserung des erweiterten PDF-Ausgabesystems in 10 kritischen Bereichen. Die Implementierung basiert auf der funktionierenden Logik aus dem `repair_pdf` Ordner und integriert diese vollständig, getestet und optimiert in den aktuellen Code.

### Hauptziele

1. **Visuelle Verbesserungen**: Transparente Hintergründe für alle Diagramme, vollständige 3D zu 2D Konvertierung, optimierte Darstellung mit dickeren Elementen und Beschreibungen
2. **UI-Integration**: Vollständige, dynamische Diagrammauswahl in pdf_ui.py mit Session State Management und Vorschau-Funktionalität
3. **Dokumenten-Integration**: Robuste Integration von Produktdatenblättern aus Produktdatenbank und firmenspe zifischen Dokumenten mit Fehlerbehandlung
4. **Layout-Verbesserungen**: Intelligenter Seitenschutz mit KeepTogether, professionelle Kopf-/Fußzeilen mit Logos und dynamischen Seitenzahlen
5. **Finanzierungs-Priorisierung**: Vollständige Finanzierungsinformationen ab Seite 9 mit Kredit, Leasing, Amortisationsplänen und dynamischen Berechnungen
6. **Code-Integration**: 100% systematische Übernahme und Verbesserung der repair_pdf Logik mit vollständiger Dokumentation

### Design-Prinzipien

- **Robustheit**: Umfassende Fehlerbehandlung für alle Edge Cases
- **Modularität**: Klare Trennung von Verantwortlichkeiten
- **Testbarkeit**: Alle Komponenten sind unit-testbar
- **Performance**: Optimierte Diagramm-Generierung und PDF-Erstellung
- **Wartbarkeit**: Klare Dokumentation und konsistente Code-Struktur
- **Rückwärtskompatibilität**: Bestehende Funktionalität bleibt erhalten

## Architecture

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    calculations.py                           │
│  - Diagramm-Generierung mit transparenten Hintergründen     │
│  - 2D statt 3D Diagramme                                    │
│  - Dickere Balken/Donuts                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              calculations_extended.py                        │
│  - Erweiterte Diagramme mit transparenten Hintergründen     │
│  - 2D Konvertierung                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     analysis.py                              │
│  - Analyse-Diagramme mit transparenten Hintergründen        │
│  - 2D Konvertierung                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      pdf_ui.py                               │
│  - Diagrammauswahl-UI                                       │
│  - Alle verfügbaren Diagramme anzeigen                     │
│  - Session State Management                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   pdf_generator.py                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  generate_offer_pdf()                                 │  │
│  │  - Hauptfunktion für PDF-Erstellung                   │  │
│  │  - Finanzierungsinformationen ab Seite 9             │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  page_layout_handler()                                │  │
│  │  - Kopf-/Fußzeilen für Seiten 9+                     │  │
│  │  - Logo, Dreieck, Seitenzahlen                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  _append_datasheets_and_documents()                   │  │
│  │  - Produktdatenblätter anhängen                       │  │
│  │  - Firmendokumente anhängen                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Transparente Diagramm-Hintergründe

**Dateien**: calculations.py, calculations_extended.py, analysis.py, doc_output.py

**Technische Spezifikation**:

Alle Diagramme müssen transparente Hintergründe haben, um professionell auf weißen PDF-Seiten zu erscheinen. Dies erfordert Änderungen sowohl bei der Diagramm-Erstellung als auch beim Speichern.

**Matplotlib-Implementierung** (für calculations.py, calculations_extended.py, doc_output.py):

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI Backend
import io
from typing import Optional

def create_chart_with_transparent_background(
    chart_type: str,
    data: Dict[str, Any],
    title: str,
    **kwargs
) -> Optional[bytes]:
    """
    Generiert ein Diagramm mit transparentem Hintergrund.
    
    Args:
        chart_type: Typ des Diagramms ('bar', 'line', 'pie', 'donut')
        data: Daten für das Diagramm
        title: Titel des Diagramms
        **kwargs: Zusätzliche Parameter
        
    Returns:
        PNG-Bytes mit transparentem Hintergrund oder None bei Fehler
    """
    try:
        # Figure und Axes erstellen
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # KRITISCH: Transparente Hintergründe setzen
        fig.patch.set_alpha(0)  # Figure-Hintergrund transparent
        ax.patch.set_alpha(0)   # Axes-Hintergrund transparent
        
        # Legende-Hintergrund transparent (falls vorhanden)
        if kwargs.get('show_legend', True):
            legend = ax.legend()
            if legend:
                legend.get_frame().set_alpha(0)
                legend.get_frame().set_facecolor('none')
        
        # Diagramm-spezifische Logik
        if chart_type == 'bar':
            ax.bar(data['x'], data['y'], width=0.6, color=data.get('colors'))
        elif chart_type == 'line':
            ax.plot(data['x'], data['y'], linewidth=2.5, color=data.get('color'))
        elif chart_type == 'pie' or chart_type == 'donut':
            wedgeprops = {'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}
            ax.pie(data['values'], labels=data['labels'], autopct='%1.1f%%',
                  wedgeprops=wedgeprops if chart_type == 'donut' else None)
        
        # Titel und Labels mit größeren Schriftarten
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        if 'xlabel' in kwargs:
            ax.set_xlabel(kwargs['xlabel'], fontsize=12)
        if 'ylabel' in kwargs:
            ax.set_ylabel(kwargs['ylabel'], fontsize=12)
        
        # Tick-Labels größer machen
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Gitternetz mit Transparenz (falls gewünscht)
        if kwargs.get('show_grid', True):
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.set_axisbelow(True)  # Gitternetz hinter Daten
        
        # Layout optimieren
        plt.tight_layout()
        
        # KRITISCH: Als PNG mit transparentem Hintergrund speichern
        buf = io.BytesIO()
        plt.savefig(
            buf,
            format='png',
            dpi=300,  # Hohe Auflösung
            bbox_inches='tight',
            facecolor='none',  # Transparenter Hintergrund
            edgecolor='none',  # Keine Ränder
            transparent=True   # Explizit transparent
        )
        buf.seek(0)
        chart_bytes = buf.getvalue()
        plt.close(fig)  # Speicher freigeben
        
        return chart_bytes
        
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des Diagramms: {e}")
        plt.close('all')  # Alle Figures schließen
        return None
```

**Plotly-Implementierung** (für analysis.py):

```python
import plotly.graph_objects as go
import plotly.io as pio
from typing import Optional

def create_plotly_chart_with_transparent_background(
    chart_type: str,
    data: Dict[str, Any],
    title: str,
    **kwargs
) -> Optional[bytes]:
    """
    Generiert ein Plotly-Diagramm mit transparentem Hintergrund.
    
    Args:
        chart_type: Typ des Diagramms
        data: Daten für das Diagramm
        title: Titel des Diagramms
        **kwargs: Zusätzliche Parameter
        
    Returns:
        PNG-Bytes mit transparentem Hintergrund oder None bei Fehler
    """
    try:
        fig = go.Figure()
        
        # Daten hinzufügen (chart_type-abhängig)
        if chart_type == 'bar':
            fig.add_trace(go.Bar(x=data['x'], y=data['y'], marker_color=data.get('color')))
        elif chart_type == 'line':
            fig.add_trace(go.Scatter(x=data['x'], y=data['y'], mode='lines', line=dict(width=2.5)))
        
        # KRITISCH: Layout mit transparenten Hintergründen
        fig.update_layout(
            title=dict(text=title, font=dict(size=14, family='Arial', color='black')),
            paper_bgcolor='rgba(0,0,0,0)',  # Transparenter Paper-Hintergrund
            plot_bgcolor='rgba(0,0,0,0)',   # Transparenter Plot-Hintergrund
            font=dict(size=12, family='Arial', color='black'),
            xaxis=dict(
                title=kwargs.get('xlabel', ''),
                gridcolor='rgba(128,128,128,0.3)',  # Transparentes Gitternetz
                showgrid=kwargs.get('show_grid', True)
            ),
            yaxis=dict(
                title=kwargs.get('ylabel', ''),
                gridcolor='rgba(128,128,128,0.3)',
                showgrid=kwargs.get('show_grid', True)
            ),
            legend=dict(
                bgcolor='rgba(0,0,0,0)',  # Transparente Legende
                bordercolor='rgba(0,0,0,0)'
            )
        )
        
        # Als PNG mit transparentem Hintergrund exportieren
        chart_bytes = pio.to_image(
            fig,
            format='png',
            width=1400,
            height=1000,
            scale=2  # Hohe Auflösung
        )
        
        return chart_bytes
        
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des Plotly-Diagramms: {e}")
        return None
```

**Betroffene Funktionen und Änderungen**:

**calculations.py**:

- `generate_monthly_production_consumption_chart()` - Zeile ~450
- `generate_cost_projection_chart()` - Zeile ~520
- `generate_cumulative_cashflow_chart()` - Zeile ~590
- `generate_roi_chart()` - Zeile ~660
- `generate_energy_balance_chart()` - Zeile ~730 (Donut)
- `generate_monthly_savings_chart()` - Zeile ~800
- `generate_yearly_comparison_chart()` - Zeile ~870
- `generate_amortization_chart()` - Zeile ~940
- `generate_co2_savings_chart()` - Zeile ~1010
- `generate_financing_comparison_chart()` - Zeile ~1080

**calculations_extended.py**:

- `generate_scenario_comparison_chart()` - Zeile ~150
- `generate_tariff_comparison_chart()` - Zeile ~220
- `generate_income_projection_chart()` - Zeile ~290
- `generate_battery_usage_chart()` - Zeile ~360
- `generate_grid_interaction_chart()` - Zeile ~430

**analysis.py**:

- `generate_advanced_analysis_chart()` - Zeile ~2006
- `generate_sensitivity_analysis_chart()` - Zeile ~2080
- `generate_optimization_chart()` - Zeile ~2150

**doc_output.py**:

- `generate_summary_chart()` - Zeile ~180
- `generate_comparison_chart()` - Zeile ~250

**Implementierungs-Checkliste**:

1. ✓ Alle `fig.patch.set_alpha(0)` hinzufügen
2. ✓ Alle `ax.patch.set_alpha(0)` hinzufügen
3. ✓ Alle `plt.savefig()` mit `facecolor='none', edgecolor='none', transparent=True` aktualisieren
4. ✓ Alle Plotly `fig.update_layout()` mit transparenten Hintergründen aktualisieren
5. ✓ Legenden-Hintergründe transparent machen
6. ✓ Gitternetz-Transparenz auf 0.3 setzen
7. ✓ Fehlerbehandlung für alle Chart-Funktionen hinzufügen
8. ✓ Unit Tests für transparente Hintergründe schreiben

### 2. 3D zu 2D Konvertierung

**Dateien**: calculations.py, calculations_extended.py, analysis.py

**Technische Spezifikation**:

Alle 3D-Diagramme müssen in 2D konvertiert werden, um bessere Lesbarkeit und professionelleres Aussehen zu gewährleisten. Die dritte Dimension wird durch Farb-Kodierung, Größen-Variation oder separate Subplots dargestellt.

**Konvertierungs-Strategien**:

**1. 3D Bar Charts → 2D Grouped/Stacked Bar Charts**:

```python
# VORHER (3D):
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# 3D Balken
xpos = np.arange(len(categories))
ypos = np.arange(len(scenarios))
xpos, ypos = np.meshgrid(xpos, ypos)
xpos = xpos.flatten()
ypos = ypos.flatten()
zpos = np.zeros_like(xpos)

dx = dy = 0.5
dz = values.flatten()

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, alpha=0.8)
ax.set_xlabel('Kategorie')
ax.set_ylabel('Szenario')
ax.set_zlabel('Wert')

# NACHHER (2D Grouped Bar Chart):
fig, ax = plt.subplots(figsize=(14, 10))

# Transparente Hintergründe
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Gruppierte Balken
x = np.arange(len(categories))
width = 0.6 / len(scenarios)  # Breite pro Gruppe

for i, scenario in enumerate(scenarios):
    offset = width * i - (width * len(scenarios) / 2)
    bars = ax.bar(
        x + offset,
        values[i],
        width,
        label=scenario,
        color=colors[i],
        alpha=0.9,
        edgecolor='white',
        linewidth=1.5
    )
    
    # Werte über Balken anzeigen
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{height:.1f}',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold'
        )

ax.set_xlabel('Kategorie', fontsize=12, fontweight='bold')
ax.set_ylabel('Wert', fontsize=12, fontweight='bold')
ax.set_title('Vergleich nach Kategorien und Szenarien', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')
ax.legend(title='Szenario', fontsize=10, title_fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
```

**2. 3D Pie Charts → 2D Pie/Donut Charts**:

```python
# VORHER (3D Pie):
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 3D Pie (nicht direkt unterstützt, oft mit Workarounds)
# Komplizierte 3D-Darstellung

# NACHHER (2D Donut mit verbesserter Darstellung):
fig, ax = plt.subplots(figsize=(12, 10))

# Transparente Hintergründe
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Donut-Chart mit dickeren Ringen
wedgeprops = {
    'width': 0.4,  # Dickerer Ring
    'edgecolor': 'white',
    'linewidth': 2
}

# Explode für Hervorhebung
explode = [0.05 if v == max(values) else 0 for v in values]

wedges, texts, autotexts = ax.pie(
    values,
    labels=labels,
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    explode=explode,
    wedgeprops=wedgeprops,
    textprops={'fontsize': 10, 'fontweight': 'bold'}
)

# Prozentsätze formatieren
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# Legende mit Werten
legend_labels = [f'{label}: {value:.2f}' for label, value in zip(labels, values)]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

ax.set_title('Verteilung nach Kategorien', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
```

**3. 3D Surface Plots → 2D Heatmaps/Contour Plots**:

```python
# VORHER (3D Surface):
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

X, Y = np.meshgrid(x_range, y_range)
Z = calculate_surface(X, Y)

surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.set_xlabel('X-Achse')
ax.set_ylabel('Y-Achse')
ax.set_zlabel('Z-Achse')
fig.colorbar(surf)

# NACHHER (2D Heatmap):
fig, ax = plt.subplots(figsize=(14, 10))

# Transparente Hintergründe
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Heatmap
im = ax.imshow(
    Z,
    cmap='viridis',
    aspect='auto',
    origin='lower',
    extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()],
    interpolation='bilinear'
)

# Colorbar
cbar = plt.colorbar(im, ax=ax, label='Wert')
cbar.ax.tick_params(labelsize=10)

# Contour-Linien für bessere Lesbarkeit
contours = ax.contour(X, Y, Z, colors='white', alpha=0.4, linewidths=0.5)
ax.clabel(contours, inline=True, fontsize=8)

ax.set_xlabel('X-Achse', fontsize=12, fontweight='bold')
ax.set_ylabel('Y-Achse', fontsize=12, fontweight='bold')
ax.set_title('Werte-Verteilung', fontsize=14, fontweight='bold')

plt.tight_layout()
```

**Betroffene Diagramme und Konvertierungen**:

**calculations.py**:

- Keine 3D-Diagramme identifiziert (bereits 2D)

**calculations_extended.py**:

- `generate_scenario_comparison_chart()` - Zeile ~150
  - **Vorher**: 3D Bar Chart mit Szenarien auf Z-Achse
  - **Nachher**: 2D Grouped Bar Chart mit Szenarien als separate Balkengruppen
  
- `generate_tariff_comparison_chart()` - Zeile ~220
  - **Vorher**: 3D Bar Chart mit Tarifen auf Z-Achse
  - **Nachher**: 2D Grouped Bar Chart mit Tarifen als separate Balkengruppen
  
- `generate_income_projection_chart()` - Zeile ~290
  - **Vorher**: 3D Line Plot mit mehreren Ebenen
  - **Nachher**: 2D Multi-Line Chart mit verschiedenen Farben und Linienstilen

**analysis.py**:

- `generate_sensitivity_analysis_chart()` - Zeile ~2080
  - **Vorher**: 3D Surface Plot
  - **Nachher**: 2D Heatmap mit Contour-Linien
  
- `generate_optimization_chart()` - Zeile ~2150
  - **Vorher**: 3D Scatter Plot
  - **Nachher**: 2D Scatter Plot mit Farb-Kodierung für dritte Dimension

**Implementierungs-Checkliste**:

1. ✓ Alle `from mpl_toolkits.mplot3d import Axes3D` Imports entfernen
2. ✓ Alle `projection='3d'` aus `add_subplot()` entfernen
3. ✓ Alle `ax.bar3d()` durch `ax.bar()` mit Gruppierung ersetzen
4. ✓ Alle `ax.plot3D()` durch `ax.plot()` mit Multi-Line ersetzen
5. ✓ Alle `ax.plot_surface()` durch `ax.imshow()` oder `ax.contourf()` ersetzen
6. ✓ Alle `ax.scatter3D()` durch `ax.scatter()` mit Farb-Kodierung ersetzen
7. ✓ Dritte Dimension durch Farben, Größen oder separate Plots darstellen
8. ✓ Alle konvertierten Diagramme mit transparenten Hintergründen versehen
9. ✓ Unit Tests für alle konvertierten Diagramme schreiben
10. ✓ Visuelle Vergleiche zwischen 3D und 2D Versionen durchführen

**Code-Beispiel für vollständige Konvertierung**:

```python
def generate_scenario_comparison_chart_2d(
    scenarios: List[str],
    categories: List[str],
    values: np.ndarray,
    colors: List[str]
) -> Optional[bytes]:
    """
    Generiert ein 2D Grouped Bar Chart für Szenario-Vergleiche.
    
    Args:
        scenarios: Liste der Szenario-Namen
        categories: Liste der Kategorie-Namen
        values: 2D Array mit Werten [scenarios x categories]
        colors: Liste der Farben für jedes Szenario
        
    Returns:
        PNG-Bytes mit transparentem Hintergrund oder None bei Fehler
    """
    try:
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Transparente Hintergründe
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        # Gruppierte Balken
        x = np.arange(len(categories))
        width = 0.6 / len(scenarios)
        
        for i, scenario in enumerate(scenarios):
            offset = width * i - (width * len(scenarios) / 2)
            bars = ax.bar(
                x + offset,
                values[i],
                width,
                label=scenario,
                color=colors[i],
                alpha=0.9,
                edgecolor='white',
                linewidth=1.5
            )
            
            # Werte über Balken
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f'{height:.1f}',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )
        
        # Styling
        ax.set_xlabel('Kategorie', fontsize=12, fontweight='bold')
        ax.set_ylabel('Wert (€)', fontsize=12, fontweight='bold')
        ax.set_title('Szenario-Vergleich', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10)
        ax.legend(title='Szenario', fontsize=10, title_fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        plt.tight_layout()
        
        # Als PNG speichern
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight',
                   facecolor='none', edgecolor='none', transparent=True)
        buf.seek(0)
        chart_bytes = buf.getvalue()
        plt.close(fig)
        
        return chart_bytes
        
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des 2D Szenario-Vergleichs: {e}")
        plt.close('all')
        return None
```

### 3. Diagrammauswahl in PDF UI

**Datei**: pdf_ui.py

**Technische Spezifikation**:

Die Diagrammauswahl-UI muss vollständig integriert werden, um Benutzern die Auswahl spezifischer Diagramme für die PDF zu ermöglichen. Dies erfordert:

1. Vollständiges Mapping aller verfügbaren Diagramme
2. Kategorisierung der Diagramme
3. Session State Management
4. Dynamische Verfügbarkeits-Prüfung
5. Vorschau-Funktionalität

**Vollständige Implementierung**:

```python
import streamlit as st
from typing import Dict, List, Optional, Set
import logging

# ============================================================================
# CHART CONFIGURATION
# ============================================================================

# Vollständiges Mapping aller Diagramme (aus repair_pdf/pdf_ui.py, Zeile 262)
CHART_KEY_TO_FRIENDLY_NAME_MAP = {
    # Basis-Diagramme aus calculations.py
    'monthly_prod_cons_chart_bytes': "📊 Monatliche Produktion/Verbrauch (2D)",
    'cost_projection_chart_bytes': "💰 Stromkosten-Hochrechnung (2D)",
    'cumulative_cashflow_chart_bytes': "📈 Kumulierter Cashflow (2D)",
    'roi_chart_bytes': "💹 ROI-Entwicklung (2D)",
    'energy_balance_chart_bytes': "🔋 Energiebilanz (Donut)",
    'monthly_savings_chart_bytes': "💵 Monatliche Einsparungen (2D)",
    'yearly_comparison_chart_bytes': "📅 Jahresvergleich (2D)",
    'amortization_chart_bytes': "⏱️ Amortisationszeit (2D)",
    'co2_savings_chart_bytes': "🌱 CO₂-Einsparung (2D)",
    'financing_comparison_chart_bytes': "🏦 Finanzierungsvergleich (2D)",
    
    # Erweiterte Diagramme aus calculations_extended.py
    'scenario_comparison_chart_bytes': "🔄 Szenario-Vergleich (2D Grouped)",
    'tariff_comparison_chart_bytes': "⚡ Tarif-Vergleich (2D Grouped)",
    'income_projection_chart_bytes': "💸 Einnahmen-Projektion (2D Multi-Line)",
    'battery_usage_chart_bytes': "🔋 Batterie-Nutzung (2D Stacked)",
    'grid_interaction_chart_bytes': "🔌 Netz-Interaktion (2D Line)",
    'self_consumption_chart_bytes': "🏠 Eigenverbrauch-Analyse (2D)",
    'feed_in_analysis_chart_bytes': "⚡ Einspeisung-Analyse (2D)",
    
    # Analyse-Diagramme aus analysis.py
    'advanced_analysis_chart_bytes': "🔬 Erweiterte Analyse (2D)",
    'sensitivity_analysis_chart_bytes': "📊 Sensitivitäts-Analyse (2D Heatmap)",
    'optimization_chart_bytes': "🎯 Optimierungs-Analyse (2D Scatter)",
    'performance_metrics_chart_bytes': "📈 Performance-Metriken (2D)",
    'comparison_matrix_chart_bytes': "🔢 Vergleichs-Matrix (2D Heatmap)",
    
    # Dokumenten-Diagramme aus doc_output.py
    'summary_chart_bytes': "📋 Zusammenfassung (2D)",
    'comparison_chart_bytes': "⚖️ Vergleich (2D)",
}

# Kategorisierung der Diagramme
CHART_CATEGORIES = {
    'Finanzierung': [
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes',
        'roi_chart_bytes',
        'monthly_savings_chart_bytes',
        'amortization_chart_bytes',
        'financing_comparison_chart_bytes',
        'income_projection_chart_bytes',
    ],
    'Energie': [
        'monthly_prod_cons_chart_bytes',
        'energy_balance_chart_bytes',
        'battery_usage_chart_bytes',
        'grid_interaction_chart_bytes',
        'self_consumption_chart_bytes',
        'feed_in_analysis_chart_bytes',
    ],
    'Vergleiche': [
        'yearly_comparison_chart_bytes',
        'scenario_comparison_chart_bytes',
        'tariff_comparison_chart_bytes',
        'comparison_chart_bytes',
        'comparison_matrix_chart_bytes',
    ],
    'Umwelt': [
        'co2_savings_chart_bytes',
    ],
    'Analyse': [
        'advanced_analysis_chart_bytes',
        'sensitivity_analysis_chart_bytes',
        'optimization_chart_bytes',
        'performance_metrics_chart_bytes',
    ],
    'Zusammenfassung': [
        'summary_chart_bytes',
    ],
}

# ============================================================================
# CHART AVAILABILITY CHECK
# ============================================================================

def check_chart_availability(
    chart_key: str,
    project_data: Dict,
    pv_details: Dict
) -> bool:
    """
    Prüft ob ein Diagramm basierend auf den Projektdaten verfügbar ist.
    
    Args:
        chart_key: Schlüssel des Diagramms
        project_data: Projekt-Daten
        pv_details: PV-Details
        
    Returns:
        True wenn Diagramm verfügbar, sonst False
    """
    try:
        # Basis-Diagramme sind immer verfügbar
        basic_charts = [
            'monthly_prod_cons_chart_bytes',
            'cost_projection_chart_bytes',
            'energy_balance_chart_bytes',
        ]
        if chart_key in basic_charts:
            return True
        
        # Finanzierungs-Diagramme benötigen Finanzierungsdaten
        financing_charts = [
            'financing_comparison_chart_bytes',
            'income_projection_chart_bytes',
        ]
        if chart_key in financing_charts:
            return pv_details.get('include_financing', False)
        
        # Batterie-Diagramme benötigen Speicher
        battery_charts = [
            'battery_usage_chart_bytes',
            'self_consumption_chart_bytes',
        ]
        if chart_key in battery_charts:
            return pv_details.get('selected_storage_id') is not None
        
        # Szenario-Diagramme benötigen mehrere Szenarien
        scenario_charts = [
            'scenario_comparison_chart_bytes',
            'tariff_comparison_chart_bytes',
        ]
        if chart_key in scenario_charts:
            return len(pv_details.get('scenarios', [])) > 1
        
        # Analyse-Diagramme benötigen erweiterte Berechnungen
        analysis_charts = [
            'sensitivity_analysis_chart_bytes',
            'optimization_chart_bytes',
        ]
        if chart_key in analysis_charts:
            return pv_details.get('include_advanced_analysis', False)
        
        # Standardmäßig verfügbar
        return True
        
    except Exception as e:
        logging.error(f"Fehler bei Verfügbarkeits-Prüfung für {chart_key}: {e}")
        return False

# ============================================================================
# CHART SELECTION UI
# ============================================================================

def render_chart_selection_ui(
    project_data: Dict,
    pv_details: Dict
) -> List[str]:
    """
    Rendert die Diagrammauswahl-UI mit Kategorisierung und Verfügbarkeits-Prüfung.
    
    Args:
        project_data: Projekt-Daten
        pv_details: PV-Details
        
    Returns:
        Liste der ausgewählten Diagramm-Schlüssel
    """
    st.subheader("📊 Diagrammauswahl für PDF")
    st.markdown("Wählen Sie die Diagramme aus, die in der erweiterten PDF enthalten sein sollen.")
    
    # Verfügbare Diagramme ermitteln
    available_charts = {}
    unavailable_charts = {}
    
    for chart_key, friendly_name in CHART_KEY_TO_FRIENDLY_NAME_MAP.items():
        if check_chart_availability(chart_key, project_data, pv_details):
            available_charts[chart_key] = friendly_name
        else:
            unavailable_charts[chart_key] = friendly_name
    
    # Statistiken anzeigen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Verfügbare Diagramme", len(available_charts))
    with col2:
        st.metric("Nicht verfügbare", len(unavailable_charts))
    with col3:
        if 'selected_charts_for_pdf' in st.session_state:
            st.metric("Ausgewählt", len(st.session_state['selected_charts_for_pdf']))
        else:
            st.metric("Ausgewählt", 0)
    
    # Schnellauswahl-Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Alle auswählen", use_container_width=True):
            st.session_state['selected_charts_for_pdf'] = list(available_charts.keys())
            st.rerun()
    with col2:
        if st.button("❌ Keine auswählen", use_container_width=True):
            st.session_state['selected_charts_for_pdf'] = []
            st.rerun()
    with col3:
        if st.button("⭐ Empfohlene auswählen", use_container_width=True):
            recommended = [
                'monthly_prod_cons_chart_bytes',
                'cost_projection_chart_bytes',
                'cumulative_cashflow_chart_bytes',
                'roi_chart_bytes',
                'energy_balance_chart_bytes',
                'amortization_chart_bytes',
                'co2_savings_chart_bytes',
            ]
            st.session_state['selected_charts_for_pdf'] = [
                c for c in recommended if c in available_charts
            ]
            st.rerun()
    
    st.markdown("---")
    
    # Kategorisierte Auswahl
    selected_charts = st.session_state.get('selected_charts_for_pdf', [])
    
    for category, chart_keys in CHART_CATEGORIES.items():
        with st.expander(f"📁 {category}", expanded=True):
            category_available = [k for k in chart_keys if k in available_charts]
            category_unavailable = [k for k in chart_keys if k in unavailable_charts]
            
            if category_available:
                st.markdown(f"**Verfügbar ({len(category_available)}):**")
                for chart_key in category_available:
                    is_selected = chart_key in selected_charts
                    if st.checkbox(
                        available_charts[chart_key],
                        value=is_selected,
                        key=f"chart_select_{chart_key}"
                    ):
                        if chart_key not in selected_charts:
                            selected_charts.append(chart_key)
                    else:
                        if chart_key in selected_charts:
                            selected_charts.remove(chart_key)
            
            if category_unavailable:
                st.markdown(f"**Nicht verfügbar ({len(category_unavailable)}):**")
                for chart_key in category_unavailable:
                    st.checkbox(
                        f"🚫 {unavailable_charts[chart_key]}",
                        value=False,
                        disabled=True,
                        key=f"chart_disabled_{chart_key}",
                        help="Dieses Diagramm ist für die aktuellen Projektdaten nicht verfügbar."
                    )
    
    # Session State aktualisieren
    st.session_state['selected_charts_for_pdf'] = selected_charts
    
    # Vorschau-Bereich
    if selected_charts:
        st.markdown("---")
        st.markdown("### 👁️ Vorschau der ausgewählten Diagramme")
        
        # Vorschau-Thumbnails (falls verfügbar)
        if st.checkbox("Vorschau-Thumbnails anzeigen", value=False):
            cols = st.columns(3)
            for idx, chart_key in enumerate(selected_charts[:9]):  # Max 9 Vorschauen
                with cols[idx % 3]:
                    st.markdown(f"**{available_charts[chart_key]}**")
                    # Hier würde die Thumbnail-Generierung erfolgen
                    st.info("Vorschau wird generiert...")
    
    return selected_charts

# ============================================================================
# INTEGRATION IN PDF GENERATION
# ============================================================================

def get_selected_chart_bytes(
    chart_key: str,
    project_data: Dict,
    pv_details: Dict
) -> Optional[bytes]:
    """
    Generiert und gibt die Bytes für ein ausgewähltes Diagramm zurück.
    
    Args:
        chart_key: Schlüssel des Diagramms
        project_data: Projekt-Daten
        pv_details: PV-Details
        
    Returns:
        PNG-Bytes des Diagramms oder None bei Fehler
    """
    try:
        # Diagramm aus Session State holen (falls bereits generiert)
        if chart_key in st.session_state:
            return st.session_state[chart_key]
        
        # Sonst neu generieren
        from calculations import generate_chart
        from calculations_extended import generate_extended_chart
        from analysis import generate_analysis_chart
        
        # Routing basierend auf chart_key
        if chart_key in ['monthly_prod_cons_chart_bytes', 'cost_projection_chart_bytes', ...]:
            chart_bytes = generate_chart(chart_key, project_data, pv_details)
        elif chart_key in ['scenario_comparison_chart_bytes', 'tariff_comparison_chart_bytes', ...]:
            chart_bytes = generate_extended_chart(chart_key, project_data, pv_details)
        elif chart_key in ['advanced_analysis_chart_bytes', 'sensitivity_analysis_chart_bytes', ...]:
            chart_bytes = generate_analysis_chart(chart_key, project_data, pv_details)
        else:
            logging.warning(f"Unbekannter Chart-Key: {chart_key}")
            return None
        
        # In Session State cachen
        if chart_bytes:
            st.session_state[chart_key] = chart_bytes
        
        return chart_bytes
        
    except Exception as e:
        logging.error(f"Fehler beim Generieren von {chart_key}: {e}")
        return None
```

**Integration in pdf_ui.py**:

```python
# In der Hauptfunktion von pdf_ui.py

def main():
    # ... bestehender Code ...
    
    # Diagrammauswahl-UI rendern
    if st.checkbox("📊 Erweiterte PDF mit Diagrammen", value=False):
        selected_charts = render_chart_selection_ui(project_data, pv_details)
        
        # In inclusion_options speichern
        inclusion_options['selected_charts_for_pdf'] = selected_charts
        inclusion_options['append_additional_pages_after_main6'] = len(selected_charts) > 0
    
    # ... restlicher Code ...
```

**Implementierungs-Checkliste**:

1. ✓ Vollständiges Chart-Mapping erstellen
2. ✓ Kategorisierung implementieren
3. ✓ Verfügbarkeits-Prüfung implementieren
4. ✓ UI mit Expanders und Checkboxen erstellen
5. ✓ Schnellauswahl-Buttons implementieren
6. ✓ Session State Management implementieren
7. ✓ Vorschau-Funktionalität vorbereiten
8. ✓ Integration in PDF-Generierung
9. ✓ Fehlerbehandlung für alle Funktionen
10. ✓ Unit Tests für UI-Komponenten

### 4. Verbesserte Diagramm-Darstellung

**Dateien**: calculations.py, calculations_extended.py, analysis.py

**Implementierung**:

```python
# Dickere Balken
ax.bar(x, height, width=0.6, color=colors)  # width >= 0.6

# Dickere Donuts
wedgeprops = {'width': 0.4, 'edgecolor': 'white'}
ax.pie(sizes, labels=labels, autopct='%1.1f%%', wedgeprops=wedgeprops)

# Beschreibung unter Diagramm
description = f"Dieses Diagramm zeigt {description_text} mit Werten: {values}"
# In PDF als Paragraph unter dem Diagramm einfügen
```

### 5. Produktdatenblätter einbinden

**Datei**: pdf_generator.py

**Technische Spezifikation**:

Produktdatenblätter müssen robust aus der Produktdatenbank geladen und an die PDF angehängt werden. Dies erfordert:

1. Sammlung aller Produkt-IDs (Hauptkomponenten + Zubehör)
2. Laden der Produktinformationen aus der Datenbank
3. Validierung der Datenblatt-Pfade
4. PDF-Zusammenführung mit Fehlerbehandlung
5. Logging aller Schritte

**Vollständige Implementierung** (aus repair_pdf/pdf_generator.py, Zeilen 4930-5050):

```python
import os
import io
import logging
from typing import Dict, List, Any, Callable, Optional
from pypdf import PdfWriter, PdfReader
from pathlib import Path

# Basis-Verzeichnisse (aus global_constants oder Konfiguration)
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(
    os.path.dirname(__file__),
    'data',
    'product_datasheets'
)

COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(
    os.path.dirname(__file__),
    'data',
    'company_documents'
)

def _append_datasheets_and_documents(
    main_pdf_bytes: bytes,
    project_data: Dict[str, Any],
    inclusion_options: Dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int]
) -> bytes:
    """
    Hängt Produktdatenblätter und Firmendokumente an die Haupt-PDF an.
    
    Diese Funktion:
    1. Sammelt alle Produkt-IDs aus project_data
    2. Lädt Produktinformationen aus der Datenbank
    3. Validiert und sammelt Datenblatt-Pfade
    4. Lädt Firmendokumente basierend auf company_document_ids_to_include
    5. Führt alle PDFs zusammen
    6. Behandelt Fehler graceful (PDF wird ohne fehlende Dokumente erstellt)
    
    Args:
        main_pdf_bytes: Bytes der Haupt-PDF
        project_data: Projekt-Daten mit pv_details
        inclusion_options: Optionen für Dokumenten-Einbindung
        get_product_by_id_func: Funktion zum Laden von Produktinformationen
        db_list_company_documents_func: Funktion zum Laden von Firmendokumenten
        active_company_id: ID der aktiven Firma
        
    Returns:
        Bytes der finalen PDF mit angehängten Dokumenten
        
    Raises:
        Exception: Bei kritischen Fehlern (wird geloggt, aber nicht propagiert)
    """
    logging.info("=== Starte Anhängen von Datenblättern und Dokumenten ===")
    
    try:
        # ====================================================================
        # SCHRITT 1: Produkt-IDs sammeln
        # ====================================================================
        pv_details = project_data.get('pv_details', {})
        product_ids = []
        product_names = {}  # Für Logging
        
        # Hauptkomponenten sammeln
        main_components = {
            'selected_module_id': 'PV-Modul',
            'selected_inverter_id': 'Wechselrichter',
            'selected_storage_id': 'Speicher',
        }
        
        for key, component_name in main_components.items():
            comp_id = pv_details.get(key)
            if comp_id:
                product_ids.append(comp_id)
                product_names[comp_id] = component_name
                logging.info(f"Hauptkomponente gefunden: {component_name} (ID: {comp_id})")
        
        # Zubehör sammeln (nur wenn include_additional_components True ist)
        if pv_details.get('include_additional_components', True):
            accessory_components = {
                'selected_wallbox_id': 'Wallbox',
                'selected_ems_id': 'EMS',
                'selected_optimizer_id': 'Optimizer',
                'selected_carport_id': 'Carport',
                'selected_notstrom_id': 'Notstrom',
                'selected_tierabwehr_id': 'Tierabwehr',
            }
            
            for key, component_name in accessory_components.items():
                comp_id = pv_details.get(key)
                if comp_id:
                    product_ids.append(comp_id)
                    product_names[comp_id] = component_name
                    logging.info(f"Zubehör gefunden: {component_name} (ID: {comp_id})")
        else:
            logging.info("Zubehör-Komponenten werden übersprungen (include_additional_components=False)")
        
        logging.info(f"Gesamt {len(product_ids)} Produkt-IDs gesammelt")
        
        # ====================================================================
        # SCHRITT 2: Datenblatt-Pfade sammeln
        # ====================================================================
        paths_to_append = []
        datasheet_info = []  # Für Logging
        
        for prod_id in product_ids:
            try:
                # Produktinformationen aus Datenbank laden
                product_info = get_product_by_id_func(prod_id)
                
                if not product_info:
                    logging.warning(f"Keine Produktinformationen für ID {prod_id} ({product_names.get(prod_id, 'Unbekannt')}) gefunden")
                    continue
                
                # Datenblatt-Pfad extrahieren
                datasheet_path = product_info.get("datasheet_link_db_path")
                
                if not datasheet_path:
                    logging.warning(f"Kein Datenblatt-Pfad für Produkt {prod_id} ({product_names.get(prod_id, 'Unbekannt')}) vorhanden")
                    continue
                
                # Vollständigen Pfad erstellen
                full_path = os.path.join(
                    PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN,
                    datasheet_path
                )
                
                # Pfad validieren
                if not os.path.exists(full_path):
                    logging.warning(f"Datenblatt-Datei nicht gefunden: {full_path}")
                    continue
                
                if not os.path.isfile(full_path):
                    logging.warning(f"Datenblatt-Pfad ist keine Datei: {full_path}")
                    continue
                
                # Dateigröße prüfen
                file_size = os.path.getsize(full_path)
                if file_size == 0:
                    logging.warning(f"Datenblatt-Datei ist leer: {full_path}")
                    continue
                
                # Dateiendung prüfen
                if not full_path.lower().endswith('.pdf'):
                    logging.warning(f"Datenblatt ist kein PDF: {full_path}")
                    continue
                
                # Pfad zur Liste hinzufügen
                paths_to_append.append(full_path)
                datasheet_info.append({
                    'product_id': prod_id,
                    'product_name': product_names.get(prod_id, 'Unbekannt'),
                    'path': full_path,
                    'size_kb': file_size / 1024
                })
                logging.info(f"Datenblatt hinzugefügt: {product_names.get(prod_id, 'Unbekannt')} ({file_size / 1024:.2f} KB)")
                
            except Exception as e:
                logging.error(f"Fehler beim Verarbeiten von Produkt {prod_id}: {e}")
                continue
        
        logging.info(f"Gesamt {len(paths_to_append)} Datenblätter gefunden")
        
        # ====================================================================
        # SCHRITT 3: Firmendokumente sammeln
        # ====================================================================
        doc_ids = inclusion_options.get("company_document_ids_to_include", [])
        
        if doc_ids and active_company_id:
            logging.info(f"Lade Firmendokumente für Firma {active_company_id}")
            
            try:
                # Alle Firmendokumente laden
                all_docs = db_list_company_documents_func(active_company_id, None)
                
                if not all_docs:
                    logging.warning(f"Keine Firmendokumente für Firma {active_company_id} gefunden")
                else:
                    logging.info(f"{len(all_docs)} Firmendokumente verfügbar")
                    
                    # Nur ausgewählte Dokumente filtern
                    for doc_info in all_docs:
                        doc_id = doc_info.get('id')
                        
                        if doc_id not in doc_ids:
                            continue
                        
                        relative_path = doc_info.get("relative_db_path")
                        doc_name = doc_info.get("name", "Unbekannt")
                        
                        if not relative_path:
                            logging.warning(f"Kein Pfad für Firmendokument {doc_id} ({doc_name})")
                            continue
                        
                        # Vollständigen Pfad erstellen
                        full_path = os.path.join(
                            COMPANY_DOCS_BASE_DIR_PDF_GEN,
                            relative_path
                        )
                        
                        # Pfad validieren
                        if not os.path.exists(full_path):
                            logging.warning(f"Firmendokument nicht gefunden: {full_path}")
                            continue
                        
                        if not os.path.isfile(full_path):
                            logging.warning(f"Firmendokument-Pfad ist keine Datei: {full_path}")
                            continue
                        
                        # Dateigröße prüfen
                        file_size = os.path.getsize(full_path)
                        if file_size == 0:
                            logging.warning(f"Firmendokument ist leer: {full_path}")
                            continue
                        
                        # Dateiendung prüfen
                        if not full_path.lower().endswith('.pdf'):
                            logging.warning(f"Firmendokument ist kein PDF: {full_path}")
                            continue
                        
                        # Pfad zur Liste hinzufügen
                        paths_to_append.append(full_path)
                        logging.info(f"Firmendokument hinzugefügt: {doc_name} ({file_size / 1024:.2f} KB)")
                        
            except Exception as e:
                logging.error(f"Fehler beim Laden von Firmendokumenten: {e}")
        else:
            if not doc_ids:
                logging.info("Keine Firmendokumente ausgewählt")
            if not active_company_id:
                logging.info("Keine aktive Firma vorhanden")
        
        # ====================================================================
        # SCHRITT 4: PDFs zusammenführen
        # ====================================================================
        if not paths_to_append:
            logging.info("Keine Dokumente zum Anhängen gefunden, gebe Haupt-PDF zurück")
            return main_pdf_bytes
        
        logging.info(f"Starte Zusammenführung von {len(paths_to_append)} Dokumenten")
        
        # PDF Writer erstellen
        pdf_writer = PdfWriter()
        
        # Haupt-PDF hinzufügen
        try:
            main_reader = PdfReader(io.BytesIO(main_pdf_bytes))
            main_page_count = len(main_reader.pages)
            logging.info(f"Haupt-PDF hat {main_page_count} Seiten")
            
            for page_num, page in enumerate(main_reader.pages, 1):
                pdf_writer.add_page(page)
                
        except Exception as e:
            logging.error(f"Fehler beim Lesen der Haupt-PDF: {e}")
            raise
        
        # Dokumente anhängen
        total_added_pages = 0
        
        for doc_path in paths_to_append:
            try:
                reader = PdfReader(doc_path)
                page_count = len(reader.pages)
                
                logging.info(f"Füge Dokument hinzu: {os.path.basename(doc_path)} ({page_count} Seiten)")
                
                for page_num, page in enumerate(reader.pages, 1):
                    pdf_writer.add_page(page)
                    total_added_pages += 1
                    
            except Exception as e:
                logging.error(f"Fehler beim Anhängen von {doc_path}: {e}")
                continue
        
        logging.info(f"Gesamt {total_added_pages} Seiten angehängt")
        
        # Finale PDF schreiben
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        final_pdf_bytes = output.getvalue()
        
        final_size_mb = len(final_pdf_bytes) / (1024 * 1024)
        logging.info(f"Finale PDF-Größe: {final_size_mb:.2f} MB")
        logging.info("=== Anhängen von Datenblättern und Dokumenten abgeschlossen ===")
        
        return final_pdf_bytes
        
    except Exception as e:
        logging.error(f"Kritischer Fehler beim Anhängen von Dokumenten: {e}")
        logging.info("Gebe Haupt-PDF ohne angehängte Dokumente zurück")
        return main_pdf_bytes
```

**Integration in generate_offer_pdf()**:

```python
def generate_offer_pdf(
    project_data: Dict[str, Any],
    inclusion_options: Dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int],
    **kwargs
) -> bytes:
    """Generiert die Angebots-PDF."""
    
    # ... bestehender Code für PDF-Generierung ...
    
    # PDF als Bytes speichern
    main_pdf_buffer = io.BytesIO()
    doc.build(story, canvasmaker=PageNumCanvas)
    main_pdf_buffer.seek(0)
    main_pdf_bytes = main_pdf_buffer.getvalue()
    
    # Datenblätter und Dokumente anhängen (falls gewünscht)
    if inclusion_options.get('include_all_documents', False):
        final_pdf_bytes = _append_datasheets_and_documents(
            main_pdf_bytes=main_pdf_bytes,
            project_data=project_data,
            inclusion_options=inclusion_options,
            get_product_by_id_func=get_product_by_id_func,
            db_list_company_documents_func=db_list_company_documents_func,
            active_company_id=active_company_id
        )
    else:
        final_pdf_bytes = main_pdf_bytes
    
    return final_pdf_bytes
```

**Implementierungs-Checkliste**:

1. ✓ Funktion `_append_datasheets_and_documents()` implementieren
2. ✓ Produkt-IDs-Sammlung für Hauptkomponenten
3. ✓ Produkt-IDs-Sammlung für Zubehör
4. ✓ Datenbank-Abfragen für Produktinformationen
5. ✓ Pfad-Validierung für Datenblätter
6. ✓ Firmendokumente-Laden und -Validierung
7. ✓ PDF-Zusammenführung mit pypdf
8. ✓ Umfassende Fehlerbehandlung
9. ✓ Detailliertes Logging
10. ✓ Integration in generate_offer_pdf()
11. ✓ Unit Tests für alle Schritte
12. ✓ Integration Tests mit echten PDFs

### 6. Firmendokumente einbinden

**Datei**: pdf_generator.py

**Technische Spezifikation**:

Firmendokumente sind bereits in Komponente 5 (_append_datasheets_and_documents) integriert. Diese Sektion beschreibt die spezifischen Details für Firmendokumente.

**Firmendokumente-Typen**:

- Vollmachten
- AGBs (Allgemeine Geschäftsbedingungen)
- Zertifikate
- Garantie-Dokumente
- Versicherungsnachweise
- Weitere firmenspe zifische Dokumente

**Implementierung** (bereits in Komponente 5 integriert, hier Details):

```python
# SCHRITT 3 aus _append_datasheets_and_documents(): Firmendokumente sammeln

# Firmendokumente-Konfiguration
COMPANY_DOCUMENT_TYPES = {
    'power_of_attorney': 'Vollmacht',
    'terms_and_conditions': 'AGB',
    'certificates': 'Zertifikate',
    'warranty': 'Garantie',
    'insurance': 'Versicherung',
    'other': 'Sonstige'
}

def _load_company_documents(
    active_company_id: int,
    doc_ids: List[int],
    db_list_company_documents_func: Callable
) -> List[str]:
    """
    Lädt Firmendokumente aus der Datenbank.
    
    Args:
        active_company_id: ID der aktiven Firma
        doc_ids: Liste der Dokument-IDs zum Laden
        db_list_company_documents_func: Funktion zum Laden von Dokumenten
        
    Returns:
        Liste der vollständigen Pfade zu den Dokumenten
    """
    document_paths = []
    
    try:
        # Alle Firmendokumente laden
        all_docs = db_list_company_documents_func(active_company_id, None)
        
        if not all_docs:
            logging.warning(f"Keine Firmendokumente für Firma {active_company_id} gefunden")
            return document_paths
        
        logging.info(f"{len(all_docs)} Firmendokumente verfügbar für Firma {active_company_id}")
        
        # Dokumente nach Typ gruppieren (für bessere Reihenfolge)
        docs_by_type = {}
        for doc_info in all_docs:
            doc_id = doc_info.get('id')
            if doc_id not in doc_ids:
                continue
            
            doc_type = doc_info.get('document_type', 'other')
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = []
            docs_by_type[doc_type].append(doc_info)
        
        # Dokumente in definierter Reihenfolge verarbeiten
        type_order = [
            'power_of_attorney',
            'terms_and_conditions',
            'certificates',
            'warranty',
            'insurance',
            'other'
        ]
        
        for doc_type in type_order:
            if doc_type not in docs_by_type:
                continue
            
            logging.info(f"Verarbeite {len(docs_by_type[doc_type])} Dokumente vom Typ '{COMPANY_DOCUMENT_TYPES.get(doc_type, doc_type)}'")
            
            for doc_info in docs_by_type[doc_type]:
                doc_id = doc_info.get('id')
                doc_name = doc_info.get('name', 'Unbekannt')
                relative_path = doc_info.get('relative_db_path')
                
                if not relative_path:
                    logging.warning(f"Kein Pfad für Firmendokument {doc_id} ({doc_name})")
                    continue
                
                # Vollständigen Pfad erstellen
                full_path = os.path.join(
                    COMPANY_DOCS_BASE_DIR_PDF_GEN,
                    relative_path
                )
                
                # Pfad validieren
                if not os.path.exists(full_path):
                    logging.warning(f"Firmendokument nicht gefunden: {full_path}")
                    continue
                
                if not os.path.isfile(full_path):
                    logging.warning(f"Firmendokument-Pfad ist keine Datei: {full_path}")
                    continue
                
                # Dateigröße prüfen
                file_size = os.path.getsize(full_path)
                if file_size == 0:
                    logging.warning(f"Firmendokument ist leer: {full_path}")
                    continue
                
                # Dateiendung prüfen
                if not full_path.lower().endswith('.pdf'):
                    logging.warning(f"Firmendokument ist kein PDF: {full_path}")
                    # Versuche Konvertierung (falls implementiert)
                    converted_path = _try_convert_to_pdf(full_path)
                    if converted_path:
                        full_path = converted_path
                    else:
                        logging.warning(f"Konvertierung fehlgeschlagen, überspringe: {full_path}")
                        continue
                
                # PDF-Integrität prüfen
                if not _validate_pdf_integrity(full_path):
                    logging.warning(f"PDF-Integrität-Prüfung fehlgeschlagen: {full_path}")
                    continue
                
                # Pfad zur Liste hinzufügen
                document_paths.append(full_path)
                logging.info(f"Firmendokument hinzugefügt: {doc_name} ({COMPANY_DOCUMENT_TYPES.get(doc_type, doc_type)}, {file_size / 1024:.2f} KB)")
        
        logging.info(f"Gesamt {len(document_paths)} Firmendokumente geladen")
        return document_paths
        
    except Exception as e:
        logging.error(f"Fehler beim Laden von Firmendokumenten: {e}")
        return document_paths

def _validate_pdf_integrity(pdf_path: str) -> bool:
    """
    Validiert die Integrität einer PDF-Datei.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        
    Returns:
        True wenn PDF valide, sonst False
    """
    try:
        reader = PdfReader(pdf_path)
        # Versuche erste Seite zu lesen
        if len(reader.pages) > 0:
            _ = reader.pages[0]
        return True
    except Exception as e:
        logging.error(f"PDF-Validierung fehlgeschlagen für {pdf_path}: {e}")
        return False

def _try_convert_to_pdf(file_path: str) -> Optional[str]:
    """
    Versucht eine Datei in PDF zu konvertieren.
    
    Args:
        file_path: Pfad zur Quelldatei
        
    Returns:
        Pfad zur konvertierten PDF oder None bei Fehler
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Unterstützte Konvertierungen
        if file_ext in ['.docx', '.doc']:
            # Word zu PDF (benötigt python-docx und reportlab)
            return _convert_word_to_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            # Bild zu PDF (benötigt PIL und reportlab)
            return _convert_image_to_pdf(file_path)
        else:
            logging.warning(f"Keine Konvertierung verfügbar für {file_ext}")
            return None
            
    except Exception as e:
        logging.error(f"Fehler bei Konvertierung von {file_path}: {e}")
        return None

def _convert_word_to_pdf(word_path: str) -> Optional[str]:
    """Konvertiert Word-Dokument zu PDF."""
    # Implementierung würde hier erfolgen
    # Für jetzt: Nicht implementiert
    logging.warning("Word zu PDF Konvertierung nicht implementiert")
    return None

def _convert_image_to_pdf(image_path: str) -> Optional[str]:
    """Konvertiert Bild zu PDF."""
    try:
        from PIL import Image
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        # Temporäre PDF erstellen
        temp_pdf_path = image_path + '.pdf'
        
        # Bild laden
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # PDF erstellen
        c = canvas.Canvas(temp_pdf_path, pagesize=A4)
        page_width, page_height = A4
        
        # Bild skalieren um auf Seite zu passen
        scale = min(page_width / img_width, page_height / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        
        # Bild zentrieren
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2
        
        c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
        c.save()
        
        logging.info(f"Bild erfolgreich zu PDF konvertiert: {temp_pdf_path}")
        return temp_pdf_path
        
    except Exception as e:
        logging.error(f"Fehler bei Bild zu PDF Konvertierung: {e}")
        return None
```

**UI-Integration für Firmendokumente-Auswahl**:

```python
# In pdf_ui.py

def render_company_documents_selection(
    active_company_id: int,
    db_list_company_documents_func: Callable
) -> List[int]:
    """
    Rendert die UI für Firmendokumente-Auswahl.
    
    Args:
        active_company_id: ID der aktiven Firma
        db_list_company_documents_func: Funktion zum Laden von Dokumenten
        
    Returns:
        Liste der ausgewählten Dokument-IDs
    """
    st.subheader("📄 Firmendokumente für PDF")
    
    if not active_company_id:
        st.warning("Keine aktive Firma ausgewählt")
        return []
    
    try:
        # Alle Firmendokumente laden
        all_docs = db_list_company_documents_func(active_company_id, None)
        
        if not all_docs:
            st.info("Keine Firmendokumente verfügbar")
            return []
        
        # Nach Typ gruppieren
        docs_by_type = {}
        for doc in all_docs:
            doc_type = doc.get('document_type', 'other')
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = []
            docs_by_type[doc_type].append(doc)
        
        # Auswahl-UI
        selected_doc_ids = []
        
        for doc_type, docs in docs_by_type.items():
            type_name = COMPANY_DOCUMENT_TYPES.get(doc_type, doc_type)
            
            with st.expander(f"📁 {type_name} ({len(docs)})", expanded=True):
                for doc in docs:
                    doc_id = doc.get('id')
                    doc_name = doc.get('name', 'Unbekannt')
                    doc_size = doc.get('file_size', 0)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.checkbox(
                            f"{doc_name}",
                            key=f"company_doc_{doc_id}",
                            value=True  # Standardmäßig ausgewählt
                        ):
                            selected_doc_ids.append(doc_id)
                    
                    with col2:
                        st.caption(f"{doc_size / 1024:.1f} KB")
        
        # Statistik
        st.info(f"✅ {len(selected_doc_ids)} von {len(all_docs)} Dokumenten ausgewählt")
        
        return selected_doc_ids
        
    except Exception as e:
        st.error(f"Fehler beim Laden der Firmendokumente: {e}")
        return []
```

**Implementierungs-Checkliste**:

1. ✓ Firmendokumente-Typen definieren
2. ✓ Funktion `_load_company_documents()` implementieren
3. ✓ Dokumente nach Typ gruppieren und sortieren
4. ✓ PDF-Integritäts-Prüfung implementieren
5. ✓ Konvertierungs-Funktionen für Nicht-PDFs
6. ✓ UI für Firmendokumente-Auswahl
7. ✓ Integration in _append_datasheets_and_documents()
8. ✓ Fehlerbehandlung für alle Schritte
9. ✓ Logging für alle Operationen
10. ✓ Unit Tests für alle Funktionen

### 7. Seitenschutz für erweiterte Seiten

**Datei**: pdf_generator.py

**Implementierung**:

```python
# KeepTogether für Diagramm + Beschreibung
from reportlab.platypus import KeepTogether

# Diagramm und Beschreibung zusammenhalten
chart_flowables = []
chart_flowables.append(Paragraph(f"<b>{chart_title}</b>", styles['Heading2']))
chart_flowables.append(Image(chart_bytes, width=width, height=height))
chart_flowables.append(Paragraph(description, styles['Normal']))

# Als KeepTogether-Gruppe hinzufügen
story.append(KeepTogether(chart_flowables))

# Für Seiten 1-8: Kein KeepTogether
# Für Seiten 9+: KeepTogether für alle Inhalte
```

### 8. Kopf- und Fußzeilen für erweiterte Seiten

**Datei**: pdf_generator.py

**Implementierung** (aus repair_pdf/pdf_generator.py, Zeile 1207):

```python
def page_layout_handler(
    canvas_obj: canvas.Canvas,
    doc_template: SimpleDocTemplate,
    texts_ref: Dict[str, str],
    company_info_ref: Dict,
    company_logo_base64_ref: Optional[str],
    offer_number_ref: str,
    page_width_ref: float,
    page_height_ref: float,
    margin_left_ref: float,
    margin_right_ref: float,
    margin_top_ref: float,
    margin_bottom_ref: float,
    doc_width_ref: float,
    doc_height_ref: float,
    include_customer_name_ref: bool,
    customer_name_ref: str,
    include_header_logo_ref: bool
):
    """Handler für Kopf- und Fußzeilen auf jeder Seite."""
    
    page_num = canvas_obj.getPageNumber()
    canvas_obj.saveState()
    
    # Für Seiten 9+ (erweiterte Seiten)
    if page_num >= 9:
        # Dreieck rechts oben
        triangle_size = 20
        canvas_obj.setFillColorRGB(0, 0.33, 0.64)  # Blau
        canvas_obj.beginPath()
        canvas_obj.moveTo(page_width_ref - margin_right_ref, page_height_ref - margin_top_ref)
        canvas_obj.lineTo(page_width_ref - margin_right_ref - triangle_size, page_height_ref - margin_top_ref)
        canvas_obj.lineTo(page_width_ref - margin_right_ref, page_height_ref - margin_top_ref - triangle_size)
        canvas_obj.closePath()
        canvas_obj.fill()
        
        # Logo links oben
        if include_header_logo_ref and company_logo_base64_ref:
            logo_width = 40
            logo_height = 20
            logo_x = margin_left_ref
            logo_y = page_height_ref - margin_top_ref - logo_height
            
            logo_img = ImageReader(io.BytesIO(base64.b64decode(company_logo_base64_ref)))
            canvas_obj.drawImage(logo_img, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')
        
        # Blauer Balken in Fußzeile
        footer_bar_height = 5
        canvas_obj.setFillColorRGB(0, 0.33, 0.64)
        canvas_obj.rect(margin_left_ref, margin_bottom_ref - footer_bar_height, 
                       doc_width_ref, footer_bar_height, fill=1, stroke=0)
        
        # Fußzeilen-Text
        footer_y = margin_bottom_ref - 15
        
        # Links: Kundenname
        if include_customer_name_ref and customer_name_ref:
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColorRGB(0, 0, 0)
            canvas_obj.drawString(margin_left_ref, footer_y, customer_name_ref)
        
        # Mitte: Angebot Datum
        offer_date = datetime.now().strftime("%d.%m.%Y")
        canvas_obj.drawCentredString(page_width_ref / 2, footer_y, f"Angebot {offer_date}")
        
        # Rechts: Seitenzahl
        total_pages = doc_template.page  # Wird dynamisch aktualisiert
        canvas_obj.drawRightString(page_width_ref - margin_right_ref, footer_y, 
                                  f"Seite {page_num} von {total_pages}")
    
    canvas_obj.restoreState()

# In generate_offer_pdf():
doc.build(story, canvasmaker=lambda *args, **kwargs_c: PageNumCanvas(
    *args, 
    onPage_callback=page_layout_handler, 
    callback_kwargs=layout_callback_kwargs_build, 
    **kwargs_c
))
```

### 9. Finanzierungsinformationen priorisieren

**Datei**: pdf_generator.py

**Implementierung**:

```python
# In generate_offer_pdf(), nach Seite 8:

# Finanzierungsinformationen ab Seite 9
if inclusion_options.get("include_financing_details", True):
    story.append(PageBreak())
    
    # Überschrift
    story.append(Paragraph("<b>Finanzierungsinformationen</b>", styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    # Finanzierungsdaten aus solar_calculator
    final_end_preis = project_data.get('pv_details', {}).get('final_end_preis', 0)
    
    # Kreditberechnung
    from financial_tools import calculate_annuity
    loan_data = calculate_annuity(
        principal=final_end_preis,
        interest_rate=4.0,  # Aus global_constants
        years=15
    )
    
    # Kredit-Tabelle
    story.append(Paragraph("<b>Kreditfinanzierung</b>", styles['Heading2']))
    credit_table_data = [
        ["Kreditbetrag", f"{final_end_preis:,.2f} €"],
        ["Zinssatz", "4,0% p.a."],
        ["Laufzeit", "15 Jahre"],
        ["Monatliche Rate", f"{loan_data['monthly_payment']:,.2f} €"],
        ["Gesamtkosten", f"{loan_data['total_cost']:,.2f} €"]
    ]
    credit_table = Table(credit_table_data, colWidths=[8*cm, 6*cm])
    credit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR_HEX)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(credit_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Leasing-Berechnung
    from financial_tools import calculate_leasing_costs
    leasing_data = calculate_leasing_costs(
        asset_value=final_end_preis,
        residual_value_percent=10,
        interest_rate=3.5,
        years=10
    )
    
    # Leasing-Tabelle
    story.append(Paragraph("<b>Leasingfinanzierung</b>", styles['Heading2']))
    leasing_table_data = [
        ["Leasingbetrag", f"{final_end_preis:,.2f} €"],
        ["Zinssatz", "3,5% p.a."],
        ["Laufzeit", "10 Jahre"],
        ["Monatliche Rate", f"{leasing_data['monthly_payment']:,.2f} €"],
        ["Restwert", f"{leasing_data['residual_value']:,.2f} €"]
    ]
    leasing_table = Table(leasing_table_data, colWidths=[8*cm, 6*cm])
    leasing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR_HEX)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(leasing_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Amortisationsplan
    story.append(Paragraph("<b>Amortisationsplan</b>", styles['Heading2']))
    # ... Amortisationsplan-Tabelle mit jährlichen Werten
```

### 10. Logik aus repair_pdf extrahieren

**Dateien**: Alle relevanten Dateien

**Extraktionsstrategie**:

1. **pdf_generator.py**:
   - Zeilen 103-428: page_layout_handler und _header_footer
   - Zeilen 4930-5050: _append_datasheets_and_documents
   - Zeilen 2660-2663: PageNumCanvas mit onPage_callback

2. **calculations.py**:
   - Alle Chart-Generierungsfunktionen mit transparenten Hintergründen
   - 3D zu 2D Konvertierungen

3. **analysis.py**:
   - Zeilen 2006-2010: Transparente Hintergründe für Plotly
   - Alle Chart-Generierungsfunktionen

4. **pdf_ui.py**:
   - Zeilen 262-265: chart_key_to_friendly_name_map
   - Diagrammauswahl-UI

5. **pdf_styles.py**:
   - Zeilen 373-376: Transparente Hintergründe beim Speichern

## Data Models

### inclusion_options Dictionary

```python
{
    "include_company_logo": bool,
    "include_product_images": bool,
    "include_all_documents": bool,
    "company_document_ids_to_include": List[int],
    "selected_charts_for_pdf": List[str],
    "include_optional_component_details": bool,
    "append_additional_pages_after_main6": bool,
    "include_financing_details": bool,  # NEU
    "chart_layout": str  # "single", "grid", etc.
}
```

### Chart Configuration Dictionary

```python
chart_config = {
    'chart_key': {
        'title': str,
        'description': str,
        'type': str,  # 'bar', 'line', 'pie', 'donut'
        'values': Dict[str, Any],
        'available': bool
    }
}
```

## Error Handling

### Fehlerbehandlungs-Strategie

1. **Graceful Degradation**: Bei Fehlern wird die PDF ohne problematische Inhalte erstellt
2. **Logging**: Alle Fehler werden detailliert geloggt
3. **Fallbacks**: Für fehlende Diagramme werden Platzhalter angezeigt
4. **Validation**: Eingaben werden vor der Verarbeitung validiert

## Testing Strategy

### Unit Tests

1. **Transparente Hintergründe**: Verifizieren, dass alle Diagramme transparente Hintergründe haben
2. **2D Konvertierung**: Verifizieren, dass keine 3D-Diagramme mehr existieren
3. **Diagrammauswahl**: Verifizieren, dass nur ausgewählte Diagramme in PDF erscheinen
4. **Produktdatenblätter**: Verifizieren, dass alle Datenblätter angehängt werden
5. **Firmendokumente**: Verifizieren, dass firmenspe zifische Dokumente angehängt werden

### Integration Tests

1. **Vollständige PDF-Generierung**: Test mit allen Features aktiviert
2. **Kopf-/Fußzeilen**: Verifizieren auf Seiten 9+
3. **Finanzierungsinformationen**: Verifizieren ab Seite 9
4. **Seitenschutz**: Verifizieren, dass Diagramme + Beschreibungen zusammenbleiben

### Manuelle Tests

1. **Visuelle Inspektion**: PDF öffnen und alle Diagramme prüfen
2. **Seitenzahlen**: Verifizieren, dass Seitenzahlen korrekt sind
3. **Logos**: Verifizieren, dass Logos korrekt positioniert sind
4. **Finanzierungsdaten**: Verifizieren, dass Berechnungen korrekt sind

## Implementation Notes

### Kritische Änderungen

1. **Alle Chart-Generierungsfunktionen**: Transparente Hintergründe hinzufügen
2. **Alle 3D-Diagramme**: In 2D konvertieren
3. **pdf_ui.py**: Vollständige Diagrammauswahl-UI implementieren
4. **pdf_generator.py**: page_layout_handler für Seiten 9+ implementieren
5. **pdf_generator.py**: Finanzierungsinformationen ab Seite 9 einfügen

### Rückwärtskompatibilität

- Bestehende PDFs funktionieren weiterhin
- Neue Features sind optional
- Standardwerte für alle neuen Optionen

### Performance-Überlegungen

- Diagramm-Generierung kann zeitaufwändig sein
- Caching für häufig verwendete Diagramme
- Lazy Loading für Datenblätter und Dokumente

## Deployment Considerations

### Abhängigkeiten

Alle erforderlichen Python-Pakete:

```python
matplotlib>=3.5.0
plotly>=5.0.0
reportlab>=3.6.0
pypdf>=3.0.0
Pillow>=9.0.0
numpy>=1.21.0
streamlit>=1.20.0
```

### Konfiguration

Umgebungsvariablen und Konstanten:

```python
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = "path/to/product/datasheets"
COMPANY_DOCS_BASE_DIR_PDF_GEN = "path/to/company/documents"
DEFAULT_DPI = 300
DEFAULT_CHART_WIDTH = 14  # cm
DEFAULT_CHART_HEIGHT = 10  # cm
```

### Migration

Schritte zur Migration von altem zu neuem System:

1. Backup aller bestehenden PDF-Generierungsfunktionen
2. Schrittweise Integration der neuen Features
3. Parallelbetrieb für Validierung
4. Vollständige Umstellung nach erfolgreichen Tests

## Security Considerations

### Datenschutz

- Kundendaten werden nur temporär im Speicher gehalten
- Keine Persistierung sensibler Daten in Logs
- PDF-Verschlüsselung optional verfügbar

### Dateizugriff

- Validierung aller Dateipfade gegen Path Traversal
- Nur autorisierte Dokumente werden angehängt
- Firmenspezifische Dokumente sind isoliert

### Input Validation

- Alle Benutzereingaben werden validiert
- SQL-Injection-Schutz bei Datenbankabfragen
- XSS-Schutz bei dynamischen Inhalten

## Monitoring and Logging

### Logging-Strategie

```python
import logging

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_generation.log'),
        logging.StreamHandler()
    ]
)

# Kritische Ereignisse
logger.info("PDF-Generierung gestartet")
logger.warning("Diagramm nicht verfügbar")
logger.error("Fehler beim Anhängen von Datenblatt")
```

### Metriken

Zu überwachende Metriken:

- PDF-Generierungszeit
- Anzahl generierter Diagramme
- Fehlerrate bei Datenblatt-Anhängen
- Speicherverbrauch während Generierung

## Maintenance and Support

### Dokumentation

- Inline-Kommentare für komplexe Logik
- Docstrings für alle öffentlichen Funktionen
- README mit Beispielen und Troubleshooting

### Versionierung

- Semantic Versioning (MAJOR.MINOR.PATCH)
- Changelog für alle Änderungen
- Git-Tags für Releases

### Support-Prozess

1. Bug-Reports über Issue-Tracker
2. Feature-Requests über Diskussionsforum
3. Hotfixes für kritische Probleme
4. Regelmäßige Updates und Patches

## Future Enhancements

### Geplante Features

1. **Interaktive PDFs**: Klickbare Diagramme mit Drill-Down
2. **Multi-Language Support**: Automatische Übersetzung
3. **Template-System**: Anpassbare PDF-Layouts
4. **Cloud-Integration**: Direktes Speichern in Cloud-Storage
5. **AI-Optimierung**: Automatische Diagrammauswahl basierend auf Daten

### Technische Verbesserungen

1. **Async PDF-Generierung**: Nicht-blockierende Verarbeitung
2. **Caching-Layer**: Redis für häufig verwendete Diagramme
3. **Microservices**: Separate Services für Diagramm-Generierung
4. **API-First**: RESTful API für PDF-Generierung
5. **Containerisierung**: Docker für einfaches Deployment

## Conclusion

Dieses Design-Dokument beschreibt eine umfassende, robuste und vollständige Lösung für alle 10 kritischen Verbesserungsbereiche des erweiterten PDF-Ausgabesystems. Die Implementierung basiert auf bewährten Praktiken aus dem `repair_pdf` Ordner und erweitert diese mit zusätzlicher Fehlerbehandlung, Testbarkeit und Wartbarkeit.

### Erfolgs-Kriterien

Die Implementierung gilt als erfolgreich, wenn:

1. ✓ Alle Diagramme transparente Hintergründe haben
2. ✓ Keine 3D-Diagramme mehr existieren
3. ✓ Diagrammauswahl in UI vollständig funktioniert
4. ✓ Alle Produktdatenblätter korrekt angehängt werden
5. ✓ Alle Firmendokumente korrekt angehängt werden
6. ✓ Seitenschutz für Seiten 9+ funktioniert
7. ✓ Kopf-/Fußzeilen auf Seiten 9+ korrekt sind
8. ✓ Finanzierungsinformationen ab Seite 9 vollständig sind
9. ✓ Alle repair_pdf Logiken integriert sind
10. ✓ Alle Tests erfolgreich durchlaufen

### Nächste Schritte

Nach Genehmigung dieses Designs:

1. Erstellen der detaillierten Task-Liste
2. Priorisierung der Tasks
3. Implementierung in iterativen Sprints
4. Kontinuierliche Tests und Validierung
5. Deployment und Monitoring
