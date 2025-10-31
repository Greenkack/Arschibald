"""Navigation History Management with Analytics"""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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


@dataclass
class HistoryEntry:
    """Navigation history entry with metadata"""
    page: str
    params: dict[str, Any]
    timestamp: datetime
    duration: timedelta | None = None
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'page': self.page,
            'params': self.params,
            'timestamp': self.timestamp.isoformat(),
            'duration': (
                self.duration.total_seconds() if self.duration else None
            ),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        duration = None
        if data.get('duration'):
            duration = timedelta(seconds=data['duration'])

        return cls(
            page=data['page'],
            params=data['params'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            duration=duration,
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            metadata=data.get('metadata', {})
        )


@dataclass
class Breadcrumb:
    """Breadcrumb item for navigation"""
    label: str
    page: str
    params: dict[str, Any] = field(default_factory=dict)
    icon: str | None = None
    is_current: bool = False


class NavigationHistory:
    """
    Navigation history stack with parameter preservation

    Manages navigation history with support for back/forward,
    breadcrumbs, and analytics.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize navigation history

        Args:
            max_size: Maximum history size
        """
        self.max_size = max_size
        self.history: deque[HistoryEntry] = deque(maxlen=max_size)
        self.current_index: int = -1
        self._page_titles: dict[str, str] = {}
        self._page_icons: dict[str, str] = {}

    def push(
        self,
        page: str,
        params: dict[str, Any] = None,
        user_id: str = None,
        session_id: str = None,
        metadata: dict[str, Any] = None
    ) -> None:
        """
        Push new entry to history

        Args:
            page: Page name
            params: Page parameters
            user_id: User ID
            session_id: Session ID
            metadata: Additional metadata
        """
        # Update duration of previous entry
        if self.history and self.current_index >= 0:
            prev_entry = self.history[self.current_index]
            prev_entry.duration = datetime.now() - prev_entry.timestamp

        # Remove forward history if we're not at the end
        if self.current_index < len(self.history) - 1:
            # Keep only entries up to current index
            entries_to_keep = list(self.history)[:self.current_index + 1]
            self.history.clear()
            self.history.extend(entries_to_keep)

        # Create new entry
        entry = HistoryEntry(
            page=page,
            params=params or {},
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )

        self.history.append(entry)
        self.current_index = len(self.history) - 1

        logger.debug(
            "Navigation history push",
            page=page,
            index=self.current_index,
            size=len(self.history)
        )

    def back(self) -> HistoryEntry | None:
        """
        Navigate back in history

        Returns:
            Previous history entry or None
        """
        if self.can_go_back():
            self.current_index -= 1
            entry = self.history[self.current_index]
            logger.debug("Navigation back", page=entry.page)
            return entry
        return None

    def forward(self) -> HistoryEntry | None:
        """
        Navigate forward in history

        Returns:
            Next history entry or None
        """
        if self.can_go_forward():
            self.current_index += 1
            entry = self.history[self.current_index]
            logger.debug("Navigation forward", page=entry.page)
            return entry
        return None

    def can_go_back(self) -> bool:
        """Check if can navigate back"""
        return self.current_index > 0

    def can_go_forward(self) -> bool:
        """Check if can navigate forward"""
        return self.current_index < len(self.history) - 1

    def get_current(self) -> HistoryEntry | None:
        """Get current history entry"""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None

    def get_previous(self) -> HistoryEntry | None:
        """Get previous history entry"""
        if self.current_index > 0:
            return self.history[self.current_index - 1]
        return None

    def clear(self) -> None:
        """Clear history"""
        self.history.clear()
        self.current_index = -1
        logger.debug("Navigation history cleared")

    def register_page_title(self, page: str, title: str) -> None:
        """Register page title for breadcrumbs"""
        self._page_titles[page] = title

    def register_page_icon(self, page: str, icon: str) -> None:
        """Register page icon for breadcrumbs"""
        self._page_icons[page] = icon

    def get_breadcrumbs(
        self,
        max_items: int = 5,
        include_home: bool = True
    ) -> list[Breadcrumb]:
        """
        Generate breadcrumbs from navigation history

        Args:
            max_items: Maximum number of breadcrumb items
            include_home: Include home page in breadcrumbs

        Returns:
            List of breadcrumb items
        """
        breadcrumbs = []

        # Add home if requested
        if include_home:
            breadcrumbs.append(Breadcrumb(
                label=self._page_titles.get('home', 'Home'),
                page='home',
                icon=self._page_icons.get('home', '🏠'),
                is_current=False
            ))

        # Get relevant history entries
        if self.current_index >= 0:
            # Get path to current page
            start_idx = max(0, self.current_index - max_items + 1)
            entries = list(self.history)[start_idx:self.current_index + 1]

            # Skip home if already added
            if include_home and entries and entries[0].page == 'home':
                entries = entries[1:]

            # Create breadcrumbs
            for i, entry in enumerate(entries):
                is_current = (i == len(entries) - 1)
                breadcrumbs.append(Breadcrumb(
                    label=self._page_titles.get(entry.page, entry.page),
                    page=entry.page,
                    params=entry.params,
                    icon=self._page_icons.get(entry.page),
                    is_current=is_current
                ))

        return breadcrumbs

    def get_journey(self) -> list[HistoryEntry]:
        """
        Get complete user journey

        Returns:
            List of all history entries
        """
        return list(self.history)

    def get_page_visits(self) -> dict[str, int]:
        """
        Get page visit counts

        Returns:
            Dictionary of page -> visit count
        """
        visits: dict[str, int] = {}
        for entry in self.history:
            visits[entry.page] = visits.get(entry.page, 0) + 1
        return visits

    def get_average_duration(self, page: str = None) -> timedelta | None:
        """
        Get average page duration

        Args:
            page: Optional page name (None for all pages)

        Returns:
            Average duration or None
        """
        durations = []

        for entry in self.history:
            if entry.duration and (page is None or entry.page == page):
                durations.append(entry.duration)

        if not durations:
            return None

        total = sum(durations, timedelta())
        return total / len(durations)

    def get_most_visited_pages(self, limit: int = 5) -> list[tuple[str, int]]:
        """
        Get most visited pages

        Args:
            limit: Maximum number of pages to return

        Returns:
            List of (page, count) tuples
        """
        visits = self.get_page_visits()
        sorted_visits = sorted(
            visits.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_visits[:limit]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'max_size': self.max_size,
            'history': [entry.to_dict() for entry in self.history],
            'current_index': self.current_index,
            'page_titles': self._page_titles,
            'page_icons': self._page_icons
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'NavigationHistory':
        """Create from dictionary"""
        history = cls(max_size=data.get('max_size', 100))
        history.current_index = data.get('current_index', -1)
        history._page_titles = data.get('page_titles', {})
        history._page_icons = data.get('page_icons', {})

        for entry_data in data.get('history', []):
            entry = HistoryEntry.from_dict(entry_data)
            history.history.append(entry)

        return history


class NavigationAnalytics:
    """
    Navigation analytics for user journey tracking

    Tracks and analyzes user navigation patterns.
    """

    def __init__(self):
        self.sessions: dict[str, NavigationHistory] = {}

    def track_navigation(
        self,
        session_id: str,
        page: str,
        params: dict[str, Any] = None,
        user_id: str = None,
        metadata: dict[str, Any] = None
    ) -> None:
        """
        Track navigation event

        Args:
            session_id: Session ID
            page: Page name
            params: Page parameters
            user_id: User ID
            metadata: Additional metadata
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = NavigationHistory()

        history = self.sessions[session_id]
        history.push(page, params, user_id, session_id, metadata)

        logger.debug(
            "Navigation tracked",
            session_id=session_id,
            page=page,
            user_id=user_id
        )

    def get_session_history(
        self,
        session_id: str
    ) -> NavigationHistory | None:
        """Get navigation history for session"""
        return self.sessions.get(session_id)

    def get_user_journeys(self, user_id: str) -> list[list[HistoryEntry]]:
        """
        Get all journeys for a user

        Args:
            user_id: User ID

        Returns:
            List of journeys (each journey is a list of entries)
        """
        journeys = []

        for history in self.sessions.values():
            user_entries = [
                entry for entry in history.get_journey()
                if entry.user_id == user_id
            ]
            if user_entries:
                journeys.append(user_entries)

        return journeys

    def get_popular_paths(
        self,
        min_length: int = 2,
        limit: int = 10
    ) -> list[tuple[tuple[str, ...], int]]:
        """
        Get popular navigation paths

        Args:
            min_length: Minimum path length
            limit: Maximum number of paths to return

        Returns:
            List of (path, count) tuples
        """
        paths: dict[tuple[str, ...], int] = {}

        for history in self.sessions.values():
            journey = history.get_journey()

            # Extract paths of different lengths
            for i in range(len(journey) - min_length + 1):
                for length in range(min_length, min(len(journey) - i + 1, 6)):
                    path = tuple(
                        entry.page for entry in journey[i:i + length]
                    )
                    paths[path] = paths.get(path, 0) + 1

        # Sort by count
        sorted_paths = sorted(
            paths.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_paths[:limit]

    def get_conversion_funnel(
        self,
        funnel_pages: list[str]
    ) -> dict[str, int]:
        """
        Calculate conversion funnel

        Args:
            funnel_pages: List of pages in funnel order

        Returns:
            Dictionary of page -> count
        """
        funnel_counts = dict.fromkeys(funnel_pages, 0)

        for history in self.sessions.values():
            journey = history.get_journey()
            pages_visited = {entry.page for entry in journey}

            # Track which funnel steps were completed
            for page in funnel_pages:
                if page in pages_visited:
                    funnel_counts[page] += 1

        return funnel_counts

    def get_drop_off_points(
        self,
        funnel_pages: list[str]
    ) -> dict[str, float]:
        """
        Calculate drop-off rates in funnel

        Args:
            funnel_pages: List of pages in funnel order

        Returns:
            Dictionary of page -> drop-off rate
        """
        funnel_counts = self.get_conversion_funnel(funnel_pages)
        drop_offs = {}

        for i in range(len(funnel_pages) - 1):
            current_page = funnel_pages[i]
            next_page = funnel_pages[i + 1]

            current_count = funnel_counts[current_page]
            next_count = funnel_counts[next_page]

            if current_count > 0:
                drop_off_rate = (current_count - next_count) / current_count
                drop_offs[current_page] = drop_off_rate
            else:
                drop_offs[current_page] = 0.0

        return drop_offs


# Global navigation analytics
_analytics: NavigationAnalytics | None = None


def get_navigation_analytics() -> NavigationAnalytics:
    """Get global navigation analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = NavigationAnalytics()
    return _analytics


# Breadcrumb rendering helper
def render_breadcrumbs(
    breadcrumbs: list[Breadcrumb],
    on_click: Callable[[str, dict[str, Any]], None] | None = None
) -> None:
    """
    Render breadcrumbs in Streamlit

    Args:
        breadcrumbs: List of breadcrumb items
        on_click: Optional click handler
    """
    if not STREAMLIT_AVAILABLE or not st:
        return

    if not breadcrumbs:
        return

    # Render breadcrumbs
    cols = st.columns(len(breadcrumbs) * 2 - 1)

    for i, breadcrumb in enumerate(breadcrumbs):
        col_idx = i * 2

        with cols[col_idx]:
            if breadcrumb.is_current:
                # Current page - not clickable
                label = breadcrumb.label
                if breadcrumb.icon:
                    label = f"{breadcrumb.icon} {label}"
                st.markdown(f"**{label}**")
            else:
                # Previous page - clickable
                label = breadcrumb.label
                if breadcrumb.icon:
                    label = f"{breadcrumb.icon} {label}"

                if on_click and st.button(
                    label,
                    key=f"breadcrumb_{breadcrumb.page}_{i}"
                ):
                    on_click(breadcrumb.page, breadcrumb.params)

        # Add separator
        if i < len(breadcrumbs) - 1:
            with cols[col_idx + 1]:
                st.markdown("›")
