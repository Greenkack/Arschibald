"""Stable Container System for Layout Stability"""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

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


class ContainerState(str, Enum):
    """Container states"""
    IDLE = "idle"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    EMPTY = "empty"


@dataclass
class ContainerConfig:
    """Configuration for stable containers"""
    min_height: int | None = None  # Minimum height in pixels
    max_height: int | None = None  # Maximum height in pixels
    fixed_height: int | None = None  # Fixed height in pixels
    border: bool = False
    use_container_width: bool = True
    show_loading: bool = True
    loading_text: str = "Loading..."
    error_boundary: bool = True
    placeholder_content: Callable[[], None] | None = None


class StableContainer:
    """
    Fixed-size container that prevents layout shifts

    This container maintains a stable size during content loading
    and transitions, preventing UI jumps.
    """

    def __init__(
        self,
        container_id: str,
        config: ContainerConfig = None
    ):
        """
        Initialize stable container

        Args:
            container_id: Unique container identifier
            config: Container configuration
        """
        self.container_id = container_id
        self.config = config or ContainerConfig()
        self.state = ContainerState.IDLE
        self._container = None
        self._error: str | None = None

    def _get_container_style(self) -> str:
        """Generate CSS style for container"""
        styles = []

        if self.config.fixed_height:
            styles.append(f"height: {self.config.fixed_height}px")
        else:
            if self.config.min_height:
                styles.append(f"min-height: {self.config.min_height}px")
            if self.config.max_height:
                styles.append(f"max-height: {self.config.max_height}px")

        if self.config.border:
            styles.append("border: 1px solid #ddd")
            styles.append("border-radius: 4px")
            styles.append("padding: 1rem")

        styles.append("overflow: auto")

        return "; ".join(styles)

    def render(self, content_fn: Callable[[], None]) -> None:
        """
        Render container with content

        Args:
            content_fn: Function that renders content
        """
        if not STREAMLIT_AVAILABLE or not st:
            return

        try:
            # Create container with stable styling
            style = self._get_container_style()

            if style:
                st.markdown(
                    f'<div id="{self.container_id}" style="{style}">',
                    unsafe_allow_html=True
                )

            # Create Streamlit container
            with st.container():
                if self.config.error_boundary:
                    try:
                        self.state = ContainerState.LOADING
                        content_fn()
                        self.state = ContainerState.LOADED
                    except Exception as e:
                        self.state = ContainerState.ERROR
                        self._error = str(e)
                        logger.error(
                            "Container error",
                            container_id=self.container_id,
                            error=str(e),
                            exc_info=True
                        )
                        self._render_error()
                else:
                    content_fn()

            if style:
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            logger.error(
                "Container render error",
                container_id=self.container_id,
                error=str(e),
                exc_info=True
            )
            if self.config.error_boundary:
                self._render_error()
            else:
                raise

    def _render_error(self) -> None:
        """Render error state"""
        if st:
            st.error(f"Error in container: {self._error}")

    @contextmanager
    def loading(self):
        """Context manager for loading state"""
        if not STREAMLIT_AVAILABLE or not st:
            yield
            return

        self.state = ContainerState.LOADING

        if self.config.show_loading:
            placeholder = st.empty()
            with placeholder.container():
                if self.config.placeholder_content:
                    self.config.placeholder_content()
                else:
                    st.info(self.config.loading_text)

        try:
            yield
            self.state = ContainerState.LOADED
        except Exception as e:
            self.state = ContainerState.ERROR
            self._error = str(e)
            raise
        finally:
            if self.config.show_loading:
                placeholder.empty()


class PlaceholderContainer:
    """
    Placeholder container for loading states without spinners

    Maintains layout stability by showing a placeholder
    instead of dynamic content insertion.
    """

    def __init__(
        self,
        container_id: str,
        height: int = 200,
        show_progress: bool = True
    ):
        """
        Initialize placeholder container

        Args:
            container_id: Unique container identifier
            height: Container height in pixels
            show_progress: Show progress bar instead of spinner
        """
        self.container_id = container_id
        self.height = height
        self.show_progress = show_progress
        self._placeholder = None

    def show(self, message: str = "Loading...", progress: float = None):
        """
        Show placeholder

        Args:
            message: Loading message
            progress: Progress value (0.0 to 1.0)
        """
        if not STREAMLIT_AVAILABLE or not st:
            return

        if self._placeholder is None:
            self._placeholder = st.empty()

        with self._placeholder.container():
            # Fixed height container
            st.markdown(
                f'<div style="height: {self.height}px; '
                f'display: flex; align-items: center; '
                f'justify-content: center; flex-direction: column;">',
                unsafe_allow_html=True
            )

            if self.show_progress and progress is not None:
                st.progress(progress, text=message)
            elif self.show_progress:
                st.progress(0.0, text=message)
            else:
                st.info(message)

            st.markdown('</div>', unsafe_allow_html=True)

    def update_progress(self, progress: float, message: str = None):
        """
        Update progress

        Args:
            progress: Progress value (0.0 to 1.0)
            message: Optional message
        """
        if message:
            self.show(message, progress)
        else:
            self.show(progress=progress)

    def clear(self):
        """Clear placeholder"""
        if self._placeholder:
            self._placeholder.empty()
            self._placeholder = None


class TransitionContainer:
    """
    Container with smooth transitions

    Provides fade-in/fade-out effects for content changes
    without layout shifts.
    """

    def __init__(
        self,
        container_id: str,
        transition_duration_ms: int = 300
    ):
        """
        Initialize transition container

        Args:
            container_id: Unique container identifier
            transition_duration_ms: Transition duration in milliseconds
        """
        self.container_id = container_id
        self.transition_duration_ms = transition_duration_ms

    def render(
        self,
        content_fn: Callable[[], None],
        fade_in: bool = True
    ) -> None:
        """
        Render content with transition

        Args:
            content_fn: Function that renders content
            fade_in: Apply fade-in effect
        """
        if not STREAMLIT_AVAILABLE or not st:
            return

        # Apply CSS transition
        if fade_in:
            st.markdown(
                f"""
                <style>
                #{self.container_id} {{
                    animation: fadeIn {self.transition_duration_ms}ms;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

        # Render content in container
        st.markdown(
            f'<div id="{self.container_id}">',
            unsafe_allow_html=True
        )

        with st.container():
            content_fn()

        st.markdown('</div>', unsafe_allow_html=True)


class ErrorBoundary:
    """
    Error boundary for isolated error handling

    Catches errors in a container and displays them
    without affecting other parts of the UI.
    """

    def __init__(
        self,
        container_id: str,
        fallback_fn: Callable[[Exception], None] | None = None
    ):
        """
        Initialize error boundary

        Args:
            container_id: Unique container identifier
            fallback_fn: Optional fallback render function
        """
        self.container_id = container_id
        self.fallback_fn = fallback_fn
        self._error: Exception | None = None

    @contextmanager
    def catch(self):
        """Context manager for error catching"""
        try:
            yield
        except Exception as e:
            self._error = e
            logger.error(
                "Error boundary caught error",
                container_id=self.container_id,
                error=str(e),
                exc_info=True
            )
            self._render_error()

    def _render_error(self):
        """Render error state"""
        if not STREAMLIT_AVAILABLE or not st:
            return

        if self.fallback_fn:
            try:
                self.fallback_fn(self._error)
            except Exception as e:
                logger.error(
                    "Fallback render error",
                    container_id=self.container_id,
                    error=str(e)
                )
                st.error(f"Error: {str(self._error)}")
        else:
            st.error(
                f"An error occurred in {self.container_id}: "
                f"{str(self._error)}"
            )

    def render(self, content_fn: Callable[[], None]) -> None:
        """
        Render content with error boundary

        Args:
            content_fn: Function that renders content
        """
        with self.catch():
            content_fn()


class PageContainer:
    """
    Main page container for stable page rendering

    Combines stable container, placeholder, and error boundary
    for complete page stability.
    """

    def __init__(
        self,
        page_id: str,
        min_height: int = 600,
        show_loading: bool = True
    ):
        """
        Initialize page container

        Args:
            page_id: Unique page identifier
            min_height: Minimum page height in pixels
            show_loading: Show loading placeholder
        """
        self.page_id = page_id
        self.min_height = min_height
        self.show_loading = show_loading

        # Create sub-containers
        self.stable_container = StableContainer(
            container_id=f"{page_id}_stable",
            config=ContainerConfig(
                min_height=min_height,
                error_boundary=True,
                show_loading=show_loading
            )
        )

        self.placeholder = PlaceholderContainer(
            container_id=f"{page_id}_placeholder",
            height=min_height
        )

        self.error_boundary = ErrorBoundary(
            container_id=f"{page_id}_error"
        )

    def render(
        self,
        content_fn: Callable[[], None],
        loading: bool = False,
        loading_message: str = "Loading page..."
    ) -> None:
        """
        Render page content

        Args:
            content_fn: Function that renders page content
            loading: Show loading state
            loading_message: Loading message
        """
        if loading:
            self.placeholder.show(loading_message)
        else:
            self.placeholder.clear()
            self.stable_container.render(content_fn)

    @contextmanager
    def loading_context(self, message: str = "Loading..."):
        """
        Context manager for loading state

        Args:
            message: Loading message
        """
        self.placeholder.show(message)
        try:
            yield
        finally:
            self.placeholder.clear()


# Container registry for managing multiple containers
class ContainerRegistry:
    """Registry for managing stable containers"""

    def __init__(self):
        self.containers: dict[str, StableContainer] = {}
        self.placeholders: dict[str, PlaceholderContainer] = {}
        self.page_containers: dict[str, PageContainer] = {}

    def register_container(
        self,
        container_id: str,
        config: ContainerConfig = None
    ) -> StableContainer:
        """Register a stable container"""
        container = StableContainer(container_id, config)
        self.containers[container_id] = container
        return container

    def register_placeholder(
        self,
        container_id: str,
        height: int = 200
    ) -> PlaceholderContainer:
        """Register a placeholder container"""
        placeholder = PlaceholderContainer(container_id, height)
        self.placeholders[container_id] = placeholder
        return placeholder

    def register_page(
        self,
        page_id: str,
        min_height: int = 600
    ) -> PageContainer:
        """Register a page container"""
        page_container = PageContainer(page_id, min_height)
        self.page_containers[page_id] = page_container
        return page_container

    def get_container(self, container_id: str) -> StableContainer | None:
        """Get container by ID"""
        return self.containers.get(container_id)

    def get_placeholder(
        self,
        container_id: str
    ) -> PlaceholderContainer | None:
        """Get placeholder by ID"""
        return self.placeholders.get(container_id)

    def get_page(self, page_id: str) -> PageContainer | None:
        """Get page container by ID"""
        return self.page_containers.get(page_id)


# Global container registry
_registry: ContainerRegistry | None = None


def get_container_registry() -> ContainerRegistry:
    """Get global container registry"""
    global _registry
    if _registry is None:
        _registry = ContainerRegistry()
    return _registry


# Convenience functions
def create_stable_container(
    container_id: str,
    config: ContainerConfig = None
) -> StableContainer:
    """Create and register a stable container"""
    registry = get_container_registry()
    return registry.register_container(container_id, config)


def create_placeholder(
    container_id: str,
    height: int = 200
) -> PlaceholderContainer:
    """Create and register a placeholder container"""
    registry = get_container_registry()
    return registry.register_placeholder(container_id, height)


def create_page_container(
    page_id: str,
    min_height: int = 600
) -> PageContainer:
    """Create and register a page container"""
    registry = get_container_registry()
    return registry.register_page(page_id, min_height)
