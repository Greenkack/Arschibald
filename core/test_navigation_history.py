"""Tests for Navigation History Management"""

from datetime import datetime, timedelta

import pytest

from .navigation_history import (
    Breadcrumb,
    HistoryEntry,
    NavigationAnalytics,
    NavigationHistory,
    get_navigation_analytics,
)


class TestHistoryEntry:
    """Test HistoryEntry class"""

    def test_history_entry_creation(self):
        """Test history entry creation"""
        entry = HistoryEntry(
            page='test',
            params={'id': '123'},
            timestamp=datetime.now(),
            user_id='user123',
            session_id='session123'
        )

        assert entry.page == 'test'
        assert entry.params == {'id': '123'}
        assert entry.user_id == 'user123'
        assert entry.session_id == 'session123'
        assert entry.duration is None

    def test_history_entry_to_dict(self):
        """Test history entry serialization"""
        entry = HistoryEntry(
            page='test',
            params={'id': '123'},
            timestamp=datetime.now(),
            duration=timedelta(seconds=30)
        )

        data = entry.to_dict()

        assert data['page'] == 'test'
        assert data['params'] == {'id': '123'}
        assert 'timestamp' in data
        assert data['duration'] == 30.0

    def test_history_entry_from_dict(self):
        """Test history entry deserialization"""
        data = {
            'page': 'test',
            'params': {'id': '123'},
            'timestamp': datetime.now().isoformat(),
            'duration': 45.0,
            'user_id': 'user123',
            'session_id': 'session123',
            'metadata': {'source': 'test'}
        }

        entry = HistoryEntry.from_dict(data)

        assert entry.page == 'test'
        assert entry.params == {'id': '123'}
        assert entry.duration == timedelta(seconds=45)
        assert entry.user_id == 'user123'
        assert entry.metadata == {'source': 'test'}


class TestBreadcrumb:
    """Test Breadcrumb class"""

    def test_breadcrumb_creation(self):
        """Test breadcrumb creation"""
        breadcrumb = Breadcrumb(
            label='Test Page',
            page='test',
            params={'id': '123'},
            icon='🧪',
            is_current=True
        )

        assert breadcrumb.label == 'Test Page'
        assert breadcrumb.page == 'test'
        assert breadcrumb.params == {'id': '123'}
        assert breadcrumb.icon == '🧪'
        assert breadcrumb.is_current is True


class TestNavigationHistory:
    """Test NavigationHistory class"""

    def test_history_initialization(self):
        """Test history initialization"""
        history = NavigationHistory(max_size=50)

        assert history.max_size == 50
        assert len(history.history) == 0
        assert history.current_index == -1

    def test_push_entry(self):
        """Test pushing entry to history"""
        history = NavigationHistory()
        history.push('home', {'test': 'value'})

        assert len(history.history) == 1
        assert history.current_index == 0
        assert history.history[0].page == 'home'
        assert history.history[0].params == {'test': 'value'}

    def test_push_multiple_entries(self):
        """Test pushing multiple entries"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('page2')

        assert len(history.history) == 3
        assert history.current_index == 2
        assert history.history[2].page == 'page2'

    def test_push_updates_duration(self):
        """Test that push updates previous entry duration"""
        history = NavigationHistory()
        history.push('home')

        # Small delay
        import time
        time.sleep(0.1)

        history.push('page1')

        # Previous entry should have duration
        assert history.history[0].duration is not None
        assert history.history[0].duration.total_seconds() > 0

    def test_back_navigation(self):
        """Test back navigation"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('page2')

        entry = history.back()

        assert entry is not None
        assert entry.page == 'page1'
        assert history.current_index == 1

    def test_back_at_start(self):
        """Test back navigation at start"""
        history = NavigationHistory()
        history.push('home')

        entry = history.back()

        assert entry is None
        assert history.current_index == 0

    def test_forward_navigation(self):
        """Test forward navigation"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('page2')

        history.back()
        entry = history.forward()

        assert entry is not None
        assert entry.page == 'page2'
        assert history.current_index == 2

    def test_forward_at_end(self):
        """Test forward navigation at end"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')

        entry = history.forward()

        assert entry is None
        assert history.current_index == 1

    def test_can_go_back(self):
        """Test can_go_back check"""
        history = NavigationHistory()
        assert history.can_go_back() is False

        history.push('home')
        assert history.can_go_back() is False

        history.push('page1')
        assert history.can_go_back() is True

    def test_can_go_forward(self):
        """Test can_go_forward check"""
        history = NavigationHistory()
        assert history.can_go_forward() is False

        history.push('home')
        history.push('page1')
        assert history.can_go_forward() is False

        history.back()
        assert history.can_go_forward() is True

    def test_get_current(self):
        """Test getting current entry"""
        history = NavigationHistory()
        assert history.get_current() is None

        history.push('home')
        current = history.get_current()
        assert current is not None
        assert current.page == 'home'

    def test_get_previous(self):
        """Test getting previous entry"""
        history = NavigationHistory()
        assert history.get_previous() is None

        history.push('home')
        assert history.get_previous() is None

        history.push('page1')
        previous = history.get_previous()
        assert previous is not None
        assert previous.page == 'home'

    def test_clear_history(self):
        """Test clearing history"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')

        history.clear()

        assert len(history.history) == 0
        assert history.current_index == -1

    def test_register_page_title(self):
        """Test registering page title"""
        history = NavigationHistory()
        history.register_page_title('home', 'Home Page')

        assert history._page_titles['home'] == 'Home Page'

    def test_register_page_icon(self):
        """Test registering page icon"""
        history = NavigationHistory()
        history.register_page_icon('home', '🏠')

        assert history._page_icons['home'] == '🏠'

    def test_get_breadcrumbs_empty(self):
        """Test getting breadcrumbs with empty history"""
        history = NavigationHistory()
        breadcrumbs = history.get_breadcrumbs()

        # Should have home breadcrumb
        assert len(breadcrumbs) == 1
        assert breadcrumbs[0].page == 'home'

    def test_get_breadcrumbs_with_history(self):
        """Test getting breadcrumbs with history"""
        history = NavigationHistory()
        history.register_page_title('home', 'Home')
        history.register_page_title('page1', 'Page 1')
        history.register_page_title('page2', 'Page 2')

        history.push('home')
        history.push('page1')
        history.push('page2')

        breadcrumbs = history.get_breadcrumbs()

        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].page == 'home'
        assert breadcrumbs[1].page == 'page1'
        assert breadcrumbs[2].page == 'page2'
        assert breadcrumbs[2].is_current is True

    def test_get_breadcrumbs_max_items(self):
        """Test breadcrumbs with max items limit"""
        history = NavigationHistory()

        for i in range(10):
            history.push(f'page{i}')

        breadcrumbs = history.get_breadcrumbs(max_items=3)

        # Should have home + 3 items
        assert len(breadcrumbs) <= 4

    def test_get_journey(self):
        """Test getting complete journey"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('page2')

        journey = history.get_journey()

        assert len(journey) == 3
        assert journey[0].page == 'home'
        assert journey[2].page == 'page2'

    def test_get_page_visits(self):
        """Test getting page visit counts"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('home')
        history.push('page2')
        history.push('home')

        visits = history.get_page_visits()

        assert visits['home'] == 3
        assert visits['page1'] == 1
        assert visits['page2'] == 1

    def test_get_most_visited_pages(self):
        """Test getting most visited pages"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')
        history.push('home')
        history.push('page2')
        history.push('home')

        most_visited = history.get_most_visited_pages(limit=2)

        assert len(most_visited) == 2
        assert most_visited[0] == ('home', 3)
        assert most_visited[1][1] == 1  # Either page1 or page2

    def test_history_serialization(self):
        """Test history serialization"""
        history = NavigationHistory()
        history.push('home')
        history.push('page1')

        data = history.to_dict()

        assert 'max_size' in data
        assert 'history' in data
        assert 'current_index' in data
        assert len(data['history']) == 2

    def test_history_deserialization(self):
        """Test history deserialization"""
        data = {
            'max_size': 50,
            'current_index': 1,
            'history': [
                {
                    'page': 'home',
                    'params': {},
                    'timestamp': datetime.now().isoformat(),
                    'duration': None,
                    'user_id': None,
                    'session_id': None,
                    'metadata': {}
                },
                {
                    'page': 'page1',
                    'params': {'id': '123'},
                    'timestamp': datetime.now().isoformat(),
                    'duration': None,
                    'user_id': None,
                    'session_id': None,
                    'metadata': {}
                }
            ],
            'page_titles': {'home': 'Home'},
            'page_icons': {'home': '🏠'}
        }

        history = NavigationHistory.from_dict(data)

        assert history.max_size == 50
        assert history.current_index == 1
        assert len(history.history) == 2
        assert history._page_titles == {'home': 'Home'}


class TestNavigationAnalytics:
    """Test NavigationAnalytics class"""

    def test_analytics_initialization(self):
        """Test analytics initialization"""
        analytics = NavigationAnalytics()

        assert analytics.sessions == {}

    def test_track_navigation(self):
        """Test tracking navigation"""
        analytics = NavigationAnalytics()
        analytics.track_navigation(
            session_id='session123',
            page='home',
            user_id='user123'
        )

        assert 'session123' in analytics.sessions
        history = analytics.sessions['session123']
        assert len(history.history) == 1

    def test_track_multiple_sessions(self):
        """Test tracking multiple sessions"""
        analytics = NavigationAnalytics()
        analytics.track_navigation('session1', 'home')
        analytics.track_navigation('session2', 'home')

        assert len(analytics.sessions) == 2

    def test_get_session_history(self):
        """Test getting session history"""
        analytics = NavigationAnalytics()
        analytics.track_navigation('session123', 'home')

        history = analytics.get_session_history('session123')

        assert history is not None
        assert len(history.history) == 1

    def test_get_user_journeys(self):
        """Test getting user journeys"""
        analytics = NavigationAnalytics()
        analytics.track_navigation('session1', 'home', user_id='user123')
        analytics.track_navigation('session1', 'page1', user_id='user123')
        analytics.track_navigation('session2', 'home', user_id='user456')

        journeys = analytics.get_user_journeys('user123')

        assert len(journeys) == 1
        assert len(journeys[0]) == 2

    def test_get_popular_paths(self):
        """Test getting popular paths"""
        analytics = NavigationAnalytics()

        # Create common path
        for i in range(3):
            analytics.track_navigation(f'session{i}', 'home')
            analytics.track_navigation(f'session{i}', 'page1')
            analytics.track_navigation(f'session{i}', 'page2')

        paths = analytics.get_popular_paths(min_length=2, limit=5)

        assert len(paths) > 0
        # Most popular should be home -> page1
        assert paths[0][0] == ('home', 'page1')
        assert paths[0][1] == 3

    def test_get_conversion_funnel(self):
        """Test conversion funnel calculation"""
        analytics = NavigationAnalytics()

        # Session 1: completes funnel
        analytics.track_navigation('session1', 'home')
        analytics.track_navigation('session1', 'product')
        analytics.track_navigation('session1', 'checkout')

        # Session 2: drops off at product
        analytics.track_navigation('session2', 'home')
        analytics.track_navigation('session2', 'product')

        # Session 3: only home
        analytics.track_navigation('session3', 'home')

        funnel = analytics.get_conversion_funnel(
            ['home', 'product', 'checkout']
        )

        assert funnel['home'] == 3
        assert funnel['product'] == 2
        assert funnel['checkout'] == 1

    def test_get_drop_off_points(self):
        """Test drop-off rate calculation"""
        analytics = NavigationAnalytics()

        # Create funnel data
        for i in range(10):
            analytics.track_navigation(f'session{i}', 'home')

        for i in range(7):
            analytics.track_navigation(f'session{i}', 'product')

        for i in range(3):
            analytics.track_navigation(f'session{i}', 'checkout')

        drop_offs = analytics.get_drop_off_points(
            ['home', 'product', 'checkout']
        )

        # 30% drop-off from home to product
        assert drop_offs['home'] == pytest.approx(0.3, abs=0.01)
        # ~57% drop-off from product to checkout
        assert drop_offs['product'] == pytest.approx(0.57, abs=0.01)


class TestGlobalAnalytics:
    """Test global analytics functions"""

    def test_get_navigation_analytics(self):
        """Test getting global analytics"""
        analytics1 = get_navigation_analytics()
        analytics2 = get_navigation_analytics()

        # Should return same instance
        assert analytics1 is analytics2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
