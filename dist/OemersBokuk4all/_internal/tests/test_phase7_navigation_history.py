"""
Test Suite für Phase 7: Navigation History

Führe umfassende Tests für NavigationHistory, Router-Integration und Widgets aus.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.navigation_history import NavigationHistory, HistoryEntry, Breadcrumb


class TestNavigationHistory:
    """Tests für NavigationHistory Klasse"""
    
    def test_initialization(self):
        """Test NavigationHistory Initialisierung"""
        nav = NavigationHistory(max_size=50)
        assert nav.max_size == 50
        assert len(nav.history) == 0
        assert nav.current_index == -1
    
    def test_push_single_entry(self):
        """Test Push einzelner Entry"""
        nav = NavigationHistory()
        nav.push('home', params={'test': True}, user_id='user_123')
        
        assert len(nav.history) == 1
        assert nav.current_index == 0
        
        entry = nav.get_current()
        assert entry.page == 'home'
        assert entry.params == {'test': True}
        assert entry.user_id == 'user_123'
    
    def test_push_multiple_entries(self):
        """Test Push mehrerer Entries"""
        nav = NavigationHistory()
        
        nav.push('home')
        nav.push('crm', params={'customer_id': 123})
        nav.push('pdf', params={'project_id': 456})
        
        assert len(nav.history) == 3
        assert nav.current_index == 2
        
        current = nav.get_current()
        assert current.page == 'pdf'
        assert current.params == {'project_id': 456}
    
    def test_back_navigation(self):
        """Test Zurück-Navigation"""
        nav = NavigationHistory()
        nav.push('home')
        nav.push('crm')
        nav.push('pdf')
        
        # Back to crm
        entry = nav.back()
        assert entry.page == 'crm'
        assert nav.current_index == 1
        
        # Back to home
        entry = nav.back()
        assert entry.page == 'home'
        assert nav.current_index == 0
        
        # Can't go back further
        entry = nav.back()
        assert entry is None
        assert nav.current_index == 0
    
    def test_forward_navigation(self):
        """Test Vorwärts-Navigation"""
        nav = NavigationHistory()
        nav.push('home')
        nav.push('crm')
        nav.push('pdf')
        
        # Go back twice
        nav.back()
        nav.back()
        assert nav.current_index == 0
        
        # Forward to crm
        entry = nav.forward()
        assert entry.page == 'crm'
        assert nav.current_index == 1
        
        # Forward to pdf
        entry = nav.forward()
        assert entry.page == 'pdf'
        assert nav.current_index == 2
        
        # Can't go forward further
        entry = nav.forward()
        assert entry is None
    
    def test_can_go_back_forward(self):
        """Test can_go_back und can_go_forward"""
        nav = NavigationHistory()
        
        # Empty history
        assert not nav.can_go_back()
        assert not nav.can_go_forward()
        
        # One entry
        nav.push('home')
        assert not nav.can_go_back()
        assert not nav.can_go_forward()
        
        # Two entries
        nav.push('crm')
        assert nav.can_go_back()
        assert not nav.can_go_forward()
        
        # After going back
        nav.back()
        assert not nav.can_go_back()
        assert nav.can_go_forward()
    
    def test_forward_history_removal(self):
        """Test dass Forward-History bei neuem Push entfernt wird"""
        nav = NavigationHistory()
        nav.push('home')
        nav.push('crm')
        nav.push('pdf')
        
        # Go back
        nav.back()  # crm
        nav.back()  # home
        
        # Push new page -> should remove crm and pdf
        nav.push('admin')
        
        assert len(nav.history) == 2
        assert nav.history[0].page == 'home'
        assert nav.history[1].page == 'admin'
        assert not nav.can_go_forward()
    
    def test_max_size_limit(self):
        """Test dass History auf max_size begrenzt wird"""
        nav = NavigationHistory(max_size=3)
        
        nav.push('page1')
        nav.push('page2')
        nav.push('page3')
        nav.push('page4')
        
        assert len(nav.history) == 3
        assert nav.history[0].page == 'page2'  # page1 wurde entfernt
        assert nav.history[-1].page == 'page4'
    
    def test_breadcrumbs_generation(self):
        """Test Breadcrumb-Generierung"""
        nav = NavigationHistory()
        nav.register_page_title('home', 'Startseite')
        nav.register_page_title('crm', 'CRM')
        nav.register_page_title('pdf', 'PDF-Angebote')
        
        nav.push('home')
        nav.push('crm', params={'customer_id': 123})
        nav.push('pdf', params={'project_id': 456})
        
        breadcrumbs = nav.get_breadcrumbs(max_items=5, include_home=True)
        
        assert len(breadcrumbs) == 3
        assert breadcrumbs[0].label == 'Startseite'
        assert breadcrumbs[1].label == 'CRM'
        assert breadcrumbs[2].label == 'PDF-Angebote'
        assert breadcrumbs[2].is_current
        assert not breadcrumbs[0].is_current
    
    def test_breadcrumbs_with_icons(self):
        """Test Breadcrumbs mit Icons"""
        nav = NavigationHistory()
        nav.register_page_title('home', 'Startseite')
        nav.register_page_icon('home', '🏠')
        nav.register_page_title('crm', 'CRM')
        nav.register_page_icon('crm', '👥')
        
        nav.push('home')
        nav.push('crm')
        
        breadcrumbs = nav.get_breadcrumbs()
        
        assert breadcrumbs[0].icon == '🏠'
        assert breadcrumbs[1].icon == '👥'
    
    def test_page_visits_tracking(self):
        """Test Seiten-Besuchs-Tracking"""
        nav = NavigationHistory()
        
        nav.push('home')
        nav.push('crm')
        nav.push('home')
        nav.push('pdf')
        nav.push('home')
        
        visits = nav.get_page_visits()
        
        assert visits['home'] == 3
        assert visits['crm'] == 1
        assert visits['pdf'] == 1
    
    def test_journey_retrieval(self):
        """Test komplette Journey-Abruf"""
        nav = NavigationHistory()
        
        nav.push('home')
        nav.push('crm')
        nav.push('pdf')
        
        journey = nav.get_journey()
        
        assert len(journey) == 3
        assert journey[0].page == 'home'
        assert journey[1].page == 'crm'
        assert journey[2].page == 'pdf'
    
    def test_clear_history(self):
        """Test History-Löschen"""
        nav = NavigationHistory()
        
        nav.push('home')
        nav.push('crm')
        nav.push('pdf')
        
        nav.clear()
        
        assert len(nav.history) == 0
        assert nav.current_index == -1
    
    def test_duration_tracking(self):
        """Test Duration-Tracking zwischen Pages"""
        nav = NavigationHistory()
        
        nav.push('home')
        # Simuliere etwas Zeit
        import time
        time.sleep(0.1)
        nav.push('crm')
        
        # Erste Entry sollte jetzt Duration haben
        first_entry = nav.history[0]
        assert first_entry.duration is not None
        assert first_entry.duration.total_seconds() >= 0.1
    
    def test_pickle_serialization(self):
        """Test Pickle-Serialisierung für Session State"""
        import pickle
        
        nav = NavigationHistory()
        nav.push('home', params={'test': True})
        nav.push('crm', params={'customer_id': 123})
        
        # Serialize
        pickled = pickle.dumps(nav)
        
        # Deserialize
        nav_restored = pickle.loads(pickled)
        
        assert len(nav_restored.history) == 2
        assert nav_restored.current_index == 1
        assert nav_restored.history[0].page == 'home'
        assert nav_restored.history[1].params == {'customer_id': 123}


class TestHistoryEntry:
    """Tests für HistoryEntry Dataclass"""
    
    def test_to_dict(self):
        """Test to_dict Konvertierung"""
        entry = HistoryEntry(
            page='crm',
            params={'customer_id': 123},
            timestamp=datetime.now(),
            duration=timedelta(seconds=10),
            user_id='user_123',
            session_id='session_456',
            metadata={'source': 'button'}
        )
        
        data = entry.to_dict()
        
        assert data['page'] == 'crm'
        assert data['params'] == {'customer_id': 123}
        assert data['duration'] == 10.0
        assert data['user_id'] == 'user_123'
    
    def test_from_dict(self):
        """Test from_dict Konvertierung"""
        data = {
            'page': 'crm',
            'params': {'customer_id': 123},
            'timestamp': datetime.now().isoformat(),
            'duration': 10.0,
            'user_id': 'user_123',
            'session_id': 'session_456',
            'metadata': {'source': 'button'}
        }
        
        entry = HistoryEntry.from_dict(data)
        
        assert entry.page == 'crm'
        assert entry.params == {'customer_id': 123}
        assert entry.duration.total_seconds() == 10.0
        assert entry.user_id == 'user_123'


class TestBreadcrumb:
    """Tests für Breadcrumb Dataclass"""
    
    def test_breadcrumb_creation(self):
        """Test Breadcrumb-Erstellung"""
        bc = Breadcrumb(
            label='CRM',
            page='crm',
            params={'customer_id': 123},
            icon='👥',
            is_current=True
        )
        
        assert bc.label == 'CRM'
        assert bc.page == 'crm'
        assert bc.icon == '👥'
        assert bc.is_current


class TestCoreIntegration:
    """Tests für Core Integration"""
    
    def test_get_navigation_history(self):
        """Test get_navigation_history aus core_integration"""
        from core_integration import get_navigation_history
        
        nav_hist = get_navigation_history()
        
        # Sollte eine Instanz zurückgeben (kann auch None sein wenn deaktiviert)
        assert nav_hist is None or isinstance(nav_hist, NavigationHistory)
    
    def test_track_navigation(self):
        """Test track_navigation Funktion"""
        from core_integration import track_navigation, get_navigation_history, is_feature_enabled
        
        if not is_feature_enabled('navigation'):
            pytest.skip("Navigation feature disabled")
        
        nav_hist = get_navigation_history()
        if not nav_hist:
            pytest.skip("NavigationHistory not available")
        
        # Clear history first
        nav_hist.clear()
        
        # Track navigation
        track_navigation(
            page='test_page',
            user_id='test_user',
            params={'test': True}
        )
        
        # Verify
        assert len(nav_hist.history) >= 1
        current = nav_hist.get_current()
        assert current.page == 'test_page'


def run_tests():
    """Führe alle Tests aus"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
