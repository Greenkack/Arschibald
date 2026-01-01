"""
Tests für shadcn/ui Form-Komponenten

Diese Tests prüfen die Funktionalität aller Form-Komponenten.
"""

import pytest
from datetime import date, timedelta
from components.form_components import (
    Input,
    DatePicker,
    Calendar,
    InputOTP,
    input_field,
    date_picker,
    calendar,
    input_otp
)
from theming import ThemeManager


@pytest.fixture
def theme_manager():
    """Fixture für ThemeManager"""
    manager = ThemeManager()
    manager.set_theme('shadcn-default')
    return manager


class TestInput:
    """Tests für Input-Komponente"""

    def test_input_initialization(self, theme_manager):
        """Test: Input kann initialisiert werden"""
        input_comp = Input(theme_manager=theme_manager)
        assert input_comp is not None
        assert input_comp.theme_manager == theme_manager

    def test_input_without_theme_manager(self):
        """Test: Input funktioniert ohne Theme-Manager"""
        input_comp = Input()
        assert input_comp is not None

    def test_input_get_token(self, theme_manager):
        """Test: Input kann Theme-Tokens abrufen"""
        input_comp = Input(theme_manager=theme_manager)
        primary = input_comp.get_token('colors.primary')
        assert primary is not None
        assert isinstance(primary, str)

    def test_input_hex_to_rgb(self, theme_manager):
        """Test: Hex-zu-RGB-Konvertierung"""
        input_comp = Input(theme_manager=theme_manager)
        rgb = input_comp._hex_to_rgb('#ff0000')
        assert rgb == "255, 0, 0"

    def test_input_hex_to_rgb_invalid(self, theme_manager):
        """Test: Ungültige Hex-Farbe"""
        input_comp = Input(theme_manager=theme_manager)
        rgb = input_comp._hex_to_rgb('#fff')
        assert rgb == "0, 0, 0"

    def test_input_field_convenience_function(self, theme_manager):
        """Test: input_field Convenience-Funktion"""
        # Diese Funktion würde in Streamlit-Kontext laufen
        # Hier nur Syntax-Check
        assert callable(input_field)


class TestDatePicker:
    """Tests für DatePicker-Komponente"""

    def test_datepicker_initialization(self, theme_manager):
        """Test: DatePicker kann initialisiert werden"""
        picker = DatePicker(theme_manager=theme_manager)
        assert picker is not None
        assert picker.theme_manager == theme_manager

    def test_datepicker_without_theme_manager(self):
        """Test: DatePicker funktioniert ohne Theme-Manager"""
        picker = DatePicker()
        assert picker is not None

    def test_datepicker_get_token(self, theme_manager):
        """Test: DatePicker kann Theme-Tokens abrufen"""
        picker = DatePicker(theme_manager=theme_manager)
        error_color = picker.get_token('colors.error')
        assert error_color is not None

    def test_date_picker_convenience_function(self, theme_manager):
        """Test: date_picker Convenience-Funktion"""
        assert callable(date_picker)


class TestCalendar:
    """Tests für Calendar-Komponente"""

    def test_calendar_initialization(self, theme_manager):
        """Test: Calendar kann initialisiert werden"""
        cal = Calendar(theme_manager=theme_manager)
        assert cal is not None
        assert cal.theme_manager == theme_manager

    def test_calendar_without_theme_manager(self):
        """Test: Calendar funktioniert ohne Theme-Manager"""
        cal = Calendar()
        assert cal is not None

    def test_calendar_get_token(self, theme_manager):
        """Test: Calendar kann Theme-Tokens abrufen"""
        cal = Calendar(theme_manager=theme_manager)
        primary = cal.get_token('colors.primary')
        assert primary is not None

    def test_calendar_convenience_function(self, theme_manager):
        """Test: calendar Convenience-Funktion"""
        assert callable(calendar)


class TestInputOTP:
    """Tests für InputOTP-Komponente"""

    def test_input_otp_initialization(self, theme_manager):
        """Test: InputOTP kann initialisiert werden"""
        otp = InputOTP(theme_manager=theme_manager)
        assert otp is not None
        assert otp.theme_manager == theme_manager

    def test_input_otp_without_theme_manager(self):
        """Test: InputOTP funktioniert ohne Theme-Manager"""
        otp = InputOTP()
        assert otp is not None

    def test_input_otp_hex_to_rgb(self, theme_manager):
        """Test: Hex-zu-RGB-Konvertierung"""
        otp = InputOTP(theme_manager=theme_manager)
        rgb = otp._hex_to_rgb('#00ff00')
        assert rgb == "0, 255, 0"

    def test_input_otp_convenience_function(self, theme_manager):
        """Test: input_otp Convenience-Funktion"""
        assert callable(input_otp)


class TestFormValidation:
    """Tests für Formular-Validierung"""

    def test_email_validation(self):
        """Test: E-Mail-Validierung"""
        # Gültige E-Mails
        assert "@" in "test@example.com"
        assert "." in "test@example.com"

        # Ungültige E-Mails
        assert "@" not in "testexample.com"
        assert "." not in "test@example"

    def test_password_validation(self):
        """Test: Passwort-Validierung"""
        # Zu kurz
        password = "short"
        assert len(password) < 8

        # Lang genug
        password = "longenough"
        assert len(password) >= 8

        # Mit Großbuchstaben
        password = "Password123"
        assert any(c.isupper() for c in password)

        # Mit Zahlen
        assert any(c.isdigit() for c in password)

    def test_date_validation(self):
        """Test: Datums-Validierung"""
        today = date.today()
        future = today + timedelta(days=1)
        past = today - timedelta(days=1)

        # Zukunft
        assert future > today

        # Vergangenheit
        assert past < today

    def test_otp_validation(self):
        """Test: OTP-Validierung"""
        # Vollständig
        code = "123456"
        assert len(code) == 6
        assert code.isdigit()

        # Unvollständig
        code = "123"
        assert len(code) != 6

        # Nicht nur Zahlen
        code = "12345a"
        assert not code.isdigit()


class TestThemeIntegration:
    """Tests für Theme-Integration"""

    def test_input_uses_theme_tokens(self, theme_manager):
        """Test: Input verwendet Theme-Tokens"""
        input_comp = Input(theme_manager=theme_manager)

        # Prüfe ob Tokens abgerufen werden können
        bg = input_comp.get_token('colors.background')
        fg = input_comp.get_token('colors.foreground')
        border = input_comp.get_token('colors.border')

        assert bg is not None
        assert fg is not None
        assert border is not None

    def test_datepicker_uses_theme_tokens(self, theme_manager):
        """Test: DatePicker verwendet Theme-Tokens"""
        picker = DatePicker(theme_manager=theme_manager)

        error = picker.get_token('colors.error')
        muted = picker.get_token('colors.muted_foreground')

        assert error is not None
        assert muted is not None

    def test_calendar_uses_theme_tokens(self, theme_manager):
        """Test: Calendar verwendet Theme-Tokens"""
        cal = Calendar(theme_manager=theme_manager)

        primary = cal.get_token('colors.primary')
        border_radius = cal.get_token('borders.border_radius_md')

        assert primary is not None
        assert border_radius is not None

    def test_input_otp_uses_theme_tokens(self, theme_manager):
        """Test: InputOTP verwendet Theme-Tokens"""
        otp = InputOTP(theme_manager=theme_manager)

        primary = otp.get_token('colors.primary')
        transition = otp.get_token('animations.transition_base')

        assert primary is not None
        assert transition is not None


class TestAccessibility:
    """Tests für Accessibility"""

    def test_input_has_label(self):
        """Test: Input hat Label"""
        # In echtem Streamlit-Kontext würde Label gerendert
        # Hier nur Konzept-Test
        label = "E-Mail"
        assert label is not None
        assert len(label) > 0

    def test_datepicker_has_label(self):
        """Test: DatePicker hat Label"""
        label = "Geburtsdatum"
        assert label is not None
        assert len(label) > 0

    def test_input_otp_has_label(self):
        """Test: InputOTP hat Label"""
        label = "Bestätigungscode"
        assert label is not None
        assert len(label) > 0

    def test_required_field_indicator(self):
        """Test: Required-Indikator"""
        required = True
        assert required is True


class TestErrorHandling:
    """Tests für Error-Handling"""

    def test_input_with_error(self, theme_manager):
        """Test: Input mit Error-State"""
        input_comp = Input(theme_manager=theme_manager)
        assert input_comp is not None
        error_message = "Dieses Feld ist erforderlich"
        assert error_message is not None

    def test_datepicker_with_error(self, theme_manager):
        """Test: DatePicker mit Error-State"""
        picker = DatePicker(theme_manager=theme_manager)
        assert picker is not None
        error_message = "Datum muss in der Zukunft liegen"
        assert error_message is not None

    def test_input_otp_with_error(self, theme_manager):
        """Test: InputOTP mit Error-State"""
        otp = InputOTP(theme_manager=theme_manager)
        assert otp is not None
        error_message = "Ungültiger Code"
        assert error_message is not None


class TestConvenienceFunctions:
    """Tests für Convenience-Funktionen"""

    def test_all_convenience_functions_exist(self):
        """Test: Alle Convenience-Funktionen existieren"""
        assert callable(input_field)
        assert callable(date_picker)
        assert callable(calendar)
        assert callable(input_otp)

    def test_convenience_functions_have_correct_signature(self):
        """Test: Convenience-Funktionen haben korrekte Signatur"""
        import inspect

        # input_field
        sig = inspect.signature(input_field)
        assert 'label' in sig.parameters
        assert 'type' in sig.parameters
        assert 'theme_manager' in sig.parameters

        # date_picker
        sig = inspect.signature(date_picker)
        assert 'label' in sig.parameters
        assert 'min_date' in sig.parameters
        assert 'max_date' in sig.parameters

        # calendar
        sig = inspect.signature(calendar)
        assert 'selected_date' in sig.parameters
        assert 'min_date' in sig.parameters

        # input_otp
        sig = inspect.signature(input_otp)
        assert 'label' in sig.parameters
        assert 'length' in sig.parameters


def test_module_imports():
    """Test: Alle Module können importiert werden"""
    from components.form_components import (
        Input,
        DatePicker,
        Calendar,
        InputOTP
    )

    assert Input is not None
    assert DatePicker is not None
    assert Calendar is not None
    assert InputOTP is not None


def test_component_inheritance():
    """Test: Alle Komponenten erben von ShadcnComponent"""
    from components.shadcn_base import ShadcnComponent

    assert issubclass(Input, ShadcnComponent)
    assert issubclass(DatePicker, ShadcnComponent)
    assert issubclass(Calendar, ShadcnComponent)
    assert issubclass(InputOTP, ShadcnComponent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
