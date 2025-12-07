"""
Tests für shadcn/ui Sidebar

Testet die Sidebar-Komponente und ihre Funktionalität.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.shadcn_sidebar import (
    MenuItem,
    MenuGroup,
    ShadcnSidebar,
    create_sidebar_menu,
    get_default_menu,
    get_solar_calculator_menu
)


class TestMenuItem:
    """Tests für MenuItem-Klasse"""

    def test_menu_item_creation(self):
        """Test: MenuItem kann erstellt werden"""
        item = MenuItem(
            label="Test",
            icon="",
            key="test",
            disabled=False
        )

        assert item.label == "Test"
        assert item.icon == ""
        assert item.key == "test"
        assert item.disabled is False
        assert item.callback is None

    def test_menu_item_with_callback(self):
        """Test: MenuItem mit Callback"""
        callback = Mock()
        item = MenuItem(
            label="Test",
            key="test",
            callback=callback
        )

        assert item.callback == callback

    def test_menu_item_defaults(self):
        """Test: MenuItem mit Default-Werten"""
        item = MenuItem(label="Test")

        assert item.label == "Test"
        assert item.icon is None
        assert item.key is None
        assert item.callback is None
        assert item.disabled is False


class TestMenuGroup:
    """Tests für MenuGroup-Klasse"""

    def test_menu_group_creation(self):
        """Test: MenuGroup kann erstellt werden"""
        items = [
            MenuItem("Item 1", key="i1"),
            MenuItem("Item 2", key="i2"),
        ]

        group = MenuGroup(
            title="Test Group",
            items=items,
            collapsible=True,
            collapsed=False
        )

        assert group.title == "Test Group"
        assert len(group.items) == 2
        assert group.collapsible is True
        assert group.collapsed is False

    def test_menu_group_defaults(self):
        """Test: MenuGroup mit Default-Werten"""
        items = [MenuItem("Item", key="i")]
        group = MenuGroup(title="Test", items=items)

        assert group.title == "Test"
        assert group.items == items
        assert group.collapsible is False
        assert group.collapsed is False


class TestShadcnSidebar:
    """Tests für ShadcnSidebar-Klasse"""

    @patch('utils.shadcn_sidebar.st')
    def test_sidebar_initialization(self, mock_st):
        """Test: Sidebar kann initialisiert werden"""
        mock_st.session_state = MagicMock()
        mock_st.session_state.get.return_value = None
        mock_st.session_state.__contains__ = lambda self, key: False
        
        sidebar = ShadcnSidebar()

        assert sidebar.theme_manager is None

    @patch('utils.shadcn_sidebar.st')
    def test_sidebar_with_theme_manager(self, mock_st):
        """Test: Sidebar mit ThemeManager"""
        mock_st.session_state = MagicMock()
        mock_st.session_state.__contains__ = lambda self, key: False
        theme_manager = Mock()

        sidebar = ShadcnSidebar(theme_manager)

        assert sidebar.theme_manager == theme_manager

    def test_get_token_without_theme_manager(self):
        """Test: get_token ohne ThemeManager gibt Default zurück"""
        with patch('utils.shadcn_sidebar.st'):
            sidebar = ShadcnSidebar()
            sidebar.theme_manager = None

            token = sidebar.get_token('colors.primary', '#000000')

            assert token == '#000000'

    @patch('utils.shadcn_sidebar.st')
    def test_get_token_with_theme_manager(self, mock_st):
        """Test: get_token mit ThemeManager"""
        mock_st.session_state = MagicMock()
        mock_st.session_state.__contains__ = lambda self, key: False
        theme_manager = Mock()
        theme_manager.get_token.return_value = '#18181b'

        sidebar = ShadcnSidebar(theme_manager)
        token = sidebar.get_token('colors.primary', '#000000')

        assert token == '#18181b'
        theme_manager.get_token.assert_called_once_with('colors.primary')

    @patch('utils.shadcn_sidebar.st')
    def test_inject_sidebar_css(self, mock_st):
        """Test: CSS-Injection"""
        mock_st.session_state = MagicMock()
        mock_st.session_state.__contains__ = lambda self, key: False
        mock_st.markdown = Mock()
        
        sidebar = ShadcnSidebar()
        sidebar.inject_sidebar_css()

        # Prüfe ob st.markdown aufgerufen wurde
        assert mock_st.markdown.called
        call_args = mock_st.markdown.call_args
        assert '<style>' in call_args[0][0]
        assert 'shadcn-menu-item' in call_args[0][0]


class TestPredefinedMenus:
    """Tests für vordefinierte Menüs"""

    def test_get_default_menu(self):
        """Test: Standard-Menü"""
        menu = get_default_menu()

        assert isinstance(menu, list)
        assert len(menu) == 3
        assert all(isinstance(g, MenuGroup) for g in menu)

        # Prüfe erste Gruppe
        assert menu[0].title == "Hauptmenü"
        assert len(menu[0].items) == 3

    def test_get_solar_calculator_menu(self):
        """Test: Solar-Rechner-Menü"""
        menu = get_solar_calculator_menu()

        assert isinstance(menu, list)
        assert len(menu) == 3
        assert all(isinstance(g, MenuGroup) for g in menu)

        # Prüfe erste Gruppe
        assert menu[0].title == "Kalkulation"
        assert any(
            item.label == "Solar-Rechner"
            for item in menu[0].items
        )


class TestConvenienceFunction:
    """Tests für Convenience-Funktionen"""

    @patch('utils.shadcn_sidebar.ShadcnSidebar')
    def test_create_sidebar_menu(self, mock_sidebar_class):
        """Test: create_sidebar_menu Funktion"""
        mock_sidebar = Mock()
        mock_sidebar.render.return_value = "test_key"
        mock_sidebar_class.return_value = mock_sidebar

        groups = [
            MenuGroup(
                title="Test",
                items=[MenuItem("Item", key="item")]
            )
        ]

        result = create_sidebar_menu(groups)

        assert result == "test_key"
        mock_sidebar_class.assert_called_once()
        mock_sidebar.render.assert_called_once()


class TestIntegration:
    """Integrations-Tests"""

    def test_full_menu_structure(self):
        """Test: Vollständige Menü-Struktur"""
        groups = [
            MenuGroup(
                title="Group 1",
                items=[
                    MenuItem("Item 1", icon="", key="i1"),
                    MenuItem("Item 2", icon="", key="i2"),
                ]
            ),
            MenuGroup(
                title="Group 2",
                items=[
                    MenuItem("Item 3", icon="", key="i3"),
                ],
                collapsible=True,
                collapsed=True
            )
        ]

        # Prüfe Struktur
        assert len(groups) == 2
        assert len(groups[0].items) == 2
        assert len(groups[1].items) == 1
        assert groups[1].collapsible is True

    def test_menu_with_callbacks(self):
        """Test: Menü mit Callbacks"""
        callback_called = []

        def callback1():
            callback_called.append(1)

        def callback2():
            callback_called.append(2)

        items = [
            MenuItem("Item 1", key="i1", callback=callback1),
            MenuItem("Item 2", key="i2", callback=callback2),
        ]

        # Simuliere Klicks
        items[0].callback()
        items[1].callback()

        assert callback_called == [1, 2]

    def test_disabled_items(self):
        """Test: Deaktivierte Einträge"""
        items = [
            MenuItem("Active", key="active", disabled=False),
            MenuItem("Disabled", key="disabled", disabled=True),
        ]

        assert items[0].disabled is False
        assert items[1].disabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
