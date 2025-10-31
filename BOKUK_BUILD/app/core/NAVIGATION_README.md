# Container-Based Navigation System

Complete navigation system for Streamlit applications with stable containers, middleware, guards, and analytics.

## Overview

The Container-Based Navigation System provides:

- **Router**: Client-side routing without page reloads
- **Stable Containers**: Fixed-size containers that prevent layout shifts
- **Middleware**: Pre-navigation processing (authentication, logging)
- **Route Guards**: Permission-based access control
- **Navigation History**: Back/forward navigation with breadcrumbs
- **Analytics**: User journey tracking and conversion funnels

## Key Features

### Zero UI Jumps

- Container-based page swapping (no browser navigation)
- Fixed-size containers prevent layout shifts
- Placeholder containers for loading states
- Smooth transitions without spinners

### Complete State Management

- Navigation history with parameter preservation
- Browser back/forward button handling
- Breadcrumb generation
- Session integration

### Security & Access Control

- Authentication middleware
- Permission-based guards
- Role-based access control
- Route-level security

### Analytics & Tracking

- Navigation event tracking
- User journey analysis
- Conversion funnel calculation
- Popular path detection

## Quick Start

### Basic Router Setup

```python
from core import Router, Page, get_router

# Define a page
class HomePage(Page):
    def render(self):
        st.title("Home")
        if st.button("Go to Dashboard"):
            self.router.navigate('dashboard')

# Setup router
router = get_router()
router.register_route('home', HomePage, title='Home', icon='🏠')
router.register_route('dashboard', DashboardPage, title='Dashboard')

# Render current page
router.render_current_page()
```

### Navigation

```python
from core import navigate

# Navigate to a page
navigate('dashboard')

# Navigate with parameters
navigate('profile', {'user_id': '123'})

# Replace current history entry
navigate('login', replace=True)
```

### Stable Containers

```python
from core import create_page_container

# Create page container
container = create_page_container('my_page', min_height=600)

# Render with loading state
container.render(
    content_fn=lambda: st.write("Page content"),
    loading=False
)

# Use loading context
with container.loading_context("Loading data..."):
    data = load_data()
    st.write(data)
```

## Router

### Registering Routes

```python
router = get_router()

# Basic route
router.register_route('home', HomePage)

# Route with metadata
router.register_route(
    'dashboard',
    DashboardPage,
    title='Dashboard',
    icon='📊',
    guards=[PermissionGuard({'dashboard': {'read'}})]
)
```

### Navigation Methods

```python
# Navigate to page
router.navigate('dashboard', {'filter': 'active'})

# Go back
if router.can_go_back():
    router.go_back()

# Go forward
if router.can_go_forward():
    router.go_forward()

# Get current page
current = router.current_page
params = router.params
```

### Navigation Events

```python
def on_navigation(event):
    print(f"Navigated from {event.from_page} to {event.to_page}")
    # Track in analytics
    analytics.track(event)

router.on_navigation(on_navigation)
```

## Middleware

Middleware processes navigation requests before they execute.

### Authentication Middleware

```python
from core import AuthenticationMiddleware

middleware = AuthenticationMiddleware(
    public_pages={'home', 'login', 'register'}
)
router.register_middleware(middleware)
```

### Logging Middleware

```python
from core import LoggingMiddleware

middleware = LoggingMiddleware()
router.register_middleware(middleware)
```

### Custom Middleware

```python
from core import Middleware

class CustomMiddleware(Middleware):
    def process(self, from_page, to_page, params, context):
        # Custom logic
        if not self.is_allowed(to_page):
            return False, "Access denied"
        return True, None

router.register_middleware(CustomMiddleware())
```

## Route Guards

Guards control access to specific routes.

### Permission Guard

```python
from core import PermissionGuard

guard = PermissionGuard(
    required_permissions={
        'admin': {'admin.read', 'admin.write'},
        'settings': {'settings.write'}
    }
)
router.register_guard(guard)
```

### Role Guard

```python
from core import RoleGuard

guard = RoleGuard(
    required_roles={
        'admin': {'admin', 'superuser'},
        'reports': {'manager', 'admin'}
    }
)
router.register_guard(guard)
```

### Custom Guard

```python
from core import RouteGuard

class CustomGuard(RouteGuard):
    def can_activate(self, to_page, params, context):
        # Custom logic
        if not self.check_access(to_page, context):
            return False, "Access denied"
        return True, None

router.register_guard(CustomGuard())
```

## Page Class

Base class for all pages.

```python
from core import Page

class MyPage(Page):
    def __init__(self, router, session=None):
        super().__init__(router, session)
        self.title = "My Page"
        self.permissions = {'read', 'write'}
    
    def render(self):
        st.title(self.title)
        # Page content
    
    def on_event(self, event):
        # Handle navigation events
        pass
    
    def can_access(self, user):
        # Custom access check
        return super().can_access(user)
```

## Stable Containers

### Container Types

#### StableContainer

Fixed-size container that prevents layout shifts.

```python
from core import StableContainer, ContainerConfig

config = ContainerConfig(
    min_height=400,
    max_height=800,
    border=True,
    error_boundary=True
)

container = StableContainer('my_container', config)
container.render(lambda: st.write("Content"))
```

#### PlaceholderContainer

Shows placeholder during loading without spinners.

```python
from core import PlaceholderContainer

placeholder = PlaceholderContainer('loading', height=300)

# Show loading
placeholder.show("Loading data...", progress=0.5)

# Update progress
placeholder.update_progress(0.75, "Almost done...")

# Clear
placeholder.clear()
```

#### PageContainer

Complete page container with all features.

```python
from core import PageContainer

container = PageContainer('my_page', min_height=600)

# Render page
container.render(
    content_fn=render_page_content,
    loading=False
)

# Use loading context
with container.loading_context("Loading..."):
    load_data()
```

#### ErrorBoundary

Isolates errors to prevent cascade failures.

```python
from core import ErrorBoundary

boundary = ErrorBoundary('my_boundary')

# Render with error boundary
boundary.render(lambda: potentially_failing_code())

# Custom fallback
def fallback(error):
    st.error(f"Custom error: {error}")

boundary = ErrorBoundary('my_boundary', fallback_fn=fallback)
```

### Container Registry

Manage multiple containers.

```python
from core import get_container_registry

registry = get_container_registry()

# Register containers
container = registry.register_container('main', config)
placeholder = registry.register_placeholder('loading', height=400)
page = registry.register_page('home', min_height=600)

# Retrieve containers
container = registry.get_container('main')
placeholder = registry.get_placeholder('loading')
page = registry.get_page('home')
```

## Navigation History

### Basic Usage

```python
from core import NavigationHistory

history = NavigationHistory(max_size=100)

# Push entries
history.push('home', {'filter': 'all'})
history.push('dashboard', {'view': 'summary'})

# Navigate
entry = history.back()  # Go back
entry = history.forward()  # Go forward

# Check navigation
can_back = history.can_go_back()
can_forward = history.can_go_forward()

# Get current
current = history.get_current()
previous = history.get_previous()
```

### Breadcrumbs

```python
# Register page titles and icons
history.register_page_title('home', 'Home')
history.register_page_icon('home', '🏠')

# Generate breadcrumbs
breadcrumbs = history.get_breadcrumbs(max_items=5)

# Render breadcrumbs
from core import render_breadcrumbs

render_breadcrumbs(
    breadcrumbs,
    on_click=lambda page, params: navigate(page, params)
)
```

### Analytics

```python
# Get page visits
visits = history.get_page_visits()
# {'home': 5, 'dashboard': 3, 'settings': 2}

# Get most visited
most_visited = history.get_most_visited_pages(limit=5)
# [('home', 5), ('dashboard', 3), ('settings', 2)]

# Get average duration
avg_duration = history.get_average_duration('dashboard')
```

## Navigation Analytics

Track and analyze user journeys.

```python
from core import get_navigation_analytics

analytics = get_navigation_analytics()

# Track navigation
analytics.track_navigation(
    session_id='session123',
    page='dashboard',
    params={'view': 'summary'},
    user_id='user123'
)

# Get session history
history = analytics.get_session_history('session123')

# Get user journeys
journeys = analytics.get_user_journeys('user123')

# Get popular paths
paths = analytics.get_popular_paths(min_length=2, limit=10)
# [(('home', 'dashboard'), 45), (('dashboard', 'settings'), 23)]

# Conversion funnel
funnel = analytics.get_conversion_funnel(
    ['home', 'product', 'checkout', 'confirmation']
)
# {'home': 100, 'product': 75, 'checkout': 30, 'confirmation': 25}

# Drop-off rates
drop_offs = analytics.get_drop_off_points(
    ['home', 'product', 'checkout']
)
# {'home': 0.25, 'product': 0.60}
```

## Complete Example

```python
import streamlit as st
from core import (
    Router, Page, get_router,
    AuthenticationMiddleware, PermissionGuard,
    create_page_container, NavigationHistory,
    render_breadcrumbs
)

# Define pages
class HomePage(Page):
    def render(self):
        st.title("🏠 Home")
        if st.button("Dashboard"):
            self.router.navigate('dashboard')

class DashboardPage(Page):
    def __init__(self, router, session=None):
        super().__init__(router, session)
        self.permissions = {'dashboard.read'}
    
    def render(self):
        st.title("📊 Dashboard")
        # Content

# Setup
def setup():
    router = get_router()
    
    # Register routes
    router.register_route('home', HomePage, title='Home', icon='🏠')
    router.register_route('dashboard', DashboardPage, title='Dashboard')
    
    # Add middleware
    router.register_middleware(AuthenticationMiddleware())
    
    # Add guards
    router.register_guard(PermissionGuard({
        'dashboard': {'dashboard.read'}
    }))
    
    return router

# Main app
def main():
    st.set_page_config(page_title="App", layout="wide")
    
    router = setup()
    
    # Sidebar navigation
    with st.sidebar:
        if st.button("🏠 Home"):
            router.navigate('home')
        if st.button("📊 Dashboard"):
            router.navigate('dashboard')
    
    # Render in stable container
    container = create_page_container(
        f"page_{router.current_page}",
        min_height=600
    )
    container.render(router.render_current_page)

if __name__ == '__main__':
    main()
```

## Best Practices

### 1. Use Stable Containers

Always render pages in stable containers to prevent layout shifts:

```python
container = create_page_container('my_page', min_height=600)
container.render(content_fn)
```

### 2. Register All Routes

Register all routes at application startup:

```python
def setup_routes(router):
    router.register_route('home', HomePage)
    router.register_route('dashboard', DashboardPage)
    # ... all routes
```

### 3. Use Middleware for Cross-Cutting Concerns

Authentication, logging, and other cross-cutting concerns should use middleware:

```python
router.register_middleware(AuthenticationMiddleware())
router.register_middleware(LoggingMiddleware())
```

### 4. Implement Guards for Security

Use guards for permission and role checks:

```python
router.register_guard(PermissionGuard(required_permissions))
router.register_guard(RoleGuard(required_roles))
```

### 5. Track Navigation Events

Always track navigation for analytics:

```python
router.on_navigation(lambda event: analytics.track(event))
```

### 6. Use Breadcrumbs

Provide breadcrumbs for better UX:

```python
breadcrumbs = history.get_breadcrumbs()
render_breadcrumbs(breadcrumbs, on_click=navigate)
```

### 7. Handle Errors Gracefully

Use error boundaries to isolate failures:

```python
boundary = ErrorBoundary('my_page')
boundary.render(content_fn)
```

## Performance Considerations

- Containers maintain fixed sizes to prevent reflows
- Navigation uses session_state (no page reloads)
- History is limited to prevent memory issues
- Analytics use efficient data structures

## Testing

See `test_router.py`, `test_containers.py`, and `test_navigation_history.py` for comprehensive test examples.

## See Also

- [Session Management](SESSION_README.md)
- [Configuration](CONFIG_README.md)
- [Logging](LOGGING_README.md)
