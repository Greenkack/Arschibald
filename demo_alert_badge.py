"""
Demo für Alert und Badge Komponenten

Zeigt alle Features der Alert und Badge Komponenten.
"""

import streamlit as st
from components.alert import Alert, AlertDialog, alert
from components.badge import Badge, BadgeGroup, badge, badge_group

# Seiten-Konfiguration
st.set_page_config(
    page_title="Alert & Badge Demo",
    page_
    layout="wide"
)

st.title(" Alert & Badge Komponenten Demo")
st.markdown("---")

# Tabs für verschiedene Komponenten
tab1, tab2, tab3, tab4 = st.tabs([
    "Alert", "AlertDialog", "Badge", "Badge Group"
])

# Tab 1: Alert
with tab1:
    st.header("Alert Komponente")
    st.markdown("""
    Die Alert-Komponente zeigt wichtige Nachrichten und Benachrichtigungen an.
    """)

    st.subheader("Alert-Typen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Info Alert**")
        alert_component = Alert()
        alert_component.render(
            message=(
                "Dies ist eine Info-Nachricht mit "
                "wichtigen Informationen."
            ),
            type="info",
            title="Information",
            key="alert_info_1"
        )

        st.markdown("**Success Alert**")
        alert_component.render(
            message="Die Aktion wurde erfolgreich ausgeführt!",
            type="success",
            title="Erfolg",
            key="alert_success_1"
        )

    with col2:
        st.markdown("**Warning Alert**")
        alert_component.render(
            message="Bitte beachten Sie diese wichtige Warnung.",
            type="warning",
            title="Warnung",
            key="alert_warning_1"
        )

        st.markdown("**Error Alert**")
        alert_component.render(
            message=(
                "Ein Fehler ist aufgetreten. "
                "Bitte versuchen Sie es erneut."
            ),
            type="error",
            title="Fehler",
            key="alert_error_1"
        )

    st.markdown("---")
    st.subheader("Alert mit Custom Icons")

    col1, col2 = st.columns(2)

    with col1:
        alert_component.render(
            message="Neue Nachricht erhalten",
            type="info",
            title="Posteingang",
            key="alert_custom_1"
        )

    with col2:
        alert_component.render(
            message="Daten wurden gespeichert",
            type="success",
            key="alert_custom_2"
        )

    st.markdown("---")
    st.subheader("Dismissible Alert")

    alert_component.render(
        message=(
            "Dieser Alert kann geschlossen werden. "
            "Klicken Sie auf das X."
        ),
        type="info",
        title="Schließbar",
        dismissible=True,
        key="alert_dismissible_1"
    )

    st.markdown("---")
    st.subheader("Alert ohne Titel")

    alert_component.render(
        message="Dies ist ein einfacher Alert ohne Titel.",
        type="success",
        key="alert_no_title"
    )

    st.markdown("---")
    st.subheader("Convenience-Funktion")
    st.code("""
from components.alert import alert

alert(
    message="Schneller Alert mit Convenience-Funktion",
    type="info",
    title="Einfach"
)
    """)

    alert(
        message="Schneller Alert mit Convenience-Funktion",
        type="info",
        title="Einfach",
        key="alert_convenience"
    )

# Tab 2: AlertDialog
with tab2:
    st.header("AlertDialog Komponente")
    st.markdown("""
    Der AlertDialog zeigt modale Dialoge für wichtige Bestätigungen an.
    """)

    st.subheader("Dialog-Typen")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Info Dialog anzeigen", key="btn_info_dialog"):
            dialog = AlertDialog()
            if dialog.render(
                title="Information",
                message=(
                    "Dies ist ein Info-Dialog mit "
                    "wichtigen Informationen."
                ),
                type="info",
                confirm_text="Verstanden",
                key="dialog_info"
            ):
                st.success("Dialog bestätigt!")

        if st.button(
            "Success Dialog anzeigen", key="btn_success_dialog"
        ):
            dialog = AlertDialog()
            if dialog.render(
                title="Erfolg",
                message="Die Aktion wurde erfolgreich ausgeführt!",
                type="success",
                confirm_text="OK",
                key="dialog_success"
            ):
                st.success("Dialog bestätigt!")

    with col2:
        if st.button(
            "Warning Dialog anzeigen", key="btn_warning_dialog"
        ):
            dialog = AlertDialog()
            if dialog.render(
                title="Warnung",
                message="Möchten Sie wirklich fortfahren?",
                type="warning",
                confirm_text="Ja, fortfahren",
                cancel_text="Abbrechen",
                key="dialog_warning"
            ):
                st.success("Aktion bestätigt!")
            else:
                st.info("Aktion abgebrochen")

        if st.button(
            "Error Dialog anzeigen", key="btn_error_dialog"
        ):
            dialog = AlertDialog()
            if dialog.render(
                title="Fehler",
                message="Ein kritischer Fehler ist aufgetreten.",
                type="error",
                confirm_text="OK",
                key="dialog_error"
            ):
                st.success("Dialog geschlossen")

    st.markdown("---")
    st.subheader("Dialog mit Callbacks")

    def on_confirm_callback():
        st.session_state.confirmed = True
        st.success("Bestätigt via Callback!")

    def on_cancel_callback():
        st.session_state.confirmed = False
        st.info("Abgebrochen via Callback!")

    if st.button("Dialog mit Callbacks", key="btn_callback_dialog"):
        dialog = AlertDialog()
        dialog.render(
            title="Bestätigung erforderlich",
            message="Möchten Sie diese Aktion ausführen?",
            type="warning",
            confirm_text="Bestätigen",
            cancel_text="Abbrechen",
            on_confirm=on_confirm_callback,
            on_cancel=on_cancel_callback,
            key="dialog_callback"
        )

# Tab 3: Badge
with tab3:
    st.header("Badge Komponente")
    st.markdown("""
    Die Badge-Komponente zeigt Labels, Status und Tags an.
    """)

    st.subheader("Badge-Varianten")

    badge_component = Badge()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Default**")
        badge_component.render(
            text="Default", variant="default", key="badge_default"
        )

        st.markdown("**Secondary**")
        badge_component.render(
            text="Secondary", variant="secondary", key="badge_secondary"
        )

        st.markdown("**Outline**")
        badge_component.render(
            text="Outline", variant="outline", key="badge_outline"
        )

    with col2:
        st.markdown("**Success**")
        badge_component.render(
            text="Success", variant="success", key="badge_success"
        )

        st.markdown("**Warning**")
        badge_component.render(
            text="Warning", variant="warning", key="badge_warning"
        )

        st.markdown("**Error**")
        badge_component.render(
            text="Error", variant="error", key="badge_error"
        )

    with col3:
        st.markdown("**Info**")
        badge_component.render(text="Info", variant="info", key="badge_info")

    st.markdown("---")
    st.subheader("Badge-Größen")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Small**")
        badge_component.render(
            text="Small Badge", variant="default", size="sm", key="badge_sm"
        )

    with col2:
        st.markdown("**Medium (Default)**")
        badge_component.render(
            text="Medium Badge", variant="default", size="md", key="badge_md"
        )

    with col3:
        st.markdown("**Large**")
        badge_component.render(
            text="Large Badge", variant="default", size="lg", key="badge_lg"
        )

    st.markdown("---")
    st.subheader("Badge mit Icons")

    col1, col2, col3 = st.columns(3)

    with col1:
        badge_component.render(
            text="Verified", variant="success", key="badge_icon_1"
        )

    with col2:
        badge_component.render(
            text="Premium", variant="warning", key="badge_icon_2"
        )

    with col3:
        badge_component.render(
            text="New", variant="info", key="badge_icon_3"
        )

    st.markdown("---")
    st.subheader("Badge mit Dot-Indikator")

    col1, col2, col3 = st.columns(3)

    with col1:
        badge_component.render(
            text="Online", variant="success", dot=True, key="badge_dot_1"
        )

    with col2:
        badge_component.render(
            text="Away", variant="warning", dot=True, key="badge_dot_2"
        )

    with col3:
        badge_component.render(
            text="Offline", variant="error", dot=True, key="badge_dot_3"
        )

    st.markdown("---")
    st.subheader("Convenience-Funktion")
    st.code("""
from components.badge import badge

badge(
    text="Quick Badge",
    variant="success"
)
    """)

    badge(
        text="Quick Badge",
        variant="success",
        key="badge_convenience"
    )

# Tab 4: Badge Group
with tab4:
    st.header("Badge Group Komponente")
    st.markdown("""
    Die Badge-Group zeigt mehrere Badges zusammen an.
    """)

    st.subheader("Einfache Badge-Gruppe")

    group_component = BadgeGroup()
    group_component.render(
        badges=[
            {"text": "Python", "variant": "info"},
            {"text": "React", "variant": "success"},
            {"text": "TypeScript", "variant": "warning"},
            {"text": "Node.js", "variant": "default"}
        ],
        key="badge_group_1"
    )

    st.markdown("---")
    st.subheader("Badge-Gruppe mit Icons")

    group_component.render(
        badges=[
            {"text": "Verified", "variant": "success", "icon": ""},
            {"text": "Premium", "variant": "warning", "icon": ""},
            {"text": "New", "variant": "info", "icon": ""},
            {"text": "Popular", "variant": "error", "icon": ""}
        ],
        key="badge_group_2"
    )

    st.markdown("---")
    st.subheader("Badge-Gruppe mit verschiedenen Größen")

    group_component.render(
        badges=[
            {"text": "Small", "variant": "default", "size": "sm"},
            {"text": "Medium", "variant": "success", "size": "md"},
            {"text": "Large", "variant": "info", "size": "lg"}
        ],
        key="badge_group_3"
    )

    st.markdown("---")
    st.subheader("Badge-Gruppe mit Spacing")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Small Spacing**")
        group_component.render(
            badges=[
                {"text": "Tag 1", "variant": "default"},
                {"text": "Tag 2", "variant": "success"},
                {"text": "Tag 3", "variant": "info"}
            ],
            spacing="sm",
            key="badge_group_spacing_sm"
        )

    with col2:
        st.markdown("**Medium Spacing**")
        group_component.render(
            badges=[
                {"text": "Tag 1", "variant": "default"},
                {"text": "Tag 2", "variant": "success"},
                {"text": "Tag 3", "variant": "info"}
            ],
            spacing="md",
            key="badge_group_spacing_md"
        )

    with col3:
        st.markdown("**Large Spacing**")
        group_component.render(
            badges=[
                {"text": "Tag 1", "variant": "default"},
                {"text": "Tag 2", "variant": "success"},
                {"text": "Tag 3", "variant": "info"}
            ],
            spacing="lg",
            key="badge_group_spacing_lg"
        )

    st.markdown("---")
    st.subheader("Badge-Gruppe mit Wrapping")

    st.markdown("**Mit Wrapping (Standard)**")
    group_component.render(
        badges=[
            {"text": f"Tag {i}", "variant": "default"}
            for i in range(1, 21)
        ],
        wrap=True,
        key="badge_group_wrap_true"
    )

    st.markdown("**Ohne Wrapping (scrollbar)**")
    group_component.render(
        badges=[
            {"text": f"Tag {i}", "variant": "success"}
            for i in range(1, 21)
        ],
        wrap=False,
        key="badge_group_wrap_false"
    )

    st.markdown("---")
    st.subheader("Convenience-Funktion")
    st.code("""
from components.badge import badge_group

badge_group(
    badges=[
        {"text": "Python", "variant": "info"},
        {"text": "React", "variant": "success"}
    ]
)
    """)

    badge_group(
        badges=[
            {"text": "Python", "variant": "info"},
            {"text": "React", "variant": "success"},
            {"text": "TypeScript", "variant": "warning"}
        ],
        key="badge_group_convenience"
    )

# Sidebar mit Informationen
with st.sidebar:
    st.header("ℹ Informationen")
    st.markdown("""
    ### Alert Komponente
    - 4 Typen: info, success, warning, error
    - Mit/ohne Titel
    - Custom Icons
    - Dismissible

    ### AlertDialog Komponente
    - Modal-Dialog
    - Bestätigung/Abbruch
    - Callbacks
    - Verschiedene Typen

    ### Badge Komponente
    - 7 Varianten
    - 3 Größen
    - Icons
    - Dot-Indikator

    ### Badge Group
    - Mehrere Badges
    - Anpassbares Spacing
    - Wrapping-Option
    """)

    st.markdown("---")
    st.markdown("**Verwendung:**")
    st.code("""
from components import (
    Alert, AlertDialog,
    Badge, BadgeGroup
)

# oder

from components.alert import alert
from components.badge import badge
    """)
