"""
shadcn/ui MetricCard-Komponente für Streamlit

Diese Komponente bietet moderne Metric-Cards für KPIs und wichtige Kennzahlen.
"""

from typing import Optional, Literal, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class MetricCard(ShadcnComponent):
    """
    shadcn/ui MetricCard-Komponente
    
    Eine flexible MetricCard-Komponente für die Anzeige von KPIs und Metriken.
    Unterstützt Trend-Indikatoren, verschiedene Größen und animierte Wert-Änderungen.
    
    Features:
    - Wert, Label und optionale Beschreibung
    - Trend-Indikatoren mit Pfeilen und Farben
    - Verschiedene Größen (small, medium, large)
    - Optionale Icons
    - Animierte Wert-Änderungen
    - Responsive Design
    
    Example:
        ```python
        from components import MetricCard
        
        metric = MetricCard()
        metric.render(
            label="Umsatz",
            value="€45,231",
            trend=12.5,
            trend_label="+12.5% vs. letzter Monat",
            icon="💰",
            size="large"
        )
        ```
    """
    
    def render(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        trend: Optional[float] = None,
        trend_label: Optional[str] = None,
        icon: Optional[str] = None,
        size: Literal["small", "medium", "large"] = "medium",
        variant: Literal["default", "outlined", "elevated"] = "default",
        show_trend_arrow: bool = True,
        animate: bool = True,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine MetricCard-Komponente
        
        Args:
            label: Label/Bezeichnung der Metrik
            value: Wert der Metrik (als String formatiert)
            description: Optionale Beschreibung unter dem Wert
            trend: Trend-Wert in Prozent (positiv = Aufwärtstrend, negativ = Abwärtstrend)
            trend_label: Optionaler Text für den Trend (z.B. "+12.5% vs. letzter Monat")
            icon: Optionales Icon (Emoji oder Unicode)
            size: Größe der Card ('small', 'medium', 'large')
            variant: Card-Variante ('default', 'outlined', 'elevated')
            show_trend_arrow: Ob Trend-Pfeil angezeigt werden soll
            animate: Ob Wert-Änderungen animiert werden sollen
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key für die Komponente
        
        Example:
            ```python
            metric = MetricCard()
            metric.render(
                label="Neue Kunden",
                value="1,234",
                trend=8.2,
                trend_label="+8.2% vs. Vormonat",
                icon="👥",
                size="medium"
            )
            ```
        """
        # Generiere eindeutige ID
        metric_id = key or self._generate_unique_id("metric")
        
        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_fg_color = self.get_token('colors.muted_foreground', '#71717a')
        success_color = self.get_token('colors.success', '#22c55e')
        error_color = self.get_token('colors.error', '#ef4444')
        border_radius = self.get_token('borders.border_radius_lg', '0.5rem')
        shadow_sm = self.get_token('shadows.shadow_sm', '0 1px 2px 0 rgba(0, 0, 0, 0.05)')
        shadow_md = self.get_token('shadows.shadow_md', '0 4px 6px -1px rgba(0, 0, 0, 0.1)')
        shadow_lg = self.get_token('shadows.shadow_lg', '0 10px 15px -3px rgba(0, 0, 0, 0.1)')
        transition = self.get_token('animations.transition_base', '200ms cubic-bezier(0.4, 0, 0.2, 1)')
        
        # Größen-spezifische Konfiguration
        size_config = {
            'small': {
                'padding': '1rem',
                'label_size': '0.75rem',
                'value_size': '1.5rem',
                'icon_size': '1.5rem',
                'trend_size': '0.75rem',
                'description_size': '0.75rem',
                'gap': '0.5rem',
            },
            'medium': {
                'padding': '1.5rem',
                'label_size': '0.875rem',
                'value_size': '2rem',
                'icon_size': '2rem',
                'trend_size': '0.875rem',
                'description_size': '0.875rem',
                'gap': '0.75rem',
            },
            'large': {
                'padding': '2rem',
                'label_size': '1rem',
                'value_size': '2.5rem',
                'icon_size': '2.5rem',
                'trend_size': '1rem',
                'description_size': '1rem',
                'gap': '1rem',
            }
        }
        
        config = size_config.get(size, size_config['medium'])
        
        # Varianten-spezifische Styles
        variant_styles = {
            'default': f"""
                background: {bg_color};
                border: 1px solid {border_color};
                box-shadow: {shadow_sm};
            """,
            'outlined': f"""
                background: {bg_color};
                border: 2px solid {border_color};
                box-shadow: none;
            """,
            'elevated': f"""
                background: {bg_color};
                border: 1px solid {border_color};
                box-shadow: {shadow_md};
            """
        }
        
        # Trend-Farbe und Pfeil
        trend_color = muted_fg_color
        trend_arrow = ""
        if trend is not None:
            if trend > 0:
                trend_color = success_color
                trend_arrow = "↑" if show_trend_arrow else ""
            elif trend < 0:
                trend_color = error_color
                trend_arrow = "↓" if show_trend_arrow else ""
            else:
                trend_arrow = "→" if show_trend_arrow else ""
        
        # Animation
        animation_css = ""
        if animate:
            animation_css = f"""
            @keyframes fadeInUp-{metric_id} {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes countUp-{metric_id} {{
                from {{
                    opacity: 0;
                    transform: scale(0.95);
                }}
                to {{
                    opacity: 1;
                    transform: scale(1);
                }}
            }}
            
            .shadcn-metric-{metric_id} {{
                animation: fadeInUp-{metric_id} 0.5s ease-out;
            }}
            
            .shadcn-metric-value-{metric_id} {{
                animation: countUp-{metric_id} 0.3s ease-out;
            }}
            """
        
        # CSS für MetricCard
        metric_css = f"""
        <style>
        .shadcn-metric-{metric_id} {{
            {variant_styles[variant]}
            border-radius: {border_radius};
            padding: {config['padding']};
            transition: all {transition};
            color: {fg_color};
            display: flex;
            flex-direction: column;
            gap: {config['gap']};
        }}
        
        .shadcn-metric-{metric_id}:hover {{
            box-shadow: {shadow_md};
            transform: translateY(-2px);
        }}
        
        .shadcn-metric-header-{metric_id} {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
        }}
        
        .shadcn-metric-label-{metric_id} {{
            font-size: {config['label_size']};
            font-weight: 500;
            color: {muted_fg_color};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            line-height: 1.2;
            flex: 1;
        }}
        
        .shadcn-metric-icon-{metric_id} {{
            font-size: {config['icon_size']};
            line-height: 1;
            flex-shrink: 0;
        }}
        
        .shadcn-metric-value-{metric_id} {{
            font-size: {config['value_size']};
            font-weight: 700;
            color: {fg_color};
            line-height: 1.2;
            margin: 0;
        }}
        
        .shadcn-metric-description-{metric_id} {{
            font-size: {config['description_size']};
            color: {muted_fg_color};
            line-height: 1.4;
            margin: 0;
        }}
        
        .shadcn-metric-trend-{metric_id} {{
            display: flex;
            align-items: center;
            gap: 0.375rem;
            font-size: {config['trend_size']};
            font-weight: 600;
            color: {trend_color};
            line-height: 1;
        }}
        
        .shadcn-metric-trend-arrow-{metric_id} {{
            font-size: 1.2em;
            line-height: 1;
        }}
        
        .shadcn-metric-trend-label-{metric_id} {{
            font-size: 0.9em;
            font-weight: 500;
            line-height: 1;
        }}
        
        {animation_css}
        {custom_css or ''}
        </style>
        """
        
        # Injiziere CSS
        st.markdown(metric_css, unsafe_allow_html=True)
        
        # Baue HTML
        html_parts = [f'<div class="shadcn-metric-{metric_id}">']
        
        # Header (Label + Icon)
        html_parts.append(f'<div class="shadcn-metric-header-{metric_id}">')
        html_parts.append(f'<div class="shadcn-metric-label-{metric_id}">{label}</div>')
        if icon:
            html_parts.append(f'<div class="shadcn-metric-icon-{metric_id}">{icon}</div>')
        html_parts.append('</div>')
        
        # Value
        html_parts.append(f'<div class="shadcn-metric-value-{metric_id}">{value}</div>')
        
        # Description
        if description:
            html_parts.append(f'<div class="shadcn-metric-description-{metric_id}">{description}</div>')
        
        # Trend
        if trend is not None or trend_label:
            html_parts.append(f'<div class="shadcn-metric-trend-{metric_id}">')
            if trend_arrow:
                html_parts.append(f'<span class="shadcn-metric-trend-arrow-{metric_id}">{trend_arrow}</span>')
            if trend_label:
                html_parts.append(f'<span class="shadcn-metric-trend-label-{metric_id}">{trend_label}</span>')
            elif trend is not None:
                trend_text = f"{abs(trend):.1f}%"
                html_parts.append(f'<span class="shadcn-metric-trend-label-{metric_id}">{trend_text}</span>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Rendere HTML
        html = ''.join(html_parts)
        st.markdown(html, unsafe_allow_html=True)


class MetricCardGroup(ShadcnComponent):
    """
    MetricCard-Gruppe für mehrere Metriken
    
    Zeigt mehrere MetricCards in einem Grid-Layout an.
    
    Example:
        ```python
        from components import MetricCardGroup
        
        group = MetricCardGroup()
        group.render(
            metrics=[
                {
                    "label": "Umsatz",
                    "value": "€45,231",
                    "trend": 12.5,
                    "icon": "💰"
                },
                {
                    "label": "Kunden",
                    "value": "1,234",
                    "trend": -3.2,
                    "icon": "👥"
                }
            ],
            columns=2
        )
        ```
    """
    
    def render(
        self,
        metrics: list[dict],
        columns: int = 3,
        gap: Literal["sm", "md", "lg"] = "md",
        size: Literal["small", "medium", "large"] = "medium",
        variant: Literal["default", "outlined", "elevated"] = "default",
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine MetricCard-Gruppe
        
        Args:
            metrics: Liste von Metric-Konfigurationen (Dicts mit MetricCard-Parametern)
            columns: Anzahl der Spalten im Grid
            gap: Abstand zwischen Cards
            size: Größe aller Cards
            variant: Variante aller Cards
            key: Eindeutiger Key
        
        Example:
            ```python
            group = MetricCardGroup()
            group.render(
                metrics=[
                    {"label": "Umsatz", "value": "€45K", "trend": 12.5},
                    {"label": "Kunden", "value": "1.2K", "trend": -3.2}
                ],
                columns=2
            )
            ```
        """
        # Generiere eindeutige ID
        group_id = key or self._generate_unique_id("metric-group")
        
        # Gap-Werte
        gap_values = {
            'sm': '0.75rem',
            'md': '1rem',
            'lg': '1.5rem'
        }
        
        gap_value = gap_values.get(gap, gap_values['md'])
        
        # CSS für MetricCard-Gruppe
        group_css = f"""
        <style>
        .shadcn-metric-group-{group_id} {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: {gap_value};
            width: 100%;
        }}
        
        @media (min-width: 768px) {{
            .shadcn-metric-group-{group_id} {{
                grid-template-columns: repeat({columns}, 1fr);
            }}
        }}
        </style>
        """
        
        st.markdown(group_css, unsafe_allow_html=True)
        
        # Baue HTML
        st.markdown(
            f'<div class="shadcn-metric-group-{group_id}">',
            unsafe_allow_html=True
        )
        
        # Rendere alle MetricCards
        metric_component = MetricCard(theme_manager=self.theme_manager)
        for i, metric_config in enumerate(metrics):
            metric_key = metric_config.get('key', f"{group_id}_metric_{i}")
            metric_component.render(
                label=metric_config.get('label', ''),
                value=metric_config.get('value', ''),
                description=metric_config.get('description'),
                trend=metric_config.get('trend'),
                trend_label=metric_config.get('trend_label'),
                icon=metric_config.get('icon'),
                size=metric_config.get('size', size),
                variant=metric_config.get('variant', variant),
                show_trend_arrow=metric_config.get('show_trend_arrow', True),
                animate=metric_config.get('animate', True),
                custom_css=metric_config.get('custom_css'),
                key=metric_key
            )
        
        st.markdown('</div>', unsafe_allow_html=True)


def metric_card(
    label: str,
    value: str,
    description: Optional[str] = None,
    trend: Optional[float] = None,
    trend_label: Optional[str] = None,
    icon: Optional[str] = None,
    size: Literal["small", "medium", "large"] = "medium",
    variant: Literal["default", "outlined", "elevated"] = "default",
    show_trend_arrow: bool = True,
    animate: bool = True,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern einer MetricCard
    
    Args:
        Siehe MetricCard.render() für Parameter-Dokumentation
    
    Example:
        ```python
        from components.metric_card import metric_card
        
        metric_card(
            label="Umsatz",
            value="€45,231",
            trend=12.5,
            icon="💰"
        )
        ```
    """
    metric = MetricCard(theme_manager=theme_manager)
    metric.render(
        label=label,
        value=value,
        description=description,
        trend=trend,
        trend_label=trend_label,
        icon=icon,
        size=size,
        variant=variant,
        show_trend_arrow=show_trend_arrow,
        animate=animate,
        custom_css=custom_css,
        key=key
    )


def metric_card_group(
    metrics: list[dict],
    columns: int = 3,
    gap: Literal["sm", "md", "lg"] = "md",
    size: Literal["small", "medium", "large"] = "medium",
    variant: Literal["default", "outlined", "elevated"] = "default",
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern einer MetricCard-Gruppe
    
    Args:
        Siehe MetricCardGroup.render() für Parameter-Dokumentation
    
    Example:
        ```python
        from components.metric_card import metric_card_group
        
        metric_card_group(
            metrics=[
                {"label": "Umsatz", "value": "€45K", "trend": 12.5},
                {"label": "Kunden", "value": "1.2K", "trend": -3.2}
            ],
            columns=2
        )
        ```
    """
    group = MetricCardGroup(theme_manager=theme_manager)
    group.render(
        metrics=metrics,
        columns=columns,
        gap=gap,
        size=size,
        variant=variant,
        key=key
    )
