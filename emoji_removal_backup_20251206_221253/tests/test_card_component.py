"""
Unit Tests für die Card-Komponente

Diese Tests prüfen die Funktionalität der Card-Komponente.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from components import Card, ShadcnComponent
from components.card import card


class TestShadcnComponent:
    """Tests für die ShadcnComponent Basis-Klasse"""
    
    def test_init_without_theme_manager(self):
        """Test: Initialisierung ohne Theme-Manager"""
        component = ShadcnComponent()
        assert component.theme_manager is None
    
    def test_init_with_theme_manager(self):
        """Test: Initialisierung mit Theme-Manager"""
        mock_theme_manager = Mock()
        component = ShadcnComponent(theme_manager=mock_theme_manager)
        assert component.theme_manager == mock_theme_manager
    
    def test_get_token_without_theme_manager(self):
        """Test: get_token ohne Theme-Manager gibt Default zurück"""
        component = ShadcnComponent()
        result = component.get_token('colors.primary', default='#000000')
        assert result == '#000000'
    
    def test_get_token_with_theme_manager(self):
        """Test: get_token mit Theme-Manager"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#18181b'
        
        component = ShadcnComponent(theme_manager=mock_theme_manager)
        result = component.get_token('colors.primary')
        
        assert result == '#18181b'
        mock_theme_manager.get_token.assert_called_once_with('colors.primary')
    
    def test_get_css_var(self):
        """Test: get_css_var konvertiert Token-Pfad zu CSS-Variable"""
        component = ShadcnComponent()
        result = component.get_css_var('colors.primary')
        assert result == 'var(--colors-primary)'
    
    def test_generate_unique_id(self):
        """Test: _generate_unique_id generiert eindeutige IDs"""
        component = ShadcnComponent()
        id1 = component._generate_unique_id()
        id2 = component._generate_unique_id()
        
        assert id1 != id2
        assert id1.startswith('shadcn-')
        assert len(id1) > 7  # shadcn- + 8 hex chars
    
    def test_generate_unique_id_with_prefix(self):
        """Test: _generate_unique_id mit Custom-Prefix"""
        component = ShadcnComponent()
        id1 = component._generate_unique_id(prefix='card')
        
        assert id1.startswith('card-')
    
    def test_sanitize_html(self):
        """Test: _sanitize_html escaped HTML"""
        component = ShadcnComponent()
        html = '<script>alert("XSS")</script>'
        result = component._sanitize_html(html)
        
        assert '<script>' not in result
        assert '&lt;script&gt;' in result
    
    def test_render_not_implemented(self):
        """Test: render() wirft NotImplementedError"""
        component = ShadcnComponent()
        
        with pytest.raises(NotImplementedError):
            component.render()


class TestCard:
    """Tests für die Card-Komponente"""
    
    @patch('components.card.st')
    def test_card_render_minimal(self, mock_st):
        """Test: Minimale Card mit nur Titel"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        card_component.render(title="Test Card")
        
        # Prüfe ob st.markdown aufgerufen wurde (2 calls: CSS + HTML)
        assert mock_st.markdown.call_count == 2
        
        # Prüfe ob CSS injiziert wurde
        call_args = mock_st.markdown.call_args_list
        css_call = str(call_args[0])
        assert '<style>' in css_call
        
        # Prüfe ob HTML gerendert wurde
        html_call = str(call_args[1])
        assert 'Test Card' in html_call
    
    @patch('components.card.st')
    def test_card_render_with_all_features(self, mock_st):
        """Test: Card mit allen Features"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        card_component.render(
            title="Full Card",
            description="Description text",
            content="Main content",
            footer="Footer text",
            icon="🎯",
            badge="New",
            badge_variant="success"
        )
        
        # Prüfe ob alle Elemente im HTML sind
        html_calls = [str(call) for call in mock_st.markdown.call_args_list]
        html_content = ' '.join(html_calls)
        
        assert 'Full Card' in html_content
        assert 'Description text' in html_content
        assert 'Main content' in html_content
        assert 'Footer text' in html_content
        assert '🎯' in html_content
        assert 'New' in html_content
    
    @patch('components.card.st')
    def test_card_variants(self, mock_st):
        """Test: Verschiedene Card-Varianten"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        
        # Test default variant
        card_component.render(title="Default", variant="default")
        
        # Test outlined variant
        card_component.render(title="Outlined", variant="outlined")
        
        # Test elevated variant
        card_component.render(title="Elevated", variant="elevated")
        
        # Prüfe ob st.markdown für jede Variante aufgerufen wurde
        assert mock_st.markdown.call_count == 6  # 2 calls per card (CSS + HTML)
    
    @patch('components.card.st')
    def test_card_badge_variants(self, mock_st):
        """Test: Verschiedene Badge-Varianten"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        
        badge_variants = ['default', 'success', 'warning', 'error', 'info']
        
        for variant in badge_variants:
            card_component.render(
                title=f"{variant} Badge",
                badge="Badge",
                badge_variant=variant
            )
        
        # Prüfe ob für jede Variante gerendert wurde
        assert mock_st.markdown.call_count == len(badge_variants) * 2
    
    @patch('components.card.st')
    def test_card_without_hover_effect(self, mock_st):
        """Test: Card ohne Hover-Effekt"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        card_component.render(
            title="No Hover",
            hover_effect=False
        )
        
        # CSS sollte trotzdem injiziert werden
        assert mock_st.markdown.called
    
    @patch('components.card.st')
    def test_card_with_custom_css(self, mock_st):
        """Test: Card mit Custom CSS"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        custom_css = ".custom-class { color: red; }"
        
        card_component = Card(theme_manager=mock_theme_manager)
        card_component.render(
            title="Custom CSS",
            custom_css=custom_css
        )
        
        # Prüfe ob Custom CSS im injizierten CSS enthalten ist
        css_calls = [str(call) for call in mock_st.markdown.call_args_list]
        css_content = ' '.join(css_calls)
        
        # Custom CSS sollte im ersten Call (CSS) enthalten sein
        assert custom_css in css_content or '.custom-class' in css_content
    
    @patch('components.card.st')
    def test_card_with_key(self, mock_st):
        """Test: Card mit eindeutigem Key"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card_component = Card(theme_manager=mock_theme_manager)
        card_component.render(
            title="Keyed Card",
            key="my-unique-key"
        )
        
        # Prüfe ob Key im HTML verwendet wird
        html_calls = [str(call) for call in mock_st.markdown.call_args_list]
        html_content = ' '.join(html_calls)
        
        assert 'my-unique-key' in html_content
    
    @patch('components.card.st')
    def test_card_convenience_function(self, mock_st):
        """Test: card() Convenience-Funktion"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        card(
            title="Convenience Card",
            content="Using shortcut function",
            theme_manager=mock_theme_manager
        )
        
        # Prüfe ob st.markdown aufgerufen wurde
        assert mock_st.markdown.called
        
        # Prüfe ob Inhalt gerendert wurde
        html_calls = [str(call) for call in mock_st.markdown.call_args_list]
        html_content = ' '.join(html_calls)
        
        assert 'Convenience Card' in html_content
        assert 'Using shortcut function' in html_content


class TestCardIntegration:
    """Integrations-Tests für Card-Komponente"""
    
    @patch('components.card.st')
    def test_multiple_cards(self, mock_st):
        """Test: Mehrere Cards rendern"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        for i in range(5):
            card(
                title=f"Card {i}",
                content=f"Content {i}",
                key=f"card_{i}",
                theme_manager=mock_theme_manager
            )
        
        # Prüfe ob für jede Card gerendert wurde
        assert mock_st.markdown.call_count == 10  # 2 calls per card
    
    @patch('components.card.st')
    def test_card_with_html_content(self, mock_st):
        """Test: Card mit HTML-Content"""
        mock_theme_manager = Mock()
        mock_theme_manager.get_token.return_value = '#ffffff'
        
        html_content = """
            <div>
                <h1>Title</h1>
                <p>Paragraph</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </div>
        """
        
        card(
            title="HTML Card",
            content=html_content,
            theme_manager=mock_theme_manager
        )
        
        # Prüfe ob HTML-Content gerendert wurde
        html_calls = [str(call) for call in mock_st.markdown.call_args_list]
        html_content_str = ' '.join(html_calls)
        
        assert '<h1>Title</h1>' in html_content_str
        assert '<ul>' in html_content_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
