"""
Unit Tests für MetricCard-Komponente
"""

import pytest
from components.metric_card import MetricCard, MetricCardGroup
from theming import ThemeManager


@pytest.fixture
def theme_manager():
    """Fixture für ThemeManager"""
    manager = ThemeManager()
    manager.set_theme('shadcn-default')
    return manager


@pytest.fixture
def metric_card(theme_manager):
    """Fixture für MetricCard"""
    return MetricCard(theme_manager=theme_manager)


@pytest.fixture
def metric_card_group(theme_manager):
    """Fixture für MetricCardGroup"""
    return MetricCardGroup(theme_manager=theme_manager)


class TestMetricCard:
    """Tests für MetricCard-Komponente"""
    
    def test_initialization(self, metric_card):
        """Test: MetricCard kann initialisiert werden"""
        assert metric_card is not None
        assert metric_card.theme_manager is not None
    
    def test_render_basic(self, metric_card):
        """Test: Basis-Rendering funktioniert"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345"
            )
            # Wenn kein Fehler auftritt, ist der Test erfolgreich
            assert True
        except Exception as e:
            pytest.fail(f"Rendering failed: {e}")
    
    def test_render_with_trend_positive(self, metric_card):
        """Test: Rendering mit positivem Trend"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                trend=12.5
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with positive trend failed: {e}")
    
    def test_render_with_trend_negative(self, metric_card):
        """Test: Rendering mit negativem Trend"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                trend=-5.2
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with negative trend failed: {e}")
    
    def test_render_with_trend_zero(self, metric_card):
        """Test: Rendering mit Null-Trend"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                trend=0
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with zero trend failed: {e}")
    
    def test_render_with_icon(self, metric_card):
        """Test: Rendering mit Icon"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                icon=""
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with icon failed: {e}")
    
    def test_render_with_description(self, metric_card):
        """Test: Rendering mit Beschreibung"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                description="Test Beschreibung"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with description failed: {e}")
    
    def test_render_with_trend_label(self, metric_card):
        """Test: Rendering mit Trend-Label"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                trend=12.5,
                trend_label="+12.5% vs. letzter Monat"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with trend label failed: {e}")
    
    def test_render_size_small(self, metric_card):
        """Test: Rendering mit Größe 'small'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                size="small"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with size 'small' failed: {e}")
    
    def test_render_size_medium(self, metric_card):
        """Test: Rendering mit Größe 'medium'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                size="medium"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with size 'medium' failed: {e}")
    
    def test_render_size_large(self, metric_card):
        """Test: Rendering mit Größe 'large'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                size="large"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with size 'large' failed: {e}")
    
    def test_render_variant_default(self, metric_card):
        """Test: Rendering mit Variante 'default'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                variant="default"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with variant 'default' failed: {e}")
    
    def test_render_variant_outlined(self, metric_card):
        """Test: Rendering mit Variante 'outlined'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                variant="outlined"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with variant 'outlined' failed: {e}")
    
    def test_render_variant_elevated(self, metric_card):
        """Test: Rendering mit Variante 'elevated'"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                variant="elevated"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with variant 'elevated' failed: {e}")
    
    def test_render_without_trend_arrow(self, metric_card):
        """Test: Rendering ohne Trend-Pfeil"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                trend=12.5,
                show_trend_arrow=False
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering without trend arrow failed: {e}")
    
    def test_render_without_animation(self, metric_card):
        """Test: Rendering ohne Animation"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                animate=False
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering without animation failed: {e}")
    
    def test_render_with_custom_css(self, metric_card):
        """Test: Rendering mit Custom-CSS"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                custom_css=".custom { color: red; }"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with custom CSS failed: {e}")
    
    def test_render_with_all_options(self, metric_card):
        """Test: Rendering mit allen Optionen"""
        try:
            metric_card.render(
                label="Test Metrik",
                value="€12,345",
                description="Test Beschreibung",
                trend=12.5,
                trend_label="+12.5% vs. letzter Monat",
                icon="",
                size="large",
                variant="elevated",
                show_trend_arrow=True,
                animate=True,
                custom_css=".custom { color: red; }",
                key="test_metric"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with all options failed: {e}")


class TestMetricCardGroup:
    """Tests für MetricCardGroup-Komponente"""
    
    def test_initialization(self, metric_card_group):
        """Test: MetricCardGroup kann initialisiert werden"""
        assert metric_card_group is not None
        assert metric_card_group.theme_manager is not None
    
    def test_render_basic(self, metric_card_group):
        """Test: Basis-Rendering funktioniert"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345"},
                    {"label": "Metrik 2", "value": "1,234"}
                ]
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering failed: {e}")
    
    def test_render_with_trends(self, metric_card_group):
        """Test: Rendering mit Trends"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345", "trend": 12.5},
                    {"label": "Metrik 2", "value": "1,234", "trend": -5.2}
                ]
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with trends failed: {e}")
    
    def test_render_with_icons(self, metric_card_group):
        """Test: Rendering mit Icons"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345", "icon": ""},
                    {"label": "Metrik 2", "value": "1,234", "icon": ""}
                ]
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with icons failed: {e}")
    
    def test_render_with_columns(self, metric_card_group):
        """Test: Rendering mit verschiedenen Spalten-Anzahlen"""
        for columns in [1, 2, 3, 4]:
            try:
                metric_card_group.render(
                    metrics=[
                        {"label": f"Metrik {i}", "value": f"€{i},000"}
                        for i in range(1, columns + 1)
                    ],
                    columns=columns
                )
                assert True
            except Exception as e:
                pytest.fail(f"Rendering with {columns} columns failed: {e}")
    
    def test_render_with_gap_sm(self, metric_card_group):
        """Test: Rendering mit Gap 'sm'"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345"},
                    {"label": "Metrik 2", "value": "1,234"}
                ],
                gap="sm"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with gap 'sm' failed: {e}")
    
    def test_render_with_gap_md(self, metric_card_group):
        """Test: Rendering mit Gap 'md'"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345"},
                    {"label": "Metrik 2", "value": "1,234"}
                ],
                gap="md"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with gap 'md' failed: {e}")
    
    def test_render_with_gap_lg(self, metric_card_group):
        """Test: Rendering mit Gap 'lg'"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": "Metrik 1", "value": "€12,345"},
                    {"label": "Metrik 2", "value": "1,234"}
                ],
                gap="lg"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with gap 'lg' failed: {e}")
    
    def test_render_with_size(self, metric_card_group):
        """Test: Rendering mit verschiedenen Größen"""
        for size in ["small", "medium", "large"]:
            try:
                metric_card_group.render(
                    metrics=[
                        {"label": "Metrik 1", "value": "€12,345"},
                        {"label": "Metrik 2", "value": "1,234"}
                    ],
                    size=size
                )
                assert True
            except Exception as e:
                pytest.fail(f"Rendering with size '{size}' failed: {e}")
    
    def test_render_with_variant(self, metric_card_group):
        """Test: Rendering mit verschiedenen Varianten"""
        for variant in ["default", "outlined", "elevated"]:
            try:
                metric_card_group.render(
                    metrics=[
                        {"label": "Metrik 1", "value": "€12,345"},
                        {"label": "Metrik 2", "value": "1,234"}
                    ],
                    variant=variant
                )
                assert True
            except Exception as e:
                pytest.fail(f"Rendering with variant '{variant}' failed: {e}")
    
    def test_render_empty_metrics(self, metric_card_group):
        """Test: Rendering mit leerer Metrics-Liste"""
        try:
            metric_card_group.render(metrics=[])
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with empty metrics failed: {e}")
    
    def test_render_many_metrics(self, metric_card_group):
        """Test: Rendering mit vielen Metriken"""
        try:
            metric_card_group.render(
                metrics=[
                    {"label": f"Metrik {i}", "value": f"€{i},000", "trend": i * 1.5}
                    for i in range(1, 11)
                ],
                columns=4
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with many metrics failed: {e}")
    
    def test_render_with_all_options(self, metric_card_group):
        """Test: Rendering mit allen Optionen"""
        try:
            metric_card_group.render(
                metrics=[
                    {
                        "label": "Metrik 1",
                        "value": "€12,345",
                        "description": "Beschreibung 1",
                        "trend": 12.5,
                        "trend_label": "+12.5%",
                        "icon": "",
                        "size": "large",
                        "variant": "elevated"
                    },
                    {
                        "label": "Metrik 2",
                        "value": "1,234",
                        "description": "Beschreibung 2",
                        "trend": -5.2,
                        "trend_label": "-5.2%",
                        "icon": "",
                        "size": "large",
                        "variant": "elevated"
                    }
                ],
                columns=2,
                gap="lg",
                size="large",
                variant="elevated",
                key="test_group"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering with all options failed: {e}")


class TestMetricCardIntegration:
    """Integrations-Tests für MetricCard"""
    
    def test_metric_card_with_different_themes(self):
        """Test: MetricCard funktioniert mit verschiedenen Themes"""
        themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean']
        
        for theme_name in themes:
            try:
                manager = ThemeManager()
                manager.set_theme(theme_name)
                metric = MetricCard(theme_manager=manager)
                metric.render(
                    label="Test Metrik",
                    value="€12,345",
                    trend=12.5,
                    icon=""
                )
                assert True
            except Exception as e:
                pytest.fail(f"Rendering with theme '{theme_name}' failed: {e}")
    
    def test_metric_card_without_theme_manager(self):
        """Test: MetricCard funktioniert ohne ThemeManager (mit Fallbacks)"""
        try:
            metric = MetricCard(theme_manager=None)
            metric.render(
                label="Test Metrik",
                value="€12,345"
            )
            assert True
        except Exception as e:
            pytest.fail(f"Rendering without theme manager failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
