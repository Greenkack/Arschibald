"""
Unit Tests für shadcn/ui Responsive Design System

Tests für:
- ResponsiveDesignSystem Klasse
- Breakpoint Management
- CSS Generation
- Convenience Functions
"""

import pytest
from utils.shadcn_responsive import (
    ResponsiveDesignSystem,
    Breakpoint,
    inject_responsive_design,
    render_mobile_sidebar_toggle,
    responsive_columns,
    responsive_container
)


class TestBreakpoint:
    """Tests für Breakpoint Klasse"""
    
    def test_breakpoint_creation(self):
        """Test: Breakpoint kann erstellt werden"""
        bp = Breakpoint('mobile', 0, 767)
        
        assert bp.name == 'mobile'
        assert bp.min_width == 0
        assert bp.max_width == 767
    
    def test_breakpoint_to_media_query_with_max(self):
        """Test: Media Query mit max-width"""
        bp = Breakpoint('mobile', 0, 767)
        query = bp.to_media_query()
        
        assert '@media' in query
        assert 'min-width: 0px' in query
        assert 'max-width: 767px' in query
    
    def test_breakpoint_to_media_query_without_max(self):
        """Test: Media Query ohne max-width"""
        bp = Breakpoint('desktop', 1024, None)
        query = bp.to_media_query()
        
        assert '@media' in query
        assert 'min-width: 1024px' in query
        assert 'max-width' not in query


class TestResponsiveDesignSystem:
    """Tests für ResponsiveDesignSystem Klasse"""
    
    def test_system_initialization(self):
        """Test: System kann initialisiert werden"""
        system = ResponsiveDesignSystem()
        
        assert system is not None
        assert len(system.breakpoints) == 3
        assert 'mobile' in system.breakpoints
        assert 'tablet' in system.breakpoints
        assert 'desktop' in system.breakpoints
    
    def test_breakpoints_configuration(self):
        """Test: Breakpoints sind korrekt konfiguriert"""
        system = ResponsiveDesignSystem()
        
        # Mobile
        mobile = system.breakpoints['mobile']
        assert mobile.min_width == 0
        assert mobile.max_width == 767
        
        # Tablet
        tablet = system.breakpoints['tablet']
        assert tablet.min_width == 768
        assert tablet.max_width == 1023
        
        # Desktop
        desktop = system.breakpoints['desktop']
        assert desktop.min_width == 1024
        assert desktop.max_width is None
    
    def test_min_touch_size(self):
        """Test: MIN_TOUCH_SIZE ist korrekt gesetzt"""
        system = ResponsiveDesignSystem()
        
        assert system.MIN_TOUCH_SIZE == 44
    
    def test_generate_responsive_css(self):
        """Test: CSS kann generiert werden"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert css is not None
        assert len(css) > 0
        assert isinstance(css, str)
    
    def test_css_contains_base_styles(self):
        """Test: CSS enthält Basis-Styles"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'overflow-x: hidden' in css
        assert 'box-sizing: border-box' in css
        assert 'responsive-container' in css
    
    def test_css_contains_mobile_styles(self):
        """Test: CSS enthält Mobile-Styles"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert '@media (min-width: 0px) and (max-width: 767px)' in css
        assert 'sidebar-toggle-mobile' in css
    
    def test_css_contains_tablet_styles(self):
        """Test: CSS enthält Tablet-Styles"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert '@media (min-width: 768px) and (max-width: 1023px)' in css
    
    def test_css_contains_desktop_styles(self):
        """Test: CSS enthält Desktop-Styles"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert '@media (min-width: 1024px)' in css
    
    def test_css_contains_touch_optimization(self):
        """Test: CSS enthält Touch-Optimierung"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'min-width: 44px' in css
        assert 'min-height: 44px' in css
        assert 'TOUCH-OPTIMIZED' in css
    
    def test_css_contains_sidebar_responsive(self):
        """Test: CSS enthält Responsive Sidebar"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'RESPONSIVE SIDEBAR' in css
        assert 'sidebar-toggle' in css
        assert 'sidebar-overlay' in css
    
    def test_css_contains_layout_responsive(self):
        """Test: CSS enthält Responsive Layouts"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'responsive-grid' in css
        assert 'responsive-flex' in css
    
    def test_css_contains_utility_classes(self):
        """Test: CSS enthält Utility Classes"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'hide-mobile' in css
        assert 'show-mobile' in css
        assert 'hide-tablet' in css
        assert 'show-desktop' in css
        assert 'w-full' in css
        assert 'mx-auto' in css
    
    def test_generate_base_responsive_css(self):
        """Test: Basis Responsive CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_base_responsive_css()
        
        assert 'BASE RESPONSIVE STYLES' in css
        assert 'overflow-x: hidden' in css
        assert 'max-width: 100vw' in css
    
    def test_generate_mobile_css(self):
        """Test: Mobile CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_mobile_css()
        
        assert 'MOBILE STYLES' in css
        assert '0-767px' in css
        assert 'width: 100%' in css
    
    def test_generate_tablet_css(self):
        """Test: Tablet CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_tablet_css()
        
        assert 'TABLET STYLES' in css
        assert '768px-1023px' in css
    
    def test_generate_desktop_css(self):
        """Test: Desktop CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_desktop_css()
        
        assert 'DESKTOP STYLES' in css
        assert '1024px+' in css
    
    def test_generate_touch_optimized_css(self):
        """Test: Touch-optimiertes CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_touch_optimized_css()
        
        assert 'TOUCH-OPTIMIZED' in css
        assert f'min-width: {system.MIN_TOUCH_SIZE}px' in css
        assert f'min-height: {system.MIN_TOUCH_SIZE}px' in css
    
    def test_generate_sidebar_responsive_css(self):
        """Test: Sidebar Responsive CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_sidebar_responsive_css()
        
        assert 'RESPONSIVE SIDEBAR' in css
        assert 'sidebar-toggle' in css
        assert 'sidebar-overlay' in css
        assert 'collapsed' in css
    
    def test_generate_layout_responsive_css(self):
        """Test: Layout Responsive CSS"""
        system = ResponsiveDesignSystem()
        css = system._generate_layout_responsive_css()
        
        assert 'RESPONSIVE LAYOUTS' in css
        assert 'responsive-grid' in css
        assert 'responsive-flex' in css
    
    def test_generate_utility_classes(self):
        """Test: Utility Classes"""
        system = ResponsiveDesignSystem()
        css = system._generate_utility_classes()
        
        assert 'RESPONSIVE UTILITIES' in css
        assert 'hide-mobile' in css
        assert 'show-mobile' in css
        assert 'w-full' in css


class TestConvenienceFunctions:
    """Tests für Convenience Functions"""
    
    def test_inject_responsive_design_callable(self):
        """Test: inject_responsive_design ist aufrufbar"""
        # Sollte keine Exception werfen
        try:
            # Kann nicht wirklich testen ohne Streamlit Context
            # Aber wir können prüfen ob die Funktion existiert
            assert callable(inject_responsive_design)
        except Exception as e:
            # Erwartete Exception ohne Streamlit Context
            assert 'streamlit' in str(e).lower() or 'session' in str(e).lower()
    
    def test_render_mobile_sidebar_toggle_callable(self):
        """Test: render_mobile_sidebar_toggle ist aufrufbar"""
        try:
            assert callable(render_mobile_sidebar_toggle)
        except Exception as e:
            assert 'streamlit' in str(e).lower() or 'session' in str(e).lower()
    
    def test_responsive_columns_callable(self):
        """Test: responsive_columns ist aufrufbar"""
        try:
            assert callable(responsive_columns)
        except Exception as e:
            assert 'streamlit' in str(e).lower() or 'session' in str(e).lower()
    
    def test_responsive_container_callable(self):
        """Test: responsive_container ist aufrufbar"""
        try:
            assert callable(responsive_container)
        except Exception as e:
            assert 'streamlit' in str(e).lower() or 'session' in str(e).lower()


class TestCSSContent:
    """Tests für spezifischen CSS Content"""
    
    def test_prevents_horizontal_scroll(self):
        """Test: CSS verhindert horizontales Scrollen"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'overflow-x: hidden' in css
        assert 'max-width: 100vw' in css
    
    def test_touch_friendly_buttons(self):
        """Test: Buttons sind touch-friendly"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        # Min. 44px für Buttons
        assert 'min-width: 44px' in css
        assert 'min-height: 44px' in css
    
    def test_mobile_stacking(self):
        """Test: Mobile Stacking für Columns"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        # Columns sollten auf Mobile 100% Breite haben
        assert 'width: 100%' in css
        assert 'flex: 0 0 100%' in css
    
    def test_sidebar_collapsible(self):
        """Test: Sidebar ist kollabierbar"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'sidebar-toggle' in css
        assert 'collapsed' in css
        assert 'transform: translateX(-100%)' in css
    
    def test_responsive_grid_system(self):
        """Test: Grid System ist responsive"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'responsive-grid-2' in css
        assert 'responsive-grid-3' in css
        assert 'responsive-grid-4' in css
        assert 'grid-template-columns' in css
    
    def test_visibility_utilities(self):
        """Test: Visibility Utilities vorhanden"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'hide-mobile' in css
        assert 'hide-tablet' in css
        assert 'hide-desktop' in css
        assert 'show-mobile' in css
        assert 'show-tablet' in css
        assert 'show-desktop' in css


class TestBreakpointLogic:
    """Tests für Breakpoint-Logik"""
    
    def test_mobile_breakpoint_range(self):
        """Test: Mobile Breakpoint Range"""
        system = ResponsiveDesignSystem()
        mobile = system.breakpoints['mobile']
        
        assert mobile.min_width == 0
        assert mobile.max_width == 767
        assert mobile.max_width < system.breakpoints['tablet'].min_width
    
    def test_tablet_breakpoint_range(self):
        """Test: Tablet Breakpoint Range"""
        system = ResponsiveDesignSystem()
        tablet = system.breakpoints['tablet']
        
        assert tablet.min_width == 768
        assert tablet.max_width == 1023
        assert tablet.min_width == system.breakpoints['mobile'].max_width + 1
        assert tablet.max_width < system.breakpoints['desktop'].min_width
    
    def test_desktop_breakpoint_range(self):
        """Test: Desktop Breakpoint Range"""
        system = ResponsiveDesignSystem()
        desktop = system.breakpoints['desktop']
        
        assert desktop.min_width == 1024
        assert desktop.max_width is None
        assert desktop.min_width == system.breakpoints['tablet'].max_width + 1
    
    def test_no_breakpoint_gaps(self):
        """Test: Keine Lücken zwischen Breakpoints"""
        system = ResponsiveDesignSystem()
        
        mobile = system.breakpoints['mobile']
        tablet = system.breakpoints['tablet']
        desktop = system.breakpoints['desktop']
        
        # Tablet startet wo Mobile endet
        assert tablet.min_width == mobile.max_width + 1
        
        # Desktop startet wo Tablet endet
        assert desktop.min_width == tablet.max_width + 1


class TestTouchOptimization:
    """Tests für Touch-Optimierung"""
    
    def test_min_touch_size_constant(self):
        """Test: MIN_TOUCH_SIZE ist 44px"""
        system = ResponsiveDesignSystem()
        
        assert system.MIN_TOUCH_SIZE == 44
    
    def test_touch_size_in_css(self):
        """Test: Touch-Größe ist im CSS"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert '44px' in css
    
    def test_input_font_size(self):
        """Test: Input font-size verhindert iOS Zoom"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        # font-size: 16px verhindert Zoom auf iOS
        assert 'font-size: 16px' in css
    
    def test_touch_feedback(self):
        """Test: Touch-Feedback vorhanden"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'hover: none' in css
        assert 'pointer: coarse' in css
        assert ':active' in css


class TestResponsiveFeatures:
    """Tests für spezifische Responsive Features"""
    
    def test_sidebar_overlay(self):
        """Test: Sidebar Overlay vorhanden"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'sidebar-overlay' in css
        assert 'rgba(0, 0, 0, 0.5)' in css
        assert 'z-index: 999' in css
    
    def test_sidebar_toggle_button(self):
        """Test: Sidebar Toggle Button"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'sidebar-toggle' in css
        assert 'position: fixed' in css
        assert 'z-index: 1001' in css
    
    def test_smooth_transitions(self):
        """Test: Smooth Transitions"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'transition' in css
        assert '0.3s' in css or '300ms' in css
    
    def test_responsive_images(self):
        """Test: Responsive Images"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'max-width: 100%' in css
        assert 'height: auto' in css
    
    def test_responsive_tables(self):
        """Test: Responsive Tables"""
        system = ResponsiveDesignSystem()
        css = system.generate_responsive_css()
        
        assert 'overflow-x: auto' in css
        assert '-webkit-overflow-scrolling: touch' in css


# Run Tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
