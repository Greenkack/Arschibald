"""Tests for Container System"""

from unittest.mock import Mock

import pytest

from .containers import (
    ContainerConfig,
    ContainerRegistry,
    ContainerState,
    ErrorBoundary,
    PageContainer,
    PlaceholderContainer,
    StableContainer,
    TransitionContainer,
    create_page_container,
    create_placeholder,
    create_stable_container,
    get_container_registry,
)


class TestContainerConfig:
    """Test ContainerConfig class"""

    def test_default_config(self):
        """Test default configuration"""
        config = ContainerConfig()

        assert config.min_height is None
        assert config.max_height is None
        assert config.fixed_height is None
        assert config.border is False
        assert config.use_container_width is True
        assert config.show_loading is True
        assert config.error_boundary is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = ContainerConfig(
            min_height=400,
            max_height=800,
            border=True,
            show_loading=False
        )

        assert config.min_height == 400
        assert config.max_height == 800
        assert config.border is True
        assert config.show_loading is False


class TestStableContainer:
    """Test StableContainer class"""

    def test_container_initialization(self):
        """Test container initialization"""
        container = StableContainer('test_container')

        assert container.container_id == 'test_container'
        assert container.state == ContainerState.IDLE
        assert container._error is None

    def test_container_with_config(self):
        """Test container with custom config"""
        config = ContainerConfig(
            min_height=500,
            border=True
        )
        container = StableContainer('test', config)

        assert container.config.min_height == 500
        assert container.config.border is True

    def test_get_container_style_fixed_height(self):
        """Test container style with fixed height"""
        config = ContainerConfig(fixed_height=600)
        container = StableContainer('test', config)

        style = container._get_container_style()

        assert 'height: 600px' in style
        assert 'overflow: auto' in style

    def test_get_container_style_min_max(self):
        """Test container style with min/max height"""
        config = ContainerConfig(
            min_height=400,
            max_height=800
        )
        container = StableContainer('test', config)

        style = container._get_container_style()

        assert 'min-height: 400px' in style
        assert 'max-height: 800px' in style

    def test_get_container_style_with_border(self):
        """Test container style with border"""
        config = ContainerConfig(border=True)
        container = StableContainer('test', config)

        style = container._get_container_style()

        assert 'border:' in style
        assert 'border-radius:' in style
        assert 'padding:' in style


class TestPlaceholderContainer:
    """Test PlaceholderContainer class"""

    def test_placeholder_initialization(self):
        """Test placeholder initialization"""
        placeholder = PlaceholderContainer('test_placeholder', height=300)

        assert placeholder.container_id == 'test_placeholder'
        assert placeholder.height == 300
        assert placeholder.show_progress is True
        assert placeholder._placeholder is None

    def test_placeholder_default_height(self):
        """Test placeholder with default height"""
        placeholder = PlaceholderContainer('test')

        assert placeholder.height == 200


class TestTransitionContainer:
    """Test TransitionContainer class"""

    def test_transition_initialization(self):
        """Test transition container initialization"""
        container = TransitionContainer('test_transition')

        assert container.container_id == 'test_transition'
        assert container.transition_duration_ms == 300

    def test_custom_transition_duration(self):
        """Test custom transition duration"""
        container = TransitionContainer('test', transition_duration_ms=500)

        assert container.transition_duration_ms == 500


class TestErrorBoundary:
    """Test ErrorBoundary class"""

    def test_error_boundary_initialization(self):
        """Test error boundary initialization"""
        boundary = ErrorBoundary('test_boundary')

        assert boundary.container_id == 'test_boundary'
        assert boundary.fallback_fn is None
        assert boundary._error is None

    def test_error_boundary_with_fallback(self):
        """Test error boundary with fallback function"""
        fallback = Mock()
        boundary = ErrorBoundary('test', fallback_fn=fallback)

        assert boundary.fallback_fn == fallback

    def test_error_boundary_catch_success(self):
        """Test error boundary catching no error"""
        boundary = ErrorBoundary('test')

        with boundary.catch():
            # No error
            pass

        assert boundary._error is None

    def test_error_boundary_catch_error(self):
        """Test error boundary catching error"""
        boundary = ErrorBoundary('test')

        with boundary.catch():
            raise ValueError("Test error")

        assert boundary._error is not None
        assert isinstance(boundary._error, ValueError)


class TestPageContainer:
    """Test PageContainer class"""

    def test_page_container_initialization(self):
        """Test page container initialization"""
        container = PageContainer('test_page')

        assert container.page_id == 'test_page'
        assert container.min_height == 600
        assert container.show_loading is True

    def test_page_container_custom_height(self):
        """Test page container with custom height"""
        container = PageContainer('test', min_height=800)

        assert container.min_height == 800

    def test_page_container_components(self):
        """Test page container has all components"""
        container = PageContainer('test')

        assert container.stable_container is not None
        assert container.placeholder is not None
        assert container.error_boundary is not None


class TestContainerRegistry:
    """Test ContainerRegistry class"""

    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = ContainerRegistry()

        assert registry.containers == {}
        assert registry.placeholders == {}
        assert registry.page_containers == {}

    def test_register_container(self):
        """Test registering container"""
        registry = ContainerRegistry()
        container = registry.register_container('test')

        assert 'test' in registry.containers
        assert registry.containers['test'] == container

    def test_register_placeholder(self):
        """Test registering placeholder"""
        registry = ContainerRegistry()
        placeholder = registry.register_placeholder('test', height=300)

        assert 'test' in registry.placeholders
        assert registry.placeholders['test'] == placeholder
        assert placeholder.height == 300

    def test_register_page(self):
        """Test registering page container"""
        registry = ContainerRegistry()
        page = registry.register_page('test', min_height=700)

        assert 'test' in registry.page_containers
        assert registry.page_containers['test'] == page
        assert page.min_height == 700

    def test_get_container(self):
        """Test getting container"""
        registry = ContainerRegistry()
        container = registry.register_container('test')

        retrieved = registry.get_container('test')
        assert retrieved == container

        # Non-existent container
        assert registry.get_container('nonexistent') is None

    def test_get_placeholder(self):
        """Test getting placeholder"""
        registry = ContainerRegistry()
        placeholder = registry.register_placeholder('test')

        retrieved = registry.get_placeholder('test')
        assert retrieved == placeholder

        # Non-existent placeholder
        assert registry.get_placeholder('nonexistent') is None

    def test_get_page(self):
        """Test getting page container"""
        registry = ContainerRegistry()
        page = registry.register_page('test')

        retrieved = registry.get_page('test')
        assert retrieved == page

        # Non-existent page
        assert registry.get_page('nonexistent') is None


class TestGlobalRegistry:
    """Test global registry functions"""

    def test_get_container_registry(self):
        """Test getting global registry"""
        registry1 = get_container_registry()
        registry2 = get_container_registry()

        # Should return same instance
        assert registry1 is registry2

    def test_create_stable_container(self):
        """Test creating stable container"""
        config = ContainerConfig(min_height=500)
        container = create_stable_container('test', config)

        assert container.container_id == 'test'
        assert container.config.min_height == 500

        # Should be registered
        registry = get_container_registry()
        assert registry.get_container('test') == container

    def test_create_placeholder(self):
        """Test creating placeholder"""
        placeholder = create_placeholder('test', height=400)

        assert placeholder.container_id == 'test'
        assert placeholder.height == 400

        # Should be registered
        registry = get_container_registry()
        assert registry.get_placeholder('test') == placeholder

    def test_create_page_container(self):
        """Test creating page container"""
        page = create_page_container('test', min_height=800)

        assert page.page_id == 'test'
        assert page.min_height == 800

        # Should be registered
        registry = get_container_registry()
        assert registry.get_page('test') == page


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
