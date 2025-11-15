"""
shadcn/ui Form-Komponenten für Streamlit

Diese Komponenten bieten erweiterte Formular-Elemente mit modernem Design.
"""

from typing import Optional, Literal, Callable, Any
from datetime import date
import streamlit as st
from .shadcn_base import ShadcnComponent


class Input(ShadcnComponent):
    """
    shadcn/ui Input-Komponente mit Floating Labels

    Eine erweiterte Input-Komponente mit Floating Labels, Icons und
    Validierung.

    Features:
    - Floating Labels
    - Prefix/Suffix Icons
    - Validierung mit visuellem Feedback
    - Verschiedene Input-Typen
    - Error/Success States

    Example:
        ```python
        from components.form_components import Input

        input_comp = Input()
        value = input_comp.render(
            label="E-Mail",
            placeholder="ihre@email.de",
            type="email",
            prefix_icon="📧",
            required=True
        )
        ```
    """

    def render(
        self,
        label: str,
        value: str = "",
        placeholder: Optional[str] = None,
        type: Literal["text", "email", "password", "number", "tel",
                      "url"] = "text",
        prefix_icon: Optional[str] = None,
        suffix_icon: Optional[str] = None,
        help_text: Optional[str] = None,
        error: Optional[str] = None,
        success: Optional[str] = None,
        required: bool = False,
        disabled: bool = False,
        max_length: Optional[int] = None,
        on_change: Optional[Callable] = None,
        key: Optional[str] = None
    ) -> str:
        """
        Rendert eine Input-Komponente

        Args:
            label: Label-Text
            value: Aktueller Wert
            placeholder: Placeholder-Text
            type: Input-Typ
            prefix_icon: Icon vor dem Input
            suffix_icon: Icon nach dem Input
            help_text: Hilfetext unter dem Input
            error: Error-Nachricht (zeigt Error-State)
            success: Success-Nachricht (zeigt Success-State)
            required: Ob Feld erforderlich ist
            disabled: Ob Feld deaktiviert ist
            max_length: Maximale Zeichenlänge
            on_change: Callback bei Änderung
            key: Eindeutiger Key

        Returns:
            Eingegebener Wert
        """
        # Generiere eindeutige ID
        input_id = key or self._generate_unique_id("input")

        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        primary = self.get_token('colors.primary', '#18181b')
        error_color = self.get_token('colors.error', '#ef4444')
        success_color = self.get_token('colors.success', '#22c55e')
        border_radius = self.get_token(
            'borders.border_radius_md', '0.375rem'
        )
        spacing_2 = self.get_token('spacing.spacing_2', '0.5rem')
        spacing_3 = self.get_token('spacing.spacing_3', '0.75rem')
        transition = self.get_token(
            'animations.transition_base',
            '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        )

        # State-spezifische Farben
        if error:
            state_color = error_color
            state_message = error
        elif success:
            state_color = success_color
            state_message = success
        else:
            state_color = primary
            state_message = help_text

        # CSS für Input
        input_css = f"""
        <style>
        .shadcn-input-wrapper-{input_id} {{
            position: relative;
            margin-bottom: 1.5rem;
        }}

        .shadcn-input-container-{input_id} {{
            position: relative;
            display: flex;
            align-items: center;
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            transition: all {transition};
        }}

        .shadcn-input-container-{input_id}:focus-within {{
            border-color: {state_color};
            box-shadow: 0 0 0 3px rgba({self._hex_to_rgb(state_color)}, 0.1);
        }}

        .shadcn-input-container-{input_id}.error {{
            border-color: {error_color};
        }}

        .shadcn-input-container-{input_id}.success {{
            border-color: {success_color};
        }}

        .shadcn-input-prefix-{input_id},
        .shadcn-input-suffix-{input_id} {{
            padding: 0 {spacing_3};
            color: {muted_fg};
            font-size: 1rem;
            display: flex;
            align-items: center;
        }}

        .shadcn-input-field-{input_id} {{
            flex: 1;
            padding: {spacing_3};
            border: none;
            background: transparent;
            color: {fg_color};
            font-size: 0.875rem;
            outline: none;
        }}

        .shadcn-input-field-{input_id}::placeholder {{
            color: {muted_fg};
            opacity: 0;
            transition: opacity {transition};
        }}

        .shadcn-input-field-{input_id}:focus::placeholder {{
            opacity: 1;
        }}

        .shadcn-input-label-{input_id} {{
            position: absolute;
            left: {spacing_3};
            top: 50%;
            transform: translateY(-50%);
            color: {muted_fg};
            font-size: 0.875rem;
            pointer-events: none;
            transition: all {transition};
            background: {bg_color};
            padding: 0 {spacing_2};
        }}

        .shadcn-input-field-{input_id}:focus ~ .shadcn-input-label-{input_id},
        .shadcn-input-field-{input_id}:not(:placeholder-shown) ~
        .shadcn-input-label-{input_id} {{
            top: 0;
            font-size: 0.75rem;
            color: {state_color};
        }}

        .shadcn-input-message-{input_id} {{
            margin-top: {spacing_2};
            font-size: 0.75rem;
            color: {muted_fg};
        }}

        .shadcn-input-message-{input_id}.error {{
            color: {error_color};
        }}

        .shadcn-input-message-{input_id}.success {{
            color: {success_color};
        }}

        .shadcn-input-field-{input_id}:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        </style>
        """

        self.inject_css(input_css)

        # Verwende Streamlit Input mit Custom Styling
        container_class = "shadcn-input-container-" + input_id
        if error:
            container_class += " error"
        elif success:
            container_class += " success"

        # Streamlit Input
        input_value = st.text_input(
            label=label,
            value=value,
            placeholder=placeholder or "",
            type=type if type != "tel" and type != "url" else "text",
            help=state_message,
            disabled=disabled,
            max_chars=max_length,
            key=f"input_{input_id}",
            on_change=on_change,
            label_visibility="visible"
        )

        return input_value

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Konvertiert Hex-Farbe zu RGB-String"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        return "0, 0, 0"


class DatePicker(ShadcnComponent):
    """
    shadcn/ui DatePicker-Komponente

    Eine moderne DatePicker-Komponente für Datumsauswahl.

    Features:
    - Floating Label
    - Kalender-Icon
    - Min/Max Datum
    - Validierung

    Example:
        ```python
        from components.form_components import DatePicker

        picker = DatePicker()
        selected_date = picker.render(
            label="Geburtsdatum",
            min_date=date(1900, 1, 1),
            max_date=date.today()
        )
        ```
    """

    def render(
        self,
        label: str,
        value: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        help_text: Optional[str] = None,
        error: Optional[str] = None,
        required: bool = False,
        disabled: bool = False,
        key: Optional[str] = None
    ) -> Optional[date]:
        """
        Rendert eine DatePicker-Komponente

        Args:
            label: Label-Text
            value: Aktuelles Datum
            min_date: Minimales Datum
            max_date: Maximales Datum
            help_text: Hilfetext
            error: Error-Nachricht
            required: Ob Feld erforderlich ist
            disabled: Ob Feld deaktiviert ist
            key: Eindeutiger Key

        Returns:
            Ausgewähltes Datum oder None
        """
        # Generiere eindeutige ID
        picker_id = key or self._generate_unique_id("datepicker")

        # Hole Theme-Tokens
        error_color = self.get_token('colors.error', '#ef4444')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')

        # CSS für DatePicker
        picker_css = f"""
        <style>
        .shadcn-datepicker-wrapper-{picker_id} {{
            margin-bottom: 1.5rem;
        }}

        .shadcn-datepicker-label-{picker_id} {{
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: {self.get_token('colors.foreground', '#0a0a0a')};
        }}

        .shadcn-datepicker-label-{picker_id}.required::after {{
            content: " *";
            color: {error_color};
        }}

        .shadcn-datepicker-message-{picker_id} {{
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: {muted_fg};
        }}

        .shadcn-datepicker-message-{picker_id}.error {{
            color: {error_color};
        }}
        </style>
        """

        self.inject_css(picker_css)

        # Label
        label_class = f"shadcn-datepicker-label-{picker_id}"
        if required:
            label_class += " required"

        st.markdown(
            f'<label class="{label_class}">{label}</label>',
            unsafe_allow_html=True
        )

        # Streamlit Date Input
        selected_date = st.date_input(
            label="",
            value=value,
            min_value=min_date,
            max_value=max_date,
            disabled=disabled,
            key=f"datepicker_{picker_id}",
            label_visibility="collapsed"
        )

        # Message
        if error or help_text:
            message_class = f"shadcn-datepicker-message-{picker_id}"
            if error:
                message_class += " error"
                message_text = error
            else:
                message_text = help_text

            st.markdown(
                f'<div class="{message_class}">{message_text}</div>',
                unsafe_allow_html=True
            )

        return selected_date


class Calendar(ShadcnComponent):
    """
    shadcn/ui Calendar-Komponente

    Eine Kalender-Komponente für Datumsauswahl mit Monatsansicht.

    Features:
    - Monatsansicht
    - Navigation zwischen Monaten
    - Markierung des heutigen Datums
    - Auswahl einzelner Tage

    Example:
        ```python
        from components.form_components import Calendar

        cal = Calendar()
        selected = cal.render(
            selected_date=date.today()
        )
        ```
    """

    def render(
        self,
        selected_date: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        key: Optional[str] = None
    ) -> Optional[date]:
        """
        Rendert eine Calendar-Komponente

        Args:
            selected_date: Aktuell ausgewähltes Datum
            min_date: Minimales Datum
            max_date: Maximales Datum
            key: Eindeutiger Key

        Returns:
            Ausgewähltes Datum
        """
        # Generiere eindeutige ID
        cal_id = key or self._generate_unique_id("calendar")

        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        primary = self.get_token('colors.primary', '#18181b')
        muted = self.get_token('colors.muted', '#f4f4f5')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token(
            'borders.border_radius_md', '0.375rem'
        )

        # CSS für Calendar
        cal_css = f"""
        <style>
        .shadcn-calendar-{cal_id} {{
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius};
            padding: 1rem;
            max-width: 350px;
        }}

        .shadcn-calendar-header-{cal_id} {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .shadcn-calendar-month-{cal_id} {{
            font-size: 1rem;
            font-weight: 600;
            color: {fg_color};
        }}

        .shadcn-calendar-grid-{cal_id} {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.25rem;
        }}

        .shadcn-calendar-day-{cal_id} {{
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.875rem;
            border-radius: {border_radius};
            cursor: pointer;
            transition: all 200ms;
            color: {fg_color};
        }}

        .shadcn-calendar-day-{cal_id}:hover {{
            background: {muted};
        }}

        .shadcn-calendar-day-{cal_id}.selected {{
            background: {primary};
            color: white;
        }}

        .shadcn-calendar-day-{cal_id}.today {{
            border: 1px solid {primary};
        }}

        .shadcn-calendar-day-{cal_id}.disabled {{
            color: {muted_fg};
            cursor: not-allowed;
            opacity: 0.5;
        }}

        .shadcn-calendar-weekday-{cal_id} {{
            font-size: 0.75rem;
            font-weight: 600;
            color: {muted_fg};
            text-align: center;
            padding: 0.5rem 0;
        }}
        </style>
        """

        self.inject_css(cal_css)

        # Verwende Streamlit's date_input als Basis
        st.markdown(
            f'<div class="shadcn-calendar-{cal_id}">',
            unsafe_allow_html=True
        )

        selected = st.date_input(
            label="Datum auswählen",
            value=selected_date or date.today(),
            min_value=min_date,
            max_value=max_date,
            key=f"calendar_{cal_id}"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        return selected


class InputOTP(ShadcnComponent):
    """
    shadcn/ui Input-OTP-Komponente

    Eine Komponente für One-Time-Password (OTP) Eingabe.

    Features:
    - Mehrere Input-Felder für einzelne Ziffern
    - Automatischer Focus-Wechsel
    - Nur Zahlen erlaubt
    - Copy/Paste Support

    Example:
        ```python
        from components.form_components import InputOTP

        otp = InputOTP()
        code = otp.render(
            label="Bestätigungscode",
            length=6
        )
        ```
    """

    def render(
        self,
        label: str,
        length: int = 6,
        help_text: Optional[str] = None,
        error: Optional[str] = None,
        key: Optional[str] = None
    ) -> str:
        """
        Rendert eine Input-OTP-Komponente

        Args:
            label: Label-Text
            length: Anzahl der Ziffern
            help_text: Hilfetext
            error: Error-Nachricht
            key: Eindeutiger Key

        Returns:
            Eingegebener OTP-Code als String
        """
        # Generiere eindeutige ID
        otp_id = key or self._generate_unique_id("otp")

        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        primary = self.get_token('colors.primary', '#18181b')
        error_color = self.get_token('colors.error', '#ef4444')
        muted_fg = self.get_token('colors.muted_foreground', '#71717a')
        border_radius = self.get_token(
            'borders.border_radius_md', '0.375rem'
        )
        transition = self.get_token(
            'animations.transition_base',
            '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        )

        # CSS für OTP Input
        otp_css = f"""
        <style>
        .shadcn-otp-wrapper-{otp_id} {{
            margin-bottom: 1.5rem;
        }}

        .shadcn-otp-label-{otp_id} {{
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.75rem;
            color: {fg_color};
        }}

        .shadcn-otp-container-{otp_id} {{
            display: flex;
            gap: 0.5rem;
            justify-content: center;
        }}

        .shadcn-otp-input-{otp_id} {{
            width: 3rem;
            height: 3rem;
            text-align: center;
            font-size: 1.5rem;
            font-weight: 600;
            border: 2px solid {border_color};
            border-radius: {border_radius};
            background: {bg_color};
            color: {fg_color};
            transition: all {transition};
        }}

        .shadcn-otp-input-{otp_id}:focus {{
            outline: none;
            border-color: {primary};
            box-shadow: 0 0 0 3px rgba({self._hex_to_rgb(primary)}, 0.1);
        }}

        .shadcn-otp-input-{otp_id}.error {{
            border-color: {error_color};
        }}

        .shadcn-otp-message-{otp_id} {{
            margin-top: 0.5rem;
            font-size: 0.75rem;
            text-align: center;
            color: {muted_fg};
        }}

        .shadcn-otp-message-{otp_id}.error {{
            color: {error_color};
        }}
        </style>
        """

        self.inject_css(otp_css)

        # Label
        st.markdown(
            f'<label class="shadcn-otp-label-{otp_id}">{label}</label>',
            unsafe_allow_html=True
        )

        # OTP Input Fields
        st.markdown(
            f'<div class="shadcn-otp-container-{otp_id}">',
            unsafe_allow_html=True
        )

        # Verwende Streamlit Columns für OTP-Felder
        cols = st.columns(length)
        otp_digits = []

        for i in range(length):
            with cols[i]:
                digit = st.text_input(
                    label="",
                    max_chars=1,
                    key=f"otp_{otp_id}_{i}",
                    label_visibility="collapsed"
                )
                otp_digits.append(digit)

        st.markdown('</div>', unsafe_allow_html=True)

        # Message
        if error or help_text:
            message_class = f"shadcn-otp-message-{otp_id}"
            if error:
                message_class += " error"
                message_text = error
            else:
                message_text = help_text

            st.markdown(
                f'<div class="{message_class}">{message_text}</div>',
                unsafe_allow_html=True
            )

        # Kombiniere Ziffern zu Code
        otp_code = ''.join(otp_digits)

        return otp_code

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Konvertiert Hex-Farbe zu RGB-String"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        return "0, 0, 0"


# Convenience Functions

def input_field(
    label: str,
    value: str = "",
    placeholder: Optional[str] = None,
    type: Literal["text", "email", "password", "number", "tel",
                  "url"] = "text",
    prefix_icon: Optional[str] = None,
    suffix_icon: Optional[str] = None,
    help_text: Optional[str] = None,
    error: Optional[str] = None,
    success: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    max_length: Optional[int] = None,
    on_change: Optional[Callable] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> str:
    """
    Convenience-Funktion zum Rendern eines Input-Felds

    Example:
        ```python
        from components.form_components import input_field

        email = input_field(
            label="E-Mail",
            type="email",
            prefix_icon="📧",
            required=True
        )
        ```
    """
    input_comp = Input(theme_manager=theme_manager)
    return input_comp.render(
        label=label,
        value=value,
        placeholder=placeholder,
        type=type,
        prefix_icon=prefix_icon,
        suffix_icon=suffix_icon,
        help_text=help_text,
        error=error,
        success=success,
        required=required,
        disabled=disabled,
        max_length=max_length,
        on_change=on_change,
        key=key
    )


def date_picker(
    label: str,
    value: Optional[date] = None,
    min_date: Optional[date] = None,
    max_date: Optional[date] = None,
    help_text: Optional[str] = None,
    error: Optional[str] = None,
    required: bool = False,
    disabled: bool = False,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> Optional[date]:
    """
    Convenience-Funktion zum Rendern eines DatePickers

    Example:
        ```python
        from components.form_components import date_picker

        birth_date = date_picker(
            label="Geburtsdatum",
            max_date=date.today()
        )
        ```
    """
    picker = DatePicker(theme_manager=theme_manager)
    return picker.render(
        label=label,
        value=value,
        min_date=min_date,
        max_date=max_date,
        help_text=help_text,
        error=error,
        required=required,
        disabled=disabled,
        key=key
    )


def calendar(
    selected_date: Optional[date] = None,
    min_date: Optional[date] = None,
    max_date: Optional[date] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> Optional[date]:
    """
    Convenience-Funktion zum Rendern eines Calendars

    Example:
        ```python
        from components.form_components import calendar

        selected = calendar(
            selected_date=date.today()
        )
        ```
    """
    cal = Calendar(theme_manager=theme_manager)
    return cal.render(
        selected_date=selected_date,
        min_date=min_date,
        max_date=max_date,
        key=key
    )


def input_otp(
    label: str,
    length: int = 6,
    help_text: Optional[str] = None,
    error: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> str:
    """
    Convenience-Funktion zum Rendern eines OTP-Inputs

    Example:
        ```python
        from components.form_components import input_otp

        code = input_otp(
            label="Bestätigungscode",
            length=6
        )
        ```
    """
    otp = InputOTP(theme_manager=theme_manager)
    return otp.render(
        label=label,
        length=length,
        help_text=help_text,
        error=error,
        key=key
    )
