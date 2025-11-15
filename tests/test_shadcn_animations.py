"""
Tests for shadcn/ui Animations and Transitions

Tests all animation functionality including transitions, fade-ins,
slides, skeleton loaders, and layout shift prevention.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.shadcn_animations import (
    AnimationManager,
    inject_base_transitions,
    inject_fade_in_animations,
    inject_slide_animations,
    inject_skeleton_loaders,
    inject_layout_shift_prevention,
    inject_all_animations,
    create_skeleton_loader,
    show_loading_skeleton,
    with_fade_in,
    prevent_layout_shift
)
from theming.theme_manager import ThemeManager


class TestAnimationManager:
    """Tests for AnimationManager class"""
    
    def test_init_without_theme_manager(self):
        """Test initialization without theme manager"""
        anim_mgr = AnimationManager()
        assert anim_mgr.theme_manager is None
    
    def test_init_with_theme_manager(self):
        """Test initialization with theme manager"""
        theme_mgr = Mock(spec=ThemeManager)
        anim_mgr = AnimationManager(theme_mgr)
        assert anim_mgr.theme_manager == theme_mgr
    
    def test_get_transition_fast(self):
        """Test getting fast transition timing"""
        anim_mgr = AnimationManager()
        transition = anim_mgr.get_transition('fast')
        assert '150ms' in transition
        assert 'cubic-bezier' in transition
    
    def test_get_transition_base(self):
        """Test getting base transition timing"""
        anim_mgr = AnimationManager()
        transition = anim_mgr.get_transition('base')
        assert '200ms' in transition
        assert 'cubic-bezier' in transition
    
    def test_get_transition_slow(self):
        """Test getting slow transition timing"""
        anim_mgr = AnimationManager()
        transition = anim_mgr.get_transition('slow')
        assert '300ms' in transition
        assert 'cubic-bezier' in transition
    
    def test_get_transition_with_theme_manager(self):
        """Test getting transition from theme manager"""
        theme_mgr = Mock(spec=ThemeManager)
        theme_mgr.get_token.return_value = '250ms ease-in-out'
        
        anim_mgr = AnimationManager(theme_mgr)
        transition = anim_mgr.get_transition('base')
        
        theme_mgr.get_token.assert_called_once_with('animations.transition_base')
        assert transition == '250ms ease-in-out'
    
    def test_get_easing_default(self):
        """Test getting default easing function"""
        anim_mgr = AnimationManager()
        easing = anim_mgr.get_easing()
        assert 'cubic-bezier' in easing
    
    def test_get_easing_with_theme_manager(self):
        """Test getting easing from theme manager"""
        theme_mgr = Mock(spec=ThemeManager)
        theme_mgr.get_token.return_value = 'ease-in-out'
        
        anim_mgr = AnimationManager(theme_mgr)
        easing = anim_mgr.get_easing()
        
        theme_mgr.get_token.assert_called_once_with('animations.easing_default')
        assert easing == 'ease-in-out'


class TestInjectionFunctions:
    """Tests for CSS injection functions"""
    
    @patch('utils.shadcn_animations.st')
    def test_inject_base_transitions(self, mock_st):
        """Test injecting base transitions"""
        inject_base_transitions()
        
        # Verify st.markdown was called
        mock_st.markdown.assert_called_once()
        
        # Get the CSS that was injected
        call_args = mock_st.markdown.call_args
        css = call_args[0][0]
        
        # Verify CSS contains key elements
        assert '<style>' in css
        assert 'transition' in css
        assert 'button' in css
        assert 'input' in css
        assert call_args[1].get('unsafe_allow_html') == True
    
    @patch('utils.shadcn_animations.st')
    def test_inject_base_transitions_with_theme(self, mock_st):
        """Test injecting base transitions with theme manager"""
        theme_mgr = Mock(spec=ThemeManager)
        theme_mgr.get_token.return_value = '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        
        inject_base_transitions(theme_mgr)
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        assert '200ms' in css
    
    @patch('utils.shadcn_animations.st')
    def test_inject_fade_in_animations(self, mock_st):
        """Test injecting fade-in animations"""
        inject_fade_in_animations()
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        
        # Verify keyframes are present
        assert '@keyframes fadeIn' in css
        assert '@keyframes fadeInUp' in css
        assert '@keyframes fadeInDown' in css
        assert '@keyframes fadeInLeft' in css
        assert '@keyframes fadeInRight' in css
        assert '@keyframes fadeInScale' in css
        
        # Verify utility classes
        assert 'animate-fade-in' in css
        assert 'animate-stagger' in css
    
    @patch('utils.shadcn_animations.st')
    def test_inject_slide_animations(self, mock_st):
        """Test injecting slide animations"""
        inject_slide_animations()
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        
        # Verify keyframes
        assert '@keyframes slideInLeft' in css
        assert '@keyframes slideInRight' in css
        assert '@keyframes slideDown' in css
        assert '@keyframes slideUp' in css
        
        # Verify utility classes
        assert 'animate-slide-in-left' in css
        assert 'animate-slide-in-right' in css
    
    @patch('utils.shadcn_animations.st')
    def test_inject_skeleton_loaders(self, mock_st):
        """Test injecting skeleton loaders"""
        inject_skeleton_loaders()
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        
        # Verify keyframes
        assert '@keyframes skeleton-pulse' in css
        assert '@keyframes skeleton-shimmer' in css
        assert '@keyframes skeleton-wave' in css
        
        # Verify skeleton classes
        assert '.skeleton' in css
        assert '.skeleton-text' in css
        assert '.skeleton-avatar' in css
        assert '.skeleton-card' in css
    
    @patch('utils.shadcn_animations.st')
    def test_inject_skeleton_loaders_with_theme(self, mock_st):
        """Test injecting skeleton loaders with theme colors"""
        theme_mgr = Mock(spec=ThemeManager)
        theme_mgr.get_token.side_effect = ['#f4f4f5', '#ffffff']
        
        inject_skeleton_loaders(theme_mgr)
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        
        # Verify theme colors are used
        assert '#f4f4f5' in css
        assert '#ffffff' in css
    
    @patch('utils.shadcn_animations.st')
    def test_inject_layout_shift_prevention(self, mock_st):
        """Test injecting layout shift prevention"""
        inject_layout_shift_prevention()
        
        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        
        # Verify aspect ratio classes
        assert '.aspect-ratio-16-9' in css
        assert '.aspect-ratio-4-3' in css
        assert '.aspect-ratio-1-1' in css
        
        # Verify stability classes
        assert '.stable-height' in css
        assert '.stable-grid' in css
        assert '.stable-flex' in css
    
    @patch('utils.shadcn_animations.st')
    @patch('utils.shadcn_animations.inject_base_transitions')
    @patch('utils.shadcn_animations.inject_fade_in_animations')
    @patch('utils.shadcn_animations.inject_slide_animations')
    @patch('utils.shadcn_animations.inject_skeleton_loaders')
    @patch('utils.shadcn_animations.inject_layout_shift_prevention')
    def test_inject_all_animations(
        self,
        mock_layout,
        mock_skeleton,
        mock_slide,
        mock_fade,
        mock_base,
        mock_st
    ):
        """Test injecting all animations at once"""
        theme_mgr = Mock(spec=ThemeManager)
        
        inject_all_animations(theme_mgr)
        
        # Verify all injection functions were called
        mock_base.assert_called_once_with(theme_mgr)
        mock_fade.assert_called_once()
        mock_slide.assert_called_once()
        mock_skeleton.assert_called_once_with(theme_mgr)
        mock_layout.assert_called_once()


class TestHelperFunctions:
    """Tests for helper functions"""
    
    @patch('utils.shadcn_animations.st')
    def test_create_skeleton_loader_text(self, mock_st):
        """Test creating text skeleton loader"""
        create_skeleton_loader('text', 'pulse', count=1)
        
        mock_st.markdown.assert_called_once()
        html = mock_st.markdown.call_args[0][0]
        
        assert 'skeleton' in html
        assert 'skeleton-text' in html
    
    @patch('utils.shadcn_animations.st')
    def test_create_skeleton_loader_multiple(self, mock_st):
        """Test creating multiple skeleton loaders"""
        create_skeleton_loader('text', 'shimmer', count=3)
        
        mock_st.markdown.assert_called_once()
        html = mock_st.markdown.call_args[0][0]
        
        # Should have 3 skeleton elements
        assert html.count('skeleton-shimmer') == 3
    
    @patch('utils.shadcn_animations.st')
    def test_create_skeleton_loader_custom_size(self, mock_st):
        """Test creating skeleton with custom size"""
        create_skeleton_loader('card', 'wave', width='80%', height='200px')
        
        mock_st.markdown.assert_called_once()
        html = mock_st.markdown.call_args[0][0]
        
        assert 'width: 80%' in html
        assert 'height: 200px' in html
    
    @patch('utils.shadcn_animations.st')
    @patch('utils.shadcn_animations.create_skeleton_loader')
    def test_show_loading_skeleton_card(self, mock_create, mock_st):
        """Test showing card loading skeleton"""
        show_loading_skeleton('card', count=3)
        
        # Should create 3 card skeletons
        assert mock_create.call_count == 3
        
        # Verify card type was used
        for call in mock_create.call_args_list:
            assert call[0][0] == 'card'
            assert call[0][1] == 'shimmer'
    
    @patch('utils.shadcn_animations.st')
    @patch('utils.shadcn_animations.create_skeleton_loader')
    def test_show_loading_skeleton_list(self, mock_create, mock_st):
        """Test showing list loading skeleton"""
        # Mock st.columns to return mock column objects
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]
        
        show_loading_skeleton('list', count=2)
        
        # Should create skeletons for 2 list items
        # Each list item has avatar + heading + 2 text lines = 4 skeletons per item
        assert mock_create.call_count >= 2
    
    @patch('utils.shadcn_animations.st')
    def test_with_fade_in(self, mock_st):
        """Test with_fade_in decorator"""
        content_func = Mock()
        
        with_fade_in(content_func, direction='up')
        
        # Verify content function was called
        content_func.assert_called_once()
        
        # Verify markdown was called for wrapper divs
        assert mock_st.markdown.call_count == 2
        
        # Check for animation class
        first_call = mock_st.markdown.call_args_list[0][0][0]
        assert 'animate-fade-in-up' in first_call
    
    @patch('utils.shadcn_animations.st')
    def test_prevent_layout_shift(self, mock_st):
        """Test prevent_layout_shift wrapper"""
        content_func = Mock()
        
        prevent_layout_shift(content_func, min_height='300px')
        
        # Verify content function was called
        content_func.assert_called_once()
        
        # Verify markdown was called for wrapper divs
        assert mock_st.markdown.call_count == 2
        
        # Check for min-height
        first_call = mock_st.markdown.call_args_list[0][0][0]
        assert 'min-height: 300px' in first_call


class TestAnimationVariants:
    """Tests for different animation variants"""
    
    @patch('utils.shadcn_animations.st')
    def test_all_skeleton_variants(self, mock_st):
        """Test all skeleton variants can be created"""
        variants = ['text', 'heading', 'avatar', 'button', 'card', 'image']
        
        for variant in variants:
            mock_st.reset_mock()
            create_skeleton_loader(variant, 'pulse')
            
            mock_st.markdown.assert_called_once()
            html = mock_st.markdown.call_args[0][0]
            assert f'skeleton-{variant}' in html
    
    @patch('utils.shadcn_animations.st')
    def test_all_animation_types(self, mock_st):
        """Test all animation types"""
        animations = ['pulse', 'shimmer', 'wave']
        
        for animation in animations:
            mock_st.reset_mock()
            create_skeleton_loader('text', animation)
            
            mock_st.markdown.assert_called_once()
            html = mock_st.markdown.call_args[0][0]
            
            if animation == 'pulse':
                assert 'skeleton' in html
            else:
                assert f'skeleton-{animation}' in html
    
    @patch('utils.shadcn_animations.st')
    def test_all_fade_directions(self, mock_st):
        """Test all fade-in directions"""
        directions = ['up', 'down', 'left', 'right', 'scale']
        
        for direction in directions:
            mock_st.reset_mock()
            content_func = Mock()
            
            with_fade_in(content_func, direction=direction)
            
            first_call = mock_st.markdown.call_args_list[0][0][0]
            
            if direction == 'scale':
                assert 'animate-fade-in-scale' in first_call
            else:
                assert f'animate-fade-in-{direction}' in first_call


class TestIntegration:
    """Integration tests"""
    
    @patch('utils.shadcn_animations.st')
    def test_full_animation_workflow(self, mock_st):
        """Test complete animation workflow"""
        theme_mgr = Mock(spec=ThemeManager)
        theme_mgr.get_token.return_value = '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        
        # Inject all animations
        inject_all_animations(theme_mgr)
        
        # Create skeleton loader
        create_skeleton_loader('card', 'shimmer')
        
        # Use fade-in
        content_func = Mock()
        with_fade_in(content_func, direction='up')
        
        # Verify all functions were called
        assert mock_st.markdown.call_count > 0
        content_func.assert_called_once()
    
    @patch('utils.shadcn_animations.st')
    def test_loading_state_pattern(self, mock_st):
        """Test common loading state pattern"""
        # Show loading skeleton
        show_loading_skeleton('card', count=3)
        
        # Then show content with fade-in
        def render_content():
            pass
        
        with_fade_in(render_content, direction='up')
        
        # Verify both were called
        assert mock_st.markdown.call_count > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
