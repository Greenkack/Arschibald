"""Tests for Router and Navigation System"""

from unittest.mock import Mock, patch

import pytest

from .router import (
    AuthenticationMiddleware,
    LoggingMiddleware,
    NavigationEvent,
    NavigationEventType,
    Page,
    PermissionGuard,
    RoleGuard,
    Router,
    get_router,
    navigate,
)


class MockPage(Page):
    """Mock page for testing"""

    def render(self):
        pass


class TestRouter:
    """Test Router class"""

    def test_router_initialization(self):
        """Test router initialization"""
        router = Router()
        assert router.routes == {}
        assert router.middleware == []
        assert router.guards == []

    def test_register_route(self):
        """Test route registration"""
        router = Router()
        router.register_route(
            'test_page',
            MockPage,
            title='Test Page',
            icon='🧪'
        )

        assert 'test_page' in router.routes
        route = router.routes['test_page']
        assert route.name == 'test_page'
        assert route.page_class == MockPage
        assert route.title == 'Test Page'
        assert route.icon == '🧪'

    def test_register_middleware(self):
        """Test middleware registration"""
        router = Router()
        middleware = LoggingMiddleware()
        router.register_middleware(middleware)

        assert len(router.middleware) == 1
        assert router.middleware[0] == middleware

    def test_register_guard(self):
        """Test guard registration"""
        router = Router()
        guard = PermissionGuard()
        router.register_guard(guard)

        assert len(router.guards) == 1
        assert router.guards[0] == guard

    def test_get_route(self):
        """Test getting route"""
        router = Router()
        router.register_route('test', MockPage)

        route = router.get_route('test')
        assert route is not None
        assert route.name == 'test'

        # Non-existent route
        assert router.get_route('nonexistent') is None

    @patch('core.router.st')
    def test_navigation_without_streamlit(self, mock_st):
        """Test navigation when Streamlit is not available"""
        mock_st.session_state = {}

        router = Router()
        router.register_route('home', MockPage)
        router.register_route('test', MockPage)

        # Should return False when Streamlit not available
        with patch('core.router.STREAMLIT_AVAILABLE', False):
            result = router.navigate('test')
            assert result is False


class TestMiddleware:
    """Test Middleware classes"""

    def test_authentication_middleware_public_page(self):
        """Test authentication middleware with public page"""
        middleware = AuthenticationMiddleware(
            public_pages={'home', 'login'}
        )

        allowed, error = middleware.process(
            from_page='home',
            to_page='login',
            params={},
            context={}
        )

        assert allowed is True
        assert error is None

    def test_authentication_middleware_authenticated(self):
        """Test authentication middleware with authenticated user"""
        middleware = AuthenticationMiddleware()

        context = {
            'user_id': 'user123',
            'user': Mock()
        }

        allowed, error = middleware.process(
            from_page='home',
            to_page='dashboard',
            params={},
            context=context
        )

        assert allowed is True
        assert error is None

    def test_authentication_middleware_not_authenticated(self):
        """Test authentication middleware without authentication"""
        middleware = AuthenticationMiddleware()

        allowed, error = middleware.process(
            from_page='home',
            to_page='dashboard',
            params={},
            context={}
        )

        assert allowed is False
        assert error == "Authentication required"

    def test_logging_middleware(self):
        """Test logging middleware"""
        middleware = LoggingMiddleware()

        allowed, error = middleware.process(
            from_page='home',
            to_page='test',
            params={'id': '123'},
            context={'user_id': 'user123'}
        )

        assert allowed is True
        assert error is None


class TestRouteGuards:
    """Test RouteGuard classes"""

    def test_permission_guard_no_requirements(self):
        """Test permission guard with no requirements"""
        guard = PermissionGuard()

        allowed, error = guard.can_activate(
            to_page='test',
            params={},
            context={}
        )

        assert allowed is True
        assert error is None

    def test_permission_guard_has_permission(self):
        """Test permission guard with required permissions"""
        guard = PermissionGuard(
            required_permissions={'admin': {'admin.read', 'admin.write'}}
        )

        context = {
            'permissions': {'admin.read', 'admin.write', 'user.read'}
        }

        allowed, error = guard.can_activate(
            to_page='admin',
            params={},
            context=context
        )

        assert allowed is True
        assert error is None

    def test_permission_guard_missing_permission(self):
        """Test permission guard with missing permissions"""
        guard = PermissionGuard(
            required_permissions={'admin': {'admin.read', 'admin.write'}}
        )

        context = {
            'permissions': {'admin.read', 'user.read'}
        }

        allowed, error = guard.can_activate(
            to_page='admin',
            params={},
            context=context
        )

        assert allowed is False
        assert 'admin.write' in error

    def test_role_guard_no_requirements(self):
        """Test role guard with no requirements"""
        guard = RoleGuard()

        allowed, error = guard.can_activate(
            to_page='test',
            params={},
            context={}
        )

        assert allowed is True
        assert error is None

    def test_role_guard_has_role(self):
        """Test role guard with required role"""
        guard = RoleGuard(
            required_roles={'admin': {'admin', 'superuser'}}
        )

        context = {
            'roles': {'admin', 'user'}
        }

        allowed, error = guard.can_activate(
            to_page='admin',
            params={},
            context=context
        )

        assert allowed is True
        assert error is None

    def test_role_guard_missing_role(self):
        """Test role guard with missing role"""
        guard = RoleGuard(
            required_roles={'admin': {'admin', 'superuser'}}
        )

        context = {
            'roles': {'user'}
        }

        allowed, error = guard.can_activate(
            to_page='admin',
            params={},
            context=context
        )

        assert allowed is False
        assert error is not None


class TestNavigationEvent:
    """Test NavigationEvent class"""

    def test_navigation_event_creation(self):
        """Test navigation event creation"""
        event = NavigationEvent(
            event_type=NavigationEventType.NAVIGATE,
            from_page='home',
            to_page='test',
            params={'id': '123'},
            user_id='user123',
            session_id='session123'
        )

        assert event.event_type == NavigationEventType.NAVIGATE
        assert event.from_page == 'home'
        assert event.to_page == 'test'
        assert event.params == {'id': '123'}
        assert event.user_id == 'user123'
        assert event.session_id == 'session123'
        assert event.success is True
        assert event.error is None

    def test_navigation_event_to_dict(self):
        """Test navigation event serialization"""
        event = NavigationEvent(
            event_type=NavigationEventType.NAVIGATE,
            from_page='home',
            to_page='test'
        )

        data = event.to_dict()

        assert data['event_type'] == 'navigate'
        assert data['from_page'] == 'home'
        assert data['to_page'] == 'test'
        assert 'event_id' in data
        assert 'timestamp' in data


class TestPage:
    """Test Page base class"""

    def test_page_initialization(self):
        """Test page initialization"""
        router = Router()
        page = MockPage(router=router)

        assert page.router == router
        assert page.title == ""
        assert page.permissions == set()

    def test_page_can_access_no_permissions(self):
        """Test page access with no permissions required"""
        router = Router()
        page = MockPage(router=router)

        user = Mock()
        user.permissions = set()

        assert page.can_access(user) is True

    def test_page_can_access_with_permissions(self):
        """Test page access with required permissions"""
        router = Router()
        page = MockPage(router=router)
        page.permissions = {'read', 'write'}

        user = Mock()
        user.permissions = {'read', 'write', 'admin'}

        assert page.can_access(user) is True

    def test_page_can_access_missing_permissions(self):
        """Test page access with missing permissions"""
        router = Router()
        page = MockPage(router=router)
        page.permissions = {'read', 'write', 'admin'}

        user = Mock()
        user.permissions = {'read', 'write'}

        assert page.can_access(user) is False


class TestGlobalRouter:
    """Test global router functions"""

    def test_get_router(self):
        """Test getting global router"""
        router1 = get_router()
        router2 = get_router()

        # Should return same instance
        assert router1 is router2

    @patch('core.router.get_router')
    def test_navigate_function(self, mock_get_router):
        """Test global navigate function"""
        mock_router = Mock()
        mock_router.navigate.return_value = True
        mock_get_router.return_value = mock_router

        result = navigate('test', {'id': '123'})

        assert result is True
        mock_router.navigate.assert_called_once_with(
            'test',
            {'id': '123'},
            False
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
