"""Example usage of Container-Based Navigation System"""

import streamlit as st

from core import (
    AuthenticationMiddleware,
    LoggingMiddleware,
    NavigationHistory,
    Page,
    PermissionGuard,
    RoleGuard,
    create_page_container,
    get_router,
    render_breadcrumbs,
)


# Define custom pages
class HomePage(Page):
    """Home page"""

    def render(self):
        st.title("🏠 Home Page")
        st.write("Welcome to the robust Streamlit application!")

        if st.button("Go to Dashboard"):
            self.router.navigate('dashboard')

        if st.button("Go to Settings"):
            self.router.navigate('settings')


class DashboardPage(Page):
    """Dashboard page"""

    def __init__(self, router, session=None):
        super().__init__(router, session)
        self.permissions = {'dashboard.read'}

    def render(self):
        st.title("📊 Dashboard")
        st.write("This is the dashboard page.")

        # Show navigation controls
        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back") and self.router.can_go_back():
                self.router.go_back()

        with col2:
            if st.button("Forward →") and self.router.can_go_forward():
                self.router.go_forward()

        # Show some data
        st.metric("Active Users", "1,234")
        st.metric("Revenue", "$56,789")


class SettingsPage(Page):
    """Settings page"""

    def __init__(self, router, session=None):
        super().__init__(router, session)
        self.permissions = {'settings.read', 'settings.write'}

    def render(self):
        st.title("⚙️ Settings")
        st.write("Configure your application settings.")

        # Settings form
        with st.form("settings_form"):
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            notifications = st.checkbox("Enable notifications")
            language = st.selectbox(
                "Language", [
                    "English", "German", "French"])

            if st.form_submit_button("Save Settings"):
                st.success("Settings saved!")


class AdminPage(Page):
    """Admin page (requires admin role)"""

    def __init__(self, router, session=None):
        super().__init__(router, session)
        self.permissions = {'admin.read', 'admin.write'}

    def render(self):
        st.title("👑 Admin Panel")
        st.write("Administrative functions.")

        st.warning("This page requires admin privileges.")


def setup_router():
    """Setup router with pages, middleware, and guards"""
    router = get_router()

    # Register pages
    router.register_route(
        'home',
        HomePage,
        title='Home',
        icon='🏠'
    )

    router.register_route(
        'dashboard',
        DashboardPage,
        title='Dashboard',
        icon='📊'
    )

    router.register_route(
        'settings',
        SettingsPage,
        title='Settings',
        icon='⚙️'
    )

    router.register_route(
        'admin',
        AdminPage,
        title='Admin',
        icon='👑',
        guards=[
            RoleGuard(required_roles={'admin': {'admin', 'superuser'}})
        ]
    )

    # Register middleware
    router.register_middleware(LoggingMiddleware())
    router.register_middleware(
        AuthenticationMiddleware(public_pages={'home', 'login'})
    )

    # Register global guards
    router.register_guard(
        PermissionGuard(required_permissions={
            'dashboard': {'dashboard.read'},
            'settings': {'settings.read'},
            'admin': {'admin.read', 'admin.write'}
        })
    )

    # Register navigation event handler
    def on_navigation(event):
        """Track navigation events"""
        st.session_state.setdefault('nav_events', []).append(event.to_dict())

    router.on_navigation(on_navigation)

    return router


def main():
    """Main application"""
    st.set_page_config(
        page_title="Navigation Example",
        page_icon="🧭",
        layout="wide"
    )

    # Setup router
    router = setup_router()

    # Initialize session with permissions
    if 'user_session' not in st.session_state:
        from core import UserSession
        session = UserSession(
            user_id='demo_user',
            permissions={'dashboard.read', 'settings.read', 'settings.write'},
            roles={'user'}
        )
        st.session_state.user_session = session

    # Sidebar navigation
    with st.sidebar:
        st.title("🧭 Navigation")

        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            router.navigate('home')

        if st.button("📊 Dashboard", use_container_width=True):
            router.navigate('dashboard')

        if st.button("⚙️ Settings", use_container_width=True):
            router.navigate('settings')

        if st.button("👑 Admin", use_container_width=True):
            router.navigate('admin')

        st.divider()

        # Navigation history
        st.subheader("History")
        if router.can_go_back():
            if st.button("← Back", use_container_width=True):
                router.go_back()

        if router.can_go_forward():
            if st.button("Forward →", use_container_width=True):
                router.go_forward()

        # Show current page
        st.info(f"Current: {router.current_page}")

    # Breadcrumbs
    session = st.session_state.user_session
    if hasattr(session, 'navigation_history'):
        history = NavigationHistory()
        history.register_page_title('home', 'Home')
        history.register_page_title('dashboard', 'Dashboard')
        history.register_page_title('settings', 'Settings')
        history.register_page_title('admin', 'Admin')

        for entry in session.navigation_history:
            history.push(entry.page, entry.params)

        breadcrumbs = history.get_breadcrumbs()
        render_breadcrumbs(
            breadcrumbs,
            on_click=lambda page, params: router.navigate(page, params)
        )

    # Create page container for stable rendering
    page_container = create_page_container(
        f"page_{router.current_page}",
        min_height=600
    )

    # Render current page in stable container
    page_container.render(
        content_fn=router.render_current_page,
        loading=False
    )

    # Show navigation analytics in expander
    with st.expander("📊 Navigation Analytics"):
        if 'nav_events' in st.session_state:
            st.write(f"Total navigations: {len(st.session_state.nav_events)}")

            # Show recent events
            recent = st.session_state.nav_events[-5:]
            for event in reversed(recent):
                st.text(
                    f"{event['event_type']}: "
                    f"{event['from_page']} → {event['to_page']}"
                )


if __name__ == '__main__':
    main()
