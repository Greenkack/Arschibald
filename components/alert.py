"""
shadcn/ui Alert und AlertDialog-Komponenten für Streamlit

Diese Komponenten bieten moderne Alert-Nachrichten und Dialoge.
"""

from typing import Optional, Literal, Callable, Any
import streamlit as st
from .shadcn_base import ShadcnComponent


class Alert(ShadcnComponent):
    """
    shadcn/ui Alert-Komponente

    Eine flexible Alert-Komponente für Benachrichtigungen und Meldungen.
    Unterstützt verschiedene Typen (info, success, warning, error).

    Features:
    - Verschiedene Alert-Typen mit passenden Farben
    - Icons für jeden Typ
    - Optionaler Titel und Beschreibung
    - Schließbar (dismissible)
    - Responsive Design

    Example:
        ```python
        from components import Alert

        alert = Alert()
        alert.render(
            type="success",
            title="Erfolg!",
            message="Die Aktion wurde erfolgreich ausgeführt.",
            icon=""
        )
        ```
    """

    # Standard-Icons für jeden Alert-Typ
    DEFAULT_ICONS = {
        'info': 'ℹ',
        'success': '',
        'warning': '',
        'error': ''
    }

    def render(
        self,
        message: str,
        type: Literal["info", "success", "warning", "error"] = "info",
        title: Optional[str] = None,
        icon: Optional[str] = None,
        dismissible: bool = False,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        """
        Rendert eine Alert-Komponente

        Args:
            message: Haupt-Nachricht des Alerts
            type: Alert-Typ ('info', 'success', 'warning', 'error')
            title: Optionaler Titel über der Nachricht
            icon: Custom Icon (überschreibt Standard-Icon)
            dismissible: Ob Alert geschlossen werden kann
            custom_css: Zusätzliches Custom-CSS
            key: Eindeutiger Key für die Komponente

        Example:
            ```python
            alert = Alert()
            alert.render(
                message="Daten wurden gespeichert",
                type="success",
                title="Erfolg",
                dismissible=True
            )
            ```
        """
        # Generiere eindeutige ID
        alert_id = key or self._generate_unique_id("alert")

        # Prüfe ob Alert geschlossen wurde
        if dismissible:
            dismissed_key = f"alert_dismissed_{alert_id}"
            if st.session_state.get(dismissed_key, False):
                return

        # Hole Theme-Tokens
        border_radius = self.get_token(
            'borders.border_radius_md', '0.375rem'
        )
        spacing_4 = self.get_token('spacing.spacing_4', '1rem')
        transition = self.get_token(
            'animations.transition_base',
            '200ms cubic-bezier(0.4, 0, 0.2, 1)'
        )

        # Typ-spezifische Farben
        type_colors = {
            'info': {
                'bg': self.get_token('colors.info', '#3b82f6'),
                'fg': '#ffffff',
                'border': self.get_token('colors.info', '#3b82f6'),
                'bg_light': 'rgba(59, 130, 246, 0.1)',
            },
            'success': {
                'bg': self.get_token('colors.success', '#22c55e'),
                'fg': '#ffffff',
                'border': self.get_token('colors.success', '#22c55e'),
                'bg_light': 'rgba(34, 197, 94, 0.1)',
            },
            'warning': {
                'bg': self.get_token('colors.warning', '#f59e0b'),
                'fg': '#ffffff',
                'border': self.get_token('colors.warning', '#f59e0b'),
                'bg_light': 'rgba(245, 158, 11, 0.1)',
            },
            'error': {
                'bg': self.get_token('colors.error', '#ef4444'),
                'fg': '#ffffff',
                'border': self.get_token('colors.error', '#ef4444'),
                'bg_light': 'rgba(239, 68, 68, 0.1)',
            }
        }

        colors = type_colors.get(type, type_colors['info'])

        # Verwende Standard-Icon falls keines angegeben
        if icon is None:
            icon = self.DEFAULT_ICONS.get(type, 'ℹ')

        # CSS für Alert
        alert_css = f"""
        <style>
        .shadcn-alert-{alert_id} {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: {spacing_4};
            border-radius: {border_radius};
            border: 1px solid {colors['border']};
            background: {colors['bg_light']};
            transition: all {transition};
            position: relative;
        }}

        .shadcn-alert-icon-{alert_id} {{
            flex-shrink: 0;
            width: 1.25rem;
            height: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            color: {colors['bg']};
            font-weight: 600;
        }}

        .shadcn-alert-content-{alert_id} {{
            flex: 1;
            min-width: 0;
        }}

        .shadcn-alert-title-{alert_id} {{
            font-size: 0.875rem;
            font-weight: 600;
            color: {colors['bg']};
            margin: 0 0 0.25rem 0;
            line-height: 1.4;
        }}

        .shadcn-alert-message-{alert_id} {{
            font-size: 0.875rem;
            color: {self.get_token('colors.foreground', '#0a0a0a')};
            margin: 0;
            line-height: 1.5;
        }}

        .shadcn-alert-close-{alert_id} {{
            flex-shrink: 0;
            width: 1.25rem;
            height: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: {colors['bg']};
            opacity: 0.7;
            transition: opacity {transition};
            font-size: 1.25rem;
            line-height: 1;
            background: none;
            border: none;
            padding: 0;
        }}

        .shadcn-alert-close-{alert_id}:hover {{
            opacity: 1;
        }}

        {custom_css or ''}
        </style>
        """

        # Injiziere CSS
        st.markdown(alert_css, unsafe_allow_html=True)

        # Baue HTML
        html_parts = [f'<div class="shadcn-alert-{alert_id}">']

        # Icon
        html_parts.append(
            f'<div class="shadcn-alert-icon-{alert_id}">{icon}</div>'
        )

        # Content
        html_parts.append(f'<div class="shadcn-alert-content-{alert_id}">')
        if title:
            html_parts.append(
                f'<div class="shadcn-alert-title-{alert_id}">{title}</div>'
            )
        html_parts.append(
            f'<div class="shadcn-alert-message-{alert_id}">{message}</div>'
        )
        html_parts.append('</div>')

        # Close Button (wenn dismissible)
        if dismissible:
            html_parts.append(
                f'<button class="shadcn-alert-close-{alert_id}" '
                f'onclick="this.parentElement.style.display=\'none\'">×'
                f'</button>'
            )

        html_parts.append('</div>')

        # Rendere HTML
        html = ''.join(html_parts)
        st.markdown(html, unsafe_allow_html=True)

        # Handle Dismiss mit Streamlit Button (für Session State)
        if dismissible:
            col1, col2 = st.columns([0.95, 0.05])
            with col2:
                if st.button(
                    "×",
                    key=f"alert_dismiss_btn_{alert_id}",
                    help="Schließen"
                ):
                    st.session_state[f"alert_dismissed_{alert_id}"] = True
                    st.rerun()


class AlertDialog(ShadcnComponent):
    """
    shadcn/ui AlertDialog-Komponente

    Ein modaler Dialog für wichtige Benachrichtigungen und Bestätigungen.

    Features:
    - Modal-Overlay
    - Titel, Beschreibung und Aktionen
    - Verschiedene Varianten (info, success, warning, error)
    - Anpassbare Buttons

    Example:
        ```python
        from components import AlertDialog

        dialog = AlertDialog()
        if dialog.render(
            title="Bestätigung erforderlich",
            message="Möchten Sie diese Aktion wirklich ausführen?",
            type="warning",
            confirm_text="Ja, fortfahren",
            cancel_text="Abbrechen"
        ):
            # Aktion wurde bestätigt
            st.success("Aktion ausgeführt!")
        ```
    """

    def render(
        self,
        title: str,
        message: str,
        type: Literal["info", "success", "warning", "error"] = "info",
        icon: Optional[str] = None,
        confirm_text: str = "OK",
        cancel_text: Optional[str] = None,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        key: Optional[str] = None
    ) -> bool:
        """
        Rendert einen AlertDialog

        Args:
            title: Dialog-Titel
            message: Dialog-Nachricht
            type: Dialog-Typ ('info', 'success', 'warning', 'error')
            icon: Custom Icon
            confirm_text: Text für Bestätigungs-Button
            cancel_text: Text für Abbrechen-Button (None = kein Button)
            on_confirm: Callback bei Bestätigung
            on_cancel: Callback bei Abbruch
            key: Eindeutiger Key

        Returns:
            True wenn bestätigt, False sonst

        Example:
            ```python
            dialog = AlertDialog()
            confirmed = dialog.render(
                title="Löschen bestätigen",
                message="Wirklich löschen?",
                type="error",
                confirm_text="Löschen",
                cancel_text="Abbrechen"
            )
            if confirmed:
                # Lösch-Aktion durchführen
                pass
            ```
        """
        # Generiere eindeutige ID
        dialog_id = key or self._generate_unique_id("dialog")

        # Hole Theme-Tokens
        bg_color = self.get_token('colors.background', '#ffffff')
        fg_color = self.get_token('colors.foreground', '#0a0a0a')
        border_color = self.get_token('colors.border', '#e4e4e7')
        border_radius = self.get_token(
            'borders.border_radius_lg', '0.5rem'
        )
        spacing_4 = self.get_token('spacing.spacing_4', '1rem')
        spacing_6 = self.get_token('spacing.spacing_6', '1.5rem')
        shadow_xl = self.get_token(
            'shadows.shadow_xl',
            '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
        )

        # Typ-spezifische Farben
        type_colors = {
            'info': self.get_token('colors.info', '#3b82f6'),
            'success': self.get_token('colors.success', '#22c55e'),
            'warning': self.get_token('colors.warning', '#f59e0b'),
            'error': self.get_token('colors.error', '#ef4444'),
        }

        accent_color = type_colors.get(type, type_colors['info'])

        # Standard-Icon
        if icon is None:
            icon = Alert.DEFAULT_ICONS.get(type, 'ℹ')

        # CSS für Dialog
        dialog_css = f"""
        <style>
        .shadcn-dialog-overlay-{dialog_id} {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }}

        .shadcn-dialog-{dialog_id} {{
            background: {bg_color};
            border-radius: {border_radius};
            box-shadow: {shadow_xl};
            padding: {spacing_6};
            max-width: 500px;
            width: 90%;
            border: 1px solid {border_color};
        }}

        .shadcn-dialog-header-{dialog_id} {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin-bottom: {spacing_4};
        }}

        .shadcn-dialog-icon-{dialog_id} {{
            flex-shrink: 0;
            width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: rgba({self._hex_to_rgb(accent_color)}, 0.1);
            color: {accent_color};
            font-size: 1.5rem;
        }}

        .shadcn-dialog-title-{dialog_id} {{
            font-size: 1.125rem;
            font-weight: 600;
            color: {fg_color};
            margin: 0;
            line-height: 1.4;
        }}

        .shadcn-dialog-message-{dialog_id} {{
            font-size: 0.875rem;
            color: {self.get_token('colors.muted_foreground', '#71717a')};
            line-height: 1.6;
            margin-bottom: {spacing_6};
        }}

        .shadcn-dialog-actions-{dialog_id} {{
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
        }}
        </style>
        """

        st.markdown(dialog_css, unsafe_allow_html=True)

        # Verwende Streamlit Columns für Dialog-Layout
        st.markdown(
            f'<div class="shadcn-dialog-overlay-{dialog_id}">',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="shadcn-dialog-{dialog_id}">',
            unsafe_allow_html=True
        )

        # Header mit Icon und Titel
        col1, col2 = st.columns([0.15, 0.85])
        with col1:
            st.markdown(
                f'<div class="shadcn-dialog-icon-{dialog_id}">{icon}</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<h3 class="shadcn-dialog-title-{dialog_id}">{title}</h3>',
                unsafe_allow_html=True
            )

        # Message
        st.markdown(
            f'<p class="shadcn-dialog-message-{dialog_id}">{message}</p>',
            unsafe_allow_html=True
        )

        # Actions
        st.markdown(
            f'<div class="shadcn-dialog-actions-{dialog_id}">',
            unsafe_allow_html=True
        )

        confirmed = False

        # Buttons
        if cancel_text:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    cancel_text,
                    key=f"dialog_cancel_{dialog_id}",
                    use_container_width=True
                ):
                    if on_cancel:
                        on_cancel()
            with col2:
                if st.button(
                    confirm_text,
                    key=f"dialog_confirm_{dialog_id}",
                    type="primary",
                    use_container_width=True
                ):
                    confirmed = True
                    if on_confirm:
                        on_confirm()
        else:
            if st.button(
                confirm_text,
                key=f"dialog_confirm_{dialog_id}",
                type="primary",
                use_container_width=True
            ):
                confirmed = True
                if on_confirm:
                    on_confirm()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        return confirmed

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Konvertiert Hex-Farbe zu RGB-String"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        return "0, 0, 0"


def alert(
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    title: Optional[str] = None,
    icon: Optional[str] = None,
    dismissible: bool = False,
    custom_css: Optional[str] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> None:
    """
    Convenience-Funktion zum Rendern eines Alerts

    Args:
        Siehe Alert.render() für Parameter-Dokumentation

    Example:
        ```python
        from components.alert import alert

        alert(
            message="Erfolgreich gespeichert!",
            type="success",
            title="Erfolg"
        )
        ```
    """
    alert_component = Alert(theme_manager=theme_manager)
    alert_component.render(
        message=message,
        type=type,
        title=title,
        icon=icon,
        dismissible=dismissible,
        custom_css=custom_css,
        key=key
    )


def alert_dialog(
    title: str,
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    icon: Optional[str] = None,
    confirm_text: str = "OK",
    cancel_text: Optional[str] = None,
    on_confirm: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
    key: Optional[str] = None,
    theme_manager: Optional[Any] = None
) -> bool:
    """
    Convenience-Funktion zum Rendern eines AlertDialogs

    Args:
        Siehe AlertDialog.render() für Parameter-Dokumentation

    Returns:
        True wenn bestätigt, False sonst

    Example:
        ```python
        from components.alert import alert_dialog

        if alert_dialog(
            title="Bestätigung",
            message="Fortfahren?",
            type="warning",
            cancel_text="Abbrechen"
        ):
            st.success("Bestätigt!")
        ```
    """
    dialog_component = AlertDialog(theme_manager=theme_manager)
    return dialog_component.render(
        title=title,
        message=message,
        type=type,
        icon=icon,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        key=key
    )
