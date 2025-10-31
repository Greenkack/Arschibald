"""Container-Based Navigation System with Router"""

import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class NavigationEventType(str, Enum):
    """Navigation event types"""
    NAVIGATE = "navigate"
    BACK = "back"
    FORWARD = "forward"
    REDIRECT = "redirect"
    GUARD_BLOCKED = "guard_blocked"
    MIDDLEWARE_ERROR = "middleware_error"


@dataclass
class NavigationEvent:
    """Navigation event for tracking and analytics"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: NavigationEventType = NavigationEventType.NAVIGATE
    from_page: str | None = None
    to_page: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None
    session_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'from_page': self.from_page,
            'to_page': self.to_page,
            'params': self.params,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'success': self.success,
            'error': self.error
        }


class Middleware(ABC):
    """Base middleware class for navigation processing"""

    @abstractmethod
    def process(
        self,
        from_page: str | None,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Process navigation request

        Args:
            from_page: Current page (None if initial navigation)
            to_page: Target page
            params: Navigation parameters
            context: Additional context (user, session, etc.)

        Returns:
            Tuple of (allow_navigation, error_message)
        """


class RouteGuard(ABC):
    """Base route guard class for permission-based access control"""

    @abstractmethod
    def can_activate(
        self,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Check if navigation to page is allowed

        Args:
            to_page: Target page
            params: Navigation parameters
            context: Additional context (user, session, etc.)

        Returns:
            Tuple of (allow_access, error_message)
        """


class AuthenticationMiddleware(Middleware):
    """Middleware for authentication checks"""

    def __init__(self, public_pages: set[str] = None):
        self.public_pages = public_pages or {'home', 'login', 'register'}

    def process(
        self,
        from_page: str | None,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """Check if user is authenticated"""
        # Public pages don't require authentication
        if to_page in self.public_pages:
            return True, None

        # Check if user is authenticated
        user = context.get('user')
        if not user or not context.get('user_id'):
            logger.warning(
                "Authentication required",
                to_page=to_page,
                from_page=from_page
            )
            return False, "Authentication required"

        return True, None


class LoggingMiddleware(Middleware):
    """Middleware for logging navigation events"""

    def process(
        self,
        from_page: str | None,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """Log navigation event"""
        logger.info(
            "Navigation",
            from_page=from_page,
            to_page=to_page,
            params=params,
            user_id=context.get('user_id'),
            session_id=context.get('session_id')
        )
        return True, None


class PermissionGuard(RouteGuard):
    """Guard for permission-based access control"""

    def __init__(self, required_permissions: dict[str, set[str]] = None):
        """
        Initialize permission guard

        Args:
            required_permissions: Map of page -> required permissions
        """
        self.required_permissions = required_permissions or {}

    def can_activate(
        self,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """Check if user has required permissions"""
        # No permissions required for this page
        if to_page not in self.required_permissions:
            return True, None

        required = self.required_permissions[to_page]
        user_permissions = context.get('permissions', set())

        # Check if user has all required permissions
        if not required.issubset(user_permissions):
            missing = required - user_permissions
            logger.warning(
                "Permission denied",
                to_page=to_page,
                required=list(required),
                missing=list(missing),
                user_id=context.get('user_id')
            )
            return False, f"Missing permissions: {', '.join(missing)}"

        return True, None


class RoleGuard(RouteGuard):
    """Guard for role-based access control"""

    def __init__(self, required_roles: dict[str, set[str]] = None):
        """
        Initialize role guard

        Args:
            required_roles: Map of page -> required roles
        """
        self.required_roles = required_roles or {}

    def can_activate(
        self,
        to_page: str,
        params: dict[str, Any],
        context: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """Check if user has required roles"""
        # No roles required for this page
        if to_page not in self.required_roles:
            return True, None

        required = self.required_roles[to_page]
        user_roles = context.get('roles', set())

        # Check if user has at least one required role
        if not required.intersection(user_roles):
            logger.warning(
                "Role required",
                to_page=to_page,
                required=list(required),
                user_roles=list(user_roles),
                user_id=context.get('user_id')
            )
            return False, f"Required role: {', '.join(required)}"

        return True, None


@dataclass
class Route:
    """Route configuration"""
    name: str
    page_class: type['Page']
    title: str = ""
    icon: str = ""
    guards: list[RouteGuard] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Page(ABC):
    """Base page class for modular page implementation"""

    def __init__(self, router: 'Router', session: Any = None):
        """
        Initialize page

        Args:
            router: Router instance
            session: User session
        """
        self.router = router
        self.session = session
        self.title: str = ""
        self.permissions: set[str] = set()

    @abstractmethod
    def render(self) -> None:
        """Render page content"""

    def on_event(self, event: NavigationEvent) -> None:
        """
        Handle navigation events

        Args:
            event: Navigation event
        """

    def can_access(self, user: Any) -> bool:
        """
        Check if user can access this page

        Args:
            user: User object

        Returns:
            True if user has required permissions
        """
        if not self.permissions:
            return True

        user_permissions = getattr(user, 'permissions', set())
        return self.permissions.issubset(user_permissions)


class Router:
    """Enhanced navigation router with container-based page swapping"""

    def __init__(self, session_key: str = 'router_state'):
        """
        Initialize router

        Args:
            session_key: Key for storing router state in session_state
        """
        self.session_key = session_key
        self.routes: dict[str, Route] = {}
        self.middleware: list[Middleware] = []
        self.guards: list[RouteGuard] = []
        self.event_handlers: list[Callable[[NavigationEvent], None]] = []

        # Initialize router state in session_state
        self._init_state()

    def _init_state(self) -> None:
        """Initialize router state in session_state"""
        if not STREAMLIT_AVAILABLE or not st:
            return

        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                'current_page': 'home',
                'params': {},
                'history': [],
                'history_index': -1
            }

    @property
    def current_page(self) -> str:
        """Get current page from session_state"""
        if not STREAMLIT_AVAILABLE or not st:
            return 'home'

        state = st.session_state.get(self.session_key, {})
        return state.get('current_page', 'home')

    @property
    def params(self) -> dict[str, Any]:
        """Get current page parameters"""
        if not STREAMLIT_AVAILABLE or not st:
            return {}

        state = st.session_state.get(self.session_key, {})
        return state.get('params', {})

    @property
    def history(self) -> list[dict[str, Any]]:
        """Get navigation history"""
        if not STREAMLIT_AVAILABLE or not st:
            return []

        state = st.session_state.get(self.session_key, {})
        return state.get('history', [])

    def register_route(
        self,
        name: str,
        page_class: type[Page],
        title: str = "",
        icon: str = "",
        guards: list[RouteGuard] = None,
        **metadata
    ) -> None:
        """
        Register a route

        Args:
            name: Route name
            page_class: Page class
            title: Page title
            icon: Page icon
            guards: Route-specific guards
            **metadata: Additional metadata
        """
        route = Route(
            name=name,
            page_class=page_class,
            title=title or name.title(),
            icon=icon,
            guards=guards or [],
            metadata=metadata
        )
        self.routes[name] = route
        logger.debug("Route registered", name=name, title=title)

    def register_middleware(self, middleware: Middleware) -> None:
        """Register navigation middleware"""
        self.middleware.append(middleware)
        logger.debug(
            "Middleware registered",
            middleware=middleware.__class__.__name__
        )

    def register_guard(self, guard: RouteGuard) -> None:
        """Register global route guard"""
        self.guards.append(guard)
        logger.debug("Guard registered", guard=guard.__class__.__name__)

    def on_navigation(
        self,
        handler: Callable[[NavigationEvent], None]
    ) -> None:
        """
        Register navigation event handler

        Args:
            handler: Event handler function
        """
        self.event_handlers.append(handler)

    def navigate(
        self,
        to: str,
        params: dict[str, Any] = None,
        replace: bool = False
    ) -> bool:
        """
        Navigate to page via container swap (no browser navigation)

        Args:
            to: Target page name
            params: Navigation parameters
            replace: If True, replace current history entry

        Returns:
            True if navigation succeeded
        """
        if not STREAMLIT_AVAILABLE or not st:
            logger.warning("Streamlit not available, navigation skipped")
            return False

        params = params or {}
        from_page = self.current_page

        # Get context for middleware and guards
        context = self._get_context()

        # Create navigation event
        event = NavigationEvent(
            event_type=NavigationEventType.NAVIGATE,
            from_page=from_page,
            to_page=to,
            params=params,
            user_id=context.get('user_id'),
            session_id=context.get('session_id')
        )

        try:
            # Run middleware
            for mw in self.middleware:
                allowed, error = mw.process(from_page, to, params, context)
                if not allowed:
                    event.success = False
                    event.error = error
                    event.event_type = NavigationEventType.MIDDLEWARE_ERROR
                    self._emit_event(event)
                    logger.warning(
                        "Navigation blocked by middleware",
                        middleware=mw.__class__.__name__,
                        error=error
                    )
                    return False

            # Run global guards
            for guard in self.guards:
                allowed, error = guard.can_activate(to, params, context)
                if not allowed:
                    event.success = False
                    event.error = error
                    event.event_type = NavigationEventType.GUARD_BLOCKED
                    self._emit_event(event)
                    logger.warning(
                        "Navigation blocked by guard",
                        guard=guard.__class__.__name__,
                        error=error
                    )
                    return False

            # Run route-specific guards
            if to in self.routes:
                route = self.routes[to]
                for guard in route.guards:
                    allowed, error = guard.can_activate(to, params, context)
                    if not allowed:
                        event.success = False
                        event.error = error
                        event.event_type = NavigationEventType.GUARD_BLOCKED
                        self._emit_event(event)
                        logger.warning(
                            "Navigation blocked by route guard",
                            guard=guard.__class__.__name__,
                            error=error
                        )
                        return False

            # Update router state
            state = st.session_state[self.session_key]

            if replace:
                # Replace current history entry
                if state['history']:
                    state['history'][-1] = {
                        'page': to,
                        'params': params,
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                # Add to history
                # Remove forward history if we're not at the end
                if state['history_index'] < len(state['history']) - 1:
                    state['history'] = (
                        state['history'][:state['history_index'] + 1]
                    )

                state['history'].append({
                    'page': to,
                    'params': params,
                    'timestamp': datetime.now().isoformat()
                })
                state['history_index'] = len(state['history']) - 1

            # Update current page and params
            state['current_page'] = to
            state['params'] = params

            # Update user session if available
            self._update_session(to, params)

            # Emit navigation event
            self._emit_event(event)

            logger.info(
                "Navigation successful",
                from_page=from_page,
                to_page=to,
                params=params
            )

            return True

        except Exception as e:
            event.success = False
            event.error = str(e)
            self._emit_event(event)
            logger.error(
                "Navigation error",
                from_page=from_page,
                to_page=to,
                error=str(e),
                exc_info=True
            )
            return False

    def go_back(self) -> bool:
        """
        Navigate back in history

        Returns:
            True if navigation succeeded
        """
        if not STREAMLIT_AVAILABLE or not st:
            return False

        state = st.session_state[self.session_key]

        if state['history_index'] > 0:
            state['history_index'] -= 1
            entry = state['history'][state['history_index']]

            state['current_page'] = entry['page']
            state['params'] = entry['params']

            # Update user session
            self._update_session(entry['page'], entry['params'])

            # Emit event
            event = NavigationEvent(
                event_type=NavigationEventType.BACK,
                from_page=self.current_page,
                to_page=entry['page'],
                params=entry['params']
            )
            self._emit_event(event)

            logger.info("Navigated back", to_page=entry['page'])
            return True

        return False

    def go_forward(self) -> bool:
        """
        Navigate forward in history

        Returns:
            True if navigation succeeded
        """
        if not STREAMLIT_AVAILABLE or not st:
            return False

        state = st.session_state[self.session_key]

        if state['history_index'] < len(state['history']) - 1:
            state['history_index'] += 1
            entry = state['history'][state['history_index']]

            state['current_page'] = entry['page']
            state['params'] = entry['params']

            # Update user session
            self._update_session(entry['page'], entry['params'])

            # Emit event
            event = NavigationEvent(
                event_type=NavigationEventType.FORWARD,
                from_page=self.current_page,
                to_page=entry['page'],
                params=entry['params']
            )
            self._emit_event(event)

            logger.info("Navigated forward", to_page=entry['page'])
            return True

        return False

    def can_go_back(self) -> bool:
        """Check if can navigate back"""
        if not STREAMLIT_AVAILABLE or not st:
            return False

        state = st.session_state.get(self.session_key, {})
        return state.get('history_index', 0) > 0

    def can_go_forward(self) -> bool:
        """Check if can navigate forward"""
        if not STREAMLIT_AVAILABLE or not st:
            return False

        state = st.session_state.get(self.session_key, {})
        history_len = len(state.get('history', []))
        return state.get('history_index', -1) < history_len - 1

    def get_route(self, name: str) -> Route | None:
        """Get route by name"""
        return self.routes.get(name)

    def render_current_page(self) -> None:
        """Render the current page"""
        if not STREAMLIT_AVAILABLE or not st:
            return

        page_name = self.current_page
        route = self.routes.get(page_name)

        if not route:
            logger.error("Route not found", page=page_name)
            if st:
                st.error(f"Page not found: {page_name}")
            return

        try:
            # Get user session
            session = self._get_session()

            # Create page instance
            page = route.page_class(router=self, session=session)

            # Render page
            page.render()

        except Exception as e:
            logger.error(
                "Page render error",
                page=page_name,
                error=str(e),
                exc_info=True
            )
            if st:
                st.error(f"Error rendering page: {str(e)}")

    def _get_context(self) -> dict[str, Any]:
        """Get context for middleware and guards"""
        context = {}

        # Get user session
        session = self._get_session()
        if session:
            context['session'] = session
            context['session_id'] = getattr(session, 'session_id', None)
            context['user_id'] = getattr(session, 'user_id', None)
            context['roles'] = getattr(session, 'roles', set())
            context['permissions'] = getattr(session, 'permissions', set())

            # Get user object if available
            if hasattr(session, 'user'):
                context['user'] = session.user

        return context

    def _get_session(self) -> Any:
        """Get user session from session_state"""
        if not STREAMLIT_AVAILABLE or not st:
            return None

        return st.session_state.get('user_session')

    def _update_session(self, page: str, params: dict[str, Any]) -> None:
        """Update user session with navigation"""
        session = self._get_session()
        if session and hasattr(session, 'add_navigation'):
            session.add_navigation(page, params)

    def _emit_event(self, event: NavigationEvent) -> None:
        """Emit navigation event to handlers"""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    "Event handler error",
                    handler=handler.__name__,
                    error=str(e)
                )


# Global router instance
_router: Router | None = None


def get_router() -> Router:
    """Get global router instance"""
    global _router
    if _router is None:
        _router = Router()
    return _router


def navigate(to: str, params: dict[str, Any] = None, replace: bool = False):
    """
    Navigate to page via Router

    Args:
        to: Target page name
        params: Navigation parameters
        replace: If True, replace current history entry

    Returns:
        True if navigation succeeded
    """
    router = get_router()
    return router.navigate(to, params, replace)
